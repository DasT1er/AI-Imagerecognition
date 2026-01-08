"""
CS2 Environment Wrapper
=======================
Gymnasium-kompatibles Interface für CS2

Erlaubt Standard RL-Libraries (Stable-Baselines3, etc.) mit CS2 zu trainieren.

State Space:
- Visual: Screenshot (84x84x3)
- Game State: HP, Armor, Ammo, Money, Time (7 dims)

Action Space:
- Discrete(20): Movement, Shooting, Economy actions
"""

import gymnasium as gym
import numpy as np
from PIL import Image
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.detector import EnemyDetector
from vision.game_state import GameStateDetector, GameState
from actions.keyboard import KeyboardController
from actions.mouse import MouseController


class CS2Environment(gym.Env):
    """
    CS2 Gym Environment

    Observation Space:
        Dict:
            - 'visual': Box(84, 84, 3) - Grayscale screenshot
            - 'game_state': Box(7,) - HP, Armor, Ammo, Money, Time, Alive
            - 'enemies': Box(5,) - Enemy count, closest dist, threat level

    Action Space:
        Discrete(20):
            0-7:   Movement (idle, forward, back, left, right, forward-left, forward-right, back-left, back-right)
            8:     Jump
            9:     Crouch
            10:    Walk
            11:    Shoot
            12:    Reload
            13-15: Switch weapon (1, 2, 3)
            16:    Buy AK47/M4A4
            17:    Buy Armor
            18:    Buy Defuse Kit
            19:    Plant/Defuse
    """

    metadata = {'render.modes': ['human']}

    def __init__(self, my_team='CT', screen_size=(84, 84)):
        """
        Initialize CS2 environment

        Args:
            my_team: 'CT' or 'T'
            screen_size: Size for visual observation
        """
        super().__init__()

        self.my_team = my_team
        self.screen_size = screen_size

        # Initialize detectors and controllers
        self.enemy_detector = EnemyDetector(my_team=my_team)
        self.game_state_detector = GameStateDetector()
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

        # Observation space
        self.observation_space = gym.spaces.Dict({
            'visual': gym.spaces.Box(
                low=0, high=255,
                shape=(*screen_size, 3),
                dtype=np.uint8
            ),
            'game_state': gym.spaces.Box(
                low=0, high=1,
                shape=(7,),
                dtype=np.float32
            ),
            'enemies': gym.spaces.Box(
                low=0, high=10,
                shape=(5,),
                dtype=np.float32
            )
        })

        # Action space
        self.action_space = gym.spaces.Discrete(20)

        # State
        self.current_state = None
        self.last_state = None
        self.step_count = 0
        self.episode_kills = 0
        self.episode_deaths = 0
        self.last_hp = 100

        print(f"🎮 CS2 Environment initialized")
        print(f"   Team: {my_team}")
        print(f"   Screen Size: {screen_size}")
        print(f"   Action Space: {self.action_space.n} actions")

    def reset(self, seed=None, options=None):
        """
        Reset environment

        Returns:
            observation, info
        """
        super().reset(seed=seed)

        # Release all keys
        self.keyboard.release_all()

        # Reset episode stats
        self.step_count = 0
        self.episode_kills = 0
        self.episode_deaths = 0
        self.last_hp = 100

        # Get initial observation
        obs = self._get_observation()
        self.current_state = obs

        info = {
            'kills': 0,
            'deaths': 0,
            'round_time': 115.0
        }

        return obs, info

    def step(self, action):
        """
        Execute action

        Args:
            action: int (0-19)

        Returns:
            observation, reward, terminated, truncated, info
        """
        # Execute action
        self._execute_action(action)

        # Wait for action to take effect
        time.sleep(0.05)  # 50ms = 20 FPS

        # Get new observation
        self.last_state = self.current_state
        obs = self._get_observation()
        self.current_state = obs

        # Calculate reward
        reward = self._calculate_reward()

        # Check if episode is done
        terminated = self._is_terminated()
        truncated = self.step_count >= 2300  # 115s at 20 FPS

        self.step_count += 1

        # Info
        info = {
            'kills': self.episode_kills,
            'deaths': self.episode_deaths,
            'step': self.step_count
        }

        return obs, reward, terminated, truncated, info

    def _get_observation(self):
        """Get current observation"""
        from PIL import ImageGrab

        # Capture screenshot
        screenshot = ImageGrab.grab()

        # Visual observation (downscaled)
        visual = screenshot.resize(self.screen_size, Image.Resampling.LANCZOS)
        visual_array = np.array(visual, dtype=np.uint8)

        # Game state
        game_state = self.game_state_detector.detect(screenshot)
        game_state_vector = self.game_state_detector.get_state_vector(game_state)

        # Enemy detection
        screenshot_np = np.array(screenshot)
        detections = self.enemy_detector.detect(screenshot_np, my_team=self.my_team)

        # Enemy features
        enemy_count = min(len(detections), 5)  # Max 5
        closest_enemy = self.enemy_detector.get_closest_enemy(detections)
        threat_level = self.enemy_detector.get_threat_level(detections) / 10.0  # Normalize

        if closest_enemy:
            closest_dist = np.linalg.norm(
                np.array(closest_enemy['center']) - np.array([960, 540])
            ) / 1000.0  # Normalize
            closest_is_head = 1.0 if closest_enemy['is_head'] else 0.0
        else:
            closest_dist = 1.0  # Max distance
            closest_is_head = 0.0

        enemies_vector = np.array([
            enemy_count / 5.0,      # 0-1
            closest_dist,           # 0-1
            closest_is_head,        # 0-1
            threat_level,           # 0-1
            1.0 if enemy_count > 0 else 0.0  # Has enemies visible
        ], dtype=np.float32)

        return {
            'visual': visual_array,
            'game_state': game_state_vector,
            'enemies': enemies_vector
        }

    def _execute_action(self, action):
        """
        Execute discrete action

        Actions:
            0-7:   Movement
            8:     Jump
            9:     Crouch
            10:    Walk
            11:    Shoot
            12:    Reload
            13-15: Switch weapon
            16-19: Economy actions
        """
        # Release previous movement keys
        self.keyboard.release_all()

        # Movement (0-7)
        if action == 0:
            # Idle
            pass
        elif action == 1:
            # Forward
            self.keyboard.move(forward=1.0)
        elif action == 2:
            # Back
            self.keyboard.move(forward=-1.0)
        elif action == 3:
            # Left
            self.keyboard.move(strafe=-1.0)
        elif action == 4:
            # Right
            self.keyboard.move(strafe=1.0)
        elif action == 5:
            # Forward-left
            self.keyboard.move(forward=1.0, strafe=-1.0)
        elif action == 6:
            # Forward-right
            self.keyboard.move(forward=1.0, strafe=1.0)
        elif action == 7:
            # Back-left
            self.keyboard.move(forward=-1.0, strafe=-1.0)

        # Jump
        elif action == 8:
            self.keyboard.move(jump=True)

        # Crouch
        elif action == 9:
            self.keyboard.move(crouch=True)

        # Walk
        elif action == 10:
            self.keyboard.move(walk=True)

        # Shoot
        elif action == 11:
            # Aim at closest enemy if visible
            if self.current_state and self.current_state['enemies'][4] > 0.5:
                # Enemy visible, aim at them
                from PIL import ImageGrab
                screenshot = ImageGrab.grab()
                detections = self.enemy_detector.detect(np.array(screenshot), my_team=self.my_team)
                closest = self.enemy_detector.get_closest_enemy(detections)

                if closest:
                    target_pos = closest['center']
                    self.mouse.aim_at_target(target_pos, smooth=False)

            self.mouse.shoot()

        # Reload
        elif action == 12:
            self.keyboard.reload()

        # Switch weapon
        elif action == 13:
            self.keyboard.switch_weapon(1)
        elif action == 14:
            self.keyboard.switch_weapon(2)
        elif action == 15:
            self.keyboard.switch_weapon(3)

        # Economy actions (simplified - just press B and numbers)
        elif action == 16:
            # Buy AK47/M4A4
            self.keyboard.press('b')
            time.sleep(0.1)
            self.keyboard.press('4')
            time.sleep(0.1)
            self.keyboard.press('2')
        elif action == 17:
            # Buy Armor
            self.keyboard.press('b')
            time.sleep(0.1)
            self.keyboard.press('6')
        elif action == 18:
            # Buy Defuse Kit (CT only)
            if self.my_team == 'CT':
                self.keyboard.press('b')
                time.sleep(0.1)
                self.keyboard.press('8')
        elif action == 19:
            # Plant/Defuse
            self.keyboard.use()

    def _calculate_reward(self):
        """
        Calculate reward for current step

        Reward components:
            - Kill: +10
            - Damage dealt: +0.1 per HP
            - Damage taken: -0.1 per HP
            - Death: -5
            - Round win: +20
            - Headshot: +2 (bonus)
        """
        reward = 0.0

        if not self.current_state or not self.last_state:
            return reward

        current_game_state = self.current_state['game_state']
        last_game_state = self.last_state['game_state']

        current_hp = current_game_state[0] * 100
        last_hp = last_game_state[0] * 100

        # Damage taken
        hp_loss = last_hp - current_hp
        if hp_loss > 0:
            reward -= hp_loss * 0.1

        # Death
        if current_game_state[6] < 0.5 and last_game_state[6] > 0.5:
            reward -= 5.0
            self.episode_deaths += 1

        # Enemy count reduction (proxy for kills)
        current_enemies = self.current_state['enemies'][0] * 5
        last_enemies = self.last_state['enemies'][0] * 5

        if last_enemies > current_enemies:
            # Possible kill
            reward += 10.0
            self.episode_kills += 1

        # Small reward for aiming at enemies
        if self.current_state['enemies'][4] > 0.5:  # Enemy visible
            reward += 0.1

        # Penalty for wasting time (encourage action)
        reward -= 0.01

        return reward

    def _is_terminated(self):
        """Check if episode is done"""
        if not self.current_state:
            return False

        game_state = self.current_state['game_state']

        # Dead
        if game_state[6] < 0.5:
            return True

        # Time up
        if game_state[5] < 0.05:  # < 5s remaining
            return True

        return False

    def render(self, mode='human'):
        """Render environment (not implemented)"""
        pass

    def close(self):
        """Clean up"""
        self.keyboard.release_all()


if __name__ == "__main__":
    """Test environment"""
    print("\n" + "="*60)
    print("  CS2 ENVIRONMENT TEST")
    print("="*60 + "\n")
    print("Testing random actions in CS2...\n")

    env = CS2Environment(my_team='CT')

    print("Resetting environment...")
    obs, info = env.reset()

    print("Observation space:")
    print(f"  Visual: {obs['visual'].shape}")
    print(f"  Game State: {obs['game_state'].shape}")
    print(f"  Enemies: {obs['enemies'].shape}")

    print("\nExecuting 10 random actions...")
    for i in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)

        print(f"  Step {i+1}: Action={action}, Reward={reward:.2f}, "
              f"Terminated={terminated}, Info={info}")

        if terminated or truncated:
            break

        time.sleep(0.5)

    env.close()
    print("\n✅ Test beendet!")

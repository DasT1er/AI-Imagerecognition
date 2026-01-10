"""
Minecraft Hierarchical Environment
===================================
Simplified Gym wrapper for MineRL with hierarchical RL support.

Simplifies:
- Action space (continuous → discrete)
- Observation space (only important features)
- Reward shaping (dense rewards!)
"""

import gym
import numpy as np
from collections import deque

try:
    import minerl
    MINERL_AVAILABLE = True
except ImportError:
    MINERL_AVAILABLE = False
    print("⚠️  MineRL not available. Install with: pip install minerl")


class MinecraftHierarchicalEnv(gym.Env):
    """
    Simplified Minecraft environment for Hierarchical RL

    Features:
    - Discrete action space (14 actions)
    - Simplified observations (POV + inventory + position)
    - Dense reward shaping
    - Frame skipping for faster training
    """

    # Action mapping
    ACTION_NAMES = [
        "noop",          # 0
        "forward",       # 1
        "back",          # 2
        "left",          # 3
        "right",         # 4
        "jump",          # 5
        "attack",        # 6
        "forward_attack",# 7 (mine!)
        "forward_jump",  # 8
        "camera_up",     # 9
        "camera_down",   # 10
        "camera_left",   # 11
        "camera_right",  # 12
        "sneak"          # 13
    ]

    def __init__(
        self,
        base_env='MineRLTreechop-v0',
        frame_skip=4,
        reward_shaping=True
    ):
        """
        Initialize Minecraft environment

        Args:
            base_env: MineRL environment name
            frame_skip: Execute same action N times (faster training)
            reward_shaping: Apply dense reward shaping
        """
        if not MINERL_AVAILABLE:
            raise ImportError("MineRL not installed!")

        self.base_env_name = base_env
        self.env = gym.make(base_env)
        self.frame_skip = frame_skip
        self.reward_shaping = reward_shaping

        # Action space (discrete!)
        self.action_space = gym.spaces.Discrete(len(self.ACTION_NAMES))

        # Observation space
        self.observation_space = gym.spaces.Dict({
            'pov': gym.spaces.Box(
                low=0, high=255,
                shape=(64, 64, 3),
                dtype=np.uint8
            ),
            'inventory_vector': gym.spaces.Box(
                low=0, high=100,
                shape=(10,),
                dtype=np.float32
            ),
            'position': gym.spaces.Box(
                low=-1000, high=1000,
                shape=(3,),
                dtype=np.float32
            )
        })

        # State tracking for reward shaping
        self.prev_inventory = {}
        self.step_count = 0

        print(f"🎮 Minecraft Environment initialized")
        print(f"   Base: {base_env}")
        print(f"   Actions: {len(self.ACTION_NAMES)}")
        print(f"   Frame skip: {frame_skip}")

    def _discretize_action(self, discrete_action):
        """
        Convert discrete action (0-13) to MineRL action dict

        Args:
            discrete_action: int (0-13)

        Returns:
            MineRL action dict
        """
        # Start with noop
        action = self.env.action_space.noop()

        action_name = self.ACTION_NAMES[discrete_action]

        if action_name == "forward":
            action['forward'] = 1
        elif action_name == "back":
            action['back'] = 1
        elif action_name == "left":
            action['left'] = 1
        elif action_name == "right":
            action['right'] = 1
        elif action_name == "jump":
            action['jump'] = 1
        elif action_name == "attack":
            action['attack'] = 1
        elif action_name == "forward_attack":
            action['forward'] = 1
            action['attack'] = 1
        elif action_name == "forward_jump":
            action['forward'] = 1
            action['jump'] = 1
        elif action_name == "camera_up":
            action['camera'] = np.array([0, 15], dtype=np.float32)
        elif action_name == "camera_down":
            action['camera'] = np.array([0, -15], dtype=np.float32)
        elif action_name == "camera_left":
            action['camera'] = np.array([-15, 0], dtype=np.float32)
        elif action_name == "camera_right":
            action['camera'] = np.array([15, 0], dtype=np.float32)
        elif action_name == "sneak":
            action['sneak'] = 1

        return action

    def _simplify_observation(self, obs):
        """
        Simplify MineRL observation to essential features

        Args:
            obs: Full MineRL observation

        Returns:
            Simplified dict with pov, inventory_vector, position
        """
        # POV (screenshot)
        pov = obs['pov']

        # Inventory → vector (10 most important items)
        inventory_vector = np.zeros(10, dtype=np.float32)
        important_items = [
            'log', 'planks', 'stick', 'cobblestone',
            'dirt', 'stone', 'coal', 'iron_ore',
            'crafting_table', 'furnace'
        ]

        for i, item in enumerate(important_items):
            if item in obs.get('inventory', {}):
                inventory_vector[i] = float(obs['inventory'][item])

        # Position (if available)
        position = np.zeros(3, dtype=np.float32)
        if 'location_stats' in obs:
            position[0] = obs['location_stats'].get('xpos', 0)
            position[1] = obs['location_stats'].get('ypos', 0)
            position[2] = obs['location_stats'].get('zpos', 0)

        return {
            'pov': pov,
            'inventory_vector': inventory_vector,
            'position': position
        }

    def _shape_reward(self, base_reward, obs, action_name):
        """
        Dense reward shaping for faster learning

        Rewards:
        - Collecting items (logs, stone, etc.)
        - Moving forward (exploration)
        - Attacking (mining attempts)

        Args:
            base_reward: Original MineRL reward
            obs: Current observation
            action_name: Name of executed action

        Returns:
            Shaped reward (float)
        """
        if not self.reward_shaping:
            return base_reward

        reward = base_reward * 10.0  # Scale base reward

        # Reward for collecting new items
        current_inventory = obs.get('inventory', {})

        for item, count in current_inventory.items():
            prev_count = self.prev_inventory.get(item, 0)
            if count > prev_count:
                # New item collected!
                delta = count - prev_count

                # Different items have different values
                if 'log' in item:
                    reward += delta * 1.0  # Logs are valuable
                elif 'planks' in item:
                    reward += delta * 0.5
                elif 'stone' in item or 'cobblestone' in item:
                    reward += delta * 0.8
                elif 'stick' in item:
                    reward += delta * 0.3
                else:
                    reward += delta * 0.2  # Any item is good

        # Small reward for attacking (mining attempts)
        if action_name == "attack" or action_name == "forward_attack":
            reward += 0.01

        # Small reward for moving (exploration)
        if action_name in ["forward", "forward_jump", "forward_attack"]:
            reward += 0.005

        # Update previous inventory
        self.prev_inventory = current_inventory.copy()

        return reward

    def reset(self):
        """Reset environment"""
        obs = self.env.reset()
        simplified_obs = self._simplify_observation(obs)

        # Reset state
        self.prev_inventory = obs.get('inventory', {}).copy()
        self.step_count = 0

        return simplified_obs

    def step(self, discrete_action):
        """
        Execute action with frame skipping

        Args:
            discrete_action: int (0-13)

        Returns:
            observation, reward, done, info
        """
        # Convert to MineRL action
        action = self._discretize_action(discrete_action)
        action_name = self.ACTION_NAMES[discrete_action]

        # Execute with frame skip
        total_reward = 0.0
        final_obs = None

        for _ in range(self.frame_skip):
            obs, reward, done, info = self.env.step(action)
            total_reward += reward
            final_obs = obs

            if done:
                break

        # Simplify observation
        simplified_obs = self._simplify_observation(final_obs)

        # Reward shaping
        shaped_reward = self._shape_reward(total_reward, final_obs, action_name)

        self.step_count += 1

        # Add action name to info (for debugging)
        info['action_name'] = action_name
        info['step'] = self.step_count

        return simplified_obs, shaped_reward, done, info

    def render(self, mode='human'):
        """Render environment (if supported)"""
        return self.env.render(mode)

    def close(self):
        """Close environment"""
        self.env.close()


def test_environment():
    """Test the environment"""
    print("\n" + "="*60)
    print("  TESTING MINECRAFT HIERARCHICAL ENVIRONMENT")
    print("="*60 + "\n")

    # Create environment
    env = MinecraftHierarchicalEnv(frame_skip=4)

    # Reset
    print("Resetting environment...")
    obs = env.reset()

    print(f"\n📊 Observation:")
    print(f"   POV shape: {obs['pov'].shape}")
    print(f"   Inventory vector: {obs['inventory_vector']}")
    print(f"   Position: {obs['position']}")

    print(f"\n🎮 Taking 20 random actions...")
    total_reward = 0

    for i in range(20):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)

        total_reward += reward

        print(f"   Step {i+1}: action={env.ACTION_NAMES[action]}, "
              f"reward={reward:.3f}, done={done}")

        if done:
            print("   Episode finished! Resetting...")
            obs = env.reset()
            total_reward = 0

    print(f"\n✅ Test complete! Total reward: {total_reward:.3f}")
    env.close()


if __name__ == "__main__":
    test_environment()

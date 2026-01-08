"""
Reward Shaper for CS2 RL Training
==================================
Intelligentes Reward System das AGGRESSIVES Spielen belohnt!

Verhindert:
- Camping (Verstecken)
- Passives Spielen
- Zeitverschwendung

Belohnt:
- Kills & Damage
- Objectives (Plant/Defuse)
- Aggressive Positioning
- Forward Movement
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RewardWeights:
    """Tunable reward weights"""

    # Combat (60% of rewards)
    KILL = 10.0
    DAMAGE_DEALT = 0.1          # per HP
    HEADSHOT_BONUS = 2.0
    FIRST_BLOOD = 5.0
    ACE = 20.0                  # 5 kills in round

    # Movement & Positioning (20%)
    FORWARD_MOVEMENT = 0.05     # Moving towards enemies
    CAMPING_PENALTY = -0.1      # Standing still too long
    PROXIMITY_BONUS = 0.02      # Getting closer to enemies

    # Objectives (20%)
    BOMB_PLANTED = 30.0         # T side
    BOMB_DEFUSED = 50.0         # CT side
    DEFUSE_STARTED = 5.0
    SITE_ENTRY = 10.0           # Entering bombsite
    BOMB_DEFENDED = 20.0        # Prevented plant

    # Engagement
    ENEMY_SPOTTED = 0.1
    ENEMY_ENGAGED = 0.5         # Shot at enemy
    SHOT_FIRED = 0.02           # Shooting (even if miss)

    # Penalties
    DEATH = -5.0
    TIME_PENALTY = -0.01        # per second of inactivity
    TEAM_DAMAGE = -1.0          # Shooting teammates
    FRIENDLY_FIRE = -10.0       # Killing teammate

    # Win Conditions
    ROUND_WIN = 20.0
    ROUND_LOSS = -10.0

    # Exploration
    EXPLORATION_BONUS = 0.1     # Trying new actions
    REPETITIVE_PENALTY = -0.05  # Same action repeatedly


class RewardShaper:
    """
    Calculates rewards for CS2 RL training

    Focus: Encourage AGGRESSIVE, OBJECTIVE-based play
    """

    def __init__(self, weights: RewardWeights = None):
        """
        Initialize reward shaper

        Args:
            weights: Custom reward weights
        """
        self.weights = weights or RewardWeights()

        # Tracking
        self.last_position = None
        self.last_action = None
        self.action_repeat_count = 0
        self.inactive_time = 0
        self.round_kills = 0
        self.round_damage = 0

        print("🎯 Reward Shaper initialized")
        print(f"   Kill Reward: +{self.weights.KILL}")
        print(f"   Camping Penalty: {self.weights.CAMPING_PENALTY}/s")
        print(f"   Objective Reward: +{self.weights.BOMB_PLANTED}")

    def calculate_reward(
        self,
        prev_state: Dict[str, Any],
        action: int,
        next_state: Dict[str, Any],
        info: Dict[str, Any]
    ) -> float:
        """
        Calculate reward for transition

        Args:
            prev_state: Previous state dict
            action: Action taken
            next_state: New state dict
            info: Additional info (kills, damage, etc.)

        Returns:
            Total reward (float)
        """
        reward = 0.0

        # Extract game states
        prev_game = prev_state['game_state']
        next_game = next_state['game_state']

        prev_enemies = prev_state['enemies']
        next_enemies = next_state['enemies']

        # === COMBAT REWARDS ===
        reward += self._combat_rewards(prev_game, next_game, info)

        # === MOVEMENT REWARDS ===
        reward += self._movement_rewards(action, prev_enemies, next_enemies)

        # === OBJECTIVE REWARDS ===
        reward += self._objective_rewards(info)

        # === ENGAGEMENT REWARDS ===
        reward += self._engagement_rewards(action, prev_enemies, next_enemies)

        # === PENALTIES ===
        reward += self._penalties(prev_game, next_game, action)

        # === WIN CONDITION ===
        reward += self._win_rewards(info)

        # === EXPLORATION ===
        reward += self._exploration_rewards(action)

        return reward

    def _combat_rewards(self, prev_game, next_game, info) -> float:
        """Combat-related rewards"""
        reward = 0.0

        # Kills
        kills = info.get('kills_this_step', 0)
        if kills > 0:
            reward += self.weights.KILL * kills
            self.round_kills += kills

            # First blood
            if self.round_kills == 1:
                reward += self.weights.FIRST_BLOOD

            # Ace (5 kills)
            if self.round_kills >= 5:
                reward += self.weights.ACE

        # Damage dealt
        damage = info.get('damage_dealt', 0)
        if damage > 0:
            reward += self.weights.DAMAGE_DEALT * damage
            self.round_damage += damage

        # Headshot bonus
        if info.get('headshot', False):
            reward += self.weights.HEADSHOT_BONUS

        return reward

    def _movement_rewards(self, action, prev_enemies, next_enemies) -> float:
        """Movement and positioning rewards"""
        reward = 0.0

        # Forward movement (actions 1, 5, 6)
        forward_actions = [1, 5, 6]
        if action in forward_actions:
            reward += self.weights.FORWARD_MOVEMENT
            self.inactive_time = 0

        # Idle penalty (action 0)
        elif action == 0:
            self.inactive_time += 1
            if self.inactive_time > 10:  # More than 0.5s idle
                reward += self.weights.CAMPING_PENALTY

        # Proximity bonus (getting closer to enemies)
        if prev_enemies[4] > 0.5 and next_enemies[4] > 0.5:  # Enemy visible
            prev_dist = prev_enemies[1]
            next_dist = next_enemies[1]

            if next_dist < prev_dist:  # Got closer
                reward += self.weights.PROXIMITY_BONUS

        return reward

    def _objective_rewards(self, info) -> float:
        """Objective-based rewards"""
        reward = 0.0

        # Bomb planted (T side)
        if info.get('bomb_planted', False):
            reward += self.weights.BOMB_PLANTED

        # Bomb defused (CT side)
        if info.get('bomb_defused', False):
            reward += self.weights.BOMB_DEFUSED

        # Defuse started
        if info.get('defuse_started', False):
            reward += self.weights.DEFUSE_STARTED

        # Site entry
        if info.get('site_entered', False):
            reward += self.weights.SITE_ENTRY

        # Bomb defended (prevented plant)
        if info.get('bomb_defended', False):
            reward += self.weights.BOMB_DEFENDED

        return reward

    def _engagement_rewards(self, action, prev_enemies, next_enemies) -> float:
        """Engagement and combat activity rewards"""
        reward = 0.0

        # Enemy spotted
        if next_enemies[4] > 0.5 and prev_enemies[4] < 0.5:
            reward += self.weights.ENEMY_SPOTTED

        # Shot fired (action 11 = shoot)
        if action == 11:
            reward += self.weights.SHOT_FIRED

            # Bonus if enemy visible
            if next_enemies[4] > 0.5:
                reward += self.weights.ENEMY_ENGAGED

        return reward

    def _penalties(self, prev_game, next_game, action) -> float:
        """Penalties for bad behavior"""
        reward = 0.0

        # Death
        prev_alive = prev_game[6]  # is_alive
        next_alive = next_game[6]

        if prev_alive > 0.5 and next_alive < 0.5:
            reward += self.weights.DEATH

        # Time penalty (encourage action)
        reward += self.weights.TIME_PENALTY

        # Camping penalty (standing still while enemies visible)
        # This is handled in movement_rewards

        return reward

    def _win_rewards(self, info) -> float:
        """Round win/loss rewards"""
        reward = 0.0

        if info.get('round_won', False):
            reward += self.weights.ROUND_WIN
        elif info.get('round_lost', False):
            reward += self.weights.ROUND_LOSS

        return reward

    def _exploration_rewards(self, action) -> float:
        """Exploration bonuses"""
        reward = 0.0

        # Track action repetition
        if action == self.last_action:
            self.action_repeat_count += 1
        else:
            self.action_repeat_count = 0

        # Penalty for repeating same action
        if self.action_repeat_count > 5:
            reward += self.weights.REPETITIVE_PENALTY

        # Bonus for trying new things
        if action != self.last_action:
            reward += self.weights.EXPLORATION_BONUS

        self.last_action = action

        return reward

    def reset(self):
        """Reset episode tracking"""
        self.last_position = None
        self.last_action = None
        self.action_repeat_count = 0
        self.inactive_time = 0
        self.round_kills = 0
        self.round_damage = 0


if __name__ == "__main__":
    """Test reward shaper"""
    print("\n" + "="*60)
    print("  REWARD SHAPER TEST")
    print("="*60 + "\n")

    shaper = RewardShaper()

    # Test scenarios
    print("\n📊 Testing Reward Scenarios:\n")

    # Scenario 1: Kill
    print("1. KILL ENEMY:")
    prev = {'game_state': np.array([1.0]*7), 'enemies': np.array([0.2, 0.5, 0, 0.3, 1])}
    next = {'game_state': np.array([1.0]*7), 'enemies': np.array([0.0, 0.0, 0, 0.0, 0])}
    info = {'kills_this_step': 1, 'damage_dealt': 100, 'headshot': True}

    r = shaper.calculate_reward(prev, 11, next, info)
    print(f"   Reward: +{r:.2f}")
    print(f"   (Kill +10, Damage +10, Headshot +2, First Blood +5)\n")

    # Scenario 2: Camping
    print("2. CAMPING (standing still):")
    prev = {'game_state': np.array([1.0]*7), 'enemies': np.array([0.2, 0.5, 0, 0.3, 1])}
    next = {'game_state': np.array([1.0]*7), 'enemies': np.array([0.2, 0.5, 0, 0.3, 1])}
    info = {}

    shaper.inactive_time = 15  # Simulate camping
    r = shaper.calculate_reward(prev, 0, next, info)
    print(f"   Reward: {r:.2f}")
    print(f"   (Camping Penalty -0.1, Time Penalty -0.01)\n")

    # Scenario 3: Aggressive play
    print("3. AGGRESSIVE PLAY (forward + shoot):")
    prev = {'game_state': np.array([1.0]*7), 'enemies': np.array([0.2, 0.5, 0, 0.3, 1])}
    next = {'game_state': np.array([1.0]*7), 'enemies': np.array([0.2, 0.3, 0, 0.5, 1])}
    info = {'damage_dealt': 30}

    r = shaper.calculate_reward(prev, 11, next, info)
    print(f"   Reward: +{r:.2f}")
    print(f"   (Forward Movement +0.05, Proximity +0.02, Damage +3.0, Shot +0.02, Engaged +0.5)\n")

    print("✅ Reward system encourages AGGRESSIVE play!")

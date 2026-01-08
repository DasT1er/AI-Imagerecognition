"""
Hybrid PPO + Imitation Learning Trainer
========================================
BESTE Methode: Kombiniert beide Approaches!

1. Startet mit Imitation Learning Model (von DIR!)
2. Verbessert sich mit PPO (Reinforcement Learning)
3. Nutzt intelligentes Reward System (Anti-Camping)

Resultat: Bot der wie DU startet, dann BESSER wird!
"""

import torch
import numpy as np
import os
import sys
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecFrameStack
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import gymnasium as gym
import torch.nn as nn

# Add to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from environment.cs2_env import CS2Environment
from reinforcement.reward_shaper import RewardShaper
from imitation.train_imitation import ImitationNetwork


class ImitationFeatureExtractor(BaseFeaturesExtractor):
    """
    Feature extractor that uses pre-trained Imitation Learning CNN

    This allows us to BOOTSTRAP from human gameplay!
    """

    def __init__(self, observation_space: gym.spaces.Dict, features_dim: int = 512):
        """
        Initialize feature extractor

        Args:
            observation_space: Observation space
            features_dim: Output feature dimension
        """
        super().__init__(observation_space, features_dim)

        # CNN for visual input (from imitation model)
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=8, stride=4, padding=2),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten()
        )

        # Calculate CNN output size
        with torch.no_grad():
            sample = torch.zeros(1, 3, 84, 84)
            cnn_out_size = self.cnn(sample).shape[1]

        # Game state FC
        game_state_size = 7  # HP, armor, ammo, money, time, alive
        enemies_size = 5     # Enemy count, dist, threat, etc.

        # Combine all features
        total_size = cnn_out_size + game_state_size + enemies_size

        # Feature combiner
        self.combiner = nn.Sequential(
            nn.Linear(total_size, features_dim),
            nn.ReLU()
        )

    def forward(self, observations) -> torch.Tensor:
        """
        Extract features from observations

        Args:
            observations: Dict with 'visual', 'game_state', 'enemies'

        Returns:
            Feature tensor [B, features_dim]
        """
        # Visual features
        visual = observations['visual'].float() / 255.0
        visual_features = self.cnn(visual)

        # Game state features
        game_state = observations['game_state']
        enemies = observations['enemies']

        # Concatenate all
        combined = torch.cat([visual_features, game_state, enemies], dim=1)

        # Final features
        features = self.combiner(combined)

        return features


class RewardShapingWrapper(gym.Wrapper):
    """Wrapper that applies reward shaping"""

    def __init__(self, env):
        super().__init__(env)
        self.reward_shaper = RewardShaper()
        self.prev_state = None

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        self.prev_state = obs
        self.reward_shaper.reset()
        return obs, info

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)

        # Apply reward shaping
        if self.prev_state is not None:
            shaped_reward = self.reward_shaper.calculate_reward(
                self.prev_state,
                action,
                obs,
                info
            )
        else:
            shaped_reward = reward

        self.prev_state = obs

        return obs, shaped_reward, terminated, truncated, info


class TrainingCallback(BaseCallback):
    """Callback for logging training progress"""

    def __init__(self, check_freq: int = 1000, verbose=1):
        super().__init__(verbose)
        self.check_freq = check_freq
        self.episode_rewards = []
        self.episode_lengths = []

    def _on_step(self) -> bool:
        # Log episode info
        for info in self.locals.get('infos', []):
            if 'episode' in info:
                self.episode_rewards.append(info['episode']['r'])
                self.episode_lengths.append(info['episode']['l'])

        # Print progress
        if self.n_calls % self.check_freq == 0:
            if len(self.episode_rewards) > 0:
                mean_reward = np.mean(self.episode_rewards[-100:])
                mean_length = np.mean(self.episode_lengths[-100:])

                print(f"\n{'='*60}")
                print(f"  Step: {self.n_calls}")
                print(f"  Episodes: {len(self.episode_rewards)}")
                print(f"  Mean Reward (last 100): {mean_reward:.2f}")
                print(f"  Mean Length (last 100): {mean_length:.0f}")
                print(f"{'='*60}\n")

        return True


class HybridPPOTrainer:
    """
    Hybrid trainer that combines Imitation Learning + PPO

    Workflow:
    1. Load pre-trained imitation model (optional)
    2. Initialize PPO with those weights
    3. Fine-tune with RL
    """

    def __init__(
        self,
        env: gym.Env,
        imitation_model_path: str = None,
        learning_rate: float = 3e-4,
        n_steps: int = 2048,
        batch_size: int = 64,
        n_epochs: int = 10,
        gamma: float = 0.99,
        device: str = 'auto'
    ):
        """
        Initialize hybrid trainer

        Args:
            env: CS2 Environment
            imitation_model_path: Path to pre-trained imitation model
            learning_rate: Learning rate
            n_steps: Steps per update
            batch_size: Batch size
            n_epochs: PPO epochs
            gamma: Discount factor
            device: 'cuda', 'cpu', or 'auto'
        """
        self.env = env
        self.imitation_model_path = imitation_model_path

        print("\n" + "="*60)
        print("  HYBRID PPO + IMITATION TRAINER")
        print("="*60 + "\n")

        # Policy kwargs
        policy_kwargs = dict(
            features_extractor_class=ImitationFeatureExtractor,
            features_extractor_kwargs=dict(features_dim=512),
            net_arch=[dict(pi=[256, 256], vf=[256, 256])]
        )

        # Create PPO model
        self.model = PPO(
            "MultiInputPolicy",
            env,
            learning_rate=learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            n_epochs=n_epochs,
            gamma=gamma,
            policy_kwargs=policy_kwargs,
            verbose=1,
            device=device,
            tensorboard_log="./logs/ppo_tensorboard/"
        )

        # Load imitation weights if available
        if imitation_model_path and os.path.exists(imitation_model_path):
            print(f"📦 Loading imitation model: {imitation_model_path}")
            self._load_imitation_weights(imitation_model_path)
            print("✅ Imitation weights loaded! Bot starts with YOUR knowledge!\n")
        else:
            print("⚠️  No imitation model found. Starting from scratch.\n")

    def _load_imitation_weights(self, model_path: str):
        """
        Load CNN weights from imitation model into PPO policy

        This is the MAGIC that makes the bot start smart!
        """
        # Load imitation checkpoint
        checkpoint = torch.load(model_path, map_location=self.model.device)
        imitation_state = checkpoint['model_state_dict']

        # Get PPO policy
        ppo_state = self.model.policy.state_dict()

        # Transfer CNN weights
        # Imitation model uses 'cnn' prefix, PPO uses 'features_extractor.cnn'
        for key in imitation_state.keys():
            if key.startswith('cnn.'):
                ppo_key = 'features_extractor.' + key

                if ppo_key in ppo_state:
                    ppo_state[ppo_key] = imitation_state[key]
                    print(f"   ✓ Transferred: {key} → {ppo_key}")

        # Load updated state
        self.model.policy.load_state_dict(ppo_state)

    def train(
        self,
        total_timesteps: int = 1000000,
        save_freq: int = 10000,
        save_path: str = "../../models/ppo_checkpoints"
    ):
        """
        Train PPO agent

        Args:
            total_timesteps: Total training steps
            save_freq: Save checkpoint every N steps
            save_path: Where to save checkpoints
        """
        print(f"🚀 Starting PPO training for {total_timesteps:,} steps...\n")

        # Callbacks
        checkpoint_callback = CheckpointCallback(
            save_freq=save_freq,
            save_path=save_path,
            name_prefix="ppo_cs2"
        )

        training_callback = TrainingCallback(check_freq=1000)

        # Train
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=[checkpoint_callback, training_callback],
            tb_log_name="ppo_hybrid"
        )

        print("\n✅ Training complete!")

        # Save final model
        final_path = "../../models/ppo_final.zip"
        self.model.save(final_path)
        print(f"💾 Final model saved: {final_path}\n")

    def evaluate(self, n_episodes: int = 10):
        """Evaluate trained model"""
        print(f"\n📊 Evaluating for {n_episodes} episodes...\n")

        episode_rewards = []

        for ep in range(n_episodes):
            obs, _ = self.env.reset()
            done = False
            total_reward = 0

            while not done:
                action, _ = self.model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                total_reward += reward

            episode_rewards.append(total_reward)
            print(f"  Episode {ep+1}/{n_episodes}: Reward = {total_reward:.2f}")

        mean_reward = np.mean(episode_rewards)
        std_reward = np.std(episode_rewards)

        print(f"\n📈 Evaluation Results:")
        print(f"   Mean Reward: {mean_reward:.2f} ± {std_reward:.2f}")
        print(f"   Min: {np.min(episode_rewards):.2f}")
        print(f"   Max: {np.max(episode_rewards):.2f}\n")


def make_env(my_team='CT'):
    """Create wrapped environment"""
    env = CS2Environment(my_team=my_team)
    env = RewardShapingWrapper(env)
    return env


if __name__ == "__main__":
    """Train hybrid PPO agent"""
    print("\n" + "="*60)
    print("  HYBRID PPO TRAINING")
    print("="*60 + "\n")

    print("Instructions:")
    print("  1. Optional: Train imitation model first (train_imitation.py)")
    print("  2. This script will load it and improve via PPO")
    print("  3. Bot learns to play BETTER than human!\n")

    # Team selection
    print("Welches Team?")
    print("  [1] CT (Counter-Terrorists)")
    print("  [2] T (Terrorists)")

    choice = input("\nWähle (1 oder 2): ").strip()
    my_team = 'T' if choice == '2' else 'CT'

    print(f"\n✅ Team: {my_team}\n")

    # Create environment
    env = make_env(my_team=my_team)
    env = DummyVecEnv([lambda: env])

    # Check for imitation model
    imitation_path = "../../models/best_model.pt"

    if os.path.exists(imitation_path):
        print(f"✅ Found imitation model: {imitation_path}")
        print("   Bot will start with YOUR knowledge and improve!\n")
    else:
        print(f"⚠️  No imitation model found: {imitation_path}")
        print("   Bot will learn from scratch (slower but works!)\n")

    use_imitation = input("Use imitation model? (y/n): ").strip().lower()

    if use_imitation == 'y' and os.path.exists(imitation_path):
        imitation_model = imitation_path
    else:
        imitation_model = None

    # Create trainer
    trainer = HybridPPOTrainer(
        env=env,
        imitation_model_path=imitation_model,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64
    )

    # Train
    print("\nStarte Training...")
    print("WICHTIG: CS2 muss LAUFEN (gegen Bots)!")
    print("Der Bot spielt automatisch und lernt!\n")

    input("Druecke Enter wenn CS2 bereit ist...")

    trainer.train(
        total_timesteps=1000000,  # 1M steps ~ 10-20 hours
        save_freq=10000
    )

    # Evaluate
    trainer.evaluate(n_episodes=10)

    print("\n✅ Training abgeschlossen!")
    print("💾 Model gespeichert: models/ppo_final.zip")
    print("\nNächster Schritt: test_bot.py zum Testen!")

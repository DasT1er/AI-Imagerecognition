"""
Minecraft Worker Network
========================
Low-level neural network for Minecraft bot.

Input: POV (screenshot) + Inventory + Position
Output: Action (14 discrete actions)

Uses PPO-style actor-critic architecture.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class MinecraftWorkerNetwork(nn.Module):
    """
    Worker Network for Minecraft

    Architecture:
    - Vision: CNN for POV (64x64x3 screenshot)
    - Inventory: MLP for inventory vector
    - Position: MLP for position
    - Combiner: Fuses all features
    - Actor: Policy network (action probabilities)
    - Critic: Value network (state value)
    """

    def __init__(self, num_actions=14):
        super().__init__()

        self.num_actions = num_actions

        # ============ VISION ENCODER (CNN) ============
        self.cnn = nn.Sequential(
            # Input: (B, 3, 64, 64)
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
            dummy_input = torch.zeros(1, 3, 64, 64)
            cnn_out_size = self.cnn(dummy_input).shape[1]

        print(f"   CNN output size: {cnn_out_size}")

        # ============ INVENTORY ENCODER (MLP) ============
        self.inventory_encoder = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU()
        )

        # ============ POSITION ENCODER (MLP) ============
        self.position_encoder = nn.Sequential(
            nn.Linear(3, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU()
        )

        # ============ FEATURE COMBINER ============
        total_features = cnn_out_size + 64 + 32

        self.combiner = nn.Sequential(
            nn.Linear(total_features, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU()
        )

        # ============ ACTOR HEAD (Policy) ============
        self.actor = nn.Linear(256, num_actions)

        # ============ CRITIC HEAD (Value) ============
        self.critic = nn.Linear(256, 1)

        print(f"✅ Worker Network initialized")
        print(f"   Total features: {total_features}")
        print(f"   Actions: {num_actions}")

    def _encode_observation(self, obs):
        """
        Encode observation into feature vector

        Args:
            obs: Dict with 'pov', 'inventory_vector', 'position'

        Returns:
            Combined feature vector (B, 256)
        """
        # Encode POV (normalize to 0-1)
        pov = obs['pov'].float() / 255.0
        if len(pov.shape) == 3:
            pov = pov.unsqueeze(0)  # Add batch dim if needed

        # Ensure channel-first format (B, C, H, W)
        if pov.shape[-1] == 3:
            pov = pov.permute(0, 3, 1, 2)

        visual_features = self.cnn(pov)

        # Encode inventory
        inventory = obs['inventory_vector']
        if len(inventory.shape) == 1:
            inventory = inventory.unsqueeze(0)
        inventory_features = self.inventory_encoder(inventory)

        # Encode position
        position = obs['position']
        if len(position.shape) == 1:
            position = position.unsqueeze(0)
        position_features = self.position_encoder(position)

        # Combine all features
        combined = torch.cat([
            visual_features,
            inventory_features,
            position_features
        ], dim=1)

        # Get final features
        features = self.combiner(combined)

        return features

    def forward(self, obs):
        """
        Forward pass

        Args:
            obs: Dict with 'pov', 'inventory_vector', 'position'

        Returns:
            action_logits: (B, num_actions)
            value: (B, 1)
        """
        # Encode observation
        features = self._encode_observation(obs)

        # Get action logits
        action_logits = self.actor(features)

        # Get state value
        value = self.critic(features)

        return action_logits, value

    def get_action(self, obs, deterministic=False):
        """
        Sample action from policy

        Args:
            obs: Observation dict
            deterministic: If True, take argmax. If False, sample.

        Returns:
            action: (B,) action indices
            log_prob: (B,) log probabilities
            value: (B, 1) state values
        """
        action_logits, value = self.forward(obs)

        # Action distribution
        action_probs = F.softmax(action_logits, dim=-1)

        if deterministic:
            # Take best action
            action = torch.argmax(action_probs, dim=-1)
        else:
            # Sample from distribution
            action = torch.multinomial(action_probs, 1).squeeze(-1)

        # Log probability of taken action
        log_probs = F.log_softmax(action_logits, dim=-1)
        log_prob = log_probs.gather(1, action.unsqueeze(-1)).squeeze(-1)

        return action, log_prob, value

    def evaluate_actions(self, obs, actions):
        """
        Evaluate actions (for PPO training)

        Args:
            obs: Observation dict
            actions: (B,) action indices

        Returns:
            log_probs: (B,) log probabilities
            values: (B, 1) state values
            entropy: (B,) entropy of action distribution
        """
        action_logits, values = self.forward(obs)

        # Log probabilities
        log_probs = F.log_softmax(action_logits, dim=-1)
        log_probs = log_probs.gather(1, actions.unsqueeze(-1)).squeeze(-1)

        # Entropy (for exploration bonus)
        probs = F.softmax(action_logits, dim=-1)
        entropy = -(probs * log_probs.exp().log()).sum(dim=-1)

        return log_probs, values, entropy


def test_network():
    """Test the worker network"""
    print("\n" + "="*60)
    print("  TESTING WORKER NETWORK")
    print("="*60 + "\n")

    # Create network
    print("Creating network...")
    network = MinecraftWorkerNetwork(num_actions=14)

    # Create dummy observation
    print("\nCreating dummy observation...")
    obs = {
        'pov': torch.randint(0, 255, (1, 64, 64, 3), dtype=torch.uint8),
        'inventory_vector': torch.randn(1, 10),
        'position': torch.randn(1, 3)
    }

    print(f"   POV shape: {obs['pov'].shape}")
    print(f"   Inventory shape: {obs['inventory_vector'].shape}")
    print(f"   Position shape: {obs['position'].shape}")

    # Forward pass
    print("\n▶️  Forward pass...")
    with torch.no_grad():
        action_logits, value = network.forward(obs)

    print(f"   Action logits shape: {action_logits.shape}")
    print(f"   Value shape: {value.shape}")
    print(f"   Action probs: {F.softmax(action_logits, dim=-1)[0][:5]}...")
    print(f"   Value: {value.item():.3f}")

    # Sample action
    print("\n🎲 Sampling action...")
    with torch.no_grad():
        action, log_prob, value = network.get_action(obs, deterministic=False)

    print(f"   Action: {action.item()}")
    print(f"   Log prob: {log_prob.item():.3f}")
    print(f"   Value: {value.item():.3f}")

    # Deterministic action
    print("\n🎯 Getting best action...")
    with torch.no_grad():
        action, log_prob, value = network.get_action(obs, deterministic=True)

    print(f"   Best action: {action.item()}")

    # Batch test
    print("\n📦 Batch test (4 samples)...")
    batch_obs = {
        'pov': torch.randint(0, 255, (4, 64, 64, 3), dtype=torch.uint8),
        'inventory_vector': torch.randn(4, 10),
        'position': torch.randn(4, 3)
    }

    with torch.no_grad():
        actions, log_probs, values = network.get_action(batch_obs)

    print(f"   Actions: {actions}")
    print(f"   Log probs: {log_probs}")
    print(f"   Values: {values.squeeze()}")

    # Test backward pass
    print("\n◀️  Testing backward pass...")
    network.train()

    action_logits, values = network.forward(batch_obs)
    loss = action_logits.mean() + values.mean()  # Dummy loss
    loss.backward()

    print(f"   Loss: {loss.item():.3f}")
    print(f"   ✅ Backward pass successful!")

    # Count parameters
    total_params = sum(p.numel() for p in network.parameters())
    trainable_params = sum(p.numel() for p in network.parameters() if p.requires_grad)

    print(f"\n📊 Network statistics:")
    print(f"   Total parameters: {total_params:,}")
    print(f"   Trainable parameters: {trainable_params:,}")

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_network()

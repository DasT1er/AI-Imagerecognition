# Minecraft Bot - Setup & Implementation Plan

## 🎮 Minecraft API Optionen

### **Option 1: MineRL (EMPFOHLEN!)** ⭐⭐⭐⭐⭐

**Was ist MineRL?**
- Offizielle Minecraft RL Library von Microsoft/OpenAI
- Python Gym Environment
- **70+ Stunden Human Gameplay Daten!**
- Fertige Observation/Action Spaces
- Aktiv maintained

**Installation:**
```bash
pip install minerl
```

**Vorteile:**
- ✅ **Plug & Play** - funktioniert sofort
- ✅ Gym Interface (wie dein CS2 Bot!)
- ✅ Pre-recorded Human Data (für Imitation Learning!)
- ✅ Verschiedene Tasks (TreeChop, Navigate, ObtainDiamond, etc.)
- ✅ Automatische Minecraft Installation
- ✅ Headless Mode (ohne GUI trainieren)

**Nachteile:**
- ⚠️ Minecraft Version 1.16 (nicht neueste)
- ⚠️ Etwas langsam (Java + Python Bridge)

**Code Beispiel:**
```python
import minerl
import gym

# Create environment
env = gym.make('MineRLTreechop-v0')

# Reset
obs = env.reset()

# Step
action = env.action_space.sample()
obs, reward, done, info = env.step(action)

# Observation enthält:
# - 'pov': (64, 64, 3) Screenshot
# - 'inventory': {'dirt': 0, 'log': 2, ...}
# - 'equipped_items': {'mainhand': {...}}
```

---

### **Option 2: Malmo (Microsoft)** ⭐⭐⭐⭐

**Was ist Malmo?**
- Microsoft Research Projekt
- Vollständige Control über Minecraft
- Python + Lua Interface
- Custom Missions/Tasks

**Installation:**
```bash
# Komplexer - braucht Java SDK, Gradle, etc.
git clone https://github.com/Microsoft/malmo
cd malmo
./gradlew build
```

**Vorteile:**
- ✅ Vollständige Kontrolle (custom worlds, tasks)
- ✅ Direkte Game-State Access
- ✅ Multi-Agent Support
- ✅ Video/Depth/Semantic Segmentation

**Nachteile:**
- ⚠️ Kompliziertes Setup
- ⚠️ Nicht mehr aktiv maintained
- ⚠️ Keine Pre-Trained Daten

---

### **Option 3: Mineflayer (NodeJS) + Python Bridge** ⭐⭐⭐⭐

**Was ist Mineflayer?**
- Bot Library in NodeJS
- Arbeitet mit echtem Minecraft (Client)
- Sehr aktiv maintained
- Kann auf jedem Server spielen!

**Installation:**
```bash
npm install mineflayer

# Python Wrapper
pip install javascript
```

**Vorteile:**
- ✅ Funktioniert mit ALLEN Minecraft Versionen
- ✅ Echte Server (auch Multiplayer!)
- ✅ Sehr schnell
- ✅ Große Community, viele Plugins

**Nachteile:**
- ⚠️ NodeJS <-> Python Bridge nötig
- ⚠️ Keine fertigen RL Environments
- ⚠️ Musst du selbst bauen

---

### **Option 4: Fabric Mod (Custom)** ⭐⭐⭐

**Was ist Fabric?**
- Minecraft Modding Framework
- Du schreibst EIGENE Mod
- Direkter Zugriff auf alles

**Installation:**
```bash
# Fabric Mod Development Kit
# Java Kenntnisse nötig!
```

**Vorteile:**
- ✅ **MAXIMALE** Kontrolle
- ✅ Keine Performance-Overhead
- ✅ Neueste Minecraft Version
- ✅ Custom Features

**Nachteile:**
- ⚠️ Du musst ALLES selbst bauen
- ⚠️ Java Kenntnisse nötig
- ⚠️ Zeitaufwendig

---

## 🎯 **Meine Empfehlung: MineRL!**

**Warum MineRL gewinnt:**
```python
✅ Funktioniert OUT OF THE BOX
✅ Gym Interface (du kennst das schon!)
✅ 70+ Stunden Human Data (Imitation Learning!)
✅ Mehrere Schwierigkeitslevel (TreeChop → ObtainDiamond)
✅ Aktiv maintained
✅ Community + Competitions
✅ Dokumentation + Tutorials

Start: 1 Tag Setup
Erste Results: 1 Woche
```

---

## 🚀 **Implementation Plan mit MineRL**

### **Phase 1: Setup & Exploration (Tag 1-2)**

```python
# minecraft_bot/setup_minerl.py
import gym
import minerl

def test_minerl_installation():
    """Test ob MineRL funktioniert"""
    print("🎮 Testing MineRL Installation...")

    # Verfügbare Environments
    envs = [env for env in gym.envs.registry.all()
            if 'MineRL' in env.id]

    print(f"\n✅ Found {len(envs)} MineRL environments:")
    for env in envs[:5]:
        print(f"   - {env.id}")

    # Test Environment
    print("\n🧪 Testing MineRLTreechop-v0...")
    env = gym.make('MineRLTreechop-v0')

    obs = env.reset()

    print("\n📊 Observation Space:")
    print(f"   POV Shape: {obs['pov'].shape}")
    print(f"   Inventory: {obs['inventory']}")

    print("\n🎮 Action Space:")
    print(f"   Type: {env.action_space}")

    # Take random actions
    print("\n▶️  Taking 10 random actions...")
    for i in range(10):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        print(f"   Step {i+1}: Reward={reward:.2f}, Done={done}")

        if done:
            obs = env.reset()

    env.close()
    print("\n✅ MineRL working perfectly!")

if __name__ == "__main__":
    test_minerl_installation()
```

---

### **Phase 2: Data Collection Module (Tag 3-4)**

```python
# minecraft_bot/data_collector.py
import gym
import minerl
import numpy as np
from PIL import Image
import os
import json

class MinecraftDataCollector:
    """
    Sammelt Daten aus Minecraft

    Für später:
    - Imitation Learning
    - Curiosity Module
    - Reward Shaping
    """

    def __init__(self, env_name='MineRLTreechop-v0'):
        self.env = gym.make(env_name)
        self.data_dir = '../../data/minecraft_gameplay'
        os.makedirs(self.data_dir, exist_ok=True)

    def collect_human_data(self, num_episodes=10):
        """
        Lade HUMAN GAMEPLAY von MineRL Dataset!

        Das ist GOLD für Imitation Learning!
        """
        print("📥 Loading MineRL Human Demonstrations...")

        data = minerl.data.make(
            'MineRLTreechop-v0',
            data_dir='../../data/minerl'
        )

        samples = []

        for trajectory_name in data.get_trajectory_names():
            print(f"   Loading: {trajectory_name}")

            for obs, action, reward, next_obs, done in data.load_data(
                trajectory_name, skip_interval=5
            ):
                # Store sample
                samples.append({
                    'pov': obs['pov'],
                    'inventory': obs['inventory'],
                    'action': action,
                    'reward': reward
                })

                if len(samples) >= 1000:
                    break

            if len(samples) >= 1000:
                break

        print(f"\n✅ Collected {len(samples)} human gameplay samples!")
        return samples

    def collect_bot_data(self, num_steps=1000):
        """
        Sammle Daten vom Bot selbst

        Für:
        - Training
        - Replay Buffer
        - Analysis
        """
        print(f"🤖 Collecting {num_steps} bot samples...")

        obs = self.env.reset()
        samples = []

        for step in range(num_steps):
            # Random action (später: Neural Network!)
            action = self.env.action_space.sample()

            # Step
            next_obs, reward, done, info = self.env.step(action)

            # Store
            samples.append({
                'obs': obs,
                'action': action,
                'reward': reward,
                'next_obs': next_obs,
                'done': done
            })

            obs = next_obs

            if done:
                obs = self.env.reset()

            if step % 100 == 0:
                print(f"   Step {step}/{num_steps}")

        print(f"✅ Collected {len(samples)} bot samples!")
        return samples

    def visualize_sample(self, sample):
        """Zeige was der Bot sieht"""
        import matplotlib.pyplot as plt

        pov = sample['obs']['pov']

        plt.figure(figsize=(8, 6))
        plt.imshow(pov)
        plt.title("Bot POV")
        plt.axis('off')
        plt.show()
```

---

### **Phase 3: Minecraft Environment Wrapper (Tag 5-6)**

```python
# minecraft_bot/minecraft_env.py
import gym
import minerl
import numpy as np
from collections import deque

class MinecraftHierarchicalEnv(gym.Env):
    """
    Wrapper für MineRL mit Hierarchical RL Support

    Simplifies:
    - Action Space (continuous → discrete)
    - Observation Space (nur wichtige Features)
    - Reward Shaping (dichte rewards!)
    """

    def __init__(self, base_env='MineRLTreechop-v0', frame_skip=4):
        self.env = gym.make(base_env)
        self.frame_skip = frame_skip

        # Simplified Action Space
        self.action_space = gym.spaces.Discrete(14)

        # Simplified Observation Space
        self.observation_space = gym.spaces.Dict({
            'pov': gym.spaces.Box(
                low=0, high=255,
                shape=(64, 64, 3),
                dtype=np.uint8
            ),
            'inventory_vector': gym.spaces.Box(
                low=0, high=100,
                shape=(10,),  # 10 wichtigste Items
                dtype=np.float32
            ),
            'position': gym.spaces.Box(
                low=-1000, high=1000,
                shape=(3,),  # x, y, z
                dtype=np.float32
            )
        })

        # Frame stacking (für temporale Info)
        self.frame_stack = deque(maxlen=4)

    def _discretize_action(self, discrete_action):
        """
        Convert discrete action (0-13) zu MineRL action

        Actions:
        0: No-op (nichts tun)
        1: Forward
        2: Back
        3: Left
        4: Right
        5: Jump
        6: Attack
        7: Forward + Attack (Mine!)
        8: Forward + Jump
        9: Camera Up
        10: Camera Down
        11: Camera Left
        12: Camera Right
        13: Sneak
        """
        # MineRL action template
        action = self.env.action_space.noop()

        if discrete_action == 1:
            action['forward'] = 1
        elif discrete_action == 2:
            action['back'] = 1
        elif discrete_action == 3:
            action['left'] = 1
        elif discrete_action == 4:
            action['right'] = 1
        elif discrete_action == 5:
            action['jump'] = 1
        elif discrete_action == 6:
            action['attack'] = 1
        elif discrete_action == 7:
            action['forward'] = 1
            action['attack'] = 1
        elif discrete_action == 8:
            action['forward'] = 1
            action['jump'] = 1
        elif discrete_action == 9:
            action['camera'] = [0, 15]  # Up
        elif discrete_action == 10:
            action['camera'] = [0, -15]  # Down
        elif discrete_action == 11:
            action['camera'] = [-15, 0]  # Left
        elif discrete_action == 12:
            action['camera'] = [15, 0]  # Right
        elif discrete_action == 13:
            action['sneak'] = 1

        return action

    def _simplify_observation(self, obs):
        """
        Simplify MineRL observation

        Full obs hat VIEL zu viel Info!
        Wir brauchen nur:
        - POV (Screenshot)
        - Inventory (wichtigste Items)
        - Position (wo bin ich?)
        """
        # POV ist schon gut
        pov = obs['pov']

        # Inventory → Vector
        inventory_vector = np.zeros(10, dtype=np.float32)
        important_items = [
            'log', 'planks', 'stick', 'cobblestone',
            'dirt', 'stone', 'coal', 'iron_ore',
            'crafting_table', 'furnace'
        ]

        for i, item in enumerate(important_items):
            if item in obs.get('inventory', {}):
                inventory_vector[i] = obs['inventory'][item]

        # Position (wenn verfügbar)
        if 'location_stats' in obs:
            position = np.array([
                obs['location_stats'].get('xpos', 0),
                obs['location_stats'].get('ypos', 0),
                obs['location_stats'].get('zpos', 0)
            ], dtype=np.float32)
        else:
            position = np.zeros(3, dtype=np.float32)

        return {
            'pov': pov,
            'inventory_vector': inventory_vector,
            'position': position
        }

    def reset(self):
        obs = self.env.reset()
        simplified_obs = self._simplify_observation(obs)

        # Reset frame stack
        self.frame_stack.clear()
        for _ in range(4):
            self.frame_stack.append(simplified_obs['pov'])

        return simplified_obs

    def step(self, discrete_action):
        """
        Execute action with frame skipping

        Frame skip = Führe gleiche Action 4x aus
        → Schnelleres Training (weniger redundante Frames)
        """
        # Convert to MineRL action
        action = self._discretize_action(discrete_action)

        # Execute with frame skip
        total_reward = 0.0
        for _ in range(self.frame_skip):
            obs, reward, done, info = self.env.step(action)
            total_reward += reward

            if done:
                break

        # Simplify observation
        simplified_obs = self._simplify_observation(obs)

        # Update frame stack
        self.frame_stack.append(simplified_obs['pov'])

        # Reward shaping (später!)
        shaped_reward = self._shape_reward(reward, obs, action)

        return simplified_obs, shaped_reward, done, info

    def _shape_reward(self, reward, obs, action):
        """
        Dense reward shaping!

        MineRL rewards sind SPARSE (nur für Task completion)
        Wir wollen DICHTE rewards!
        """
        shaped_reward = reward

        # Bonus für Log sammeln (TreeChop task)
        if 'log' in obs.get('inventory', {}):
            log_count = obs['inventory']['log']
            shaped_reward += log_count * 0.1

        # Penalty für Stillstand
        # (später: track ob sich position ändert)

        # Bonus für neue Items discovered
        # (später: curiosity module)

        return shaped_reward

    def close(self):
        self.env.close()
```

---

### **Phase 4: Worker Network (Tag 7-10)**

```python
# minecraft_bot/networks/worker_network.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class MinecraftWorkerNetwork(nn.Module):
    """
    Low-Level Worker für Minecraft

    Input: Screenshot (POV) + Inventory + Position
    Output: Action (14 discrete actions)
    """

    def __init__(self, num_actions=14):
        super().__init__()

        # Vision Encoder (CNN für POV)
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

        # Inventory Encoder
        self.inventory_encoder = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU()
        )

        # Position Encoder
        self.position_encoder = nn.Sequential(
            nn.Linear(3, 32),
            nn.ReLU()
        )

        # Combiner
        total_features = cnn_out_size + 64 + 32

        self.combiner = nn.Sequential(
            nn.Linear(total_features, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU()
        )

        # Actor head (policy)
        self.actor = nn.Linear(256, num_actions)

        # Critic head (value)
        self.critic = nn.Linear(256, 1)

    def forward(self, obs):
        """
        Forward pass

        Args:
            obs: Dict with 'pov', 'inventory_vector', 'position'

        Returns:
            action_logits, value
        """
        # Encode POV
        pov = obs['pov'].float() / 255.0  # Normalize
        visual_features = self.cnn(pov)

        # Encode inventory
        inventory_features = self.inventory_encoder(
            obs['inventory_vector']
        )

        # Encode position
        position_features = self.position_encoder(obs['position'])

        # Combine
        combined = torch.cat([
            visual_features,
            inventory_features,
            position_features
        ], dim=1)

        # Get features
        features = self.combiner(combined)

        # Action distribution
        action_logits = self.actor(features)

        # Value
        value = self.critic(features)

        return action_logits, value

    def get_action(self, obs, deterministic=False):
        """
        Sample action from policy

        Args:
            obs: Observation dict
            deterministic: If True, take argmax. If False, sample.

        Returns:
            action, log_prob
        """
        action_logits, value = self.forward(obs)

        # Action distribution
        action_probs = F.softmax(action_logits, dim=-1)

        if deterministic:
            action = torch.argmax(action_probs, dim=-1)
        else:
            action = torch.multinomial(action_probs, 1).squeeze(-1)

        # Log probability
        log_prob = F.log_softmax(action_logits, dim=-1)
        log_prob = log_prob.gather(1, action.unsqueeze(-1)).squeeze(-1)

        return action, log_prob, value
```

---

## 📅 **Timeline für Minecraft Bot**

| Woche | Phase | Was passiert |
|-------|-------|--------------|
| **1** | Setup | MineRL installieren, testen, Daten sammeln |
| **2** | Environment | Wrapper bauen, Action/Obs Space simplifizieren |
| **3** | Worker Network | Low-level NN implementieren |
| **4-5** | Level 1 Training | Basic Movement lernen |
| **6-7** | Level 2 Training | Mining lernen |
| **8-9** | Level 3 Training | Crafting lernen |
| **10-12** | Level 4-5 Training | Building + Advanced |

**Total: 12 Wochen für Basic → Advanced** ✅

---

## 🎯 **Next Steps**

1. **Installiere MineRL** (heute!)
2. **Teste Installation** (test script)
3. **Lade Human Data** (für später)
4. **Baue Environment Wrapper**
5. **Implementiere Worker Network**
6. **Start Training!**

Los geht's! 🚀

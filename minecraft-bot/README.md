# 🎮 Minecraft Bot - Hierarchical Reinforcement Learning

Autonomous Minecraft bot that learns to play using hierarchical neural networks and curriculum learning.

## 🎯 Features

- **Hierarchical RL**: Multi-level neural networks (Meta-Controller → Manager → Worker)
- **Curriculum Learning**: Progressive difficulty levels (Movement → Mining → Crafting → Building)
- **Dense Rewards**: Shaped rewards for faster learning
- **MineRL Integration**: Uses official Minecraft RL environment
- **Human Demonstrations**: Can learn from 70+ hours of human gameplay data

## 📦 Installation

### 1. Install Requirements

```bash
cd minecraft-bot
pip install -r requirements.txt
```

**Note:** MineRL requires Java 8. Install with:
```bash
# Ubuntu/Debian
sudo apt-get install openjdk-8-jdk

# macOS
brew install java8
```

### 2. Test Installation

```bash
python setup_test.py
```

This will:
- ✅ Check all dependencies
- ✅ Test MineRL environments
- ✅ Verify data availability
- ✅ Run sample episode

## 🚀 Quick Start

### Test Environment

```bash
# Test simplified Minecraft environment
python environments/minecraft_env.py
```

### Test Worker Network

```bash
# Test neural network architecture
python networks/worker_network.py
```

### Train Bot (Coming Soon!)

```bash
# Train Level 1: Basic Movement
python train_level1.py

# Train Level 2: Mining
python train_level2.py
```

## 🏗️ Project Structure

```
minecraft-bot/
├── environments/
│   └── minecraft_env.py      # Simplified Gym wrapper
├── networks/
│   ├── worker_network.py     # Low-level actor-critic
│   ├── manager_network.py    # Mid-level goal planner (TODO)
│   └── meta_controller.py    # High-level strategy (TODO)
├── data/
│   └── minerl/               # Human demonstration data
├── utils/
│   ├── replay_buffer.py      # Experience storage (TODO)
│   └── reward_shaper.py      # Reward functions (TODO)
├── setup_test.py             # Installation test
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## 🎓 Curriculum Learning Levels

### Level 1: Basic Movement (Week 1-2)
**Goal:** Learn to walk and look around
- Actions: Forward, back, left, right, jump, camera
- Reward: Distance traveled, exploration
- Success: Navigate to target location 80% of the time

### Level 2: Mining (Week 3-4)
**Goal:** Learn to mine blocks
- Actions: Attack while moving
- Reward: Blocks mined, logs collected
- Success: Collect 10 logs within time limit

### Level 3: Crafting (Week 5-6)
**Goal:** Learn to craft items
- Actions: Open inventory, craft items
- Reward: Items crafted, progression
- Success: Craft pickaxe from scratch

### Level 4: Building (Week 7-8)
**Goal:** Learn to place blocks
- Actions: Place blocks, build structures
- Reward: Structures completed
- Success: Build simple house

### Level 5: Survival (Week 9-12)
**Goal:** Full survival gameplay
- Actions: All actions combined
- Reward: Long-term survival, achievements
- Success: Kill Ender Dragon (aspirational!)

## 🧠 Architecture

### Worker Network (Low-Level)
```
Screenshot (64x64x3) → CNN → Features
Inventory (10,)      → MLP → Features
Position (3,)        → MLP → Features
                            ↓
                       Combiner → Actor + Critic
                            ↓
                    14 Discrete Actions
```

### Manager Network (Mid-Level) [TODO]
```
Game State → LSTM → Sub-Goals → Worker
```

### Meta-Controller (High-Level) [TODO]
```
World History → Transformer → Strategy → Manager
```

## 📊 Training Progress

| Level | Status | Success Rate | Training Time |
|-------|--------|--------------|---------------|
| 1. Movement | 🔵 Planned | - | - |
| 2. Mining | 🔵 Planned | - | - |
| 3. Crafting | 🔵 Planned | - | - |
| 4. Building | 🔵 Planned | - | - |
| 5. Survival | 🔵 Planned | - | - |

## 🎮 Available MineRL Environments

- `MineRLTreechop-v0` - Chop trees (Level 2)
- `MineRLNavigate-v0` - Navigate to location (Level 1)
- `MineRLObtainDiamond-v0` - Full gameplay (Level 5)
- `MineRLObtainIronPickaxe-v0` - Crafting focus (Level 3)

## 📚 Resources

- [MineRL Documentation](https://minerl.readthedocs.io/)
- [MineRL Competition](https://www.aicrowd.com/challenges/neurips-2021-minerl-competition)
- [Hierarchical RL Paper](https://arxiv.org/abs/1604.06057)

## 🤝 Contributing

This is a learning project! Contributions welcome:
- 🐛 Bug reports
- 💡 Feature suggestions
- 📝 Documentation improvements
- 🧪 Experiment results

## 📝 TODO

- [ ] Implement Manager Network
- [ ] Implement Meta-Controller
- [ ] Add Replay Buffer
- [ ] Implement PPO Training Loop
- [ ] Add Curiosity Module (ICM)
- [ ] Imitation Learning from Human Data
- [ ] Tensorboard Logging
- [ ] Checkpoint Saving/Loading
- [ ] Evaluation Scripts

## 🎯 Goals

**Short-term (1-2 months):**
- ✅ Basic navigation
- ✅ Mining and collecting logs
- ✅ Simple crafting

**Mid-term (3-6 months):**
- Building structures
- Tool progression (wood → stone → iron)
- Combat basics

**Long-term (6-12 months):**
- Full survival gameplay
- Complex crafting chains
- Advanced strategies
- Beat Ender Dragon 🐉

## 📄 License

MIT

## 🙏 Acknowledgments

- MineRL Team for the amazing environment
- OpenAI for hierarchical RL research
- Minecraft community

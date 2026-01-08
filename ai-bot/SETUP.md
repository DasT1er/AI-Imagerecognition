# AI Bot Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Tesseract OCR (for game state detection)
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

### 2. Verify Installation

```bash
# Check GPU (optional but recommended)
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"

# Test imports
python -c "import gymnasium; import stable_baselines3; print('✅ All imports OK')"
```

### 3. Phase 1: Imitation Learning

#### Step 1: Collect Human Gameplay

```bash
python 3_learning/imitation/collect_human_data.py
```

- Press F9 to start/stop recording
- Play 10-20 rounds normally
- Bot will learn YOUR playstyle!

#### Step 2: Train Model

```bash
python 3_learning/imitation/train_imitation.py
```

- Training takes 10-30 minutes
- Model saved to: `models/best_model.pt`
- Training curves saved to: `models/training_curves.png`

#### Step 3: Test Bot

```bash
python test_bot.py
```

- Bot plays CS2 automatically!
- Press F9 to stop

## Using START_BOT.bat (Windows)

```cmd
START_BOT.bat
```

Simple menu for all AI bot features:
- [1] Record gameplay (F9 start/stop)
- [2] Train model
- [3] Test bot (plays automatically!)
- [4] Test game state detector
- [5] Test environment
- [6] View README

## Troubleshooting

### "Model not found"
- Train model first with option [2]
- Or check path: `models/best_model.pt`

### "No data found"
- Record gameplay first with option [1]
- Data saved to: `data/human_gameplay/`

### "Tesseract not found"
- Install Tesseract OCR
- Add to PATH
- Test: `tesseract --version`

### Poor Bot Performance
- Collect more data (20+ rounds recommended)
- Train for more epochs (50-100)
- Check training curves (loss should decrease)

## Architecture

### Phase 1: Imitation Learning (CURRENT)
- ✅ Human data collection
- ✅ CNN-based action prediction
- ✅ Supervised learning from gameplay
- 🎯 Goal: Bot plays like you!

### Phase 2: Reinforcement Learning (TODO)
- PPO (Proximal Policy Optimization)
- Self-improvement via rewards
- 🎯 Goal: Bot improves beyond human!

### Phase 3: Full Autonomy (TODO)
- Economy management
- Buy menu automation
- Multi-map learning
- Advanced tactics
- 🎯 Goal: Fully autonomous CS2 agent!

## File Structure

```
ai-bot/
├── 1_vision/              # Enemy & game state detection
│   ├── detector.py        # Uses YOLO from main project
│   └── game_state.py      # HP, armor, ammo, money, time
│
├── 2_actions/             # Keyboard & mouse control
│   ├── keyboard.py        # Movement, jump, crouch, etc.
│   └── mouse.py           # Aiming, shooting, recoil control
│
├── 3_learning/
│   ├── imitation/         # Phase 1
│   │   ├── collect_human_data.py
│   │   └── train_imitation.py
│   └── reinforcement/     # Phase 2 (TODO)
│
├── 4_environment/         # Gym environment for RL
│   └── cs2_env.py
│
├── models/                # Saved models
├── configs/               # Configuration files
├── logs/                  # Training logs
│
├── test_bot.py           # Main bot script
├── START_BOT.bat         # Windows menu
├── README.md             # Architecture docs
└── requirements.txt      # Python dependencies
```

## Next Steps

1. ✅ **Phase 1 Complete** - Bot learns from human gameplay
2. ⏳ **Phase 2 Next** - Implement PPO for self-improvement
3. 🔮 **Phase 3 Future** - Full autonomy with economy & strategy

## Tips for Best Results

### Data Collection
- Play naturally (don't try to be perfect)
- Record diverse situations:
  - Different weapons
  - Different positions
  - Both attacking and defending
  - Combat and movement
- 10,000+ frames recommended (20+ rounds)

### Training
- Start with 50 epochs
- Monitor validation accuracy
- If overfitting: reduce epochs or add dropout
- If underfitting: increase epochs or network size

### Testing
- Test on same map as training data first
- Bot works best in similar situations to training
- Performance improves with more diverse training data

## Performance Expectations

### Phase 1 (Imitation Learning)
- **10 rounds of data:** Bot basic movement ✓
- **20 rounds of data:** Bot decent aiming ✓✓
- **50+ rounds of data:** Bot plays like you! ✓✓✓

### Phase 2 (Reinforcement Learning)
- **Initial:** Same as Phase 1
- **After training:** Better decision making
- **Long-term:** Potentially superhuman aim/timing

## Resources

- [Gymnasium Docs](https://gymnasium.farama.org/)
- [Stable-Baselines3 Docs](https://stable-baselines3.readthedocs.io/)
- [PyTorch Docs](https://pytorch.org/docs/)
- [YOLOv8 Docs](https://docs.ultralytics.com/)

## Support

Questions? Check:
1. README.md - Architecture overview
2. SETUP.md - This file
3. Code comments - Detailed explanations

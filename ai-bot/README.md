# CS2 AI Bot - Autonomous Playing Agent

Dieser Bot lernt Counter-Strike 2 **vollständig autonom** zu spielen!

## 🎯 Ziel

Ein AI-Agent der:
- ✅ **Gegner erkennt** (nutzt unser trainiertes YOLO-Model!)
- ✅ **Sich bewegt** (WASD, Ducken, Springen)
- ✅ **Schießt** (Zielt und feuert)
- ✅ **Waffen kauft** (Economy Management)
- ✅ **Taktisch spielt** (Deckung, Positioning)
- ✅ **Gegen Bots gewinnt** (vollständig autonom!)

## 🧠 Architektur - 3 Phasen

### **Phase 1: Imitation Learning** (2-4 Wochen)
Lernt von deinen Daten!

```
Input: Screenshots von dir beim Spielen
Output: Tastatur/Maus Aktionen
```

**Vorteile:**
- Nutzt deine existierenden Screenshots
- Schneller Start (kein Random Herumprobieren)
- Lernt "vernünftiges" Verhalten

**Was der Bot lernt:**
- Wie man sich zu Gegnern bewegt
- Wann man schießt
- Grundlegende Positionierung

---

### **Phase 2: Reinforcement Learning** (1-2 Monate)
Bot verbessert sich selbst!

```
Algorithmus: PPO (Proximal Policy Optimization)
- Belohnung für Kills: +10
- Belohnung für Schaden: +1
- Strafe für Tod: -5
- Belohnung für Runden-Sieg: +50
```

**Was der Bot lernt:**
- Optimales Zielen
- Deckung nutzen
- Timing (wann peeken, wann warten)
- Teamplay (falls mehrere Bots)

---

### **Phase 3: Full Autonomy** (Advanced)
Komplettes Spiel-Management!

```
Features:
- Economy System (Waffen kaufen basierend auf Geld)
- Map Learning (verschiedene Maps beherrschen)
- Strategy (T-Side: Plant, CT-Side: Defend)
- Adaptation (gegen verschiedene Gegner-Strategien)
```

---

## 📁 Projekt-Struktur

```
ai-bot/
├── 1_vision/          # Gegner-Erkennung (nutzt YOLO)
│   ├── detector.py    # Wrapper für existierendes Model
│   └── game_state.py  # Extrahiert Spiel-Info (HP, Ammo, etc.)
│
├── 2_actions/         # Bot-Aktionen
│   ├── keyboard.py    # WASD, Ducken, Springen
│   ├── mouse.py       # Zielen, Schießen
│   └── buy_menu.py    # Waffen kaufen
│
├── 3_learning/        # AI Training
│   ├── imitation/     # Phase 1: Von Daten lernen
│   │   ├── collect_human_data.py    # Sammle deine Spielweise
│   │   └── train_imitation.py       # Lerne von dir
│   │
│   ├── reinforcement/ # Phase 2: Selbst optimieren
│   │   ├── ppo_agent.py             # PPO Algorithmus
│   │   ├── reward.py                # Belohnungs-System
│   │   └── train_rl.py              # RL Training
│   │
│   └── full_agent/    # Phase 3: Kompletter Bot
│       ├── economy.py               # Waffen-Kauf Logik
│       ├── strategy.py              # Taktik
│       └── agent.py                 # Alles zusammen
│
├── 4_environment/     # CS2 Wrapper
│   ├── cs2_env.py     # Gym-like Environment
│   └── game_interface.py  # Low-Level CS2 Control
│
├── models/            # Gespeicherte AI-Models
├── configs/           # Konfigurations-Dateien
└── logs/              # Training Logs & Stats
```

---

## 🚀 Quick Start - Phase 1

### 1. Sammle deine Spiel-Daten
```bash
python 1_vision/collect_human_data.py
```
- Spiele 10-20 Runden
- Tool zeichnet auf: Screenshots + Tastatur/Maus Inputs
- Speichert: `data/human_gameplay/`

### 2. Trainiere Imitation Model
```bash
python 3_learning/imitation/train_imitation.py
```
- Lernt deine Bewegungen
- Nach ~5000 Frames: Bot kann grundlegende Bewegungen
- Nach ~20000 Frames: Bot kann einfache Fights gewinnen

### 3. Teste den Bot
```bash
python test_bot.py --mode imitation
```

---

## 🎮 Bot-Aktionen (Action Space)

### **Movement (8 Aktionen)**
- `W` - Vorwärts
- `S` - Rückwärts
- `A` - Links
- `D` - Rechts
- `SHIFT` - Schleichen
- `CTRL` - Ducken
- `SPACE` - Springen
- `NONE` - Stillstehen

### **Shooting (3 Aktionen)**
- `SHOOT` - Feuern
- `RELOAD` - Nachladen
- `SWITCH_WEAPON` - Waffe wechseln

### **Aiming (Kontinuierlich)**
- `mouse_x` - Horizontal (-1 bis +1)
- `mouse_y` - Vertikal (-1 bis +1)

### **Economy (5 Aktionen)**
- `BUY_RIFLE` - AK/M4
- `BUY_SMG` - MP9/MAC-10
- `BUY_PISTOL` - Desert Eagle
- `BUY_ARMOR` - Kevlar + Helm
- `BUY_GRENADES` - Flash/Smoke

**Gesamt: ~20 mögliche Aktionen pro Frame**

---

## 📊 State Space (Was der Bot sieht)

### **Visual Input**
- Screenshot (640x360 RGB)
- Gegner-Detections (YOLO Bounding Boxes)
- Crosshair Position

### **Game State**
- HP (0-100)
- Armor (0-100)
- Ammo (current/reserve)
- Geld ($0-$16000)
- Team (CT/T)
- Round Time (0-115s)

**Format:**
```python
state = {
    'image': np.array(640, 360, 3),
    'detections': [(x, y, w, h, class, conf), ...],
    'hp': 100,
    'armor': 100,
    'ammo': [30, 90],  # current, reserve
    'money': 800,
    'team': 'CT',
    'time_left': 115
}
```

---

## 🏆 Belohnungs-System (Rewards)

### **Combat**
```python
kill_enemy = +10.0
damage_enemy = +0.1 * damage
headshot_kill = +15.0
get_damaged = -0.1 * damage
death = -5.0
```

### **Objectives**
```python
plant_bomb = +20.0  # T-Side
defuse_bomb = +25.0  # CT-Side
win_round = +50.0
lose_round = -10.0
```

### **Efficiency**
```python
ammo_efficiency = kills / shots_fired
survival_time = +0.01 * seconds_alive
```

---

## 🔧 Technologie-Stack

### **AI/ML**
- **PyTorch** - Neural Networks
- **Stable-Baselines3** - RL Algorithmen (PPO, DQN)
- **Gymnasium** - Environment Wrapper
- **TensorBoard** - Training Visualization

### **Game Interface**
- **PyAutoGUI** - Keyboard/Mouse Control
- **PIL** - Screenshots
- **Existing YOLO** - Gegner-Erkennung

### **Performance**
- **CUDA** - GPU Training
- **Multi-Processing** - Paralleles Training
- **Model Quantization** - Schnellere Inference

---

## 📈 Erwartete Ergebnisse

### **Nach Phase 1 (Imitation)**
- Bot kann sich bewegen
- Bot schießt auf Gegner (wenn sichtbar)
- **Win-Rate vs Easy Bots: ~30-40%**

### **Nach Phase 2 (Reinforcement Learning)**
- Bot nutzt Deckung
- Bot hat gutes Aim
- Bot macht taktische Entscheidungen
- **Win-Rate vs Medium Bots: ~60-70%**

### **Nach Phase 3 (Full Autonomy)**
- Bot kauft optimal
- Bot spielt verschiedene Maps
- Bot adaptiert Strategie
- **Win-Rate vs Hard Bots: ~70-80%**
- **Win-Rate vs Human Players: ~40-50%**

---

## 🎯 Nächste Schritte

1. **Jetzt:** Erstelle Vision System (nutzt existierendes YOLO)
2. **Dann:** Action System (Keyboard/Mouse Control)
3. **Dann:** Data Collection Tool (zeichne dich beim Spielen auf)
4. **Dann:** Imitation Learning Training
5. **Später:** RL Training

---

## 🚨 Wichtige Hinweise

- **NUR für Offline-Bots!** Nicht online nutzen!
- **VAC-Ban Risiko:** Nicht auf VAC-gesicherten Servern!
- **Nur zum Lernen:** Bildungszwecke!

---

## 📚 Weitere Infos

- **PPO Algorithmus:** https://spinningup.openai.com/en/latest/algorithms/ppo.html
- **Imitation Learning:** https://arxiv.org/abs/1606.03476
- **CS:GO AI Research:** OpenAI Five (Dota 2) ähnlicher Ansatz

---

**Lass uns starten! Der Bot wird epic! 🎮🤖**

# X4 Bot - End-to-End Neural Network Approach

## 🎯 Konzept: Bot lernt ALLES mit Neural Networks

Statt Scripting → Neural Networks lernen durch Trial & Error!

---

## 🧠 **Architecture: Hierarchical Neural Networks**

```
┌─────────────────────────────────────────────────────┐
│         Meta-Controller (High-Level NN)             │
│  "Was ist mein aktuelles Ziel?"                     │
│  → "Ich will reich werden"                          │
│  → "Ich brauche Mining Ships"                       │
└──────────────────┬──────────────────────────────────┘
                   │ Output: Goal Embedding
                   ▼
┌─────────────────────────────────────────────────────┐
│      Manager Network (Mid-Level NN)                 │
│  "Wie erreiche ich dieses Ziel?"                    │
│  → "Fliege zu Shipyard"                             │
│  → "Öffne Shop"                                     │
│  → "Kaufe Miner"                                    │
└──────────────────┬──────────────────────────────────┘
                   │ Output: Sub-Goal
                   ▼
┌─────────────────────────────────────────────────────┐
│      Worker Network (Low-Level NN)                  │
│  "Welche Tasten/Mausklicks jetzt?"                  │
│  → Press 'M' (Map)                                  │
│  → Click position (x, y)                            │
│  → Press 'Enter'                                    │
└─────────────────────────────────────────────────────┘
```

Diese Architektur heißt **"Hierarchical Reinforcement Learning"** (HRL)

---

## 📋 **Konkrete Implementation**

### **1. Low-Level Worker: Pixel-to-Action Neural Network**

```python
# x4_worker_network.py
import torch
import torch.nn as nn

class X4WorkerNetwork(nn.Module):
    """
    Low-Level NN: Screenshot → Actions

    Lernt SELBST:
    - Wie man Menüs navigiert
    - Wo man klicken muss
    - Welche Tasten drücken

    Kein Hard-Coding!
    """

    def __init__(self, action_space_size=50):
        super().__init__()

        # Vision: Screenshot → Features
        self.vision_encoder = nn.Sequential(
            # CNN für Screenshot (wie CS2 Bot)
            nn.Conv2d(3, 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(128 * 7 * 7, 512),
            nn.ReLU()
        )

        # Goal Encoder: "Was will der Manager dass ich tue?"
        self.goal_encoder = nn.Sequential(
            nn.Linear(64, 128),  # Goal embedding vom Manager
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU()
        )

        # Action Head: Vision + Goal → Actions
        self.actor = nn.Sequential(
            nn.Linear(512 + 128, 256),
            nn.ReLU(),
            nn.Linear(256, action_space_size)
        )

        # Value Head: "Wie gut ist meine Situation?"
        self.critic = nn.Sequential(
            nn.Linear(512 + 128, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )

    def forward(self, screenshot, goal_embedding):
        """
        Args:
            screenshot: (B, 3, H, W) - Game Screen
            goal_embedding: (B, 64) - Was der Manager will

        Returns:
            action_probs: (B, action_space_size)
            value: (B, 1)
        """
        # Encode screenshot
        vision_features = self.vision_encoder(screenshot)

        # Encode goal
        goal_features = self.goal_encoder(goal_embedding)

        # Combine
        combined = torch.cat([vision_features, goal_features], dim=1)

        # Action distribution
        action_logits = self.actor(combined)
        action_probs = torch.softmax(action_logits, dim=-1)

        # Value
        value = self.critic(combined)

        return action_probs, value

# Action Space für Worker
WORKER_ACTIONS = {
    # Keyboard
    0: 'press_w',
    1: 'press_a',
    2: 'press_s',
    3: 'press_d',
    4: 'press_space',
    5: 'press_enter',
    6: 'press_esc',
    7: 'press_m',  # Map
    8: 'press_tab',
    9: 'press_i',  # Inventory
    10: 'press_1',
    11: 'press_2',
    # ...

    # Mouse (diskretisiert)
    30: 'click_left',
    31: 'click_right',
    32: 'move_mouse_up',
    33: 'move_mouse_down',
    34: 'move_mouse_left',
    35: 'move_mouse_right',

    # Oder: Continuous actions für Maus
    # action[40:42] = (mouse_x, mouse_y) als continuous values
}
```

**Wie lernt das Worker Network?**

```python
# Reward für Worker (vom Manager gegeben!)
def worker_reward(goal, achieved):
    """
    Manager sagt: "Öffne Shop"
    Worker versucht es
    Wenn Shop offen → +1 Reward
    Sonst → 0
    """
    if goal == "open_shop" and achieved:
        return +1.0
    return 0.0

# Training: Worker lernt durch Trial & Error
# "Ich muss M drücken, dann klicken, dann... ah! Shop ist offen!"
```

---

### **2. Mid-Level Manager: Goal-to-SubGoals Neural Network**

```python
# x4_manager_network.py
class X4ManagerNetwork(nn.Module):
    """
    Manager NN: Strategisches Ziel → Konkrete Sub-Goals

    Lernt SELBST:
    - "Um Mining Ship zu kaufen muss ich erst zu Shipyard"
    - "Um Station zu bauen brauche ich erst Geld"
    - "Um Geld zu verdienen muss ich erst Traden"

    Entdeckt Abhängigkeiten durch Exploration!
    """

    def __init__(self, num_subgoals=20):
        super().__init__()

        # Game State Encoder
        self.state_encoder = nn.Sequential(
            # Nimmt: Credits, Ships, Stations, etc.
            nn.Linear(50, 256),  # 50 state features
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU()
        )

        # High-Level Goal Encoder (vom Meta-Controller)
        self.goal_encoder = nn.Sequential(
            nn.Linear(32, 128),
            nn.ReLU()
        )

        # LSTM für temporale Planung
        self.lstm = nn.LSTM(256 + 128, 256, num_layers=2)

        # Sub-Goal Prediction
        self.subgoal_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, num_subgoals)
        )

    def forward(self, game_state, high_level_goal, hidden=None):
        """
        Args:
            game_state: (B, 50) - Credits, Ships, etc.
            high_level_goal: (B, 32) - "Werde reich!"

        Returns:
            subgoal: (B, num_subgoals) - "Kaufe Mining Ship"
            hidden: LSTM hidden state
        """
        # Encode state
        state_features = self.state_encoder(game_state)
        goal_features = self.goal_encoder(high_level_goal)

        # Combine
        combined = torch.cat([state_features, goal_features], dim=1)

        # LSTM für Sequenz-Planung
        lstm_out, hidden = self.lstm(combined.unsqueeze(0), hidden)

        # Predict next sub-goal
        subgoal_logits = self.subgoal_head(lstm_out.squeeze(0))
        subgoal_probs = torch.softmax(subgoal_logits, dim=-1)

        return subgoal_probs, hidden

# Sub-Goals die der Manager lernen kann
MANAGER_SUBGOALS = {
    0: "explore_sector",           # Erkunde neuen Sektor
    1: "goto_shipyard",            # Fliege zu Shipyard
    2: "goto_station_X",           # Fliege zu bestimmter Station
    3: "buy_mining_ship",          # Kaufe Mining Ship
    4: "buy_trade_ship",           # Kaufe Trade Ship
    5: "build_station",            # Baue Station
    6: "assign_ship_to_mine",      # Weise Schiff zum Mining zu
    7: "setup_trade_route",        # Setup Trading
    8: "wait_for_income",          # Warte bis genug Geld
    9: "scan_market_prices",       # Analysiere Markt
    10: "defend_against_enemies",  # Verteidigung
    # ...
}
```

**Wie lernt das Manager Network?**

```python
# Intrinsic Motivation / Curiosity
def manager_reward(subgoal, outcome, meta_goal):
    """
    Manager bekommt Reward für:
    1. Sub-Goal erreicht (intrinsic)
    2. Meta-Goal näher gekommen (extrinsic)
    """
    reward = 0.0

    # Intrinsic: Hat Sub-Goal funktioniert?
    if outcome['subgoal_achieved']:
        reward += 1.0

    # Extrinsic: Sind wir dem Meta-Goal näher?
    if meta_goal == "become_rich":
        if outcome['credits_increased']:
            reward += outcome['credit_delta'] / 100000

    # Curiosity: Neue Dinge entdeckt?
    if outcome['discovered_new_mechanic']:
        reward += 5.0  # Großer Bonus!

    return reward

# Manager lernt durch Experimentation:
# "Wenn ich 'buy_mining_ship' wähle ohne zu Shipyard zu gehen → Fail!"
# "Ah! Ich muss ERST 'goto_shipyard', DANN 'buy_mining_ship'!"
```

---

### **3. High-Level Meta-Controller: Strategic Neural Network**

```python
# x4_meta_controller.py
class X4MetaController(nn.Module):
    """
    Meta-Controller: Setzt langfristige Ziele

    Lernt:
    - "Wann ist der richtige Zeitpunkt für Expansion?"
    - "Trading vs Production - was ist profitabler?"
    - "Welche Strategie führt zum Erfolg?"
    """

    def __init__(self, num_strategies=10):
        super().__init__()

        # World Model: Versteht Spiel-Zustand
        self.world_model = nn.Sequential(
            nn.Linear(100, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU()
        )

        # Transformer für langfristige Planung
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=512, nhead=8),
            num_layers=4
        )

        # Strategy Selection
        self.strategy_head = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, num_strategies)
        )

    def forward(self, world_state_history):
        """
        Args:
            world_state_history: (T, B, 100) - Letzte T Zeitschritte

        Returns:
            strategy: (B, num_strategies) - Langfristige Strategie
        """
        # Encode world state
        encoded = self.world_model(world_state_history)

        # Transformer für temporal reasoning
        temporal_features = self.transformer(encoded)

        # Pick strategy
        strategy_logits = self.strategy_head(temporal_features[-1])
        strategy_probs = torch.softmax(strategy_logits, dim=-1)

        return strategy_probs

# High-Level Strategies
META_STRATEGIES = {
    0: "aggressive_expansion",     # Schnell expandieren
    1: "economic_focus",           # Economy first
    2: "military_buildup",         # Militär aufbauen
    3: "trade_empire",             # Trading fokussieren
    4: "production_empire",        # Production fokussieren
    5: "balanced_growth",          # Alles bisschen
    6: "risk_averse",              # Sicher spielen
    7: "high_risk_high_reward",    # Riskant aber profitabel
    # ...
}
```

---

## 🎓 **Curriculum Learning: Bot lernt Schritt für Schritt**

Das Geheimnis: **Nicht alles auf einmal lernen!**

```python
# x4_curriculum.py
class X4Curriculum:
    """
    Bot lernt in Stufen (wie Schule!)

    Level 1: Navigation
    Level 2: Trading
    Level 3: Ship Management
    Level 4: Station Building
    Level 5: Empire Management
    """

    def __init__(self):
        self.current_level = 1
        self.levels = {
            1: {
                'name': 'Navigation',
                'goal': 'Lerne zu fliegen und Menüs zu öffnen',
                'reward': 'Reward für: Sektor erreichen, Menü öffnen',
                'max_steps': 10000,
                'success_threshold': 0.8  # 80% Erfolgsrate
            },
            2: {
                'name': 'Basic Trading',
                'goal': 'Kaufe billig, verkaufe teuer',
                'reward': 'Reward für: Profitablen Trade abschließen',
                'max_steps': 50000,
                'success_threshold': 0.7
            },
            3: {
                'name': 'Ship Management',
                'goal': 'Kaufe und verwalte erste Schiffe',
                'reward': 'Reward für: Schiffe kaufen, zu Tasks zuweisen',
                'max_steps': 100000,
                'success_threshold': 0.7
            },
            4: {
                'name': 'Station Building',
                'goal': 'Baue erste Station',
                'reward': 'Reward für: Station gebaut, produziert',
                'max_steps': 200000,
                'success_threshold': 0.6
            },
            5: {
                'name': 'Empire Management',
                'goal': 'Optimiere gesamte Economy',
                'reward': 'Reward für: Credits/Hour maximieren',
                'max_steps': 1000000,
                'success_threshold': 0.5
            }
        }

    def get_current_task(self):
        """Welche Task ist gerade dran?"""
        return self.levels[self.current_level]

    def check_level_up(self, success_rate):
        """Ist Bot bereit für nächstes Level?"""
        threshold = self.levels[self.current_level]['success_threshold']

        if success_rate >= threshold:
            print(f"🎓 Level {self.current_level} bestanden!")
            print(f"   Success Rate: {success_rate:.1%}")
            self.current_level += 1

            if self.current_level <= len(self.levels):
                print(f"📚 Nächstes Level: {self.levels[self.current_level]['name']}")
            else:
                print("🏆 Alle Levels abgeschlossen! Bot ist Expert!")

            return True
        return False

# Training mit Curriculum
curriculum = X4Curriculum()

while curriculum.current_level <= 5:
    task = curriculum.get_current_task()

    print(f"Training Level {curriculum.current_level}: {task['name']}")

    # Train bot auf diesem Level
    success_rate = train_on_task(
        task=task,
        max_steps=task['max_steps']
    )

    # Check ob bereit für nächstes Level
    if not curriculum.check_level_up(success_rate):
        print("❌ Level nicht bestanden. Nochmal trainieren...")
        continue
```

---

## 🎯 **Curiosity-Driven Learning: Bot exploriert selbst**

```python
# x4_curiosity.py
class CuriosityModule(nn.Module):
    """
    Intrinsic Curiosity Module (ICM)

    Bot bekommt Reward für:
    - Neue Dinge entdecken
    - Unbekannte Bereiche erkunden
    - Überraschende Outcomes

    → Lernt Spiel-Mechaniken von selbst!
    """

    def __init__(self, state_dim=512, action_dim=50):
        super().__init__()

        # Forward Model: Predict nächster State
        self.forward_model = nn.Sequential(
            nn.Linear(state_dim + action_dim, 512),
            nn.ReLU(),
            nn.Linear(512, state_dim)
        )

        # Inverse Model: Predict Action von States
        self.inverse_model = nn.Sequential(
            nn.Linear(state_dim * 2, 512),
            nn.ReLU(),
            nn.Linear(512, action_dim)
        )

    def calculate_curiosity_reward(self, state, action, next_state):
        """
        Curiosity Reward = Prediction Error

        Wenn Bot etwas NEUES sieht → Hoher Error → Hoher Reward!
        """
        # Predict was passieren sollte
        predicted_next_state = self.forward_model(
            torch.cat([state, action], dim=1)
        )

        # Wie weit daneben?
        prediction_error = F.mse_loss(predicted_next_state, next_state)

        # Error = Novelty = Curiosity Reward!
        curiosity_reward = prediction_error.item()

        return curiosity_reward

# Total Reward = External + Intrinsic
def total_reward(external_reward, curiosity_reward, beta=0.2):
    """
    beta: Wie wichtig ist Curiosity?
    0.2 = 20% Curiosity, 80% Task Reward
    """
    return external_reward + beta * curiosity_reward

# Bot lernt selbst:
# "Hmm, was passiert wenn ich HIER klicke?" → Neues Menü! → +Reward
# "Was ist dieser Button?" → Ausprobieren → Station bauen! → +Reward
```

---

## 🚀 **Kompletter Training Loop**

```python
# train_x4_neural.py
def train_x4_bot_neural():
    """
    End-to-End Training mit Neural Networks

    Kein Hard-Coding!
    Bot lernt alles selbst!
    """

    # Initialize Networks
    worker = X4WorkerNetwork(action_space_size=50)
    manager = X4ManagerNetwork(num_subgoals=20)
    meta_controller = X4MetaController(num_strategies=10)
    curiosity = CuriosityModule()
    curriculum = X4Curriculum()

    # Initialize Environment
    env = X4Environment()

    # Optimizer
    optimizer = torch.optim.Adam(
        list(worker.parameters()) +
        list(manager.parameters()) +
        list(meta_controller.parameters()),
        lr=3e-4
    )

    # Training Loop
    for episode in range(100000):
        # Reset
        state = env.reset()
        done = False
        episode_reward = 0

        # Meta-Controller wählt Strategie
        strategy = meta_controller(state_history)

        # Manager wählt Sub-Goals
        subgoal = manager(state, strategy)

        step = 0
        while not done:
            # Worker führt Actions aus
            action = worker(screenshot, subgoal)

            # Execute in environment
            next_state, reward, done, info = env.step(action)

            # Curiosity Bonus
            curiosity_reward = curiosity.calculate_curiosity_reward(
                state, action, next_state
            )

            total_reward = reward + curiosity_reward

            # Store experience
            buffer.store(state, action, total_reward, next_state, done)

            # Update networks
            if len(buffer) > batch_size:
                batch = buffer.sample(batch_size)
                loss = compute_loss(batch)  # PPO / SAC / etc.

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # Check if subgoal achieved
            if info['subgoal_achieved']:
                # Manager wählt neues Sub-Goal
                subgoal = manager(next_state, strategy)

            state = next_state
            episode_reward += total_reward
            step += 1

        # Curriculum: Check Level Up
        if episode % 100 == 0:
            success_rate = evaluate_success_rate()
            curriculum.check_level_up(success_rate)

        # Logging
        if episode % 10 == 0:
            print(f"Episode {episode}, Reward: {episode_reward:.2f}, "
                  f"Level: {curriculum.current_level}")

    print("🏆 Training complete! Bot hat X4 gelernt!")
```

---

## ⏱️ **Realistische Timeline für Neural-Ansatz**

| Phase | Dauer | Was passiert |
|-------|-------|--------------|
| **Level 1: Navigation** | 1-2 Tage | Bot lernt: Fliegen, Menüs öffnen |
| **Level 2: Trading** | 3-5 Tage | Bot lernt: Kaufen/Verkaufen |
| **Level 3: Ships** | 1 Woche | Bot lernt: Schiffe kaufen/verwalten |
| **Level 4: Stations** | 2 Wochen | Bot lernt: Stationen bauen |
| **Level 5: Strategy** | 3-4 Wochen | Bot lernt: Optimale Strategie |

**Total: 6-8 Wochen Training** (mit Curriculum Learning)

**OHNE Curriculum:** 6+ Monate oder gar nicht! ❌

---

## 💡 **Warum das funktioniert:**

1. **Hierarchische Networks** → Jedes Level hat eigene Aufgabe
2. **Curriculum Learning** → Lernt Schritt für Schritt (nicht alles auf einmal)
3. **Curiosity** → Exploriert selbst (findet Mechaniken)
4. **Intrinsic Rewards** → Belohnung für Sub-Goals (nicht nur Endziel)

---

## 🎮 **Minimales Scripting nötig:**

```python
# Nur diese Basis-Funktionen sind hard-coded:
- Screenshot nehmen (PIL/MSS)
- Tastatur/Maus senden (pynput)
- X4 API auslesen (Game State: Credits, Ships, etc.)

# Rest: ALLES Neural Networks! ✅
```

---

## 🔥 **Das Coole daran:**

- ✅ Bot lernt **eigene Strategien** (nicht nur deine)
- ✅ **Emergentes Verhalten**: Bot findet Tricks die DU nicht kennst!
- ✅ **Adaptiv**: Funktioniert auch wenn X4 Updates bekommt
- ✅ **Transferable**: Gelerntes könnte auf andere Spiele übertragen werden
- ✅ **Echte AI** - nicht nur Scripting!

---

## 🚀 **Next Steps:**

1. **Implementiere Worker Network** (Low-Level Pixel → Actions)
2. **Trainiere Level 1** (Navigation) mit Curriculum
3. **Füge Manager hinzu** wenn Worker funktioniert
4. **Meta-Controller** als letztes

**Start simple, dann komplexer!** 🎯

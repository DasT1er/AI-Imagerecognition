# MMO Automation Bot - Gathering, Crafting, Farming

## 🎯 Konzept
Ein RL-Bot der repetitive MMO-Tasks automatisiert.

## 🎮 Beste MMOs für Bot-Training

### 1. **Old School RuneScape (OSRS)** ⭐⭐⭐⭐⭐
**Warum PERFEKT:**
- ✅ **2D Grid-basiert**: Einfach zu navigieren
- ✅ **Klare Tasks**: Mining, Woodcutting, Fishing, etc.
- ✅ **Große Bot-Community**: Viel Wissen verfügbar
- ✅ **Private Server**: Legal zum Bot-Training!
- ✅ **Skill Progression**: Messbarer Fortschritt

**⚠️ Problem:** Jagex bannt Bots (aber auf Private Servern okay!)

### 2. **Albion Online** ⭐⭐⭐⭐
**Warum gut:**
- ✅ **Player-driven Economy**: Dein Bot hat echten Impact
- ✅ **Gathering = Profitabel**: Kann Ingame-Geld verdienen
- ✅ **Sandbox**: Viele Freiheiten
- ✅ **Einfache Mechaniken**: Klicken, Laufen, Sammeln

**⚠️ Problem:** Anti-Cheat, aber RL-Bot ist schwerer zu erkennen als Scripts

### 3. **New World** ⭐⭐⭐
**Warum okay:**
- ✅ **Schöne Grafik**: Gut für Vision-Models
- ✅ **Gathering = Wichtig**: Viele Resources
- ⚠️ **3D Navigation**: Komplexer

### 4. **EVE Online** ⭐⭐⭐⭐⭐
**Warum EXZELLENT:**
- ✅ **Erlaubt Automation**: CCP erlaubt Bots teilweise (APIs!)
- ✅ **Komplexe Economy**: Wie X4 aber Multiplayer
- ✅ **Mining, Trading, Manufacturing**: Alles vorhanden
- ✅ **Sehr profitabel**: Bot kann echtes Ingame-Geld machen

---

## 🤖 Bot Architektur

### **Hierarchical Task Agent**

```python
Strategic Layer (RL Agent):
├── Task Selection
│   ├── Was ist gerade profitabel? (Mining vs. Crafting vs. Trading)
│   ├── Welche Ressourcen sind knapp? (Market analysis)
│   └── Wo sind die besten Farming-Spots? (Risk vs. Reward)
│
└── Skill Progression
    ├── Welche Skills leveln?
    └── In welcher Reihenfolge?

Tactical Layer (RL/Scripted):
├── Path Finding (navigiere zu Resource)
├── Gathering (klicke Resource, warte, repeat)
├── Inventory Management (voll? → Bank)
├── Crafting (sammle Materials → Craft Item)
└── Market Interaction (verkaufe Produkte)
```

---

## 📋 Beispiel: OSRS Mining Bot

### Observation Space:
```python
{
    'player_state': {
        'position': (x, y),
        'hp': int,
        'inventory_full': bool,
        'mining_level': int,
        'current_action': str  # 'idle', 'mining', 'walking'
    },
    'environment': {
        'nearest_ore': (x, y, type),  # Position + Typ (Iron, Coal, etc.)
        'ore_respawn_timer': float,    # Wann respawnt Ore?
        'bank_distance': float,
        'players_nearby': int          # Risiko (PKs)
    },
    'inventory': {
        'ore_count': int,
        'pickaxe_equipped': bool,
        'free_slots': int
    },
    'economy': {
        'ore_prices': {ore_type: price},  # Marktpreise
        'profit_per_hour': float
    }
}
```

### Action Space:
```python
Discrete(10):
    0: Idle / Wait
    1: Mine nearest ore
    2: Walk to ore spot
    3: Walk to bank
    4: Deposit inventory at bank
    5: Switch mining spot (find better one)
    6: Eat food (heal)
    7: Run away (if danger)
    8: Hop worlds (if spot crowded)
    9: Sell ores at Grand Exchange
```

### Reward Function:
```python
reward = (
    +1.0 * ore_mined_value +           # Ores abbauen = Geld
    +5.0 * successful_bank +           # Erfolgreich zur Bank = gut
    -0.01 * time_idle +                # Idle time = schlecht
    -10.0 * death_penalty +            # Sterben = sehr schlecht
    +0.1 * experience_gained / 100 +   # Skill XP = gut
    +2.0 * inventory_efficiency        # Vollen Inventory nutzen
)
```

---

## 🎯 **Konkrete Implementation: OSRS Gathering Bot**

### Phase 1: Computer Vision (1-2 Tage)
```python
# osrs_vision.py
class OSRSVision:
    """Erkennt Spielelemente via OCR + Template Matching"""

    def detect_ores(self, screenshot):
        """Finde alle Ores auf dem Screen"""
        # Template Matching für Ore-Icons
        # Oder: Train YOLOv8 auf OSRS Sprites

    def detect_inventory(self, screenshot):
        """Lese Inventory (Items + Count)"""
        # OCR auf Inventory-Bereich

    def detect_player_position(self, screenshot):
        """Wo ist der Spieler?"""
        # Minimap analysis

    def detect_hp(self, screenshot):
        """Lese HP bar"""
        # OCR oder color detection
```

### Phase 2: Action Execution (1 Tag)
```python
# osrs_actions.py
class OSRSController:
    """Führt Actions im Spiel aus"""

    def click_ore(self, ore_position):
        """Klicke auf Ore zum Abbauen"""
        self.mouse.click(ore_position)

    def walk_to(self, target_position):
        """Laufe zu Position (Minimap click)"""
        self.mouse.click_minimap(target_position)

    def open_bank(self):
        """Öffne Bank"""
        self.mouse.click_bank_npc()

    def deposit_all(self):
        """Alles in Bank legen"""
        self.keyboard.press('deposit_all_button')
```

### Phase 3: RL Environment (2-3 Tage)
```python
# osrs_env.py
class OSRSGatheringEnv(gym.Env):
    """Gym Environment für OSRS Gathering"""

    def __init__(self, task='mining'):
        self.task = task  # 'mining', 'woodcutting', 'fishing'
        self.vision = OSRSVision()
        self.controller = OSRSController()

    def reset(self):
        # Teleportiere zu Mining spot
        # Leere Inventory
        return self._get_obs()

    def step(self, action):
        self._execute_action(action)
        time.sleep(1.0)  # OSRS ist langsam (ticks)

        obs = self._get_obs()
        reward = self._calculate_reward()
        done = self._check_done()

        return obs, reward, done, {}

    def _calculate_reward(self):
        # Reward für abgebaute Ores
        # Penalty für Idle time
        # Bonus für Banking
        pass
```

### Phase 4: Training (1-2 Wochen)
```python
# train_osrs_bot.py
from stable_baselines3 import PPO

env = OSRSGatheringEnv(task='mining')
model = PPO("MultiInputPolicy", env, verbose=1)

# Train
model.learn(total_timesteps=100000)
model.save("osrs_mining_bot")
```

---

## ⚖️ Legal & Ethics

### ❌ **NICHT machen:**
- Bots auf offiziellen Servern (= Bannable)
- RMT (Real Money Trading) mit Bot-Farmed items
- PvP-Bots (unfair für andere Spieler)

### ✅ **OK:**
- Training auf Private Servers
- Proof-of-Concept / Research
- Singleplayer/Offline Mods
- Mit Erlaubnis der Game-Devs

### 🎮 **Best Practice:**
Kontaktiere Game-Devs:
> "Hey, ich trainiere einen RL-Bot für Research-Zwecke.
> Kann ich das auf einem Test-Server machen?"

Viele Indie-Devs finden das cool! ✅

---

## 🏆 **Welches MMO ist am besten?**

| MMO | RL-Schwierigkeit | Legal | Profit | Coolness |
|-----|------------------|-------|--------|----------|
| **OSRS (Private Server)** | ⭐⭐☆☆☆ | ✅ Legal | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐☆ |
| **EVE Online** | ⭐⭐⭐⭐☆ | ⚠️ Gray Area | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Albion Online** | ⭐⭐⭐☆☆ | ❌ Risky | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐☆ |

**Empfehlung:** OSRS auf Private Server = Perfekt zum Lernen! ✅

---

## 💰 Expected Results

Nach Training sollte der Bot:
- ✅ **Autonom Gathering** (finde Ores → mine → bank → repeat)
- ✅ **Intelligente Spot-Wahl** (wenig Spieler, viele Resources)
- ✅ **Profitabel** (verdient mehr Gold pro Stunde als Anfänger-Spieler)
- ✅ **Adaptive** (wechselt Task wenn Marktpreise sich ändern)

**Profit:** 500k-1M GP/Stunde mit gutem Bot (comparable mit echten Spielern!)

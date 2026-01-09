# X4: Foundations - Autonomous AI Empire Bot

## 🎯 Konzept
Ein hierarchischer RL-Bot, der eine komplette Fraktion in X4 autonom steuert.

## 🏗️ Architektur

### 1. **Strategic Layer (Reinforcement Learning)**
**Agent Typ:** PPO oder A3C
**Observation Space:**
```python
{
    'economy': {
        'credits': float,              # Aktuelles Geld
        'income_per_hour': float,      # Stündliches Einkommen
        'production_balance': [float], # Für jede Ware: Produktion vs Verbrauch
        'station_count': int,
        'ship_count': int
    },
    'territory': {
        'controlled_sectors': int,
        'sector_danger_levels': [float], # Feindliche Aktivität pro Sektor
        'resource_richness': [float]     # Ressourcen pro Sektor
    },
    'military': {
        'fleet_strength': float,
        'combat_ships': int,
        'total_firepower': float
    },
    'market': {
        'profitable_trades': [[ware, profit_margin]], # Top 10 profitable Waren
        'market_prices': {ware: price}
    }
}
```

**Action Space:**
```python
Discrete(15):
    0:  Idle (Continue current strategy)
    1:  Build Mining Station
    2:  Build Production Station (Smart choice based on market)
    3:  Build Shipyard
    4:  Expand to new Sector
    5:  Buy Trader Ship
    6:  Buy Mining Ship
    7:  Buy Combat Ship (S/M)
    8:  Buy Combat Ship (L)
    9:  Focus on Trading
    10: Focus on Production
    11: Focus on Military
    12: Sell unprofitable assets
    13: Upgrade existing stations
    14: Research/Improve efficiency
```

**Reward Function:**
```python
reward = (
    0.5 * delta_credits / 1000000 +        # Geld verdienen
    0.2 * delta_sectors_controlled +        # Expansion
    0.15 * delta_production_efficiency +    # Bessere Economy
    0.1 * delta_fleet_power +               # Militärische Stärke
    0.05 * sustainability_bonus             # Stabile Economy (kein Crash)
    - 1.0 * station_destroyed_penalty       # Verluste vermeiden
    - 0.5 * bankruptcy_penalty              # Nicht pleite gehen
)
```

**Episode:**
- Zeitbasiert: 2-4 Stunden echte Spielzeit
- Oder: Bis Bankrott / Tod / Dominanz erreicht

---

### 2. **Tactical Layer (Rule-Based + einfaches RL)**

#### **Trading Module:**
```python
class TraderAgent:
    """Findet profitable Handelsrouten und führt sie aus"""

    def find_best_trades(self, max_routes=10):
        # Analysiere Marktpreise
        # Finde: Kaufe Ware X bei Station A, verkaufe bei Station B
        # Berücksichtige: Transportkosten, Reisezeit, Risiko

    def execute_trade_route(self, ship_id, route):
        # Low-level commands: Fliege zu A -> Kaufe -> Fliege zu B -> Verkaufe
```

#### **Mining Module:**
```python
class MiningAgent:
    """Automatisches Mining von Ressourcen"""

    def assign_miners_to_sectors(self):
        # Verteile Mining-Schiffe auf ressourcenreiche Sektoren
        # Berücksichtige Sicherheit (feindliche Aktivität)
```

#### **Station Builder:**
```python
class StationBuilder:
    """Baut Stationen basierend auf Strategic Layer Entscheidungen"""

    def build_station(self, type, sector, resources):
        # 1. Finde besten Standort in Sektor
        # 2. Sammle Ressourcen (kaufe oder produziere)
        # 3. Baue Station
        # 4. Konfiguriere Produktion/Trading
```

---

## 🔧 Implementation Plan

### Phase 1: Game Interface (2-3 Tage)
```python
# x4_api.py - Kommunikation mit X4
class X4Interface:
    def __init__(self):
        # Verwende X4 API oder OCR + UI automation

    def get_game_state(self):
        """Lese aktuellen Spielzustand"""
        # Via API: Credits, Ships, Stations, Market Data
        # Via OCR: Wenn kein API, dann Screen-Reading

    def execute_action(self, action):
        """Führe Aktion aus"""
        # Keyboard/Mouse control oder API calls

    def get_market_data(self):
        """Hole Marktpreise für alle Waren"""

    def get_fleet_status(self):
        """Status aller Schiffe"""
```

**X4 hat GLÜCKLICHERWEISE eine Modding-API!**
- LUA Scripting Interface
- Kann Daten auslesen UND Befehle geben
- VIEL einfacher als OCR!

### Phase 2: Tactical Layer (1 Woche)
Implementiere zuerst die einfachen Module:
- ✅ Auto-Trading (findet profitable Routen)
- ✅ Auto-Mining (schickt Miner zu Ressourcen)
- ✅ Fleet Management (kauft Schiffe, weist Aufgaben zu)

### Phase 3: Strategic RL Agent (2-3 Wochen)
- ✅ Training Environment (Gym wrapper)
- ✅ Reward Shaping
- ✅ PPO Training
- ✅ Evaluation

### Phase 4: Integration & Testing
- ✅ Verbinde Strategic + Tactical Layer
- ✅ Lange Test-Runs (lasse Bot 10+ Stunden laufen)
- ✅ Optimierung

---

## 💡 Warum das GEIL ist:

1. **Praktischer Nutzen**: Du kannst den Bot laufen lassen während du arbeitest/schläfst
2. **Komplexes Problem**: Echte Multi-Agent Koordination
3. **Messbare Erfolge**: Credits, Sectors, Fleet Power
4. **Open-Ended**: Kann immer besser werden
5. **Community Interest**: X4 Community würde das LIEBEN!
6. **Research-Relevant**: Hierarchical RL, Economy AI, Multi-Agent Systems

---

## 🎮 Alternative: X4 Python API

X4 hat Community-Mods die Python APIs bereitstellen:
- **X4 Foundations Mod SDK**: LUA <-> Python Bridge
- **Pipe Server Mod**: Externe Programme können Befehle senden

Damit brauchst du KEIN OCR, sondern hast direkten Zugriff auf:
```python
# Beispiel API calls
x4.get_player_money()
x4.get_all_ships()
x4.get_station_info(station_id)
x4.order_ship_to_mine(ship_id, sector, resource)
x4.build_station(type, sector, modules)
x4.get_market_prices()
```

---

## 🚀 Quick Start für X4 Bot

**Schritt 1:** Installiere X4 Modding Tools
**Schritt 2:** Erstelle einfachen Trading Bot (ohne RL)
**Schritt 3:** Erweitere zu Strategic RL Agent
**Schritt 4:** Lasse ihn laufen und schaue zu wie er ein Empire aufbaut! 🏆

---

## 📊 Expected Results

Nach Training:
- Bot sollte **profitables Trading** lernen
- Intelligente **Station Placement** (wo Resources sind)
- **Economy Balance** (nicht in Waren investieren die keiner kauft)
- **Expansion Timing** (wann ist der richtige Zeitpunkt?)
- **Risk Management** (nicht alles in gefährliche Sektore)

Das wäre ein **Research-Level Projekt**! 🔥

# X4 Bot - Realistischer Gestufter Ansatz

## ❌ **Was NICHT funktioniert:**
```
"Lass RL-Agent das Spiel von 0 lernen"
└─> Würde 10+ Jahre Training brauchen
└─> Exploration Problem zu groß
└─> Reward zu sparse
```

## ✅ **Was FUNKTIONIERT: 3-Stufen-Pyramide**

```
        ┌─────────────────────────────┐
        │   Stufe 3: Strategic RL     │  ← HIER lernt der Bot
        │   "WANN/WO/WAS bauen?"      │     (Strategie optimieren)
        └─────────────────────────────┘
                    ▲
        ┌─────────────────────────────┐
        │  Stufe 2: Imitation Learning│  ← DU zeigst ihm WIE
        │  "WIE spielt man X4?"       │     (von dir lernen)
        └─────────────────────────────┘
                    ▲
        ┌─────────────────────────────┐
        │   Stufe 1: Scripted Basics  │  ← Hard-coded Grundlagen
        │   "API Calls + UI Navigation"│    (kein Learning)
        └─────────────────────────────┘
```

---

## 🎯 **Stufe 1: Scripted Foundation (Hard-coded)**

Diese Dinge sind zu komplex/spezifisch für RL → Einfach implementieren!

```python
# x4_basic_actions.py
class X4BasicActions:
    """Hard-coded Basis-Funktionen (kein Learning!)"""

    def __init__(self):
        self.api = X4ModAPI()  # X4 LUA API Interface

    # ============ NAVIGATION ============
    def fly_to_sector(self, sector_name):
        """Fliege zu Sektor (API call)"""
        self.api.command_ship_travel(self.player_ship, sector_name)
        self.wait_for_arrival()

    def dock_at_station(self, station_id):
        """Docke an Station (API call)"""
        self.api.command_ship_dock(self.player_ship, station_id)

    # ============ TRADING ============
    def buy_ware(self, station_id, ware, amount):
        """Kaufe Ware (API call)"""
        result = self.api.buy_ware(station_id, ware, amount)
        return result  # {'success': bool, 'cost': int}

    def sell_ware(self, station_id, ware, amount):
        """Verkaufe Ware (API call)"""
        result = self.api.sell_ware(station_id, ware, amount)
        return result  # {'success': bool, 'profit': int}

    # ============ FLEET MANAGEMENT ============
    def buy_ship(self, shipyard_id, ship_type):
        """Kaufe Schiff (API call)"""
        cost = self.api.get_ship_price(shipyard_id, ship_type)
        if self.get_credits() >= cost:
            ship_id = self.api.buy_ship(shipyard_id, ship_type)
            return ship_id
        return None

    def assign_ship_to_mine(self, ship_id, sector, resource):
        """Weise Schiff zum Mining zu (API call)"""
        self.api.command_ship_mine(ship_id, sector, resource)

    def assign_ship_to_trade(self, ship_id, route):
        """Weise Schiff zu Handelsroute zu (API call)"""
        self.api.set_ship_trade_route(ship_id, route)

    # ============ STATION BUILDING ============
    def build_station(self, sector, station_type, modules):
        """
        Baue Station (Komplex, aber scriptbar!)

        Args:
            sector: Sektor-Name
            station_type: 'mining', 'factory', 'shipyard'
            modules: Liste von Modulen

        Returns:
            station_id oder None
        """
        # 1. Check ob genug Geld
        cost = self.api.calculate_station_cost(station_type, modules)
        if self.get_credits() < cost:
            return None

        # 2. Finde gute Position im Sektor
        position = self.find_good_station_position(sector, station_type)

        # 3. Baue Station (API call)
        station_id = self.api.build_station(
            sector=sector,
            position=position,
            modules=modules
        )

        # 4. Warte bis fertig
        while not self.api.is_station_built(station_id):
            time.sleep(10)

        return station_id

    def find_good_station_position(self, sector, station_type):
        """
        Finde gute Position für Station (Rule-based!)

        Mining Station → Nahe an Asteroiden
        Factory → Nahe an Handelsrouten
        Shipyard → Zentral im Sektor
        """
        if station_type == 'mining':
            # Finde Asteroid-Felder
            asteroids = self.api.get_sector_resources(sector)
            return asteroids[0]['position']  # Nah am ersten Feld

        elif station_type == 'factory':
            # Zentral platzieren
            return self.api.get_sector_center(sector)

        elif station_type == 'shipyard':
            # Nahe an Gate (Traffic)
            gates = self.api.get_sector_gates(sector)
            return gates[0]['position']

    # ============ MARKET ANALYSIS ============
    def get_profitable_trades(self, max_results=10):
        """
        Finde profitable Handelsrouten (Rule-based!)

        Returns:
            List of {
                'ware': str,
                'buy_station': id,
                'buy_price': int,
                'sell_station': id,
                'sell_price': int,
                'profit_per_unit': int
            }
        """
        all_trades = []

        # Hole alle Stationen
        stations = self.api.get_all_stations()

        # Für jede Ware
        for ware in self.api.get_all_wares():
            # Finde billigste Verkäufer
            sellers = [(s, self.api.get_sell_price(s, ware))
                       for s in stations
                       if self.api.station_sells(s, ware)]

            # Finde teuerste Käufer
            buyers = [(s, self.api.get_buy_price(s, ware))
                      for s in stations
                      if self.api.station_buys(s, ware)]

            if not sellers or not buyers:
                continue

            # Beste Kombination
            cheapest_seller = min(sellers, key=lambda x: x[1])
            best_buyer = max(buyers, key=lambda x: x[1])

            profit = best_buyer[1] - cheapest_seller[1]

            if profit > 0:
                all_trades.append({
                    'ware': ware,
                    'buy_station': cheapest_seller[0],
                    'buy_price': cheapest_seller[1],
                    'sell_station': best_buyer[0],
                    'sell_price': best_buyer[1],
                    'profit_per_unit': profit
                })

        # Sortiere nach Profit
        all_trades.sort(key=lambda x: x['profit_per_unit'], reverse=True)
        return all_trades[:max_results]

    # ============ INFO GATHERING ============
    def get_credits(self):
        """Aktuelles Geld"""
        return self.api.get_player_money()

    def get_all_my_ships(self):
        """Alle meine Schiffe"""
        return self.api.get_player_ships()

    def get_all_my_stations(self):
        """Alle meine Stationen"""
        return self.api.get_player_stations()

    def get_sector_danger_level(self, sector):
        """Wie gefährlich ist Sektor? (Feinde)"""
        enemies = self.api.get_sector_enemy_ships(sector)
        return len(enemies)  # Simpel: Mehr Feinde = gefährlicher
```

**Diese Funktionen sind HARD-CODED** - kein Learning nötig! ✅

---

## 🎮 **Stufe 2: Imitation Learning - DU zeigst es ihm!**

Wie bei deinem CS2 Bot! Du spielst X4, der Bot schaut zu und lernt.

```python
# x4_imitation_learning.py
class X4ImitationLearner:
    """
    Lernt VON DIR wie man X4 spielt!

    Du spielst → Bot zeichnet auf → Bot lernt deine Entscheidungen
    """

    def record_human_gameplay(self, duration_minutes=60):
        """
        Zeichne dein Gameplay auf

        Speichert:
        - Game State (Geld, Schiffe, Stationen, Market)
        - Deine Aktion (z.B. "Baue Mining Station in Sektor X")
        """
        print("🎥 Aufnahme startet! Spiel X4 wie gewohnt...")
        print("   Der Bot lernt von deinen Entscheidungen!")

        data = []
        start_time = time.time()

        while time.time() - start_time < duration_minutes * 60:
            # Capture Game State
            state = {
                'credits': self.actions.get_credits(),
                'ships': self.actions.get_all_my_ships(),
                'stations': self.actions.get_all_my_stations(),
                'market': self.actions.get_profitable_trades(),
                'time_in_game': self.api.get_game_time()
            }

            # Warte auf deine Aktion (z.B. du baust eine Station)
            # Erkenne durch API Monitoring was du machst
            action = self.detect_player_action()

            if action:
                data.append({
                    'state': state,
                    'action': action  # z.B. "BUILD_MINING_STATION"
                })

            time.sleep(5)  # Check alle 5 Sekunden

        # Speichere Daten
        with open('data/human_gameplay_x4.json', 'w') as f:
            json.dump(data, f)

        print(f"✅ Aufnahme beendet! {len(data)} Entscheidungen aufgezeichnet")

    def train_from_human_data(self, data_file='data/human_gameplay_x4.json'):
        """
        Trainiere Bot von deinen Aufnahmen

        Supervised Learning:
        State → Action Mapping
        """
        # Lade Daten
        with open(data_file, 'r') as f:
            data = json.load(f)

        # Erstelle Dataset
        states = [d['state'] for d in data]
        actions = [d['action'] for d in data]

        # Train Neural Network
        # State → Action
        # "Bei 1M Credits und keinen Mining Ships → Baue Mining Ship"
        # "Bei 5M Credits → Baue erste Station"

        model = ImitationNetwork(state_dim=..., action_dim=15)
        model.train(states, actions, epochs=100)

        print("✅ Training beendet! Bot kann jetzt spielen wie DU!")
```

### Was der Bot nach Imitation Learning kann:

Nach 2-3 Stunden **deinem** Gameplay lernt der Bot:
- ✅ "Wenn ich wenig Geld habe → Handel mit profitablen Waren"
- ✅ "Wenn ich 1M Credits habe → Kaufe Mining Ship"
- ✅ "Wenn ich 5M Credits habe → Baue erste Station"
- ✅ "Baue Mining Stations in resourcen-reichen Sektoren"
- ✅ "Kaufe Trading Ships wenn viele profitable Routen da sind"

**Er spielt wie DU!** Aber noch nicht besser. Jetzt kommt Stufe 3...

---

## 🧠 **Stufe 3: Reinforcement Learning - Bot wird BESSER als du!**

Jetzt nutzen wir RL, aber **NUR** für High-Level Strategie!

```python
# x4_strategic_rl.py
class X4StrategyAgent:
    """
    RL Agent für strategische Entscheidungen

    LERNT:
    - Wann/Wo Stationen bauen? (Timing + Location)
    - Welche Waren produzieren? (Market analysis)
    - Expansion-Strategie (welche Sektoren zuerst?)
    """

    def __init__(self, basic_actions, imitation_model):
        self.actions = basic_actions  # Stufe 1: Scripted
        self.imitation = imitation_model  # Stufe 2: Von dir gelernt
        # Stufe 3: RL für Optimierung

    # State Space (VIEL simpler als ganzes Spiel!)
    def get_strategic_state(self):
        """
        Nur HIGH-LEVEL Info!

        Nicht: "Wo ist jedes Schiff?"
        Sondern: "Wie viele Schiffe habe ich?"
        """
        return {
            'credits': self.actions.get_credits(),
            'credits_per_hour': self.calculate_income(),
            'num_mining_ships': len([s for s in self.actions.get_all_my_ships()
                                      if s['type'] == 'miner']),
            'num_trade_ships': len([s for s in self.actions.get_all_my_ships()
                                     if s['type'] == 'trader']),
            'num_stations': len(self.actions.get_all_my_stations()),
            'controlled_sectors': self.get_controlled_sectors(),
            'best_trade_profit': self.actions.get_profitable_trades()[0]['profit_per_unit'],
            'time_played_hours': self.api.get_game_time() / 3600
        }

    # Action Space (VIEL simpler!)
    ACTION_SPACE = [
        0:  "WAIT",  # Nichts tun, Income sammeln
        1:  "BUY_MINING_SHIP",
        2:  "BUY_TRADE_SHIP",
        3:  "BUILD_MINING_STATION",
        4:  "BUILD_FACTORY_STATION",
        5:  "BUILD_SHIPYARD",
        6:  "EXPAND_TO_NEW_SECTOR",
        7:  "UPGRADE_EXISTING_STATION",
        8:  "SELL_UNPROFITABLE_ASSETS",
        9:  "FOCUS_ON_TRADING",  # Viele Trader kaufen
        10: "FOCUS_ON_PRODUCTION",  # Factories bauen
        11: "FOCUS_ON_MILITARY",  # Combat ships
    ]

    def execute_strategic_action(self, action):
        """
        Führe strategische Aktion aus (nutzt Stufe 1+2!)

        Beispiel: Action = BUILD_MINING_STATION

        Bot muss NICHT lernen:
        - ❌ WIE man Menü öffnet
        - ❌ WIE man Module auswählt
        - ❌ WIE man Blueprint kauft

        Bot lernt NUR:
        - ✅ IST JETZT der richtige Zeitpunkt? (genug Geld?)
        - ✅ WELCHER Sektor ist am besten? (meiste Ressourcen)
        - ✅ WELCHE Station bringt meisten Profit?
        """
        if action == 3:  # BUILD_MINING_STATION
            # 1. Check: Kann ich es mir leisten?
            cost = 5_000_000  # Mining Station Kosten
            if self.actions.get_credits() < cost:
                return {'success': False, 'reason': 'not_enough_money'}

            # 2. Finde besten Sektor (Rule-based oder von Imitation gelernt)
            sectors = self.actions.api.get_all_sectors()
            best_sector = max(sectors,
                            key=lambda s: self.get_sector_resource_value(s))

            # 3. STUFE 1 macht die Arbeit! (Hard-coded)
            station_id = self.actions.build_station(
                sector=best_sector,
                station_type='mining',
                modules=['ore_mine', 'storage', 'defense']
            )

            if station_id:
                return {'success': True, 'station_id': station_id}

        # ... andere Aktionen ...

    # Reward Function (NUR für strategische Erfolge!)
    def calculate_reward(self, prev_state, action, new_state):
        """
        Belohne STRATEGIE-Erfolge

        NICHT: "Hast du richtig geklickt?"
        SONDERN: "War diese Investition profitabel?"
        """
        reward = 0.0

        # Hauptziel: Geld verdienen
        credit_gain = new_state['credits'] - prev_state['credits']
        reward += credit_gain / 1_000_000  # Normalisiert

        # Effizienz: Credits per Hour steigern
        income_gain = new_state['credits_per_hour'] - prev_state['credits_per_hour']
        reward += income_gain / 100_000 * 5  # Sehr wichtig!

        # Expansion
        sector_gain = new_state['controlled_sectors'] - prev_state['controlled_sectors']
        reward += sector_gain * 10

        # Penalty für schlechte Investments
        if action in [3, 4, 5]:  # Station gebaut
            # War es profitabel? Check nach 10min
            if self.time_since_action(action) > 600:
                if new_state['credits_per_hour'] <= prev_state['credits_per_hour']:
                    reward -= 20  # Station bringt nichts!

        # Penalty für Idle mit viel Geld
        if action == 0 and new_state['credits'] > 10_000_000:
            reward -= 0.5  # Geld rumliegen lassen = schlecht

        return reward
```

### Was der Bot nach RL-Training kann:

Nach Training lernt er:
- ✅ **Optimales Timing**: "Baue Station bei 5.2M Credits, nicht 5M" (effizienter!)
- ✅ **Bessere Sektor-Wahl**: "Sektor X hat mehr Ressourcen als Y wo DU gebaut hast"
- ✅ **Market-Timing**: "Warte mit Factory bis Material-Preise fallen"
- ✅ **Risk Management**: "Baue Defense bevor du in gefährlichen Sektor expandierst"
- ✅ **Long-term Planning**: "Investiere früh in Shipyard für späteren Profit"

**Er spielt jetzt BESSER als DU!** 🏆

---

## 📊 **Realistische Timeline**

### Phase 1: Scripted Foundation (1-2 Wochen)
- ✅ X4 Mod API Integration
- ✅ Basic Actions implementieren
- ✅ Testing: "Kann der Bot ein Schiff kaufen?" etc.

**Milestone:** Bot kann auf Kommando Trading/Building/etc. ausführen

### Phase 2: Imitation Learning (1 Woche)
- ✅ Recording System (zeichne dein Gameplay auf)
- ✅ Du spielst 3-5 Stunden X4
- ✅ Training: Bot lernt von dir
- ✅ Testing: Lasse Bot autonom spielen

**Milestone:** Bot spielt wie ein "durchschnittlicher Spieler"

### Phase 3: RL Training (2-4 Wochen)
- ✅ Strategic RL Agent
- ✅ Reward Shaping
- ✅ Training (lange Runs)
- ✅ Evaluation

**Milestone:** Bot schlägt menschliche Spieler in Credits/Hour

---

## 🎯 **Total Realistic Scope**

| Complexity | Approach | Learning Time |
|------------|----------|---------------|
| UI Navigation | ❌ ~~RL~~ ✅ **Scripted** | 0 (hard-coded) |
| Basic Trading | ❌ ~~RL~~ ✅ **Scripted** | 0 (rules) |
| Station Building | ❌ ~~RL~~ ✅ **Scripted** | 0 (API calls) |
| "Wie spielt man?" | ❌ ~~RL~~ ✅ **Imitation** | 2-3h deinem Gameplay |
| Strategic Decisions | ✅ **RL** | 100-500 episodes (~1-2 weeks) |

**Gesamt: 6-8 Wochen für funktionierenden strategischen Bot** ✅

---

## 💡 **Die Wahrheit:**

Reines RL funktioniert nur für:
- ✅ Einfache Spiele (Pong, Breakout)
- ✅ Spiele mit klaren Regeln (Chess, Go)
- ✅ Spiele mit dichten Rewards (Racing)

Für komplexe Spiele (X4, MMOs, Strategy) brauchst du:
- 📋 **Scripted Foundation** (40% des Codes)
- 🎮 **Imitation Learning** (30% des Wissens)
- 🧠 **RL für Optimierung** (30% Strategie)

**Genau wie dein CS2 Bot!** Du hast ja auch:
1. Hard-coded Keyboard/Mouse Control
2. Imitation Learning von deinem Gameplay
3. PPO für Verbesserung

Gleicher Ansatz, nur anderes Spiel! 🚀

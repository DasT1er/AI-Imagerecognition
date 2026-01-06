# CS2 AI Aimbot - Team-Aware System 🎯

**Machine Learning System das Gegner erkennt UND zwischen Teams unterscheidet!**

**⚠️ NUR FÜR OFFLINE-BOTS! Nicht online verwenden!**

---

## ✨ Besonderes Feature: Team-Detection

Die AI erkennt **automatisch** dein Team und zielt **NUR** auf Gegner!

- 🔵 **Blau UI** = Du bist CT → Zielt auf Terroristen
- 🟠 **Orange UI** = Du bist T → Zielt auf Counter-Terrorists
- ✅ **Kein Friendly Fire!**

---

## 🎯 4-Klassen System

Labele für jeden Gegner:
1. **Enemy CT** (Blau) oder **Enemy T** (Orange) - Ganzer Körper
2. **Head** - Kopf (exakte Position!)
3. **Legs** - Beine (für Wallbang/Movement)

Die AI lernt:
- ✅ Team-Unterscheidung (CT vs T)
- ✅ Exakte Kopf-Position
- ✅ Beine für bessere Detection
- → **Nur auf Gegner zielen!**

---

## 🚀 Schnellstart

### Doppelklick auf:
```
START.bat
```

### Oder manuell:
```bash
# 1. Dependencies
pip install -r requirements.txt

# 2. Screenshots (10-15 Min spielen)
cd 1_data_collection
python capture_auto.py

# 3. Labeling (4 Klassen!)
python label_team_aware.py
# Für jeden Gegner:
# - 1/2 = Enemy (CT oder T)
# - 3 = Head
# - 4 = Legs

# 4. Dataset vorbereiten
python prepare_dataset_team_aware.py

# 5. Training (30 Min - 2h)
cd ../2_training
python train_model.py

# 6. Team-Aware Auto-Aim!
cd ../3_detection
python auto_aim_team_aware.py
```

---

## 🎮 Labeling Workflow

**Pro Gegner im Bild:**

1. Schaue UI-Farbe: Blau (CT) oder Orange (T)?
2. Drücke **1** (CT) oder **2** (T)
3. Ziehe Box um **ganzen Gegner**
4. Drücke **3**
5. Ziehe Box um **Kopf**
6. Drücke **4**
7. Ziehe Box um **Beine**
8. Wiederhole für alle Gegner
9. Drücke **S** zum Speichern

**Farben:**
- 🔵 Blau = Enemy CT
- 🟠 Orange = Enemy T
- 🔴 Rot = Head
- 🟣 Magenta = Legs

---

## 🎯 Auto-Aim Features

```bash
python auto_aim_team_aware.py
```

- **Automatische Team-Erkennung**
  - Analysiert UI oben links
  - Erkennt Blau (CT) oder Orange (T)

- **Nur gegnerische Targets**
  - Du = CT → Zielt auf T
  - Du = T → Zielt auf CT

- **Kein Friendly Fire**
  - Eigenes Team wird ignoriert!
  - Markiert Teammates grau

- **RMB halten** = Aim aktiv

---

## 📁 Struktur

```
cs2-aimbot-ml/
├── START.bat                           # Hauptmenü
├── 1_data_collection/
│   ├── capture_auto.py                 # Auto-Screenshots
│   ├── label_team_aware.py             # 4-Klassen Labeling
│   └── prepare_dataset_team_aware.py   # Dataset Prep
├── 2_training/
│   └── train_model.py                  # YOLOv8 Training
├── 3_detection/
│   └── auto_aim_team_aware.py          # Team-Aware Aim!
└── 4_evaluation/
    └── evaluate_model.py
```

---

## 📊 Erwartete Ergebnisse

**Mit 300 Bildern, gut gelabelt:**
- mAP@50 (Enemy CT): ~0.85
- mAP@50 (Enemy T): ~0.85
- mAP@50 (Head): ~0.75
- mAP@50 (Legs): ~0.70

**Auto-Aim:**
- Team-Erkennungsrate: ~95%+
- Kein Friendly Fire
- Headshot-Rate: ~85%

---

## 🔧 Requirements

```
Python 3.8+
GPU empfohlen
OpenCV, PyTorch, YOLOv8
```

---

## ⚠️ Disclaimer

**Nur für:**
- ✅ Lernzwecke
- ✅ Offline-Bots
- ✅ Zum Verstehen von ML/CV

**NICHT für:**
- ❌ Online-Multiplayer (BAN!)
- ❌ Competitive Gaming
- ❌ Unfairer Vorteil

---

## 💡 Technische Details

### Team-Erkennung:
```python
# Analysiert UI-Bereich oben links (0:150, 0:200)
# HSV-Farberkennung:
# Blau (90-130 HSV) = CT
# Orange (10-30 HSV) = T
```

### Target-Validierung:
```python
if player_team == 'CT' and enemy_class == 'enemy_t':
    # Ziele auf T
elif player_team == 'T' and enemy_class == 'enemy_ct':
    # Ziele auf CT
else:
    # Ignoriere (eigenes Team!)
```

---

Made with YOLOv8 | PyTorch | OpenCV | Computer Vision

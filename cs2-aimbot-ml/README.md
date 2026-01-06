# CS2 AI Aimbot - Complete Training System

Ein Machine Learning Projekt zum Trainieren einer KI die Gegner und Köpfe in CS2 erkennt.

**⚠️ NUR FÜR OFFLINE-BOTS! Nicht in Online-Matches verwenden!**

---

## 🚀 Schnellstart (Windows)

### Einfach:
```
Doppelklick auf START.bat
```

### Manuell:
```bash
# 1. Dependencies installieren
pip install -r requirements.txt

# 2. Screenshots sammeln
cd 1_data_collection
python capture_auto.py

# 3. Labeling (Enemy + Head)
python label_advanced.py

# 4. Dataset vorbereiten
python prepare_dataset_advanced.py

# 5. Training
cd ../2_training
python train_model.py

# 6. Testen
cd ../3_detection
python auto_aim_advanced.py
```

---

## 📁 Struktur

```
1_data_collection/
  - capture_auto.py          # Screenshots sammeln
  - label_advanced.py        # Multi-Class Labeling
  - prepare_dataset_advanced.py

2_training/
  - train_model.py           # YOLOv8 Training
  - visualize_training.py    # Plots

3_detection/
  - detect_realtime.py       # Live Detection
  - auto_aim_advanced.py     # Auto-Aim

4_evaluation/
  - evaluate_model.py        # Metriken
```

---

## 🎯 Multi-Class System

Labele **BEIDE** für jeden Gegner:
- **Enemy (E)**: Grüne Box um ganzen Gegner
- **Head (H)**: Rote Box um Kopf

Die AI lernt dann:
- Wo Gegner sind
- Wo Köpfe EXAKT sind → 90%+ Headshot-Genauigkeit!

---

## 📊 Workflow

1. **Screenshots**: `capture_auto.py` - Spiele 10-15 Min
2. **Labeling**: `label_advanced.py` - Markiere Enemy + Head
3. **Dataset**: `prepare_dataset_advanced.py` - Auto train/val split
4. **Training**: `train_model.py` - 30 Min - 2h
5. **Testing**: `auto_aim_advanced.py` - RMB = Aim

---

## ⚙️ Labeling Steuerung

- **E** = Enemy Mode (grün)
- **H** = Head Mode (rot)
- **S** = Speichern & weiter
- **D** = Überspringen
- **U** = Letzte Box löschen
- **Q** = Beenden

---

## 🎯 Auto-Aim

```bash
python auto_aim_advanced.py
```

- **RMB halten** = Aim aktiv
- Zielt auf exakte Kopf-Position (Class 1)
- ~90%+ Headshot-Rate

---

## 📈 Erwartete Ergebnisse

**Mit 300 Bildern:**
- mAP@50: ~0.8
- Headshot-Rate: ~85%

**Mit 500+ Bildern:**
- mAP@50: >0.9
- Headshot-Rate: ~95%

---

## 🔧 Requirements

```
Python 3.8+
GPU empfohlen (10x schneller)
~2GB Speicher
```

---

## 📚 Weitere Infos

Detaillierte Anleitung: **MULTI_CLASS_GUIDE.md**

---

## ⚠️ Disclaimer

Nur für:
- ✅ Lernzwecke
- ✅ Offline-Bots
- ❌ NICHT für Online-Multiplayer (BAN-Risiko!)

---

Made with YOLOv8 | PyTorch | OpenCV

# CS2 AI Target Detection - Projekt-Übersicht

## 🎯 Was ist das?

Ein **vollständiges Machine Learning Projekt** zum Trainieren einer KI, die automatisch Gegner in Counter-Strike 2 erkennt.

**Verwendungszweck:** Nur für Bildung und Offline-Nutzung!

---

## ✨ Was macht dieses Projekt besonders?

### 1. **Komplett & Einsatzbereit**
- Alle Scripts fertig
- Keine zusätzliche Konfiguration nötig
- Einfach installieren und loslegen

### 2. **Anfängerfreundlich**
- Schritt-für-Schritt Anleitungen
- Klare Kommentare in jedem Script
- Interaktiver Workflow-Helper
- Farbige Terminal-Ausgaben zur besseren Orientierung

### 3. **Lernfokus**
- **Siehst LIVE wie die AI lernt**
- Training-Metriken werden erklärt
- Visualisierungen zeigen Fortschritt
- Verständliche Fehlerbehandlung

### 4. **Production-Ready Code**
- Saubere Struktur
- Error Handling
- Performance-Optimierungen
- Best Practices

---

## 📦 Was ist enthalten?

### Data Collection Tools
- **capture_screenshots.py** - Screenshot-Tool mit F9-Hotkey
- **label_targets.py** - Grafisches Labeling-Tool
- **prepare_dataset.py** - Automatischer Train/Val Split

### Training Pipeline
- **train_model.py** - YOLOv8 Training mit Live-Metriken
- **visualize_training.py** - Detaillierte Trainings-Plots

### Detection & Testing
- **detect_realtime.py** - Live-Detection mit Overlay
- **evaluate_model.py** - Performance-Metriken & Beispiele

### Dokumentation
- **README.md** - Vollständige Dokumentation
- **QUICKSTART.md** - 30-Minuten Schnellstart
- **workflow_helper.py** - Interaktiver Guide

---

## 🔧 Technologie-Stack

- **YOLOv8** (Ultralytics) - State-of-the-art Object Detection
- **PyTorch** - Deep Learning Framework
- **OpenCV** - Computer Vision
- **MSS** - Schnelle Screen Capture
- **TensorBoard** - Training Visualisierung
- **Colorama** - Schöne Terminal-Ausgaben

---

## 📊 Was lernst du hier?

### Machine Learning Konzepte:
- ✅ Data Collection & Labeling
- ✅ Train/Validation Split
- ✅ Transfer Learning
- ✅ Model Training & Evaluation
- ✅ Hyperparameter Tuning

### Computer Vision:
- ✅ Object Detection
- ✅ Bounding Box Regression
- ✅ Image Preprocessing
- ✅ Real-time Inference

### Software Engineering:
- ✅ Projekt-Struktur
- ✅ CLI Tools
- ✅ Error Handling
- ✅ Performance Optimization

---

## 🚀 Quick Start

```bash
# 1. Installation
pip install -r requirements.txt

# 2. Workflow starten
python workflow_helper.py
```

**Oder folge dem QUICKSTART.md für detaillierte Schritte.**

---

## 📈 Erwartete Ergebnisse

### Mit 100 Bildern & 100 Epochs:
- mAP@50: ~0.5-0.6 (OK für ersten Test)
- Training: ~30 Min (GPU) / ~2h (CPU)

### Mit 300+ Bildern & 200 Epochs:
- mAP@50: ~0.7-0.9 (Gut bis Exzellent)
- Training: ~1-2h (GPU) / ~4-6h (CPU)

### Mit 500+ Bildern & professionellem Setup:
- mAP@50: >0.9 (Production-Ready)
- Erkennt Gegner zuverlässig in Echtzeit

---

## 🎮 Workflow-Übersicht

```
1. Screenshots sammeln (20-60 Min)
   └─> data/raw/*.png

2. Gegner markieren (30-90 Min)
   └─> data/labeled/{images,labels}

3. Dataset vorbereiten (1 Min)
   └─> data/{train,val}

4. Model trainieren (30 Min - 2h)
   └─> models/cs2_target_detector_*/weights/best.pt

5. Evaluieren & Testen
   └─> Live Detection in CS2!
```

---

## 🔍 Projekt-Struktur

```
cs2-aimbot-ml/
│
├── 📄 README.md                    # Vollständige Doku
├── 📄 QUICKSTART.md                # 30-Min Schnellstart
├── 📄 PROJECT_OVERVIEW.md          # Diese Datei
├── 🐍 workflow_helper.py           # Interaktiver Guide
├── 📋 requirements.txt             # Dependencies
├── 🚫 .gitignore                   # Git Ignore
│
├── 📁 1_data_collection/           # Daten sammeln
│   ├── capture_screenshots.py      # Screenshots (F9)
│   ├── label_targets.py            # Labeling Tool
│   └── prepare_dataset.py          # Dataset Prep
│
├── 📁 2_training/                  # Training
│   ├── train_model.py              # Haupt-Training
│   └── visualize_training.py       # Plots erstellen
│
├── 📁 3_detection/                 # Live-Detection
│   └── detect_realtime.py          # Echtzeit-Erkennung
│
├── 📁 4_evaluation/                # Evaluation
│   └── evaluate_model.py           # Metriken & Tests
│
├── 📁 data/                        # Daten (auto-generiert)
│   ├── raw/                        # Screenshots
│   ├── labeled/                    # Labels
│   ├── train/                      # Training Set
│   ├── val/                        # Validation Set
│   └── data.yaml                   # Config
│
└── 📁 models/                      # Trainierte Models
    └── cs2_target_detector_*/
        └── weights/
            ├── best.pt             # Bestes Model
            └── last.pt             # Letztes Model
```

---

## 🎓 Lernpfad-Empfehlung

### Für absolute Anfänger:
1. Lies **QUICKSTART.md**
2. Führe **workflow_helper.py** aus
3. Folge den Anweisungen

### Für ML-Einsteiger:
1. Lies **README.md**
2. Verstehe jeden Schritt
3. Experimentiere mit Parametern

### Für Fortgeschrittene:
1. Analysiere den Code
2. Erweitere das Projekt
3. Implementiere eigene Features

---

## 💡 Erweiterungs-Ideen

- [ ] Multi-Class Detection (Gegner, Teammates, Waffen)
- [ ] Headshot-Only Detection
- [ ] Action Recognition (Stehen, Hocken, Laufen)
- [ ] Model Export (ONNX, TensorRT)
- [ ] Mobile Deployment
- [ ] Web Interface für Labeling
- [ ] Automatisches Data Augmentation
- [ ] Custom Architecturen

---

## ⚠️ Wichtige Hinweise

### Ethik:
- ✅ Nur für Bildung & Offline-Nutzung
- ❌ NICHT in Online-Matches verwenden
- ❌ Cheating ist unfair und verboten

### Performance:
- GPU empfohlen (10x schneller)
- Min. 8GB RAM
- ~2GB freier Speicher

### Anti-Cheat:
- Screen-based AI ist schwer zu erkennen
- Aber: ToS-Verstoß = Ban-Risiko
- Nur gegen Offline-Bots!

---

## 📞 Support & Troubleshooting

### Häufige Probleme:

**"No module named 'ultralytics'"**
→ `pip install -r requirements.txt`

**"Model not found"**
→ Training noch nicht abgeschlossen

**"CUDA out of memory"**
→ Reduziere `batch=16` zu `batch=4`

**"mAP ist sehr niedrig"**
→ Mehr Daten sammeln (300+)
→ Länger trainieren (200 Epochs)

---

## 🎉 Credits

**Erstellt für:** Lernzwecke & ML-Education

**Basiert auf:**
- YOLOv8 (Ultralytics)
- PyTorch
- OpenCV

**Inspiriert von:**
- Computer Vision Community
- ML-Forschung
- Game AI Research

---

## 📜 Lizenz

Dieses Projekt ist für **Bildungszwecke** erstellt.

**Nutzungsbedingungen:**
- ✅ Lernen & Experimentieren
- ✅ Teilen & Anpassen (mit Attribution)
- ❌ Kommerzieller Missbrauch
- ❌ Online-Gaming Cheating

---

## 🚀 Los geht's!

**Bereit zum Starten?**

```bash
# Für Anfänger:
python workflow_helper.py

# Für Schnellstart:
cat QUICKSTART.md

# Für vollständige Doku:
cat README.md
```

**Happy Learning & Coding!** 🎯

---

**Version:** 1.0
**Erstellt:** 2026
**Status:** Production Ready ✅

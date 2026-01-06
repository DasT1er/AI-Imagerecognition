# CS2 AI Target Detection System 🎯

Ein Machine Learning Projekt zum Trainieren einer KI, die Gegner in Counter-Strike 2 erkennt.

**⚠️ Wichtig: Nur für Lernzwecke! Nur gegen Offline-Bots verwenden!**

## 🎓 Was lernst du hier?

- **Computer Vision** - Wie Bilder analysiert werden
- **Object Detection** - Wie Objekte in Bildern gefunden werden
- **Deep Learning** - Wie neuronale Netze trainiert werden
- **YOLOv8** - Moderne Object Detection Architektur
- **Training Pipeline** - Kompletter ML-Workflow von Daten bis Deployment

## 📊 Features

✅ **Live Training-Visualisierung** - Sieh genau wie deine AI lernt!
✅ **Echtzeit-Detection** - Teste die AI live während du spielst
✅ **Performance-Metriken** - Klare Zahlen zum Fortschritt
✅ **Einfache Bedienung** - Schritt-für-Schritt Anleitung
✅ **Vollständig kommentiert** - Verstehe jeden Schritt

---

## 🚀 Schnellstart - 5 Schritte zum eigenen AI-Aimbot

### Schritt 1: Installation (5 Minuten)

```bash
# 1. Python 3.8+ installiert? Prüfe:
python --version

# 2. Navigiere ins Projekt
cd cs2-aimbot-ml

# 3. Installiere Dependencies
pip install -r requirements.txt
```

**Hinweis:** Bei GPU-Support (schnelleres Training):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

### Schritt 2: Daten sammeln (30-60 Minuten)

**Ziel: 300-500 Screenshots mit Gegnern**

```bash
# 1. Starte CS2
#    - Spiele gegen OFFLINE BOTS
#    - Casual Match oder Deathmatch
#    - Stelle Bot-Schwierigkeit niedrig (damit sie dich nicht sofort killen!)

# 2. Starte Screenshot-Tool
cd 1_data_collection
python capture_screenshots.py

# 3. Während du spielst:
#    - Drücke F9 wenn Gegner im Bild sind
#    - Versuche verschiedene:
#      • Entfernungen (nah, mittel, weit)
#      • Posen (stehend, hockend, springend)
#      • Maps und Beleuchtung
#    - Drücke ESC zum Beenden

# Ziel: Min. 300 Screenshots (mehr = besser!)
```

**💡 Tipp:** Spiele 3-4 Runden und mache alle paar Sekunden Screenshots wenn Gegner sichtbar sind.

---

### Schritt 3: Gegner markieren (1-2 Stunden)

**Jetzt bringst du der AI bei, WAS ein Gegner ist**

```bash
# Starte Labeling-Tool
python label_targets.py

# Verwendung:
# 1. Klicke und ziehe eine Box um JEDEN Gegner im Bild
# 2. Drücke 's' zum Speichern und nächstes Bild
# 3. Drücke 'd' zum Überspringen (wenn kein Gegner sichtbar)
# 4. Drücke 'u' um letzte Box rückgängig zu machen
```

**💡 Tipps für gute Labels:**
- Box sollte den **ganzen Gegner** umschließen (Kopf bis Fuß)
- Auch teilweise sichtbare Gegner markieren
- Präzise sein! Gute Labels = bessere AI

**Beispiel:**
```
✓ Box um ganzen Körper
✗ Nur Kopf markieren
✗ Zu viel Hintergrund in der Box
```

---

### Schritt 4: Dataset vorbereiten (1 Minute)

```bash
# Teilt Daten in Training (80%) und Validation (20%)
python prepare_dataset.py
```

Das Script erstellt automatisch:
- `data/train/` - Training-Daten
- `data/val/` - Validation-Daten
- `data/data.yaml` - Konfigurations-Datei

---

### Schritt 5: Training starten! 🚀 (30 Min - 2 Stunden)

**JETZT WIRD'S SPANNEND! Die AI lernt!**

```bash
cd ../2_training
python train_model.py
```

**Was passiert jetzt:**

```
Epoch 1/100:  ███░░░░░░░░ 10%
  Loss: 2.543  ⬇️ (sollte sinken)
  mAP@50: 0.234  ⬆️ (sollte steigen)

Epoch 10/100: ██████░░░░░ 60%
  Loss: 1.234  ⬇️ Besser!
  mAP@50: 0.567  ⬆️ Wird besser!

Epoch 50/100: ██████████░ 90%
  Loss: 0.423  ⬇️ Sehr gut!
  mAP@50: 0.867  ⬆️ Exzellent!
```

**💡 Was bedeuten die Zahlen?**

- **Loss** (Verlust):
  - Wie "falsch" die AI liegt
  - **Je niedriger, desto besser**
  - Startet hoch (2-3), sollte sinken (0.3-0.5)

- **mAP@50** (Mean Average Precision):
  - Wie gut die AI Gegner erkennt
  - **Je höher, desto besser** (0.0 - 1.0)
  - 0.5 = OK, 0.7 = Gut, 0.9+ = Exzellent

**Live-Visualisierung (Optional):**

Öffne ein zweites Terminal:
```bash
tensorboard --logdir ../models/cs2_target_detector_n
```
Dann öffne: `http://localhost:6006`

Hier siehst du:
- 📈 Loss-Kurven
- 📊 mAP-Entwicklung
- 🖼️ Beispiel-Detections
- 📉 Learning Rate

---

### Schritt 6: Testen! 🎮

**A) Evaluation (Zahlen ansehen):**

```bash
cd ../4_evaluation
python evaluate_model.py
```

Zeigt dir:
- **Precision**: Von allen Detections, wie viele sind korrekt?
- **Recall**: Von allen Gegnern, wie viele wurden gefunden?
- **mAP**: Gesamt-Performance
- Beispiel-Predictions

**B) Live-Test (IN CS2!):**

```bash
cd ../3_detection
python detect_realtime.py
```

1. Starte CS2 (gegen Bots)
2. Das Script zeigt ein Overlay-Fenster
3. Grüne Boxen = Erkannte Gegner!
4. Du siehst:
   - Bounding Boxes um Gegner
   - Confidence Score (Wie sicher die AI ist)
   - FPS (Frames pro Sekunde)
   - Anzahl erkannter Targets

**Drücke Q zum Beenden**

---

## 📊 Training-Fortschritt verstehen

### Gute Werte nach Training:

| Metrik | Schlecht | OK | Gut | Exzellent |
|--------|----------|-----|-----|-----------|
| **mAP@50** | < 0.5 | 0.5 - 0.7 | 0.7 - 0.9 | > 0.9 |
| **Precision** | < 0.6 | 0.6 - 0.8 | 0.8 - 0.95 | > 0.95 |
| **Recall** | < 0.5 | 0.5 - 0.7 | 0.7 - 0.9 | > 0.9 |

### Loss-Kurven interpretieren:

```
Gutes Training:              Schlechtes Training:
Loss                         Loss
 │ ╲                          │ ╱╲╱╲
 │  ╲                         │    ╲╱╲
 │   ╲___                     │
 │       ────                 │ (nicht stabil)
 └────────── Epochs           └────────── Epochs
```

---

## 🔧 Troubleshooting

### Problem: mAP ist niedrig (< 0.5)

**Lösungen:**
1. **Mehr Daten sammeln**
   - Ziel: Min. 500 Bilder
   - Verschiedene Maps, Positionen, Lichtverhältnisse

2. **Labels überprüfen**
   - Sind die Boxen präzise?
   - Wurde jeder Gegner markiert?

3. **Länger trainieren**
   - Erhöhe `epochs=100` auf `epochs=200` in `train_model.py`

4. **Größeres Model**
   - In `train_model.py`: Ändere `model_size="n"` zu `model_size="s"` oder `"m"`

### Problem: GPU Out of Memory

**Lösung:** Reduziere Batch Size in `train_model.py`:
```python
batch=16  →  batch=8  (oder batch=4)
```

### Problem: Training ist sehr langsam

**Lösungen:**
- Nutze GPU (siehe Installation oben)
- Kleineres Model: `model_size="n"` (nano)
- Kleinere Bilder: `imgsz=416` statt `640`

### Problem: FPS zu niedrig bei Real-time Detection

**Lösungen:**
1. Nutze kleineres Model (`yolov8n`)
2. Reduziere Auflösung in `detect_realtime.py`
3. Erhöhe `confidence_threshold` (weniger Detections)

---

## 📁 Projekt-Struktur

```
cs2-aimbot-ml/
│
├── 1_data_collection/          # Daten sammeln & labeln
│   ├── capture_screenshots.py  # Screenshots machen (F9)
│   ├── label_targets.py        # Gegner markieren
│   └── prepare_dataset.py      # Train/Val Split
│
├── 2_training/                 # Model trainieren
│   ├── train_model.py          # Haupttraining
│   └── visualize_training.py   # Training-Plots ansehen
│
├── 3_detection/                # Live-Detection
│   └── detect_realtime.py      # AI live testen
│
├── 4_evaluation/               # Performance messen
│   └── evaluate_model.py       # Metriken & Beispiele
│
├── data/                       # Daten (automatisch erstellt)
│   ├── raw/                    # Rohe Screenshots
│   ├── labeled/                # Gelabelte Daten
│   ├── train/                  # Training Set
│   ├── val/                    # Validation Set
│   └── data.yaml              # Konfiguration
│
├── models/                     # Trainierte Models
│   └── cs2_target_detector_*/
│       └── weights/
│           ├── best.pt         # Bestes Model
│           └── last.pt         # Letztes Model
│
└── requirements.txt            # Dependencies
```

---

## 🎯 Nächste Schritte & Erweiterungen

Wenn dein Model gut funktioniert, kannst du:

### 1. **Multi-Class Detection**
Erkenne verschiedene Dinge:
- Gegner
- Teammates
- Waffen
- Granaten

### 2. **Action Prediction**
Erkenne was Gegner tun:
- Stehen
- Laufen
- Hocken
- Schießen

### 3. **Automatisches Aim** (nur zum Lernen!)
```python
# In detect_realtime.py ergänzen:
if target_detected:
    center_x, center_y = get_target_center()
    move_mouse_to(center_x, center_y)
```

### 4. **Head-Only Detection**
Trainiere für Headshots:
- Labele nur Köpfe
- Kleinere Bounding Boxes
- Höhere Precision nötig

---

## 📚 Weitere Resourcen

### YOLOv8 Dokumentation:
https://docs.ultralytics.com/

### TensorBoard Guide:
https://www.tensorflow.org/tensorboard

### Computer Vision Basics:
https://opencv.org/

---

## ⚠️ Disclaimer

**Dieses Projekt ist NUR für Bildungszwecke!**

- ✅ Gegen Offline-Bots trainieren und testen
- ✅ Zum Lernen von ML/CV Konzepten
- ✅ Für eigene Experimente

- ❌ NICHT in Online-Multiplayer verwenden
- ❌ NICHT gegen echte Spieler
- ❌ Cheating ist unfair und gegen ToS

**Verwendung in Online-Games kann zu:**
- Account-Bans
- Hardware-Bans (HWID)
- Rechtlichen Konsequenzen

**Sei verantwortungsvoll!** 🙏

---

## 📞 Support

**Probleme?**

1. Lies die Fehlermeldung genau
2. Check "Troubleshooting" Sektion oben
3. Prüfe dass alle Dependencies installiert sind
4. Stelle sicher dass genug Daten vorhanden sind

**Häufige Anfängerfehler:**
- Zu wenige Trainings-Daten (< 200 Bilder)
- Schlechte Labels (zu groß/klein/falsch)
- Training zu kurz (< 50 Epochs)
- Kein GPU (Training dauert sehr lange)

---

## 🎉 Viel Erfolg!

Du hast jetzt alle Tools um:
- ✅ Eigene Daten zu sammeln
- ✅ Ein AI-Model zu trainieren
- ✅ Den Fortschritt zu sehen
- ✅ Die AI live zu testen

**Happy Training!** 🚀

---

**Credits:**
- YOLOv8: Ultralytics
- Framework: PyTorch
- Inspiration: Computer Vision Community

---

Made with ❤️ for Learning

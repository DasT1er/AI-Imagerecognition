# Testing & Evaluation Guide

So testest du wie gut dein trainiertes Model funktioniert!

---

## 🎯 Test-Methoden

### 1. **Visuelles Testing** (Empfohlen zuerst!)

Zeigt dir **genau** was das Model erkennt auf deinen Screenshots.

```bash
cd 4_evaluation
python test_detection_visual.py ../data/yolo_6class/runs/detect/train/weights/best.pt
```

**Was du siehst:**
- ✅ Bounding Boxes um erkannte Spieler
- ✅ Klassen-Labels (CT Body, T Head, etc.)
- ✅ Confidence Scores (0.0-1.0)
- ✅ Statistiken pro Bild

**Steuerung:**
- `SPACE` = Nächstes Bild
- `Q` = Beenden

**Interpretation:**
- Viele richtige Detections? ✅ Gut!
- Falsche Klassen? ❌ Mehr Training-Daten
- Spieler nicht erkannt? ❌ Mehr Beispiele labeln

---

### 2. **Metrics Evaluation**

Berechnet **wissenschaftliche Metriken** auf dem Validation-Set.

```bash
cd 4_evaluation
python evaluate_metrics.py ../data/yolo_6class/runs/detect/train/weights/best.pt
```

**Wichtige Metriken:**

- **mAP@50** (mean Average Precision @ 50% IoU)
  - `> 0.7` = 🟢 Sehr gut!
  - `0.5 - 0.7` = 🟡 Okay
  - `< 0.5` = 🔴 Mehr Daten nötig

- **Precision** = Von allen Detections, wie viele waren richtig?
  - Hohe Precision = Wenige False Positives

- **Recall** = Von allen Spielern im Bild, wie viele wurden erkannt?
  - Hoher Recall = Wenige Missed Detections

**Output:**
- Confusion Matrix als PNG
- Pro-Klasse Metriken
- Validation Visualisierungen

---

### 3. **Live Detection Test** (OHNE Aimbot!)

Zeigt dir **LIVE** während du CS2 spielst was die AI sieht.

```bash
cd 4_evaluation
python test_live_detection.py ../data/yolo_6class/runs/detect/train/weights/best.pt
```

**Was du siehst:**
- Live-Feed mit Bounding Boxes
- FPS Counter
- Detection Count (CT / T)

**Vorteile:**
- ✅ Siehst sofort ob Model funktioniert
- ✅ Testest in echten Gameplay-Situationen
- ✅ Kein Risiko (nur Visualisierung, kein Aimbot)

**Steuerung:**
- `Q` = Beenden

---

## 📊 Workflow: Vom Training zum fertigen Aimbot

```
1. Training abgeschlossen
   ↓
2. Visuelles Testing
   python test_detection_visual.py <model>
   → Schau ob Detections gut aussehen
   ↓
3. Metrics Evaluation
   python evaluate_metrics.py <model>
   → Prüfe mAP@50 Score
   ↓
4. Live Detection Test
   python test_live_detection.py <model>
   → Teste in echtem Gameplay
   ↓
5. Wenn alles gut → Auto-Aim starten!
   cd ../3_detection
   python auto_aim_6class.py <model>
```

---

## 🎮 Aimbot Testing (nur Offline!)

Wenn alle Tests gut sind, teste den Aimbot:

```bash
cd ../3_detection
python auto_aim_6class.py ../data/yolo_6class/runs/detect/train/weights/best.pt
```

**Test-Kriterien:**

1. **Team-Erkennung**
   - Zielt nur auf Gegner? ✅
   - Ignoriert Teammates? ✅

2. **Head Detection**
   - Zielt auf Köpfe? ✅
   - Precision gut? ✅

3. **Smooth Aiming**
   - Bewegung natürlich? ✅
   - Keine ruckartigen Sprünge? ✅

4. **FOV-Filtering**
   - Zielt nur auf nahe Targets? ✅

---

## 🔧 Troubleshooting

### "Model findet keine Targets"

**Lösung:**
1. Senke Confidence Threshold:
   ```python
   # In test script ändern
   confidence=0.3  # statt 0.4
   ```

2. Mehr Training-Daten:
   - Sammle 100+ mehr Screenshots
   - Labele sie sorgfältig
   - Trainiere nochmal

### "Viele False Positives"

**Lösung:**
1. Erhöhe Confidence Threshold:
   ```python
   confidence=0.5  # statt 0.4
   ```

2. Mehr negative Beispiele:
   - Screenshots von leeren Bereichen
   - Screenshots ohne Spieler

### "Head Detection schlecht"

**Lösung:**
1. Head-Boxes präziser labeln
   - Nur Kopf, keine Schultern!
   - Mehr Head-Beispiele

2. Head Priority erhöhen:
   ```python
   head_priority = True
   ```

### "Verwechselt CT und T"

**Lösung:**
1. Mehr Beispiele von beiden Teams
2. Achte beim Labeln auf Ausrüstung
3. Variety: Verschiedene Skins/Waffen

---

## 📈 Gute Benchmark-Werte

**Mit 300+ gut gelabelten Bildern:**

```
Metrics:
  mAP@50:    0.75 - 0.85
  Precision: 0.80 - 0.90
  Recall:    0.70 - 0.85

Pro-Klasse (mAP@50):
  CT Body:   0.80 - 0.90
  CT Head:   0.70 - 0.80
  CT Legs:   0.65 - 0.75
  T Body:    0.80 - 0.90
  T Head:    0.70 - 0.80
  T Legs:    0.65 - 0.75

Live Performance:
  FPS:       30-60 (GPU), 10-20 (CPU)
  Accuracy:  85%+
```

---

## 💡 Tipps für bessere Performance

### Training verbessern:
- ✅ 400+ Bilder statt 300
- ✅ Balance: Gleich viele CT und T
- ✅ Variety: Verschiedene Maps, Lichtverhältnisse
- ✅ Precision: Head-Boxes sehr genau
- ✅ Consistency: Immer Body+Head+Legs labeln

### Model-Größe wählen:
```bash
# Schneller, weniger genau:
model_size="n"  # nano

# Langsamer, genauer:
model_size="s"  # small
model_size="m"  # medium
```

### Confidence Threshold tunen:
```python
# Mehr Detections (+ mehr False Positives):
confidence=0.3

# Weniger Detections (+ höhere Genauigkeit):
confidence=0.6

# Balanced (Standard):
confidence=0.4
```

---

## 📁 Test-Output Locations

```
4_evaluation/
├── runs/detect/val/              # Metrics Evaluation Output
│   ├── confusion_matrix.png      # Confusion Matrix
│   ├── val_batch_labels.jpg      # Ground Truth
│   └── val_batch_pred.jpg        # Predictions
```

---

## 🎓 Understanding Metrics

### mAP (mean Average Precision)
- Kombiniert Precision und Recall
- Standard-Metrik für Object Detection
- `mAP@50` = IoU Threshold von 50%
- `mAP@50-95` = Durchschnitt über IoU 50%-95%

### Precision
```
Precision = True Positives / (True Positives + False Positives)
```
Von allen Detections, wie viele waren korrekt?

### Recall
```
Recall = True Positives / (True Positives + False Negatives)
```
Von allen Spielern, wie viele wurden gefunden?

### IoU (Intersection over Union)
```
IoU = Overlap Area / Union Area
```
Wie gut stimmt die Box mit Ground Truth überein?

---

**Version:** 1.0 - 6-Class Testing & Evaluation

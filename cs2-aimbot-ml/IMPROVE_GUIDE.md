# Guide: Bot verbessern & Head-Detection optimieren

Du hast 200 Bilder gelabelt aber Köpfe werden nicht gut erkannt? Hier ist wie du **massiv** verbesserst!

---

## 🎯 Problem: Köpfe werden schlecht erkannt

**Gründe:**
1. **Zu wenig Daten** - 200 Bilder sind OK, aber für präzise Heads brauchst du 400-600
2. **Köpfe sind klein** - Schwerer zu erkennen als Körper
3. **Labeling-Qualität** - Head-Boxen müssen SEHR präzise sein
4. **Unbalanciert** - Mehr Body als Head Samples

---

## ✅ Lösung 1: Semi-Auto Labeling (5x SCHNELLER!)

**Nutze dein bestehendes Model um neue Bilder VORZULABELN!**

```bash
# 1. Sammle 200 NEUE Screenshots
cd 1_data_collection
python capture_auto.py

# 2. Semi-Auto Labeling (nutzt bestehendes Model)
python label_semi_auto.py

# Workflow:
# → Model macht Predictions
# → Du korrigierst nur noch (statt von Grund auf)
# → 5x schneller als manuell!
```

**Features:**
- ✅ Model macht erste Predictions
- ✅ Du korrigierst/ergänzt nur
- ✅ Drücke `A` zum Akzeptieren wenn gut
- ✅ Oder korrigiere manuell wie gewohnt
- ✅ **5x schneller** als manuelles Labeln!

**So kommst du schnell auf 400+ Bilder!**

---

## ✅ Lösung 2: Head-Focused Training

**Spezial-Training das Köpfe PRIORISIERT:**

```bash
cd 2_training
python train_head_focused.py
```

**Was ist anders:**
- ✅ **Höhere Auflösung** (800px statt 640px) → Kleine Köpfe besser sichtbar
- ✅ **Mehr Epochs** (150 statt 100) → Besseres Finetuning
- ✅ **YOLOv8s** statt n → Präziseres Model
- ✅ **Copy-Paste Augmentation** → Mehr Head-Variationen
- ✅ **Close-Crop** → Fokus auf kleine Details

**Erwarte 20-30% bessere Head-Detection!**

---

## ✅ Lösung 3: Active Learning (Intelligente Auswahl)

**Finde die WERTVOLLSTEN Bilder zum Labeln:**

```bash
cd 1_data_collection
python find_hard_examples.py
```

**Was passiert:**
1. Script analysiert ALLE deine Screenshots
2. Findet Bilder wo Model UNSICHER ist:
   - Niedrige Confidence
   - Keine Detections
   - Keine Köpfe erkannt
3. Kopiert Top 100 nach `data/hard_examples/`
4. Erstellt Report

**Diese Bilder labeln bringt den GRÖSSTEN Fortschritt!**

**Dann:**
```bash
# Labele nur diese 100 wertvollen Bilder
python label_semi_auto.py
# (Ändere input_dir zu "../data/hard_examples")
```

**Mehr Impact mit weniger Arbeit!**

---

## 💡 Beste Strategie (Empfohlen):

```
1. Semi-Auto Labeling
   → Sammle 200 neue Screenshots
   → python label_semi_auto.py
   → In 1-2 Stunden hast du 200 neue Labels!
   → Gesamt: 400 Bilder ✓

2. Active Learning
   → python find_hard_examples.py
   → Labele die schwierigen Top 100
   → Gesamt: 500 Bilder ✓✓

3. Head-Focused Training
   → python train_head_focused.py
   → Mit 500 guten Bildern + Head-Focus
   → DEUTLICH bessere Ergebnisse! 🎯

4. Testen
   → python test_detection_visual.py
   → Sollte jetzt 90%+ Heads erkennen!
```

**Timeline:** 3-4 Stunden für massiven Improvement!

---

## 📊 Data Quality Tipps:

### **Für beste Head-Detection:**

1. **Head-Boxen sehr präzise!**
   ```
   ❌ Box zu groß (mit Schultern)
   ✅ Box NUR um Kopf (eng!)
   ```

2. **Variety sammeln:**
   ```
   ✅ Verschiedene Maps
   ✅ Verschiedene Distanzen (nah + fern)
   ✅ Verschiedene Winkel (von vorne, Seite, hinten)
   ✅ Verschiedene Waffen (Skins ändern Silhouette)
   ✅ Verschiedene Lichtverhältnisse
   ```

3. **Balance:**
   ```
   Pro Spieler im Bild:
   - 1x Body Box
   - 1x Head Box  ← WICHTIG!
   - 1x Legs Box

   Ziel: Gleichviele Body/Head/Legs Labels
   ```

4. **Schwierige Fälle labeln:**
   ```
   ✅ Teilweise verdeckte Köpfe
   ✅ Köpfe in Bewegung
   ✅ Weit entfernte Köpfe
   ✅ Köpfe gegen komplexen Hintergrund

   → Genau diese machen Model robust!
   ```

---

## 🚀 Advanced: Noch bessere Algorithmen?

### **YOLOv8 ist bereits sehr gut für Aimbots!**

Aber wenn du noch mehr willst:

### **1. Größeres Model:**
```python
# In train_head_focused.py:
model_size = "m"  # Medium statt Small
# Genauer, aber 2x langsamer
```

### **2. Ensemble (Mehrere Models kombinieren):**
```python
# Nutze 3 Models:
model1 = YOLO("best_v1.pt")  # Normales Training
model2 = YOLO("best_v2.pt")  # Head-Focused
model3 = YOLO("best_v3.pt")  # Nochmal trainiert

# Combine predictions → Robuster!
```

### **3. Two-Stage Detection:**
```
Stage 1: Erkenne Body (leicht)
Stage 2: In jeder Body-Box → Suche Head (präzise)

→ Höhere Präzision aber langsamer
```

### **4. NMS Tuning:**
```python
# In auto_aim.py:
results = model.predict(
    frame,
    conf=0.4,
    iou=0.3,    # Niedriger für dicht stehende Spieler
    agnostic_nms=False
)
```

**Aber:** YOLOv8 mit guten Daten ist >90% der Lösung!

---

## 📈 Expected Results:

**Nach Optimierungen:**

| Metrik | Vorher (200 Bilder) | Nachher (500 Bilder + Head-Focus) |
|--------|---------------------|-----------------------------------|
| Head mAP@50 | 0.60 | **0.85+** |
| Body mAP@50 | 0.75 | **0.90+** |
| Head Detection Rate | 70% | **95%+** |
| False Positives | 15% | **<5%** |

**Head-Detection sollte massiv besser werden!**

---

## ⚡ Quick Wins (Sofort besser):

### **1. Confidence Threshold anpassen:**
```python
# In auto_aim_6class.py:
self.confidence_threshold = 0.5  # Erhöhen für weniger False Positives
# Oder
self.confidence_threshold = 0.3  # Senken für mehr Detections
```

### **2. FOV erweitern:**
```python
self.fov_radius = 400  # Größer für weiter entfernte Targets
```

### **3. Head Priority erhöhen:**
```python
def get_target_priority(self, class_id):
    if class_id in [HEAD_CT, HEAD_T]:
        return 10  # Viel höher! (statt 3)
```

### **4. Smooth Factor anpassen:**
```python
self.smooth_factor = 0.15  # Langsamer (genauer)
# Oder
self.smooth_factor = 0.35  # Schneller (reaktiver)
```

---

## 🎯 Checklist für perfekte Head-Detection:

- [ ] 400+ Bilder gelabelt (mit Semi-Auto)
- [ ] Head-Boxen sehr präzise (nur Kopf!)
- [ ] Variety: Verschiedene Maps/Distanzen/Winkel
- [ ] Balance: Gleich viele Head/Body/Legs Labels
- [ ] Hard Examples gelabelt (Active Learning)
- [ ] Head-Focused Training durchgeführt
- [ ] Model tested (mAP@50 >0.8 für Heads)
- [ ] Confidence threshold getuned
- [ ] Live Test zeigt gute Results

**Wenn alle ✓ → Head-Detection sollte exzellent sein!**

---

## 💬 FAQ:

**Q: Wie viele Bilder brauche ich wirklich?**
A: Minimum 300, besser 500, optimal 800+ für Production-Quality

**Q: Semi-Auto macht Fehler - ist das schlimm?**
A: Nein! Du korrigierst ja. Selbst 50% korrekte Predictions sparen 50% Zeit!

**Q: Head-Focused Training dauert länger?**
A: Ja, ~1-2 Stunden mit GPU wegen höherer Auflösung. Aber lohnt sich!

**Q: Active Learning findet 100 Bilder - muss ich alle labeln?**
A: Nein! Top 50 reichen oft. Oder labele 20/Tag über 5 Tage.

**Q: Kann ich einfach mehr Epochs trainieren?**
A: Hilft, aber nicht so viel wie mehr/bessere Daten!

---

**Viel Erfolg! Mit diesen Methoden wird dein Bot deutlich besser! 🚀**

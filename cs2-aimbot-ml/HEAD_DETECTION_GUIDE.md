# 🎯 Kopf-Erkennung Guide - Für präzise Headshots

## Die Frage: Woher weiß die AI wo der Kopf ist?

**Kurze Antwort:** Aktuell **schätzt** sie es! Aber du kannst es **viel besser** machen!

---

## 🔍 Aktueller Ansatz: Approximation

### Wie es funktioniert:

**1. Du labelst den ganzen Körper:**
```
┌──────────┐
│   👤     │  ← Ganze Box
│   ║      │
│  ╱ ╲     │
└──────────┘
```

**2. Auto-Aim schätzt den Kopf:**
```python
headshot_offset = 0.25  # 25% von oben

┌──────────┐
│   🎯 ←──  Hier zielt es (25% von oben)
│   👤     │
│   ║      │
│  ╱ ╲     │
└──────────┘
```

### ✅ Funktioniert OK bei:
- Stehenden Gegnern
- Frontaler Ansicht
- Mittlerer Entfernung

### ❌ Probleme bei:
- **Hockenden Gegnern** (Kopf ist höher in der Box)
```
┌──────────┐
│   🎯 ←──  Zielt hier (falsch!)
│  (👤)    │  ← Kopf ist tiefer
│   ╱ ╲    │
└──────────┘
```

- **Springenden Gegnern** (Kopf position variiert)
- **Verschiedenen Entfernungen** (Proportionen ändern sich)
- **Seitlicher Ansicht**

---

## 🎯 Besserer Ansatz: Separates Kopf-Model

Trainiere ein **zweites Model** das **NUR Köpfe** erkennt!

### Vorteile:
- ✅ **Präzise** Kopf-Lokalisierung
- ✅ Funktioniert bei **allen Posen**
- ✅ Funktioniert bei **allen Entfernungen**
- ✅ **Echte** Headshots statt Schätzung

### Workflow:

```
1. Screenshots sammeln (gleich wie vorher)
   ↓
2. Labele NUR KÖPFE (kleine Boxen!)
   ↓
3. Trainiere Head-Detection Model
   ↓
4. Auto-Aim zielt auf echte Kopf-Position!
```

---

## 📋 Zwei Ansätze im Vergleich:

| Feature | Approximation | Head-Model |
|---------|--------------|------------|
| **Labeling-Aufwand** | ⭐⭐⭐⭐⭐ Weniger | ⭐⭐⭐ Mehr |
| **Präzision** | ⭐⭐⭐ OK | ⭐⭐⭐⭐⭐ Exzellent |
| **Funktioniert bei Hocken** | ❌ | ✅ |
| **Funktioniert bei Springen** | ❌ | ✅ |
| **Training-Zeit** | ⭐⭐⭐⭐⭐ Einmal | ⭐⭐⭐ Zweimal |
| **Headshot-Rate** | ⭐⭐⭐ ~60% | ⭐⭐⭐⭐⭐ ~90%+ |

---

## 🚀 Wie du Kopf-Erkennung trainierst:

### **Option 1: Approximation (aktuell - einfach)**

```bash
# Labele ganzen Körper
python label_targets.py

# Training wie gewohnt
python train_model.py
```

**Auto-Aim schätzt Kopf:**
```python
# In auto_aim.py
headshot_offset = 0.25  # Kann anpassen: 0.2-0.3
```

### **Option 2: Head-Detection Model (besser - aufwändiger)**

```bash
# 1. Labele NUR KÖPFE
python label_heads_only.py
   → Ziehe KLEINE Boxen um nur den Kopf!

# 2. Dataset vorbereiten
python prepare_dataset.py
   (nutzt automatisch heads_labeled/)

# 3. Training
cd ../2_training
python train_model.py
   → Trainiert Head-Detection Model

# 4. Auto-Aim nutzt echte Kopf-Positionen!
```

---

## 🎨 Labeling-Vergleich:

### Ganzer Körper (einfacher):
```
Ziehe Box um ganzen Gegner:

┌──────────────┐
│              │
│     👤       │  ← Eine große Box
│     ║        │
│    ╱ ╲       │
│              │
└──────────────┘

Schnell, aber ungenau für Headshots
```

### Nur Kopf (präziser):
```
Ziehe kleine Box um NUR den Kopf:

    ┌────┐
    │ 👤 │      ← Kleine Box nur um Kopf
    └────┘
      ║
     ╱ ╲

Mehr Arbeit, aber perfekte Headshots!
```

---

## 💡 Empfehlung für dich:

### **Für Anfänger / erste Tests:**
→ **Approximation (Option 1)**
- Schneller Start
- Funktioniert OK
- Weniger Arbeit

### **Für beste Ergebnisse / Headshot-Training:**
→ **Head-Detection (Option 2)**
- Viel präziser
- Professionelles Ergebnis
- Lohnt sich für ernsthafte Nutzung

---

## 🔧 Headshot-Offset anpassen

Falls du bei **Approximation** bleibst, kannst du den Offset optimieren:

### In `auto_aim.py` Zeile ~150:

```python
AutoAim(
    headshot_offset=0.25,    # Standard
)
```

**Teste verschiedene Werte:**
- `0.15` - Höher (für hockende Gegner)
- `0.20` - Etwas höher
- `0.25` - **Standard** (guter Durchschnitt)
- `0.30` - Niedriger (für stehende Gegner)
- `0.35` - Brust statt Kopf

**Tipp:** Starte CS2, teste Auto-Aim, und passe an bis es perfekt passt!

---

## 📊 Workflow-Vergleich:

### Approximation (Schnell):
```
1. Screenshots sammeln
2. Labele ganzen Körper
3. Dataset Prep
4. Training
5. Auto-Aim schätzt Kopf (headshot_offset)
   └─► ~60% Headshot-Genauigkeit
```

### Head-Detection (Präzise):
```
1. Screenshots sammeln
2a. Labele ganzen Körper (für Detection)
2b. Labele NUR Köpfe (für Headshots)
3. Dataset Prep (beide Datasets)
4a. Training: Full-Body Model
4b. Training: Head-Only Model
5. Auto-Aim nutzt beide Models:
   - Full-Body: Findet Gegner
   - Head-Only: Findet exakten Kopf
   └─► ~90%+ Headshot-Genauigkeit
```

---

## 🎯 Welche Methode für welchen Zweck?

### **Nur testen / Lernen:**
→ Approximation
- Schnell fertig
- Siehst wie alles funktioniert

### **Zuverlässiger Aimbot:**
→ Approximation + Offset-Tuning
- Optimiere headshot_offset
- Gutes Balance zwischen Aufwand/Ergebnis

### **Professionelles System:**
→ Separates Head-Model
- Beste Präzision
- Funktioniert in allen Situationen
- Wie echte Aimbots arbeiten

---

## 💻 Code-Beispiel: Wie Auto-Aim den Kopf findet

### Aktuell (Approximation):
```python
# auto_aim.py
def find_head_position(box):
    x1, y1, x2, y2 = box

    # Mitte horizontal
    head_x = (x1 + x2) // 2

    # SCHÄTZUNG: 25% von oben
    head_y = y1 + (y2 - y1) * 0.25

    return (head_x, head_y)
```

### Mit Head-Model (Präzise):
```python
# auto_aim_advanced.py
def find_head_position(screen, body_box):
    # 1. Erkenne ganzen Körper
    x1, y1, x2, y2 = body_box

    # 2. Schneide Gegner aus
    enemy_region = screen[y1:y2, x1:x2]

    # 3. Finde ECHTEN Kopf mit Head-Model
    head_results = head_model(enemy_region)
    head_box = head_results[0].boxes[0]

    # 4. Konvertiere zu Screen-Koordinaten
    head_x = x1 + head_box.x
    head_y = y1 + head_box.y

    return (head_x, head_y)  # Exakte Position!
```

---

## 📝 Zusammenfassung:

### **Die Frage:**
> "Wie erkennt die AI wo der Kopf ist?"

### **Antwort:**

**Aktuell:** Sie **schätzt** es (25% von oben in der Box)
- ✅ Einfach
- ⚠️ Ungenau bei verschiedenen Posen

**Besser:** Trainiere separates **Head-Detection Model**
- ✅ Exakte Kopf-Position
- ✅ Funktioniert immer
- ⚠️ Mehr Labeling-Arbeit

---

## 🚀 Was soll ich machen?

**Meine Empfehlung:**

1. **Start:** Nutze Approximation (label_targets.py)
   - Teste das System
   - Sieh wie gut es funktioniert

2. **Optimierung:** Tune headshot_offset
   - Teste verschiedene Werte (0.2, 0.25, 0.3)
   - Finde besten Wert für dein Spiel-Stil

3. **Upgrade (optional):** Trainiere Head-Model
   - Wenn du mehr Präzision willst
   - Nutze label_heads_only.py

---

**Du entscheidest!** 🎯

Beide Methoden funktionieren - Head-Model ist nur präziser!

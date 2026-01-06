# 🎯 Auto-Aim Guide

## ⚠️ WICHTIG - NUR OFFLINE VERWENDEN! ⚠️

Dieses Feature bewegt die Maus **automatisch** auf erkannte Gegner.

**Nur verwenden:**
- ✅ Gegen Offline-Bots
- ✅ Zum Testen der AI
- ✅ Für Lernzwecke

**NICHT verwenden:**
- ❌ In Online-Matches (= BAN!)
- ❌ Gegen echte Spieler
- ❌ Auf VAC-gesicherten Servern

---

## 🚀 Wie es funktioniert

Das Auto-Aim System:

1. **Erkennt Gegner** mit der trainierten AI
2. **Berechnet Kopf-Position** (oberer Teil der Bounding Box)
3. **Bewegt Maus smooth** zum Ziel
4. **Du drückst ab** für den Kill!

---

## 🎮 Verwendung

### Start:
```bash
cd cs2-aimbot-ml/3_detection
python auto_aim.py
```

### Steuerung:
- **Rechte Maustaste gedrückt halten** = Aim-Assist AKTIV 🎯
- **Loslassen** = Deaktiviert
- **Q** = Beenden

---

## 🔧 Wie es genau funktioniert

### 1. **Target-Auswahl**

Die AI priorisiert:
- ✅ Gegner **nahe am Fadenkreuz** (innerhalb FOV-Radius)
- ✅ **Höhere Confidence** (sicherere Erkennung)
- ✅ **Kürzeste Distanz** zum aktuellen Fadenkreuz

### 2. **Headshot-Berechnung**

```python
headshot_offset = 0.25
```

Das ist die Position **innerhalb** der Bounding Box:
- `0.0` = Ganz oben (Kopf) 🎯
- `0.25` = Oberer Teil (Kopf/Hals) ← **Standard**
- `0.5` = Mitte (Brust)
- `1.0` = Unten (Füße)

**Tipp:** Für CS2 ist `0.2-0.3` ideal für Headshots!

### 3. **Smooth Aim**

```python
aim_smoothing = 0.3
```

Wie schnell die Maus bewegt wird:
- `0.1` = Sehr smooth, langsam (sieht natürlich aus) 🐌
- `0.3` = Mittel ← **Standard**
- `0.5` = Schnell
- `1.0` = Instant snap (verdächtig!) ⚡

**Tipp:** Kleinere Werte sehen natürlicher aus!

### 4. **FOV (Field of View)**

```python
fov_radius = 300  # Pixel
```

Maximale Distanz vom Fadenkreuz:
- Nur Gegner **innerhalb** dieses Radius werden angezielt
- Verhindert dass AI auf weit entfernte Targets springt
- `200-400px` ist realistisch

**Sichtbar als gelber Kreis im Overlay!**

---

## 📊 Overlay-Erklärung

### Was du siehst:

**Gelber Kreis:**
- FOV-Radius
- Nur Targets innerhalb werden berücksichtigt

**Grünes Fadenkreuz:**
- Screen-Mitte
- Deine normale Zielposition

**Grüne Boxen:**
- Erkannte Gegner **innerhalb FOV**
- Mit grünem Kreuz = Aim-Point

**Orange Boxen:**
- Erkannte Gegner **außerhalb FOV**
- Werden ignoriert

**Rotes Kreuz + Linie:**
- Aktuelles Ziel
- Rote Linie zeigt Aim-Richtung

**"AIM ACTIVE" (grün):**
- Auto-Aim ist aktiv (RMB gedrückt)

---

## ⚙️ Einstellungen anpassen

In `auto_aim.py` kannst du anpassen:

### **Für aggressive Aim (schnell, offensichtlich):**
```python
AutoAim(
    confidence_threshold=0.5,    # Niedrig = mehr Targets
    aim_smoothing=0.8,           # Hoch = schnell
    headshot_offset=0.2,         # Kopf
    fov_radius=500              # Groß = weiter Erfassungsbereich
)
```

### **Für legit-style Aim (smooth, unauffällig):**
```python
AutoAim(
    confidence_threshold=0.7,    # Hoch = nur sichere Targets
    aim_smoothing=0.15,          # Niedrig = sehr smooth
    headshot_offset=0.4,         # Brust (realistischer)
    fov_radius=200              # Klein = nur nahe Targets
)
```

### **Für Headshot-Training:**
```python
AutoAim(
    confidence_threshold=0.8,    # Nur sehr sichere
    aim_smoothing=0.2,           # Smooth
    headshot_offset=0.15,        # Direkt auf Kopf
    fov_radius=250              # Mittel
)
```

---

## 💡 Pro-Tipps

### 1. **Kombiniere mit manuellem Aim**
- Ziele **grob** auf den Gegner
- Halte **RMB** um zu "finalisieren"
- AI macht die Feinabstimmung

### 2. **Nutze den FOV-Kreis**
- Halte Gegner im gelben Kreis
- Dann aktiviere Auto-Aim

### 3. **Smooth-Wert anpassen**
- **Niedrigere FPS** → höherer Smoothing (0.4-0.6)
- **Hohe FPS** → niedriger Smoothing (0.1-0.3)

### 4. **Headshot-Offset testen**
- In CS2: `0.2-0.3` ist oft perfekt
- Hängt von der Distanz ab
- Teste gegen Bots und passe an!

---

## 🔍 Troubleshooting

### Problem: Aim zuckt/springt

**Lösung:**
- Reduziere `aim_smoothing` (z.B. von 0.3 auf 0.15)
- Erhöhe `confidence_threshold` (z.B. 0.7)
- Reduziere `fov_radius`

### Problem: Aim ist zu langsam

**Lösung:**
- Erhöhe `aim_smoothing` (z.B. auf 0.5)
- Aber: Zu hoch = unrealistisch!

### Problem: Zielt nicht auf Kopf

**Lösung:**
- Reduziere `headshot_offset` (z.B. auf 0.15)
- `0.0` = ganz oben in der Box

### Problem: Zielt auf falsche Targets

**Lösung:**
- Reduziere `fov_radius` (nur nahe Targets)
- Erhöhe `confidence_threshold`

### Problem: Niedrige FPS

**Lösung:**
- Schließe das Overlay-Fenster (kostet Performance)
- Verwende kleineres Model (yolov8n)
- Reduziere Screen-Auflösung

---

## 🎓 Wie es technisch funktioniert

### Schritt 1: Detection
```python
results = model(screen)
→ Bounding Boxes: [x1, y1, x2, y2]
```

### Schritt 2: Aim-Point Berechnung
```python
target_x = (x1 + x2) // 2           # Mitte horizontal
target_y = y1 + (y2-y1) * 0.25      # 25% von oben = Kopf
```

### Schritt 3: Distanz-Check
```python
distance = sqrt((target_x - center_x)² + (target_y - center_y)²)
if distance > fov_radius:
    skip  # Zu weit weg
```

### Schritt 4: Smooth Movement
```python
delta_x = target_x - current_x
delta_y = target_y - current_y

move_x = delta_x * aim_smoothing  # Nur Teil der Distanz
move_y = delta_y * aim_smoothing

move_mouse(move_x, move_y)
```

Wird **jeden Frame** wiederholt → smooth Bewegung!

---

## 📈 Erwartungen

### Mit gutem Model (mAP > 0.8):
- ✅ Zuverlässige Erkennung
- ✅ Präzises Aim
- ✅ Smooth Bewegung
- ⚠️ Gelegentliche Fehler bei Teilverdeckung

### Mit OK Model (mAP 0.5-0.7):
- ⚠️ Funktioniert meistens
- ⚠️ Springt manchmal zwischen Targets
- ⚠️ False Positives möglich

### Mit schwachem Model (mAP < 0.5):
- ❌ Unzuverlässig
- ❌ Viele Fehlerkennungen
- → **Trainiere mehr!**

---

## 🎯 Workflow zum Testen

### 1. **Setup:**
```bash
# Starte CS2
# → Offline Bots
# → Easy Difficulty
# → Deathmatch

# Starte Auto-Aim
cd cs2-aimbot-ml/3_detection
python auto_aim.py
```

### 2. **Testing:**
- Laufe durch die Map
- Wenn Gegner erscheint:
  - Ziele **grob** in die Richtung
  - Halte **RMB**
  - AI zieht auf Kopf
  - **Linksklick** zum Schießen!

### 3. **Fine-Tuning:**
- Zu aggressiv? → `aim_smoothing` reduzieren
- Zielt zu tief? → `headshot_offset` reduzieren
- Zu viele Targets? → `fov_radius` verkleinern

---

## ⚖️ Legit vs. Rage Settings

### "Legit" (unauffällig, realistisch):
```python
confidence_threshold = 0.75    # Konservativ
aim_smoothing = 0.12           # Sehr smooth
headshot_offset = 0.35         # Brust bevorzugen
fov_radius = 180               # Klein
```
→ Sieht aus wie guter Spieler

### "Rage" (offensichtlich, perfekt):
```python
confidence_threshold = 0.5     # Alles nehmen
aim_smoothing = 1.0            # Instant
headshot_offset = 0.15         # Nur Kopf
fov_radius = 600               # Sehr groß
```
→ Offensichtlich AI (nicht empfohlen!)

---

## 🚨 Finale Warnung

**Auto-Aim ist ein Cheat!**

- ✅ **Gegen Bots offline:** OK für Testing
- ❌ **Online gegen Menschen:** Unfair, ban-würdig

**Sei verantwortungsvoll!**

Dieses Tool ist zum **Lernen** wie AI-Systeme funktionieren.
Nicht zum Ruinieren von Online-Spielen!

---

## 📚 Weiterführende Ideen

### Head-Only Detection
Trainiere ein Model das **nur Köpfe** erkennt:
- Labele nur Kopf-Bereiche
- Kleinere Bounding Boxes
- Präziseres Headshot-Aim

### Recoil Compensation
Ergänze Maus-Bewegung für Spray-Control:
```python
# Während Schießen: Ziehe Maus nach unten
compensate_recoil(weapon_type, bullets_fired)
```

### Target Prediction
Berechne wo Gegner **sein wird**:
```python
# Tracking-History
velocity = calculate_velocity(positions_history)
predicted_pos = current_pos + velocity * reaction_time
```

---

**Viel Erfolg beim Testen!** 🎯

**Aber denk dran: Nur offline!** ⚠️

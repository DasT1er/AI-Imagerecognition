# 🚀 Batch-Dateien Guide (Windows)

Für **Windows-Nutzer** - Einfache Bedienung per Doppelklick!

---

## 📂 Verfügbare Batch-Dateien

Du hast **2 verschiedene Batch-Dateien** zur Auswahl:

---

## 1️⃣ START_MENU.bat ⭐ EMPFOHLEN

**Das Hauptmenü - Vollständige Kontrolle**

### Was ist das?
Ein interaktives Menü wo du **auswählen** kannst was du machen willst.

### Wie verwenden?
```
Doppelklick auf START_MENU.bat
```

### Features:
- ✅ Übersichtliches Menü
- ✅ Wähle jeden Schritt einzeln
- ✅ Hilfe-Funktion integriert
- ✅ Farbiges CMD-Interface
- ✅ Für erfahrene Nutzer & Anfänger

### Optionen:
```
[1] Screenshots sammeln (Auto)
[2] Screenshots sammeln (Manual)
[3] Gegner markieren
[4] Dataset vorbereiten
[5] Model trainieren
[6] Training visualisieren
[7] Live Detection
[8] Auto-Aim
[9] Model evaluieren
[H] Hilfe
[0] Beenden
```

**Perfekt wenn:** Du Kontrolle über jeden Schritt willst

---

## 2️⃣ QUICK_WORKFLOW.bat

**Automatischer Durchlauf - Für Anfänger**

### Was ist das?
Führt dich **automatisch** durch alle Schritte nacheinander.

### Wie verwenden?
```
Doppelklick auf QUICK_WORKFLOW.bat
```

### Ablauf:
```
1. Screenshots sammeln → 2. Labeling → 3. Dataset Prep
→ 4. Training → 5. Evaluation → 6. Live-Test
```

**Perfekt wenn:** Du zum ersten Mal trainierst und den kompletten Workflow durchlaufen willst

---

## 🎯 Welche soll ich verwenden?

### Für das **erste Mal**:
→ **QUICK_WORKFLOW.bat**
- Führt dich Schritt für Schritt durch
- Kannst nicht vergessen
- Einfacher Einstieg

### Für **tägliche Nutzung**:
→ **START_MENU.bat**
- Flexibler
- Springe zu beliebigen Schritten
- Professioneller

---

## 📖 Schritt-für-Schritt: Erste Verwendung

### Option A: Komplett-Durchlauf (Anfänger)

```
1. Doppelklick: QUICK_WORKFLOW.bat
2. Folge den Anweisungen auf dem Bildschirm
3. Fertig!
```

### Option B: Manuell (Fortgeschritten)

```
1. Doppelklick: START_MENU.bat
2. Wähle [1] - Screenshots sammeln
3. Wähle [3] - Gegner markieren
4. Wähle [4] - Dataset vorbereiten
5. Wähle [5] - Model trainieren
6. Wähle [7] - Live Detection
```

---

## 🔧 Troubleshooting

### Problem: "Python nicht gefunden"

**Lösung:**
1. Installiere Python 3.8+
2. Füge Python zu PATH hinzu bei Installation
3. Oder öffne CMD als Administrator

### Problem: "Module nicht gefunden"

**Lösung:**
```cmd
pip install -r requirements.txt
```

### Problem: Batch-Datei öffnet und schließt sofort

**Lösung:**
1. Rechtsklick auf die .bat Datei
2. "Als Administrator ausführen"

### Problem: Umlaute werden falsch angezeigt

**Lösung:**
- Normal! Windows CMD hat manchmal Probleme mit UTF-8
- Funktioniert trotzdem einwandfrei

---

## 🎨 CMD-Farben Erklärung

Die Batch-Dateien nutzen Farben:

- **Grün (0A)**: Normaler Betrieb, alles OK
- **Blau (0B)**: Workflow-Modus
- **Rot (0C)**: Auto-Aim Warnung (Offline only!)

---

## ⌨️ Tastenkombinationen im CMD

Während ein Script läuft:

- **STRG+C**: Beenden / Abbrechen
- **ENTER**: Weiter (bei Pausen)
- **Pfeiltasten**: Navigation (im Menü)

---

## 💡 Pro-Tipps

### Tipp 1: Mehrere CMD-Fenster
Du kannst **mehrere** Batch-Dateien gleichzeitig öffnen!

Beispiel:
- Fenster 1: `START_MENU.bat` → [5] Training läuft
- Fenster 2: `START_MENU.bat` → [6] Visualisierung ansehen

### Tipp 2: Schnelle Navigation
Im Menü kannst du direkt die **Zahl tippen** ohne ENTER.

### Tipp 3: Log-Dateien
Wenn du die Ausgabe speichern willst:
```cmd
START_MENU.bat > log.txt
```

---

## 📊 Workflow-Übersicht

### Kompletter Workflow (ca. 2-3 Stunden):

```
┌─────────────────────────────────────────┐
│ START_MENU.bat oder QUICK_WORKFLOW.bat │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
[1] Auto        [3] Label      [4] Prepare
Screenshot      Targets        Dataset
(10-15 Min)     (30-60 Min)    (1 Min)
    │               │               │
    └───────────────┴───────────────┘
                    │
                    ▼
              [5] Training
              (30 Min - 2h)
                    │
    ┌───────────────┴───────────────┐
    │                               │
    ▼                               ▼
[6] Visualize                  [9] Evaluate
 (Optional)                    (5 Min)
    │                               │
    └───────────────┬───────────────┘
                    │
    ┌───────────────┴───────────────┐
    │                               │
    ▼                               ▼
[7] Live                       [8] Auto-Aim
Detection                      (Optional)
```

---

## ⚠️ Wichtige Hinweise

### Sicherheit:
- ✅ Nur gegen **Offline-Bots** verwenden!
- ❌ **NICHT** in Online-Matches!
- ❌ **KEIN** Cheating!

### Performance:
- GPU empfohlen für Training (10x schneller)
- Min. 8GB RAM
- ~2GB freier Speicher

### Admin-Rechte:
- Manche Schritte brauchen evtl. Admin-Rechte
- Rechtsklick → "Als Administrator ausführen"

---

## 📚 Weitere Dokumentation

Für detaillierte Infos, lies:
- `README.md` - Vollständige Dokumentation
- `QUICKSTART.md` - 30-Min Schnellstart
- `AUTO_AIM_GUIDE.md` - Auto-Aim Anleitung

---

## 🎉 Viel Erfolg!

Die Batch-Dateien machen die Bedienung **super einfach**!

**Empfehlung:**
1. Erstes Mal: `QUICK_WORKFLOW.bat`
2. Danach: `START_MENU.bat` für tägliche Nutzung

**Los geht's!** 🚀

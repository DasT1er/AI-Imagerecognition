# Screenshot Tools - Welches soll ich verwenden?

Du hast **3 verschiedene Tools** zur Auswahl. Nutze das, was für dich am besten funktioniert!

---

## 🚀 Option 1: Auto-Screenshot (EMPFOHLEN - Am einfachsten!)

**Datei:** `capture_auto.py`

### Wie es funktioniert:
- Macht **automatisch** alle paar Sekunden einen Screenshot
- Kein Hotkey nötig
- Einfach laufen lassen!

### Verwendung:
```bash
cd 1_data_collection
python capture_auto.py
```

Dann:
1. Starte CS2
2. Spiele einfach normal
3. Tool macht alle 2 Sekunden automatisch Screenshots
4. Drücke CTRL+C im Terminal zum Beenden

### Einstellungen anpassen:
In `capture_auto.py` Zeile 69:
```python
interval_seconds=2.0    # Ändern für schneller/langsamer
                        # 1.0 = jede Sekunde
                        # 3.0 = alle 3 Sekunden
```

### ✅ Vorteile:
- Funktioniert IMMER
- Keine Hotkey-Probleme
- Super einfach
- Sammelt viele Screenshots automatisch

### ⚠️ Nachteile:
- Sammelt auch "unnötige" Screenshots (z.B. Menu, Tod-Screen)
- Kannst du später beim Labeling aussortieren

---

## ⌨️ Option 2: Manual Screenshot (100% zuverlässig!)

**Datei:** `capture_manual.py`

### Wie es funktioniert:
- Wechsle ins Terminal
- Drücke ENTER für Screenshot
- Super simpel!

### Verwendung:
```bash
cd 1_data_collection
python capture_manual.py
```

Dann:
1. Starte CS2
2. Wenn Gegner sichtbar:
   - ALT+TAB ins Terminal
   - Drücke ENTER
   - ALT+TAB zurück zu CS2
3. Tippe 'q' und ENTER zum Beenden

### ✅ Vorteile:
- Funktioniert garantiert
- Volle Kontrolle wann Screenshot
- Keine Hotkey-Probleme

### ⚠️ Nachteile:
- Musst du ALT+TAB machen
- Langsamer
- Unterbricht Gameplay

---

## 🎮 Option 3: Hotkey Screenshot (Original - kann Probleme haben)

**Datei:** `capture_screenshots.py`

### Wie es funktioniert:
- Drücke F9 für Screenshot
- Wie im Original geplant

### Verwendung:
```bash
cd 1_data_collection
python capture_screenshots.py
```

### ⚠️ Problem unter Linux:
- `pynput` braucht evtl. Root-Rechte
- Oder funktioniert nicht mit allen Keyboards

### Fix versuchen:
```bash
# Mit sudo ausführen
sudo python capture_screenshots.py

# ODER: pynput neu installieren
pip install --upgrade pynput
```

### Wenn F9 nicht funktioniert:
→ Nutze **Option 1 (Auto)** oder **Option 2 (Manual)**!

---

## 📊 Empfehlung nach Situation:

### Du willst es EINFACH und SCHNELL:
→ **Option 1: `capture_auto.py`** ✅
- Einfach starten und spielen
- Sammelt automatisch viele Screenshots

### Du willst KONTROLLE über jeden Screenshot:
→ **Option 2: `capture_manual.py`** ✅
- Nur Screenshots wenn Gegner sichtbar
- Weniger Müll-Daten

### F9 funktioniert bei dir:
→ **Option 3: `capture_screenshots.py`** ✅
- Wie geplant
- Am komfortabelsten

---

## 💡 Pro-Tipp: Kombiniere!

**Beste Methode:**
1. Nutze **`capture_auto.py`** um schnell 300-500 Screenshots zu sammeln
2. Beim Labeling überspringe unnötige Bilder mit 'd'
3. Fertig!

**Warum?**
- Schnellste Methode
- Funktioniert immer
- Kein Stress mit Hotkeys
- Beim Labeling kannst du eh auswählen welche gut sind

---

## 🎯 Workflow-Beispiel:

### Mit Auto-Screenshot:
```bash
# Terminal 1: Screenshot-Tool
cd cs2-aimbot-ml/1_data_collection
python capture_auto.py

# Jetzt: Starte CS2 und spiele 10-15 Minuten
# Tool macht automatisch ~300 Screenshots (bei interval=2s)

# Wenn fertig: CTRL+C im Terminal
```

Dann später:
```bash
# Labeling
python label_targets.py
# Überspringe mit 'd' alle Bilder ohne Gegner
```

---

## ❓ Troubleshooting

**"Keine Screenshots werden erstellt"**
→ Check ob `data/raw/` Ordner existiert
→ Script zeigt Fehler? Zeig mir die Nachricht

**"Permission denied"**
→ Versuche mit `sudo python ...`
→ Oder nutze Auto/Manual statt Hotkey

**"Screen capture nicht möglich"**
→ Check ob `mss` installiert: `pip install mss`

**"Zu viele unnötige Screenshots"**
→ Erhöhe `interval_seconds` in capture_auto.py
→ Oder nutze Manual-Tool

---

## ⚙️ Alle Optionen im Vergleich:

| Feature | Auto | Manual | Hotkey |
|---------|------|--------|--------|
| **Einfachheit** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Zuverlässigkeit** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Geschwindigkeit** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Kontrolle** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Komfort** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎉 Fazit:

**Für die meisten Nutzer:**
→ Nutze **`capture_auto.py`** !

**Warum?**
- ✅ Funktioniert immer
- ✅ Keine Hotkey-Probleme
- ✅ Super schnell
- ✅ Einfach zu bedienen

**Viel Erfolg beim Screenshots sammeln!** 📸

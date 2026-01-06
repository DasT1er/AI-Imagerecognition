# 🚀 Quickstart Guide - In 30 Minuten zur ersten AI!

**Super-schneller Start für absolute Anfänger**

---

## ✅ Checkliste vor dem Start

- [ ] Python 3.8+ installiert
- [ ] CS2 installiert
- [ ] ~2 GB freier Speicher
- [ ] 30-60 Minuten Zeit

---

## 📋 Die 6 Schritte (Kopiere einfach die Befehle!)

### Step 1: Setup (2 Minuten)

```bash
cd cs2-aimbot-ml
pip install -r requirements.txt
```

Warte bis alles installiert ist. ☕

---

### Step 2: Screenshots sammeln (20 Minuten)

**Wichtig:** Spiele gegen **OFFLINE BOTS**!

```bash
# Terminal-Fenster 1:
cd 1_data_collection
python capture_screenshots.py
```

**Jetzt:**
1. Starte CS2
2. Wähle: **Spielen → Übung → Offline mit Bots**
3. Map: Dust 2 oder Mirage (egal welche)
4. Bot-Schwierigkeit: **Leicht** (damit sie dich nicht killen)
5. **Spiele und drücke F9 wenn Gegner im Bild sind**

**Ziel: Min. 100 Screenshots** (mehr ist besser, aber 100 reicht für ersten Test)

Drücke **ESC** wenn du fertig bist.

---

### Step 3: Gegner markieren (30 Minuten)

```bash
python label_targets.py
```

**So geht's:**
1. Fenster öffnet sich mit Screenshot
2. **Klicke und ziehe** eine Box um jeden Gegner
3. Drücke **'s'** zum Speichern
4. Nächstes Bild erscheint
5. Wiederhole!

**Tipps:**
- Markiere den **ganzen Körper** (Kopf bis Fuß)
- Drücke **'d'** wenn kein Gegner im Bild ist
- Drücke **'u'** um Fehler rückgängig zu machen

Labele alle 100 Bilder!

---

### Step 4: Daten vorbereiten (10 Sekunden)

```bash
python prepare_dataset.py
```

Fertig! ✅

---

### Step 5: Training (30-60 Minuten)

```bash
cd ../2_training
python train_model.py
```

**JETZT LÄUFT DIE AI!** 🚀

Du siehst:
```
Epoch 1/100: Loss: 2.543, mAP: 0.123
Epoch 2/100: Loss: 2.234, mAP: 0.234
...
```

**Was soll passieren:**
- **Loss sinkt** (von ~2.5 auf ~0.5)
- **mAP steigt** (von ~0.1 auf ~0.6+)

Lass es laufen! Geh Kaffee trinken. ☕

**Training dauert:**
- Mit GPU: ~15-30 Min
- Ohne GPU: ~1-2 Stunden

---

### Step 6: TESTEN! 🎮

```bash
cd ../3_detection
python detect_realtime.py
```

**Jetzt:**
1. Starte CS2 (wieder Offline-Bots)
2. Ein Fenster zeigt was die AI sieht
3. **Grüne Boxen** um erkannte Gegner!

**Drücke Q zum Beenden**

---

## 🎯 Erwartungen

Mit **100 Bildern** und **100 Epochs**:
- ✅ AI funktioniert (erkennt manche Gegner)
- ⚠️ Noch nicht perfekt (~50-60% Genauigkeit)

**Um besser zu werden:**
1. Sammle **300-500 Bilder**
2. Trainiere **200 Epochs**
3. Verwende verschiedene Maps

---

## ❓ Probleme?

### "Model not found"
→ Training ist noch nicht fertig oder fehlgeschlagen
→ Check Terminal-Output vom Training

### "No images found"
→ Du hast vergessen Screenshots zu sammeln (Step 2)

### "CUDA out of memory"
→ Kein Problem! In `2_training/train_model.py`:
   Ändere `batch=16` zu `batch=4`

### Training ist sehr langsam
→ Normal ohne GPU. Reduziere `epochs=100` zu `epochs=50` für schnelleren Test

---

## 🎉 Geschafft!

Du hast jetzt:
- ✅ Daten gesammelt
- ✅ Ein Model trainiert
- ✅ Die AI getestet

**Next Level:**
Lies die vollständige [README.md](README.md) für:
- Bessere Ergebnisse
- Fortgeschrittene Features
- Troubleshooting

---

**Viel Spaß beim Experimentieren!** 🚀

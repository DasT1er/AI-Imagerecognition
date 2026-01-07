# Screenshots sind überbelichtet - Lösung

Wenn deine Screenshots zu hell/überbelichtet sind, gibt es **3 Lösungen**:

## 1. CS2 In-Game Brightness senken (EMPFOHLEN!)

Das ist die **beste Lösung**, weil es das Problem an der Quelle behebt:

1. Starte CS2
2. Gehe zu: **Einstellungen → Video → Erweitert**
3. Finde: **Brightness** oder **Gamma**
4. **Setze auf 0.7 oder niedriger** (Standard ist oft 1.0-1.2)
5. Speichern und neu starten

→ Danach sind Screenshots automatisch dunkler!

---

## 2. Windows HDR deaktivieren

HDR kann zu überbelichteten Screenshots führen:

1. **Windows-Einstellungen** öffnen
2. Gehe zu: **System → Bildschirm**
3. Suche nach: **HDR** oder **Auto-HDR**
4. **Deaktiviere beides**

---

## 3. Brightness-Korrektur im Screenshot-Tool

Falls 1+2 nicht helfen, passe `capture_auto.py` an:

### A) Teste verschiedene Einstellungen:
```bash
START.bat → [1a] Brightness Test
```

Das zeigt dir 6 Einstellungen:
- Original
- Gamma Only
- 80% + Gamma
- 70% + Gamma
- **65% + Gamma** ← Empfohlen bei starker Überbelichtung
- 60% + Gamma

### B) Passe capture_auto.py an:

Öffne `1_data_collection/capture_auto.py` und ändere Zeile 159:

```python
# FÜR STARK ÜBERBELICHTETE SCREENSHOTS:
brightness_correction=0.65,  # 35% dunkler

# Andere Optionen:
# brightness_correction=0.60,  # 40% dunkler (sehr dunkel)
# brightness_correction=0.70,  # 30% dunkler
# brightness_correction=0.80,  # 20% dunkler
```

---

## Empfohlener Workflow:

1. **ZUERST:** Senke CS2 Brightness auf 0.7
2. **DANN:** Teste mit Brightness Test Tool
3. **FALLS NÖTIG:** Passe `brightness_correction` an

Mit CS2 Brightness 0.7 + Screenshot-Korrektur 0.65 sollten die Screenshots **perfekt** sein!

---

## Warum sind die Screenshots überbelichtet?

- CS2 hat oft sehr hohe Standard-Brightness (1.0-1.2)
- Windows HDR kann die Helligkeit verstärken
- Manche Monitore haben aggressive Auto-Brightness
- Die `mss` Screenshot-Library ignoriert Farbprofile

Die Kombination aus allen 3 Lösungen gibt die besten Ergebnisse!

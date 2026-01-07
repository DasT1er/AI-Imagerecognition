# DXCam Setup - OBS-Qualität für Screenshots!

DXCam nutzt die **gleiche Methode wie OBS** - die Windows Graphics Capture API!

## Warum DXCam?

- ✅ **GLEICHE Technologie wie OBS**
- ✅ **Perfekte Farbgenauigkeit** (keine Überbelichtung!)
- ✅ **Ultra-schnell** (GPU-basiert)
- ✅ **Funktioniert mit Fullscreen-Spielen**
- ✅ **Beste Qualität** für AI-Training

## Installation

```bash
pip install dxcam
```

Das war's! Kein Setup, keine Konfiguration nötig.

## Verwendung

```bash
START.bat → [1] Screenshots → [4] DXCam
```

Oder manuell:
```bash
cd 1_data_collection
python capture_auto_dxcam.py
```

## Wie es funktioniert

DXCam nutzt die **Windows Desktop Duplication API**:
- Direkter Zugriff auf GPU Frame-Buffer
- Keine CPU-Encoding-Probleme
- Kein Farbraum-Konvertierungs-Overhead
- Identisch zu OBS Game-Capture

## Vergleich der Methoden

| Methode | Geschwindigkeit | Farbgenauigkeit | Fullscreen | OBS-Qualität |
|---------|----------------|-----------------|------------|--------------|
| MSS     | ⚡⚡⚡ Sehr schnell | ⚠️ Probleme | ❌ Nein | ❌ |
| PIL ImageGrab | ⚡⚡ Schnell | ✅ Gut | ⚠️ Manchmal | ⚠️ |
| PyAutoGUI | ⚡ Mittel | ✅ Gut | ⚠️ Manchmal | ⚠️ |
| **DXCam** | ⚡⚡⚡ Sehr schnell | ✅✅ Perfekt | ✅ Ja | ✅ **JA!** |
| OBS WebSocket | ⚡ Langsam | ✅✅ Perfekt | ✅ Ja | ✅ **JA!** |

## Empfehlung

Für **beste Ergebnisse beim AI-Training:**

1. **Nutze DXCam** für Screenshots (Option [4])
2. Alternativ: **OBS WebSocket** wenn du eh OBS laufen hast (Option [5])

Mit DXCam erhältst du **exakt die gleiche Qualität wie in deinem OBS-Screenshot!**

## Troubleshooting

### "DXCam nicht installiert"
```bash
pip install dxcam
```

### "Frame capture fehlgeschlagen"
- CS2 minimiert? Stelle sicher CS2 läuft
- Fullscreen Windowed Mode nutzen (empfohlen)

### "Zu langsam"
- DXCam ist GPU-basiert und sollte sehr schnell sein
- Prüfe GPU-Auslastung
- Verkleinere Interval (z.B. 1 Sekunde statt 2)

## Performance

**DXCam Performance:**
- ~1-2ms pro Screenshot (GPU)
- Kein CPU-Overhead
- Kann 500+ FPS capturen (wenn nötig)

**Perfekt für:**
- AI-Training (beste Qualität)
- Echtzeit-Detection
- Game-Capture ohne Performance-Loss

## Technische Details

DXCam nutzt:
- **DXGI Desktop Duplication API**
- DirectX 11 Frame-Buffer Zugriff
- GPU-zu-GPU Transfer (kein CPU-Bottleneck)
- Identisch zu OBS "Display Capture" Source

Dies ist **die professionellste Lösung** für Game-Screenshot-Capture!

@echo off
chcp 65001 >nul
title CS2 AI Aimbot - Hauptmenü
color 0A

:MENU
cls
echo ═══════════════════════════════════════════════════════════════════
echo                   CS2 AI TARGET DETECTION SYSTEM
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  ⚠️  NUR FÜR OFFLINE-BOTS VERWENDEN! ⚠️
echo.
echo ═══════════════════════════════════════════════════════════════════
echo                          HAUPTMENÜ
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  [1] 📸 Screenshots sammeln (Auto)
echo  [2] 📸 Screenshots sammeln (Manual)
echo  [3] 🏷️  Gegner markieren (Labeling)
echo  [4] 📊 Dataset vorbereiten
echo.
echo ───────────────────────────────────────────────────────────────────
echo.
echo  [5] 🧠 Model trainieren
echo  [6] 📈 Training visualisieren
echo.
echo ───────────────────────────────────────────────────────────────────
echo.
echo  [7] 🔍 Live Detection testen
echo  [8] 🎯 Auto-Aim aktivieren
echo  [9] 📊 Model evaluieren
echo.
echo ───────────────────────────────────────────────────────────────────
echo.
echo  [H] 📚 Hilfe / Workflow-Guide
echo  [0] ❌ Beenden
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.

set /p choice="Wähle eine Option: "

if "%choice%"=="1" goto AUTO_SCREENSHOT
if "%choice%"=="2" goto MANUAL_SCREENSHOT
if "%choice%"=="3" goto LABELING
if "%choice%"=="4" goto PREPARE_DATASET
if "%choice%"=="5" goto TRAINING
if "%choice%"=="6" goto VISUALIZE
if "%choice%"=="7" goto DETECTION
if "%choice%"=="8" goto AUTO_AIM
if "%choice%"=="9" goto EVALUATION
if "%choice%"=="h" goto HELP
if "%choice%"=="H" goto HELP
if "%choice%"=="0" goto EXIT

echo.
echo ❌ Ungültige Auswahl! Bitte wähle 1-9, H oder 0.
timeout /t 2 >nul
goto MENU

:AUTO_SCREENSHOT
cls
echo ═══════════════════════════════════════════════════════════════════
echo                    📸 AUTO-SCREENSHOT TOOL
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  ✅ Macht automatisch alle 2 Sekunden Screenshots
echo  ✅ Kein Hotkey nötig - läuft einfach!
echo.
echo  ANLEITUNG:
echo  1. Dieser Tool startet jetzt
echo  2. Starte CS2 (Offline Bots!)
echo  3. Spiele 10-15 Minuten normal
echo  4. Drücke STRG+C hier im Fenster zum Beenden
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
echo.
echo Starte Auto-Screenshot Tool...
cd 1_data_collection
python capture_auto.py
cd ..
echo.
pause
goto MENU

:MANUAL_SCREENSHOT
cls
echo ═══════════════════════════════════════════════════════════════════
echo                    📸 MANUAL SCREENSHOT TOOL
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  ✅ Drücke ENTER für Screenshot
echo  ✅ 100%% zuverlässig
echo.
echo  ANLEITUNG:
echo  1. Dieser Tool startet jetzt
echo  2. Starte CS2 (Offline Bots!)
echo  3. Wenn Gegner sichtbar: ALT+TAB hier und ENTER drücken
echo  4. Tippe 'q' und ENTER zum Beenden
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
echo.
echo Starte Manual Screenshot Tool...
cd 1_data_collection
python capture_manual.py
cd ..
echo.
pause
goto MENU

:LABELING
cls
echo ═══════════════════════════════════════════════════════════════════
echo                      🏷️  GEGNER MARKIEREN
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  ANLEITUNG:
echo  1. Ziehe Boxen um JEDEN Gegner (ganzer Körper!)
echo  2. Drücke 'S' zum Speichern
echo  3. Drücke 'D' zum Überspringen (kein Gegner im Bild)
echo  4. Drücke 'U' um letzte Box rückgängig zu machen
echo  5. Drücke 'Q' zum Beenden
echo.
echo  💡 TIPP: Markiere den GANZEN Körper, nicht nur den Kopf!
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
echo.
echo Starte Labeling Tool...
cd 1_data_collection
python label_targets.py
cd ..
echo.
pause
goto MENU

:PREPARE_DATASET
cls
echo ═══════════════════════════════════════════════════════════════════
echo                     📊 DATASET VORBEREITEN
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  Teilt die Daten in Training (80%%) und Validation (20%%)
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
echo.
echo Starte Dataset Preparation...
cd 1_data_collection
python prepare_dataset.py
cd ..
echo.
echo ✅ Dataset vorbereitet!
echo.
pause
goto MENU

:TRAINING
cls
echo ═══════════════════════════════════════════════════════════════════
echo                       🧠 MODEL TRAINIEREN
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  ⚠️  ACHTUNG: Training kann 30 Min - 2 Stunden dauern!
echo.
echo  Du siehst live:
echo  • Loss (sollte sinken)
echo  • mAP (sollte steigen)
echo  • Fortschritt in %%
echo.
echo  💡 TIPP: Lass das Fenster offen und warte bis fertig!
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
echo.
echo Starte Training...
cd 2_training
python train_model.py
cd ..
echo.
echo ✅ Training abgeschlossen!
echo.
pause
goto MENU

:VISUALIZE
cls
echo ═══════════════════════════════════════════════════════════════════
echo                   📈 TRAINING VISUALISIEREN
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  Zeigt Training-Plots:
echo  • Loss-Kurven
echo  • mAP-Entwicklung
echo  • Precision/Recall
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
echo.
echo Starte Visualisierung...
cd 2_training
python visualize_training.py
cd ..
echo.
pause
goto MENU

:DETECTION
cls
echo ═══════════════════════════════════════════════════════════════════
echo                     🔍 LIVE DETECTION TESTEN
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  ✅ Zeigt grüne Boxen um erkannte Gegner
echo  ✅ FPS Counter
echo  ✅ Confidence Scores
echo.
echo  ANLEITUNG:
echo  1. Dieser Tool startet jetzt
echo  2. Starte CS2 (Offline Bots!)
echo  3. Sieh die grünen Boxen um Gegner!
echo  4. Drücke 'Q' zum Beenden
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
echo.
echo Starte Live Detection...
cd 3_detection
python detect_realtime.py
cd ..
echo.
pause
goto MENU

:AUTO_AIM
cls
color 0C
echo ═══════════════════════════════════════════════════════════════════
echo                      🎯 AUTO-AIM SYSTEM
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  ⚠️⚠️⚠️  NUR FÜR OFFLINE-BOTS VERWENDEN! ⚠️⚠️⚠️
echo.
echo  STEUERUNG:
echo  • Rechte Maustaste HALTEN = Aim aktiv
echo  • Loslassen = Deaktiviert
echo  • Q = Beenden
echo.
echo  FUNKTIONEN:
echo  ✅ Automatisches Zielen auf Kopf
echo  ✅ Smooth Bewegung
echo  ✅ FOV-basierte Zielauswahl
echo.
echo  ANLEITUNG:
echo  1. Dieser Tool startet jetzt
echo  2. Starte CS2 (Offline Bots!)
echo  3. Ziele grob auf Gegner
echo  4. Halte rechte Maustaste = Auto-Aim
echo  5. Drücke linke Maustaste zum Schießen!
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
color 0A
echo.
echo Starte Auto-Aim...
cd 3_detection
python auto_aim.py
cd ..
echo.
pause
goto MENU

:EVALUATION
cls
echo ═══════════════════════════════════════════════════════════════════
echo                      📊 MODEL EVALUIEREN
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  Zeigt Performance-Metriken:
echo  • Precision
echo  • Recall
echo  • mAP@50 / mAP@50-95
echo  • Beispiel-Predictions
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
echo.
echo Starte Evaluation...
cd 4_evaluation
python evaluate_model.py
cd ..
echo.
pause
goto MENU

:HELP
cls
echo ═══════════════════════════════════════════════════════════════════
echo                     📚 WORKFLOW-GUIDE
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  SCHRITT-FÜR-SCHRITT ANLEITUNG:
echo.
echo  ┌─ PHASE 1: DATEN SAMMELN
echo  │
echo  │  [1] Screenshots sammeln (Auto)
echo  │      └─► Spiele CS2 für 10-15 Min, Tool macht auto Screenshots
echo  │
echo  │  [2] Gegner markieren (Labeling)
echo  │      └─► Ziehe Boxen um jeden Gegner, drücke 'S' zum Speichern
echo  │
echo  │  [3] Dataset vorbereiten
echo  │      └─► Teilt Daten in Training/Validation (automatisch)
echo  │
echo  ├─ PHASE 2: TRAINING
echo  │
echo  │  [4] Model trainieren
echo  │      └─► Trainiere AI (30 Min - 2h), sieh Loss sinken!
echo  │
echo  │  [5] Training visualisieren (Optional)
echo  │      └─► Plots ansehen
echo  │
echo  ├─ PHASE 3: TESTEN
echo  │
echo  │  [6] Model evaluieren
echo  │      └─► Sieh Metriken (mAP, Precision, Recall)
echo  │
echo  │  [7] Live Detection testen
echo  │      └─► Teste in CS2, sieh grüne Boxen!
echo  │
echo  └─ PHASE 4: AUTO-AIM (Optional)
echo.
echo     [8] Auto-Aim aktivieren
echo         └─► RMB halten = Auto-Aim auf Kopf!
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  💡 EMPFEHLUNG FÜR ANFÄNGER:
echo.
echo  1. Starte mit [1] - Sammle 100 Screenshots zum Testen
echo  2. Dann [2] - Labele alle Bilder
echo  3. Dann [3] - Dataset vorbereiten
echo  4. Dann [4] - Trainiere (dauert, aber warte bis fertig!)
echo  5. Dann [6] - Evaluiere (sieh wie gut die AI ist)
echo  6. Dann [7] - Teste live in CS2!
echo.
echo  Wenn alles gut funktioniert → Sammle mehr Daten für bessere AI!
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  ⚠️  WICHTIG:
echo  • Nur gegen Offline-Bots verwenden!
echo  • Nicht in Online-Matches (BAN-Risiko!)
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
goto MENU

:EXIT
cls
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
echo                  Vielen Dank fürs Nutzen!
echo.
echo                      Happy Training! 🎯
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
timeout /t 2 >nul
exit

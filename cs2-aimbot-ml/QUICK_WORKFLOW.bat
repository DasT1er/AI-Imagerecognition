@echo off
chcp 65001 >nul
title CS2 AI - Quick Workflow
color 0B

cls
echo ═══════════════════════════════════════════════════════════════════
echo              CS2 AI - AUTOMATISCHER WORKFLOW
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  Dieser Workflow führt dich automatisch durch alle Schritte!
echo.
echo  SCHRITTE:
echo  1. Screenshots sammeln (Auto)
echo  2. Gegner labeln
echo  3. Dataset vorbereiten
echo  4. Model trainieren
echo  5. Evaluation
echo  6. Live-Test
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause

:STEP1
cls
echo ═══════════════════════════════════════════════════════════════════
echo                    SCHRITT 1/6: SCREENSHOTS SAMMELN
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  📸 Auto-Screenshot Tool startet jetzt!
echo.
echo  AUFGABE:
echo  1. Warte bis Tool läuft
echo  2. Starte CS2 (Offline Bots!)
echo  3. Spiele 10-15 Minuten
echo  4. Drücke STRG+C wenn du genug Screenshots hast
echo.
echo  Ziel: Min. 100 Screenshots (besser 300+)
echo.
echo ═══════════════════════════════════════════════════════════════════
pause
echo.
cd 1_data_collection
python capture_auto.py
cd ..

:STEP2
cls
echo ═══════════════════════════════════════════════════════════════════
echo                    SCHRITT 2/6: GEGNER LABELN
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  🏷️  Labeling Tool startet jetzt!
echo.
echo  AUFGABE:
echo  1. Ziehe Box um JEDEN Gegner (ganzer Körper!)
echo  2. Drücke 'S' zum Speichern
echo  3. Drücke 'D' zum Überspringen (kein Gegner)
echo  4. Drücke 'Q' wenn alle Bilder gelabelt sind
echo.
echo  💡 TIPP: Präzise Boxen = bessere AI!
echo.
echo ═══════════════════════════════════════════════════════════════════
pause
echo.
cd 1_data_collection
python label_targets.py
cd ..

:STEP3
cls
echo ═══════════════════════════════════════════════════════════════════
echo                  SCHRITT 3/6: DATASET VORBEREITEN
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  📊 Bereite Dataset vor...
echo.
echo ═══════════════════════════════════════════════════════════════════
pause
echo.
cd 1_data_collection
python prepare_dataset.py
cd ..
echo.
echo ✅ Dataset vorbereitet!
pause

:STEP4
cls
echo ═══════════════════════════════════════════════════════════════════
echo                   SCHRITT 4/6: MODEL TRAINIEREN
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  🧠 Training startet!
echo.
echo  ⚠️  WICHTIG: Dauert 30 Min - 2 Stunden!
echo.
echo  Du siehst live:
echo  • Loss sinken (gut!)
echo  • mAP steigen (gut!)
echo  • Epoch-Fortschritt
echo.
echo  💡 TIPP: Geh Kaffee trinken und lass es laufen! ☕
echo.
echo ═══════════════════════════════════════════════════════════════════
pause
echo.
cd 2_training
python train_model.py
cd ..
echo.
echo ✅ Training abgeschlossen!
pause

:STEP5
cls
echo ═══════════════════════════════════════════════════════════════════
echo                    SCHRITT 5/6: EVALUATION
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  📊 Evaluiere Model...
echo.
echo  Zeigt Performance-Metriken:
echo  • mAP@50 (sollte ^> 0.7 sein für gut)
echo  • Precision & Recall
echo  • Beispiel-Predictions
echo.
echo ═══════════════════════════════════════════════════════════════════
pause
echo.
cd 4_evaluation
python evaluate_model.py
cd ..
echo.
pause

:STEP6
cls
echo ═══════════════════════════════════════════════════════════════════
echo                     SCHRITT 6/6: LIVE-TEST!
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  🔍 Live Detection startet!
echo.
echo  AUFGABE:
echo  1. Warte bis Tool läuft
echo  2. Starte CS2 (Offline Bots!)
echo  3. Sieh die grünen Boxen um Gegner!
echo  4. Drücke 'Q' zum Beenden
echo.
echo  💡 Wenn die AI gut funktioniert → Glückwunsch! 🎉
echo.
echo ═══════════════════════════════════════════════════════════════════
pause
echo.
cd 3_detection
python detect_realtime.py
cd ..

:FINISH
cls
echo ═══════════════════════════════════════════════════════════════════
echo                    🎉 WORKFLOW ABGESCHLOSSEN! 🎉
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  Du hast erfolgreich:
echo  ✅ Daten gesammelt
echo  ✅ Eine AI trainiert
echo  ✅ Das Model getestet
echo.
echo  NÄCHSTE SCHRITTE:
echo.
echo  📈 Wenn mAP ^< 0.7:
echo     → Sammle MEHR Daten (300+ Bilder)
echo     → Trainiere länger (200 Epochs)
echo.
echo  📈 Wenn mAP ^> 0.7:
echo     → Super! Die AI funktioniert gut!
echo     → Teste das Auto-Aim Feature (START_MENU.bat → Option 8)
echo.
echo  💡 Pro-Tipp:
echo     Für bessere Ergebnisse:
echo     • 500+ gelabelte Bilder
echo     • Verschiedene Maps
echo     • Verschiedene Lichtverhältnisse
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  Zurück zum Hauptmenü? (START_MENU.bat)
echo.
pause
exit

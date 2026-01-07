@echo off
chcp 65001 >nul
title CS2 AI - 6-Class System
color 0A

:MENU
cls
echo ====================================================================
echo              CS2 AI AIMBOT - 6-CLASS SYSTEM
echo ====================================================================
echo.
echo  WICHTIG: Nur fuer Offline-Bots verwenden!
echo.
echo  [1] Screenshots sammeln
echo  [2] Gegner labeln (6 Klassen: CT/T x Body/Head/Legs)
echo  [3] Dataset vorbereiten
echo  [4] Model trainieren
echo  [5] Model testen (Visuell)
echo  [6] Model evaluieren (Metrics)
echo  [7] Live Detection Test
echo  [8] Auto-Aim starten (Erweiterte Team-Erkennung!)
echo  [0] Beenden
echo.
echo ====================================================================
echo.

set /p choice=Waehle eine Option:

if "%choice%"=="1" goto SCREENSHOT
if "%choice%"=="2" goto LABELING
if "%choice%"=="3" goto PREPARE
if "%choice%"=="4" goto TRAINING
if "%choice%"=="5" goto TEST_VISUAL
if "%choice%"=="6" goto TEST_METRICS
if "%choice%"=="7" goto TEST_LIVE
if "%choice%"=="8" goto AUTOAIM
if "%choice%"=="0" goto EXIT

echo.
echo Ungueltige Auswahl!
timeout /t 2 >nul
goto MENU

:SCREENSHOT
cls
echo ====================================================================
echo                    SCREENSHOTS SAMMELN
echo ====================================================================
echo.
echo Macht automatisch alle 2 Sekunden einen Screenshot!
echo.
echo 1. Starte CS2 (Offline Bots!)
echo 2. Spiele 10-15 Minuten
echo 3. Druecke STRG+C zum Beenden
echo.
pause
cd 1_data_collection
python capture_auto.py
cd ..
pause
goto MENU

:LABELING
cls
echo ====================================================================
echo                  6-CLASS LABELING SYSTEM
echo ====================================================================
echo.
echo 6 Klassen zum Labeln:
echo  CT Team:                     T Team:
echo    [1] CT Body (Koerper)        [4] T Body (Koerper)
echo    [2] CT Head (Kopf)           [5] T Head (Kopf)
echo    [3] CT Legs (Beine)          [6] T Legs (Beine)
echo.
echo Workflow pro Spieler:
echo  1. TAB druecken zum Team-Wechsel (CT oder T)
echo  2. B/H/L druecken fuer Body/Head/Legs
echo  3. Box um Spieler-Teil ziehen
echo  4. Fuer jeden Spieler wiederholen
echo  5. S druecken zum Speichern
echo.
echo TIPP: Du entscheidest beim Labeln welches Team!
echo       Schaue auf Ausruestung/Farbe der Spieler.
echo.
pause
cd 1_data_collection
python label_6_class.py
cd ..
pause
goto MENU

:PREPARE
cls
echo ====================================================================
echo                    DATASET VORBEREITEN
echo ====================================================================
echo.
echo Bereitet 6-Klassen Dataset vor...
echo.
pause
cd 1_data_collection
python prepare_dataset_6class.py
cd ..
pause
goto MENU

:TRAINING
cls
echo ====================================================================
echo                    MODEL TRAINIEREN
echo ====================================================================
echo.
echo Waehle Training-Modus:
echo.
echo  [1] Standard Training (100 Epochs, ~30-60 Min mit GPU)
echo  [2] Fast Training (50 Epochs, ~10-20 Min mit GPU)
echo.
echo Fast Training ist gut genug fuer die meisten Faelle!
echo.
set /p train_choice=Waehle (1 oder 2):

if "%train_choice%"=="1" goto TRAINING_STANDARD
if "%train_choice%"=="2" goto TRAINING_FAST

echo Ungueltige Auswahl!
timeout /t 2 >nul
goto TRAINING

:TRAINING_STANDARD
cls
echo ====================================================================
echo                  STANDARD TRAINING (100 Epochs)
echo ====================================================================
echo.
echo ACHTUNG: Dauert 30-60 Min mit GPU, 2-3 Stunden ohne GPU!
echo.
echo Die AI lernt:
echo  - CT Team: Body, Head, Legs
echo  - T Team: Body, Head, Legs
echo  - 6 separate Klassen fuer praezise Erkennung
echo.
pause
cd 2_training
python train_model.py
cd ..
pause
goto MENU

:TRAINING_FAST
cls
echo ====================================================================
echo                    FAST TRAINING (50 Epochs)
echo ====================================================================
echo.
echo ACHTUNG: Dauert 10-20 Min mit GPU, 1-2 Stunden ohne GPU!
echo.
echo Fast Training:
echo  - Schneller durch weniger Epochs
echo  - Auto-optimierte Batch Size
echo  - Immer noch gute Ergebnisse!
echo.
echo GPU Status wird beim Start angezeigt.
echo Falls keine GPU: Siehe GPU_SETUP.txt
echo.
pause
cd 2_training
python train_model_fast.py
cd ..
pause
goto MENU

:TEST_VISUAL
cls
echo ====================================================================
echo                    MODEL TESTEN - VISUELL
echo ====================================================================
echo.
echo Zeigt Detections auf Test-Bildern
echo.
echo Du siehst:
echo  - Bounding Boxes (farbig nach Klasse)
echo  - Labels mit Confidence Scores
echo  - Statistiken pro Bild
echo.
echo Steuerung:
echo  SPACE = Naechstes Bild
echo  Q = Beenden
echo.
pause
cd 4_evaluation
python test_detection_visual.py
cd ..
pause
goto MENU

:TEST_METRICS
cls
echo ====================================================================
echo                  MODEL EVALUIEREN - METRICS
echo ====================================================================
echo.
echo Berechnet wissenschaftliche Metriken:
echo  - mAP@50 (^> 0.7 = gut)
echo  - Precision (wenige False Positives)
echo  - Recall (alle Targets gefunden)
echo.
echo Output:
echo  - Confusion Matrix
echo  - Pro-Klasse Scores
echo.
pause
cd 4_evaluation
python evaluate_metrics.py
cd ..
pause
goto MENU

:TEST_LIVE
cls
echo ====================================================================
echo                  LIVE DETECTION TEST
echo ====================================================================
echo.
echo Zeigt LIVE was die AI sieht - OHNE Aimbot!
echo.
echo 1. Waehle deinen Monitor
echo 2. Starte CS2 Offline mit Bots
echo 3. Tool zeigt Live-Feed mit Detections
echo.
echo Steuerung:
echo  Q = Beenden
echo.
pause
cd 4_evaluation
python test_live_detection.py
cd ..
pause
goto MENU

:AUTOAIM
cls
color 0C
echo ====================================================================
echo           6-CLASS AUTO-AIM MIT ERWEITERTER TEAM-ERKENNUNG
echo ====================================================================
echo.
echo NUR FUER OFFLINE-BOTS!
echo.
echo Features:
echo  - 3-Fach Team-Erkennung:
echo    1. UI-Farbe (Blau=CT, Orange=T)
echo    2. Icons ueber Spielern
echo    3. Crosshair-Kreis mit X (Teammates)
echo  - Zielt NUR auf gegnerisches Team
echo  - KEIN Friendly Fire!
echo  - Separate Erkennung fuer CT/T x Body/Head/Legs
echo.
echo Steuerung:
echo  SHIFT halten = Aim aktiv
echo  Q = Beenden
echo.
pause
color 0A
cd 3_detection
python auto_aim_6class.py
cd ..
pause
goto MENU

:EXIT
cls
echo.
echo Vielen Dank!
echo.
timeout /t 2 >nul
exit

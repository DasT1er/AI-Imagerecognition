@echo off
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
echo  [1a] Brightness Test
echo  [2] Gegner labeln (Semi-Auto mit AI!)
echo  [2a] Hard Examples finden
echo  [3] Dataset vorbereiten
echo  [4] Model trainieren (Standard)
echo  [4a] Fast Training (GPU)
echo  [4b] Head-Focused Training
echo  [5] Model testen (Visuell)
echo  [6] Model evaluieren (Metrics)
echo  [7] Live Detection Test
echo  [8] Auto-Aim starten
echo  [9] IMPROVE GUIDE
echo  [0] Beenden
echo.
echo ====================================================================
echo.

set /p choice=Waehle eine Option: 

if "%choice%"=="1" goto SCREENSHOT
if "%choice%"=="1a" goto BRIGHTNESS_TEST
if "%choice%"=="2" goto LABELING_SEMI
if "%choice%"=="2a" goto FIND_HARD
if "%choice%"=="3" goto PREPARE
if "%choice%"=="4" goto TRAINING
if "%choice%"=="4a" goto TRAINING_FAST
if "%choice%"=="4b" goto TRAINING_HEAD
if "%choice%"=="5" goto TEST_VISUAL
if "%choice%"=="6" goto TEST_METRICS
if "%choice%"=="7" goto TEST_LIVE
if "%choice%"=="8" goto AUTOAIM
if "%choice%"=="9" goto IMPROVE_GUIDE
if "%choice%"=="0" goto EXIT

echo.
echo Ungueltige Auswahl!
pause
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

:BRIGHTNESS_TEST
cls
echo ====================================================================
echo                    BRIGHTNESS TEST
echo ====================================================================
echo.
echo Zeigt 6 verschiedene Helligkeits-Einstellungen zum Vergleich!
echo.
pause
cd 1_data_collection
python test_brightness.py
cd ..
pause
goto MENU

:LABELING_SEMI
cls
echo ====================================================================
echo            SEMI-AUTO LABELING MIT AI!
echo ====================================================================
echo.
echo Model macht automatische Predictions!
echo Rechtsklick um falsche Boxen zu loeschen!
echo.
pause
cd 1_data_collection
python label_semi_auto.py
cd ..
pause
goto MENU

:FIND_HARD
cls
echo ====================================================================
echo        HARD EXAMPLES FINDEN (Active Learning)
echo ====================================================================
echo.
echo Findet Bilder wo dein Model UNSICHER ist!
echo.
pause
cd 1_data_collection
python find_hard_examples.py
cd ..
pause
goto MENU

:PREPARE
cls
echo ====================================================================
echo                    DATASET VORBEREITEN
echo ====================================================================
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
echo                  STANDARD TRAINING
echo ====================================================================
echo.
echo DAUERT: 30-60 Min mit GPU, 2-3 Stunden ohne GPU
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
echo                  FAST TRAINING (GPU-Optimiert)
echo ====================================================================
echo.
echo DAUERT: 10-20 Min mit GPU
echo.
pause
cd 2_training
python train_model_fast.py
cd ..
pause
goto MENU

:TRAINING_HEAD
cls
echo ====================================================================
echo            HEAD-FOCUSED TRAINING
echo ====================================================================
echo.
echo Spezial-Training optimiert fuer Kopf-Erkennung!
echo DAUERT: 1-2 Stunden mit GPU
echo.
pause
cd 2_training
python train_head_focused.py
cd ..
pause
goto MENU

:TEST_VISUAL
cls
echo ====================================================================
echo                  MODEL TESTEN - VISUELL
echo ====================================================================
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
echo                MODEL EVALUIEREN - METRICS
echo ====================================================================
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
echo                LIVE DETECTION TEST
echo ====================================================================
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
echo         6-CLASS AUTO-AIM MIT TEAM-ERKENNUNG
echo ====================================================================
echo.
echo NUR FUER OFFLINE-BOTS!
echo.
pause
color 0A
cd 3_detection
python auto_aim_6class.py
cd ..
pause
goto MENU

:IMPROVE_GUIDE
cls
echo ====================================================================
echo                    IMPROVE GUIDE
echo ====================================================================
echo.
pause
start IMPROVE_GUIDE.md
goto MENU

:EXIT
cls
echo.
echo Vielen Dank!
echo.
timeout /t 2
exit

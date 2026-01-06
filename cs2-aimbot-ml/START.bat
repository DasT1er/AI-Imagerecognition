@echo off
chcp 65001 >nul
title CS2 AI - Hauptmenu
color 0A

:MENU
cls
echo ====================================================================
echo                   CS2 AI TARGET DETECTION
echo ====================================================================
echo.
echo  [1] Screenshots sammeln
echo  [2] Gegner labeln (Multi-Class)
echo  [3] Dataset vorbereiten
echo  [4] Model trainieren
echo  [5] Live Detection testen
echo  [6] Auto-Aim starten
echo  [7] Model evaluieren
echo  [0] Beenden
echo.
echo ====================================================================
echo.

set /p choice=Waehle eine Option:

if "%choice%"=="1" goto SCREENSHOT
if "%choice%"=="2" goto LABELING
if "%choice%"=="3" goto PREPARE
if "%choice%"=="4" goto TRAINING
if "%choice%"=="5" goto DETECTION
if "%choice%"=="6" goto AUTOAIM
if "%choice%"=="7" goto EVALUATION
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
echo 1. Dieses Tool startet jetzt
echo 2. Starte CS2 (Offline Bots!)
echo 3. Spiele 10-15 Minuten
echo 4. Druecke STRG+C zum Beenden
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
echo                    GEGNER LABELN
echo ====================================================================
echo.
echo Multi-Class Labeling: Enemy (gruen) + Head (rot)
echo.
echo Steuerung:
echo  E - Enemy Mode (ganzer Gegner)
echo  H - Head Mode (nur Kopf)
echo  S - Speichern
echo  Q - Beenden
echo.
pause
cd 1_data_collection
python label_advanced.py
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
python prepare_dataset_advanced.py
cd ..
pause
goto MENU

:TRAINING
cls
echo ====================================================================
echo                    MODEL TRAINIEREN
echo ====================================================================
echo.
echo ACHTUNG: Dauert 30 Min - 2 Stunden!
echo.
pause
cd 2_training
python train_model.py
cd ..
pause
goto MENU

:DETECTION
cls
echo ====================================================================
echo                    LIVE DETECTION
echo ====================================================================
echo.
echo Zeigt gruene/rote Boxen um Gegner/Koepfe
echo Druecke Q zum Beenden
echo.
pause
cd 3_detection
python detect_realtime.py
cd ..
pause
goto MENU

:AUTOAIM
cls
color 0C
echo ====================================================================
echo                    AUTO-AIM SYSTEM
echo ====================================================================
echo.
echo NUR FUER OFFLINE-BOTS VERWENDEN!
echo.
echo Steuerung:
echo  RMB halten = Aim aktiv
echo  Q = Beenden
echo.
pause
color 0A
cd 3_detection
python auto_aim_advanced.py
cd ..
pause
goto MENU

:EVALUATION
cls
echo ====================================================================
echo                    MODEL EVALUIEREN
echo ====================================================================
echo.
pause
cd 4_evaluation
python evaluate_model.py
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

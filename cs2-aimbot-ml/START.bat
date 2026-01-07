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
echo  [1] Screenshots sammeln (DXCam - beste Qualitaet!)
echo  [2] Gegner labeln (Semi-Auto mit AI!)
echo  [3] Hard Examples finden
echo  [4] Dataset vorbereiten
echo  [5] Model trainieren (Head-Focused)
echo  [6] Model testen (Visuell)
echo  [7] Live Detection Test
echo  [8] Auto-Aim starten
echo  [9] IMPROVE GUIDE
echo  [0] Beenden
echo.
echo ====================================================================
echo.

set /p choice=Waehle eine Option: 

if "%choice%"=="1" goto SCREENSHOT
if "%choice%"=="2" goto LABELING
if "%choice%"=="3" goto FIND_HARD
if "%choice%"=="4" goto PREPARE
if "%choice%"=="5" goto TRAINING
if "%choice%"=="6" goto TEST_VISUAL
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
echo        SCREENSHOTS - DXCam (OBS-Qualitaet!)
echo ====================================================================
echo.
echo Nutzt Windows Graphics Capture API - wie OBS!
echo.
echo Vorteile:
echo  + Perfekte Farbgenauigkeit
echo  + Keine Ueberbelichtung
echo  + Ultra-schnell (GPU-basiert)
echo  + Funktioniert mit Fullscreen
echo.
echo WICHTIG: Installiere erst DXCam:
echo   pip install dxcam
echo.
echo TIPP: Deaktiviere Windows Auto-HDR:
echo   Windows Einstellungen - System - Bildschirm - Auto-HDR AUS
echo.
pause
cd 1_data_collection
python capture_auto_dxcam.py
cd ..
pause
goto MENU

:LABELING
cls
echo ====================================================================
echo            SEMI-AUTO LABELING MIT AI!
echo ====================================================================
echo.
echo Model macht automatische Predictions!
echo.
echo Features:
echo  • Rechtsklick um falsche Boxen zu loeschen
echo  • TAB + B/H/L um Klasse zu aendern
echo  • 1-6 fuer direkte Klassenwahl
echo  • A zum Akzeptieren, S zum Speichern
echo  • Professionelle Sidebar mit Statistiken
echo.
echo 5x SCHNELLER als manuelles Labeln!
echo Wird mit der Zeit automatisch besser!
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
echo Diese zu labeln bringt den GROESSTEN Fortschritt!
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
echo            HEAD-FOCUSED TRAINING (BESTE ERGEBNISSE!)
echo ====================================================================
echo.
echo Spezial-Training optimiert fuer Kopf-Erkennung!
echo.
echo Einstellungen:
echo  - YOLOv8s (bessere Precision als nano)
echo  - 800px Aufloesung (fuer kleine Heads)
echo  - 150 Epochs
echo  - Spezielle Augmentation fuer Heads
echo.
echo DAUERT: 1-2 Stunden mit GPU
echo ERGEBNIS: 20-30 Prozent bessere Head-Detection!
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

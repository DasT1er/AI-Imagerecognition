@echo off
chcp 65001 >nul
title CS2 AI - Team-Aware System
color 0A

:MENU
cls
echo ====================================================================
echo              CS2 AI AIMBOT - TEAM-AWARE SYSTEM
echo ====================================================================
echo.
echo  WICHTIG: Nur fuer Offline-Bots verwenden!
echo.
echo  [1] Screenshots sammeln
echo  [2] Gegner labeln (4 Klassen: CT/T/Head/Legs)
echo  [3] Dataset vorbereiten
echo  [4] Model trainieren
echo  [5] Auto-Aim starten (Team-Aware!)
echo  [0] Beenden
echo.
echo ====================================================================
echo.

set /p choice=Waehle eine Option:

if "%choice%"=="1" goto SCREENSHOT
if "%choice%"=="2" goto LABELING
if "%choice%"=="3" goto PREPARE
if "%choice%"=="4" goto TRAINING
if "%choice%"=="5" goto AUTOAIM
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
echo                TEAM-AWARE MULTI-CLASS LABELING
echo ====================================================================
echo.
echo 4 Klassen zum Labeln:
echo  [1] Enemy CT  - Counter-Terrorist (Blau)
echo  [2] Enemy T   - Terrorist (Orange)
echo  [3] Head      - Kopf
echo  [4] Legs      - Beine
echo.
echo Workflow pro Gegner:
echo  1. Schaue ob CT (blau) oder T (orange)
echo  2. Druecke 1 oder 2 -^> Box um ganzen Gegner
echo  3. Druecke 3 -^> Box um Kopf
echo  4. Druecke 4 -^> Box um Beine
echo  5. Druecke S zum Speichern
echo.
pause
cd 1_data_collection
python label_team_aware.py
cd ..
pause
goto MENU

:PREPARE
cls
echo ====================================================================
echo                    DATASET VORBEREITEN
echo ====================================================================
echo.
echo Bereitet 4-Klassen Dataset vor...
echo.
pause
cd 1_data_collection
python prepare_dataset_team_aware.py
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
echo Die AI lernt:
echo  - CT vs T erkennen
echo  - Koepfe finden
echo  - Beine erkennen
echo.
pause
cd 2_training
python train_model.py
cd ..
pause
goto MENU

:AUTOAIM
cls
color 0C
echo ====================================================================
echo              TEAM-AWARE AUTO-AIM SYSTEM
echo ====================================================================
echo.
echo NUR FUER OFFLINE-BOTS!
echo.
echo Features:
echo  - Erkennt DEIN Team (Blau=CT, Orange=T)
echo  - Zielt NUR auf gegnerisches Team
echo  - KEIN Friendly Fire!
echo  - Praezise Kopf-Erkennung
echo.
echo Steuerung:
echo  RMB halten = Aim aktiv
echo  Q = Beenden
echo.
pause
color 0A
cd 3_detection
python auto_aim_team_aware.py
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

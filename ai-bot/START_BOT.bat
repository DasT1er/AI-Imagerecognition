@echo off
chcp 65001 >nul 2>&1
if errorlevel 1 chcp 1252 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ================================================================
echo   CS2 AI BOT - AUTONOMOUS GAMEPLAY
echo ================================================================
echo.
echo   PHASE 1: Imitation Learning (Lerne von DIR!)
echo   PHASE 2: Reinforcement Learning (Self-Improvement)
echo   PHASE 3: Full Autonomy (Economy, Strategy, Multi-Map)
echo.
echo ================================================================
echo.

:MENU
echo.
echo Wähle eine Option:
echo.
echo   [1] Human Gameplay aufnehmen (F9 Start/Stop)
echo   [2] Model trainieren (Imitation Learning)
echo   [3] Bot testen (Spielt automatisch!)
echo   [4] Game State Detector testen
echo   [5] Environment testen
echo   [6] README anzeigen (Architektur)
echo.
echo   [9] Zurück zum Hauptmenü
echo   [0] Beenden
echo.

set /p choice="Deine Wahl: "

if "%choice%"=="1" goto COLLECT
if "%choice%"=="2" goto TRAIN
if "%choice%"=="3" goto TEST
if "%choice%"=="4" goto GAMESTATE
if "%choice%"=="5" goto ENVIRONMENT
if "%choice%"=="6" goto README
if "%choice%"=="9" goto MAINMENU
if "%choice%"=="0" goto END

echo.
echo Ungültige Eingabe!
goto MENU

:COLLECT
echo.
echo ================================================================
echo   HUMAN GAMEPLAY AUFNEHMEN
echo ================================================================
echo.
echo Anleitung:
echo   1. Starte CS2 (Offline gegen Bots)
echo   2. Druecke F9 zum Starten der Aufnahme
echo   3. Spiele 1-2 Runden NORMAL (wie DU spielen würdest!)
echo   4. Druecke F9 zum Stoppen
echo   5. Wiederhole für mehrere Sessions
echo.
echo Ziel: 10-20 Runden (5000-20000 Frames)
echo.
pause
python 3_learning/imitation/collect_human_data.py
goto MENU

:TRAIN
echo.
echo ================================================================
echo   MODEL TRAINIEREN (IMITATION LEARNING)
echo ================================================================
echo.
echo Der Bot lernt DEINE Actions!
echo.
echo Architektur:
echo   - CNN für Screenshots (84x84)
echo   - Fully Connected für Actions
echo   - Supervised Learning (CrossEntropy Loss)
echo.
echo Training dauert ca. 10-30 Minuten (je nach Daten Menge)
echo.
pause
python 3_learning/imitation/train_imitation.py
echo.
echo ✅ Training abgeschlossen!
echo    Model: models/best_model.pt
echo.
pause
goto MENU

:TEST
echo.
echo ================================================================
echo   BOT TESTEN
echo ================================================================
echo.
echo Der Bot spielt CS2 AUTOMATISCH!
echo.
echo Anleitung:
echo   1. Starte CS2 (Offline gegen Bots)
echo   2. Bot startet nach 3 Sekunden
echo   3. Druecke F9 zum Stoppen
echo.
echo Der Bot nutzt das trainierte Model und spielt wie DU!
echo.
pause
python test_bot.py
goto MENU

:GAMESTATE
echo.
echo ================================================================
echo   GAME STATE DETECTOR TEST
echo ================================================================
echo.
echo Testet Erkennung von:
echo   - HP (Health Points)
echo   - Armor
echo   - Ammo (Current/Reserve)
echo   - Money
echo   - Round Time
echo.
pause
python 1_vision/game_state.py
goto MENU

:ENVIRONMENT
echo.
echo ================================================================
echo   CS2 ENVIRONMENT TEST
echo ================================================================
echo.
echo Testet Gymnasium-kompatibles Environment:
echo   - Observation Space (visual + game state + enemies)
echo   - Action Space (20 discrete actions)
echo   - Reward System
echo.
pause
python 4_environment/cs2_env.py
goto MENU

:README
echo.
echo ================================================================
echo   README - AI BOT ARCHITEKTUR
echo ================================================================
echo.
type README.md
echo.
pause
goto MENU

:MAINMENU
cd ..
call START.bat
exit

:END
echo.
echo ✅ Bis zum naechsten Mal!
echo.
pause
exit

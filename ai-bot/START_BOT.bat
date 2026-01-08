@echo off
title CS2 AI Bot
color 0A

:MENU
cls
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
echo === PHASE 1: Imitation Learning ===
echo   [1] Human Gameplay aufnehmen (F9 Start/Stop)
echo   [2] Model trainieren (Imitation Learning)
echo   [3] Bot testen (Basic - nur Imitation)
echo.
echo === PHASE 2: Reinforcement Learning (NEU!) ===
echo   [4] PPO Training (Hybrid - von DIR lernen + selbst verbessern!)
echo   [5] ADVANCED Bot (VOLLAUTOMATISCH - macht ALLES selbst!)
echo.
echo === Tests und Tools ===
echo   [6] Game State Detector testen
echo   [7] Visual Overlay testen
echo   [8] Reward System testen
echo.
echo   [R] README anzeigen (Architektur)
echo   [0] Beenden
echo.

set /p choice=Deine Wahl:

if "%choice%"=="1" goto COLLECT
if "%choice%"=="2" goto TRAIN
if "%choice%"=="3" goto TEST
if "%choice%"=="4" goto TRAIN_PPO
if "%choice%"=="5" goto TEST_ADVANCED
if "%choice%"=="6" goto GAMESTATE
if "%choice%"=="7" goto TEST_OVERLAY
if "%choice%"=="8" goto TEST_REWARD
if /I "%choice%"=="R" goto README
if "%choice%"=="0" goto END

echo.
echo Ungueltige Eingabe!
pause
goto MENU

:COLLECT
cls
echo.
echo ================================================================
echo   HUMAN GAMEPLAY AUFNEHMEN
echo ================================================================
echo.
echo Anleitung:
echo   1. Starte CS2 (Offline gegen Bots)
echo   2. Druecke F9 zum Starten der Aufnahme
echo   3. Spiele 1-2 Runden NORMAL (wie DU spielen wuerdest!)
echo   4. Druecke F9 zum Stoppen
echo   5. Wiederhole fuer mehrere Sessions
echo.
echo Ziel: 10-20 Runden (5000-20000 Frames)
echo.
pause
python 3_learning/imitation/collect_human_data.py
goto MENU

:TRAIN
cls
echo.
echo ================================================================
echo   MODEL TRAINIEREN (IMITATION LEARNING)
echo ================================================================
echo.
echo Der Bot lernt DEINE Actions!
echo.
echo Architektur:
echo   - CNN fuer Screenshots (84x84)
echo   - Fully Connected fuer Actions
echo   - Supervised Learning (CrossEntropy Loss)
echo.
echo Training dauert ca. 10-30 Minuten (je nach Daten Menge)
echo.
pause
python 3_learning/imitation/train_imitation.py
echo.
echo Training abgeschlossen!
echo    Model: models/best_model.pt
echo.
pause
goto MENU

:TEST
cls
echo.
echo ================================================================
echo   BOT TESTEN (PHASE 1 - Imitation Only)
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

:TRAIN_PPO
cls
echo.
echo ================================================================
echo   PPO TRAINING (PHASE 2 - HYBRID!)
echo ================================================================
echo.
echo HYBRID APPROACH:
echo   1. Startet mit DEINEM Imitation Model
echo   2. Verbessert sich SELBST durch Reinforcement Learning
echo   3. Nutzt cleveres Reward System (Anti-Camping!)
echo.
echo Features:
echo   + Lernt von deinem Gameplay
echo   + Verbessert sich selbstaendig
echo   + Belohnt aggressive Aktionen
echo   + Bestraft Camping/Zeitverschwendung
echo.
echo WICHTIG:
echo   - CS2 muss LAUFEN (gegen Bots)!
echo   - Training dauert 10-20 Stunden!
echo   - Bot spielt automatisch und lernt
echo.
echo Empfehlung: Erst Imitation Model trainieren (Option 2)!
echo.
pause
python 3_learning/reinforcement/train_ppo_hybrid.py
echo.
echo PPO Training abgeschlossen!
echo    Model: models/ppo_final.zip
echo.
pause
goto MENU

:TEST_ADVANCED
cls
color 0C
echo.
echo ================================================================
echo   ADVANCED BOT - VOLLAUTOMATISCH!
echo ================================================================
echo.
echo FEATURES:
echo   * PPO oder Imitation Model
echo   * BOT MACHT ALLES SELBST (Bewegung + Zielen + Schießen!)
echo   * VISUAL OVERLAY (siehst was Bot sieht!)
echo   * Gegner-Boxen (Gelb = Kopf, Rot = Body)
echo   * Game State HUD (HP, Armor, Ammo, Money)
echo   * Threat Level Bar
echo   * Action Display
echo   * FPS Counter
echo.
echo BOT LERNT ZIELEN SELBST - KEINE AIMBOT-HILFE!
echo DU SIEHST GENAU WAS DER BOT MACHT!
echo.
pause
color 0A
python test_bot_advanced.py
goto MENU

:GAMESTATE
cls
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

:TEST_OVERLAY
cls
echo.
echo ================================================================
echo   VISUAL OVERLAY TEST
echo ================================================================
echo.
echo Testet das Visual Overlay System:
echo   - Enemy Detection Boxes
echo   - Crosshair mit Target Lock
echo   - Game State HUD
echo   - Threat Level Bar
echo   - Action Display
echo.
pause
python utils/visual_overlay.py
goto MENU

:TEST_REWARD
cls
echo.
echo ================================================================
echo   REWARD SYSTEM TEST
echo ================================================================
echo.
echo Testet das Reward Shaping System:
echo   - Kill Rewards
echo   - Camping Penalties
echo   - Movement Rewards
echo   - Objective Rewards
echo.
echo Zeigt wie verschiedene Actions belohnt werden!
echo.
pause
python 3_learning/reinforcement/reward_shaper.py
goto MENU

:README
cls
echo.
echo ================================================================
echo   README - AI BOT ARCHITEKTUR
echo ================================================================
echo.
type README.md
echo.
pause
goto MENU

:END
cls
echo.
echo Bis zum naechsten Mal!
echo.
timeout /t 2
exit

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
echo  [2] Gegner labeln (Manual)
echo  [2a] Semi-Auto Labeln (5x schneller!)
echo  [2b] Hard Examples finden (Active Learning)
echo  [3] Dataset vorbereiten
echo  [4] Model trainieren (Standard)
echo  [4a] Fast Training (GPU-optimiert)
echo  [4b] Head-Focused Training (besser fuer Koepfe!)
echo  [5] Model testen (Visuell)
echo  [6] Model evaluieren (Metrics)
echo  [7] Live Detection Test
echo  [8] Auto-Aim starten
echo  [9] IMPROVE GUIDE oeffnen
echo  [0] Beenden
echo.
echo ====================================================================
echo.

set /p choice=Waehle eine Option:

if "%choice%"=="1" goto SCREENSHOT
if "%choice%"=="2" goto LABELING
if "%choice%"=="2a" goto LABELING_SEMI
if "%choice%"=="2b" goto FIND_HARD
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
echo                  6-CLASS LABELING (Manual)
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

:LABELING_SEMI
cls
echo ====================================================================
echo            SEMI-AUTO LABELING (5x SCHNELLER!)
echo ====================================================================
echo.
echo Nutzt dein bestehendes Model um VORZULABELN!
echo.
echo Workflow:
echo  1. Model macht automatische Predictions
echo  2. Du korrigierst/ergaenzt nur noch
echo  3. Druecke A zum Akzeptieren wenn gut
echo  4. Oder korrigiere manuell
echo  5. 5x schneller als von Grund auf!
echo.
echo TIPP:
echo  - Sammle erst 100-200 neue Screenshots
echo  - Dann nutze dieses Tool
echo  - In 1-2 Stunden hast du 200 neue Labels!
echo.
echo Braucht: Trainiertes Model (best.pt)
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
echo Analysiert alle Screenshots und findet:
echo  - Bilder mit niedrigem Confidence Score
echo  - Bilder ohne Head-Detections
echo  - Bilder mit wenigen/keinen Detections
echo  - Schwierige Szenen
echo.
echo Diese zu labeln bringt den GROESSTEN Fortschritt!
echo.
echo Output: data/hard_examples/ (Top 100)
echo         + Detaillierter Report
echo.
echo Dann labeln mit Semi-Auto Tool!
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
echo                  STANDARD TRAINING
echo ====================================================================
echo.
echo DAUERT: 30-60 Min mit GPU, 2-3 Stunden ohne GPU
echo.
echo Settings:
echo  - YOLOv8n (nano - schnell)
echo  - 100 Epochs
echo  - 640px Aufloesung
echo  - Standard Augmentation
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
echo                  FAST TRAINING (GPU-Optimiert)
echo ====================================================================
echo.
echo DAUERT: 10-20 Min mit GPU, 1-2 Stunden ohne GPU
echo.
echo Fast Training Features:
echo  - Weniger Epochs (50 statt 100)
echo  - Auto-optimierte Batch Size
echo  - Image Caching
echo  - Mixed Precision (GPU)
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

:TRAINING_HEAD
cls
echo ====================================================================
echo            HEAD-FOCUSED TRAINING
echo ====================================================================
echo.
echo Spezial-Training optimiert fuer Kopf-Erkennung!
echo.
echo DAUERT: ~1-2 Stunden mit GPU
echo.
echo Head-Optimierungen:
echo  - Hoehere Aufloesung (800px statt 640px)
echo  - YOLOv8s (praeziser als nano)
echo  - Mehr Epochs (150)
echo  - Copy-Paste Augmentation
echo  - Close-Crop fuer kleine Koepfe
echo.
echo Erwarte 20-30 Prozent bessere Head-Detection!
echo.
echo TIPP: Nutze dies wenn Koepfe schlecht erkannt werden
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
echo                MODEL EVALUIEREN - METRICS
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
echo                LIVE DETECTION TEST
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
echo         6-CLASS AUTO-AIM MIT TEAM-ERKENNUNG
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

:IMPROVE_GUIDE
cls
echo ====================================================================
echo                    IMPROVE GUIDE
echo ====================================================================
echo.
echo Oeffne IMPROVE_GUIDE.md fuer:
echo.
echo  - Semi-Auto Labeling Tutorial
echo  - Head-Detection Optimierung
echo  - Active Learning Strategie
echo  - Data Quality Tipps
echo  - Advanced Algorithmen
echo  - Expected Performance Improvements
echo.
echo Beste Strategie fuer bessere Ergebnisse:
echo  1. Semi-Auto Labeling (400+ Bilder in 2h)
echo  2. Hard Examples finden und labeln
echo  3. Head-Focused Training
echo  = DEUTLICH bessere Head-Detection!
echo.
pause
start IMPROVE_GUIDE.md
goto MENU

:EXIT
cls
echo.
echo Vielen Dank!
echo.
timeout /t 2 >nul
exit

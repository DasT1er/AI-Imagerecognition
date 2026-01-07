@echo off
chcp 65001 >nul
title GPU Check
color 0A

cls
echo ====================================================================
echo                        GPU STATUS CHECK
echo ====================================================================
echo.
echo Pruefe ob CUDA-kompatibles PyTorch installiert ist...
echo.

python -c "import torch; print('PyTorch Version:', torch.__version__); print('CUDA verfuegbar:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'KEINE GPU'); print('VRAM:', str(round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1)) + ' GB' if torch.cuda.is_available() else 'N/A')"

echo.
echo ====================================================================
echo.

if errorlevel 1 (
    echo PyTorch nicht installiert oder FEHLER!
    echo.
    echo Installation:
    echo Siehe GPU_SETUP.txt fuer Anleitung
) else (
    echo Wenn "CUDA verfuegbar: True" steht, bist du bereit!
    echo Wenn "False" oder "KEINE GPU":
    echo   - Siehe GPU_SETUP.txt
    echo   - Installiere CUDA-kompatibles PyTorch
)

echo.
pause

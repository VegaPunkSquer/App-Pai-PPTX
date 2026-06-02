@echo off
echo ==========================================
echo   Gerador de Executavel - App Pai Vega
echo ==========================================
echo.

:: 1. Garante que o pyinstaller está instalado no ambiente do uv
echo [1/3] Verificando/Instalando PyInstaller...
uv pip install pyinstaller

echo.
:: 2. Roda o pyinstaller.
:: --noconsole: esconde o terminal do windows
:: --onefile: junta tudo num unico .exe
:: --name: nome do arquivo final
echo [2/3] Compilando o aplicativo (isso pode levar alguns minutos)...
uv run pyinstaller --noconsole --onefile --name "App_Pai_Vega" main.py

echo.
echo [3/3] Limpando arquivos temporarios...
:: Remove a pasta build e o arquivo .spec que o pyinstaller cria (opcional, deixa a pasta mais limpa)
rmdir /s /q build
del /q App_Pai_Vega.spec

echo.
echo ==========================================
echo SUCESSO! O seu executavel esta na pasta "dist".
echo Pode pegar o App_Pai_Vega.exe la e mandar pro seu pai!
echo ==========================================
pause
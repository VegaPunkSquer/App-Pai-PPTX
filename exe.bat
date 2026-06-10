@echo off
echo ==========================================
echo   Gerador de Executavel - App Pai Vega
echo ==========================================
echo.

echo [1/3] Verificando/Instalando PyInstaller e dependencias...
uv pip install pyinstaller comtypes

echo.
echo [2/3] Compilando o aplicativo (isso pode levar alguns minutos)...
:: --noconsole: esconde o terminal
:: --onefile: junta tudo num unico .exe
:: --collect-all: Força a inclusao de bibliotecas dificeis de rastrear
:: --add-data: Embuti arquivos extras
uv run pyinstaller --clean --noconsole --onefile --add-data "vega_manifesto.json;." --name "SmartSlides Pro" --icon "assets/SmartSlides.ico" --collect-all pptx --collect-all google --hidden-import comtypes --hidden-import comtypes.client --add-data ".env;." --add-data "assets;assets" main.py

echo.
echo [3/3] Limpando arquivos temporarios...
rmdir /s /q build
del /q "SmartSlides Pro.spec"
del /q App_Pai_Vega.spec

echo.
echo ==========================================
echo SUCESSO ABSOLUTO! 
echo O seu App_Pai_Vega.exe blindado e autonomo esta na pasta "dist".
echo Pode enviar SOH ELE pro seu pai que agora vai voar!
echo ==========================================
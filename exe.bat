@echo off
echo ==========================================
echo   Gerador de Executavel - App Pai Vega
echo ==========================================
echo.

echo [1/3] Verificando/Instalando PyInstaller e TODAS as dependencias...
uv pip install pyinstaller comtypes python-pptx google-genai PySide6 python-dotenv requests

echo.
echo [2/3] Compilando o aplicativo (isso pode levar alguns minutos)...
:: --noconsole: esconde o terminal
:: --onefile: junta tudo num unico .exe
:: --collect-all: Forca a inclusao de bibliotecas dificeis de rastrear
:: --hidden-import: Arma na cabeca do PyInstaller pra ele nao esquecer os modulos
:: --add-data: Embuti arquivos extras
uv run pyinstaller --clean --noconsole --onefile --add-data "vega_manifesto.json;." --name "SmartSlides Pro" --icon "assets/SmartSlides.ico" --collect-all pptx --collect-all google --hidden-import pptx --hidden-import comtypes --hidden-import comtypes.client --add-data ".env;." --add-data "assets;assets" main.py

echo.
echo [3/3] Limpando arquivos temporarios...
rmdir /s /q build
del /q "SmartSlides Pro.spec"
del /q App_Pai_Vega.spec

echo.
echo ==========================================
echo SUCESSO ABSOLUTO! 
echo O seu "SmartSlides Pro.exe" blindado e autonomo esta na pasta "dist".
echo Pode enviar SOH ELE pro seu pai que agora vai voar!
echo ==========================================
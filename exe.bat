@echo off
echo ==========================================
echo   Gerador de Executavel - App Pai Vega
echo ==========================================
echo.

echo [1/3] Verificando/Instalando PyInstaller...
uv pip install pyinstaller

echo.
echo [2/3] Compilando o aplicativo (isso pode levar alguns minutos)...
:: --noconsole: esconde o terminal
:: --onefile: junta tudo num unico .exe
:: --collect-all: Força a inclusao de bibliotecas dificeis de rastrear
:: --add-data: Embuti o arquivo .env dentro do .exe compilado
uv run pyinstaller --noconsole --onefile --name "App_Pai_Vega" --collect-all pptx --collect-all google --add-data ".env;." main.py

echo.
echo [3/3] Limpando arquivos temporarios...
rmdir /s /q build
del /q App_Pai_Vega.spec

echo.
echo ==========================================
echo SUCESSO ABSOLUTO! 
echo O seu App_Pai_Vega.exe blindado e autonomo esta na pasta "dist".
echo Pode enviar SOH ELE pro seu pai que agora vai voar!
echo ==========================================
pause
```
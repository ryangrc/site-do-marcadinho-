@echo off
echo Iniciando Mercadinho Conectado...
cd /d "%~dp0"
start /b python app.py
timeout /t 3 /nobreak > nul
start http://127.0.0.1:5000
echo Servidor iniciado. Pressione qualquer tecla para fechar...
pause > nul
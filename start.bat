@echo off
echo ========================================
echo   VacancyBot - Запуск
echo ========================================
echo.

REM Остановка старых процессов
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo [1/3] Запуск сервера Web App...
start "Web App Server" cmd /k "cd /d %~dp0 && python server.py"

timeout /t 3 /nobreak >nul

echo [2/3] Запуск Telegram бота...
start "Telegram Bot" cmd /k "cd /d %~dp0 && python bot.py"

timeout /t 2 /nobreak >nul

echo [3/3] Готово!
echo.
echo ========================================
echo   Сервер: http://localhost:5000
echo   Бот: @Recruit2026_bot
echo ========================================
echo.
echo Нажмите любую клавишу для выхода...
pause >nul

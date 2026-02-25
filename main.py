import os
import sys
import subprocess
import time
import threading

def run_server():
    """Запуск Flask сервера"""
    print("[START] Запуск server.py...")
    subprocess.run([sys.executable, "server.py"])

def run_bot():
    """Запуск Telegram бота"""
    print("[START] Запуск bot.py...")
    time.sleep(2)  # Ждём пока сервер запустится
    subprocess.run([sys.executable, "bot.py"])

if __name__ == "__main__":
    print("[INFO] Запуск VacancyBot...")
    
    # Запускаем сервер в отдельном потоке
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Запускаем бота в главном потоке
    run_bot()

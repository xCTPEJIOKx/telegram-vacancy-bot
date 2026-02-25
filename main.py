#!/usr/bin/env python
import subprocess
import sys
import os

# Запуск server.py и bot.py одновременно
server_proc = subprocess.Popen([sys.executable, "server.py"])
bot_proc = subprocess.Popen([sys.executable, "bot.py"])

# Ожидание завершения
server_proc.wait()
bot_proc.wait()

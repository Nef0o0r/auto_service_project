# services/logger.py
import os
from datetime import datetime


class Logger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def log(self, user, action, details=""):
        """Запись действия в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | {user} | {action} | {details}\n"

        # Дневной лог-файл
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"activity_{date_str}.log")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def get_logs(self, date_str=None):
        """Чтение логов за указанную дату"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        log_file = os.path.join(self.log_dir, f"activity_{date_str}.log")

        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                return f.read().splitlines()
        return []
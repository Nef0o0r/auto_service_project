# services/backup.py
import os
import shutil
from datetime import datetime
import json


class BackupService:
    def __init__(self, backup_dir="backups"):
        self.backup_dir = backup_dir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

    def create_backup(self, db_config_file=".env"):
        """Создание резервной копии конфигурации и данных"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(self.backup_dir, f"backup_{timestamp}")

        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        # Копируем конфигурацию БД
        if os.path.exists(db_config_file):
            shutil.copy2(db_config_file, os.path.join(backup_folder, "db_config.env"))

        # Создаем файл с метаданными бэкапа
        metadata = {
            "timestamp": timestamp,
            "backup_folder": backup_folder,
            "files": ["db_config.env"]
        }

        # Сохраняем метаданные
        with open(os.path.join(backup_folder, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return backup_folder

    def list_backups(self):
        """Список доступных резервных копий"""
        if not os.path.exists(self.backup_dir):
            return []

        backups = []
        for folder in os.listdir(self.backup_dir):
            folder_path = os.path.join(self.backup_dir, folder)
            if os.path.isdir(folder_path):
                metadata_file = os.path.join(folder_path, "metadata.json")
                if os.path.exists(metadata_file):
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                        backups.append({
                            "folder": folder,
                            "timestamp": metadata["timestamp"],
                            "path": folder_path
                        })

        # Сортируем по времени (новые сначала)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        return backups

    def restore_backup(self, backup_folder):
        """Восстановление из резервной копии"""
        source_env = os.path.join(backup_folder, "db_config.env")
        if os.path.exists(source_env):
            shutil.copy2(source_env, ".env")
            return True
        return False
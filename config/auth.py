import hashlib
import json
import os


class AuthManager:
    def __init__(self, auth_file="users.json"):
        self.auth_file = auth_file
        self.current_user = None
        self.users = self.load_users()

    def load_users(self):
        """Загрузка пользователей из файла"""
        if os.path.exists(self.auth_file):
            with open(self.auth_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # Создание пользователей по умолчанию
            default_users = {
                "admin": {
                    "password": self.hash_password("admin123"),
                    "role": "admin"
                },
                "dispatcher": {
                    "password": self.hash_password("dispatcher123"),
                    "role": "dispatcher"
                }
            }
            self.save_users(default_users)
            return default_users

    def save_users(self, users=None):
        """Сохранение пользователей в файл"""
        if users is None:
            users = self.users

        with open(self.auth_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)

    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username, password):
        """Аутентификация пользователя"""
        if username in self.users:
            hashed_password = self.hash_password(password)
            if self.users[username]["password"] == hashed_password:
                self.current_user = username
                return self.users[username]["role"]
        return None

    def create_user(self, username, password, role="dispatcher"):
        """Создание нового пользователя"""
        if username not in self.users:
            self.users[username] = {
                "password": self.hash_password(password),
                "role": role
            }
            self.save_users()
            return True
        return False

    def change_password(self, username, new_password):
        """Изменение пароля пользователя"""
        if username in self.users:
            self.users[username]["password"] = self.hash_password(new_password)
            self.save_users()
            return True
        return False

    def logout(self):
        """Выход из системы"""
        self.current_user = None

    def get_current_user(self):
        """Получение текущего пользователя"""
        return self.current_user

    def get_user_role(self, username):
        """Получение роли пользователя"""
        if username in self.users:
            return self.users[username]["role"]
        return None
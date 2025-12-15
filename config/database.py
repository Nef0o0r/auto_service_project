import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'auto_service'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'password'),
                port=os.getenv('DB_PORT', '5432')
            )
            # Устанавливаем autocommit после подключения
            self.connection.autocommit = True
        return self.connection

    def close_connection(self):
        if self.connection and not self.connection.closed:
            self.connection.close()

    # В config/database.py изменим execute_query
    def execute_query(self, query, params=None, fetch=False, transaction=False):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            if transaction:
                conn.autocommit = False

            cursor.execute(query, params)

            if fetch:
                result = cursor.fetchall()
            else:
                result = cursor.rowcount

            if transaction:
                conn.commit()

            return result

        except Exception as e:
            if transaction:
                conn.rollback()
            raise e

        finally:
            cursor.close()
            if transaction:
                conn.autocommit = True


# Добавим в config/database.py
class SecurityManager:
    def __init__(self):
        self.db = Database()

    def create_roles(self):
        """Создание ролей пользователей"""
        queries = [
            # Роль диспетчера
            "CREATE ROLE IF NOT EXISTS dispatcher WITH LOGIN PASSWORD 'dispatcher_pass'",
            # Роль администратора
            "CREATE ROLE IF NOT EXISTS admin WITH LOGIN PASSWORD 'admin_pass' SUPERUSER",

            # Права для диспетчера
            "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO dispatcher",
            "GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO dispatcher",

            # Запрет изменения структуры
            "REVOKE CREATE ON SCHEMA public FROM dispatcher"
        ]

        for query in queries:
            try:
                self.db.execute_query(query)
            except:
                pass

    def authenticate_user(self, username, password):
        """Аутентификация пользователя"""
        # Здесь должна быть реализация проверки через систему ролей PostgreSQL
        # Для упрощения можно использовать словарь
        users = {
            'dispatcher': {'role': 'dispatcher', 'password': 'dispatcher_pass'},
            'admin': {'role': 'admin', 'password': 'admin_pass'}
        }

        if username in users and users[username]['password'] == password:
            return users[username]['role']
        return None
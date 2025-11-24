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

    def execute_query(self, query, params=None, fetch=False):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
            else:
                # При autocommit = True commit не нужен
                result = None
            return result
        except Exception as e:
            # При autocommit = True rollback не нужен
            raise e
        finally:
            cursor.close()
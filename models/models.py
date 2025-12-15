from config.database import Database


class AutoServiceModels:
    def __init__(self):
        self.db = Database()
        self.init_database()

    def diagnose_database(self):
        """Диагностика структуры базы данных"""
        print("\n=== ДИАГНОСТИКА БАЗЫ ДАННЫХ ===")

        try:
            # Проверяем существование таблиц
            tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """

            tables = self.db.execute_query(tables_query, fetch=True)
            print("Таблицы в базе данных:")
            for table in tables:
                print(f"  - {table['table_name']}")

            # Проверяем колонки для каждой таблицы
            for table in tables:
                table_name = table['table_name']
                columns_query = f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                """
                columns = self.db.execute_query(columns_query, fetch=True)
                print(f"\nКолонки таблицы {table_name}:")
                for col in columns:
                    print(f"  - {col['column_name']} ({col['data_type']})")

        except Exception as e:
            print(f"Ошибка при диагностике базы данных: {e}")

    def is_database_empty(self):
        """Проверяет, пустая ли база данных"""
        try:
            # Проверяем все основные таблицы
            tables = ['Владелец', 'Автомобиль', 'Работник', 'Неисправность', 'Факт_ремонта']

            for table in tables:
                result = self.db.execute_query(
                    f"SELECT COUNT(*) as count FROM {table}",
                    fetch=True
                )
                if result[0]['count'] > 0:
                    return False
            return True
        except:
            return True

    def init_database(self):
        """Инициализация структуры базы данных"""
        queries = [
            # Таблица Владельцев
            """
            CREATE TABLE IF NOT EXISTS Владелец (
                ID_Владельца SERIAL PRIMARY KEY,
                ФИО VARCHAR(100) NOT NULL,
                Адрес VARCHAR(200)
            )
            """,

            # Таблица Автомобилей
            """
            CREATE TABLE IF NOT EXISTS Автомобиль (
                ID_Автомобиля SERIAL PRIMARY KEY,
                Номер_госрегистрации VARCHAR(15) NOT NULL UNIQUE,
                Марка VARCHAR(50) NOT NULL,
                Год_выпуска INTEGER,
                Изготовитель VARCHAR(50),
                ID_Владельца INTEGER NOT NULL REFERENCES Владелец(ID_Владельца) ON DELETE CASCADE
            )
            """,

            # Таблица Работников
            """
            CREATE TABLE IF NOT EXISTS Работник (
                ID_Работника SERIAL PRIMARY KEY,
                ФИО VARCHAR(100) NOT NULL
            )
            """,

            # Таблица Неисправностей
            """
            CREATE TABLE IF NOT EXISTS Неисправность (
                ID_Неисправности SERIAL PRIMARY KEY,
                Тип_неисправности VARCHAR(100) NOT NULL UNIQUE
            )
            """,

            # Таблица Фактов ремонта
            """
            CREATE TABLE IF NOT EXISTS Факт_ремонта (
                ID_Ремонта SERIAL PRIMARY KEY,
                ID_Автомобиля INTEGER NOT NULL REFERENCES Автомобиль(ID_Автомобиля) ON DELETE CASCADE,
                ID_Работника INTEGER NOT NULL REFERENCES Работник(ID_Работника),
                ID_Неисправности INTEGER NOT NULL REFERENCES Неисправность(ID_Неисправности),
                Время_устранения TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Индексы для оптимизации
            """
            CREATE INDEX IF NOT EXISTS idx_автомобиль_владелец ON Автомобиль(ID_Владельца)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_автомобиль_номер ON Автомобиль(Номер_госрегистрации)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_ремонт_автомобиль ON Факт_ремонта(ID_Автомобиля)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_ремонт_работник ON Факт_ремонта(ID_Работника)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_ремонт_неисправность ON Факт_ремонта(ID_Неисправности)
            """
        ]
        additional_constraints = [
            # Проверка года выпуска автомобиля
            """
            ALTER TABLE Автомобиль 
            ADD CONSTRAINT check_year 
            CHECK (Год_выпуска BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE) + 1)
            """,

            # Проверка формата номера госрегистрации (российский формат)
            """
            ALTER TABLE Автомобиль
            ADD CONSTRAINT check_license_plate
            CHECK (Номер_госрегистрации SIMILAR TO '[АВЕКМНОРСТУХ][0-9]{3}[АВЕКМНОРСТУХ]{2}[0-9]{2,3}')
            """,

            # Ограничение на время устранения неисправности (не в будущем)
            """
            ALTER TABLE Факт_ремонта
            ADD CONSTRAINT check_repair_time
            CHECK (Время_устранения <= CURRENT_TIMESTAMP)
            """
        ]

        for query in queries:
            try:
                self.db.execute_query(query)
            except Exception as e:
                print(f"Ошибка при выполнении запроса: {e}")

    def insert_test_data(self):
        """Вставка тестовых данных (только если база пустая)"""
        if not self.is_database_empty():
            print("База данных уже содержит данные. Пропускаем добавление тестовых данных.")
            return False

        print("Добавление тестовых данных...")

        try:
            # Сначала очистим все данные для чистого состояния
            self.clear_test_data()

            # Вставляем данные в правильном порядке с учетом зависимостей

            # 1. Владельцы
            print("Добавление владельцев...")
            owners_data = [
                ("Иванов Сергей Петрович", "ул. Ленина, 10"),
                ("Петрова Анна Владимировна", "пр. Мира, 25"),
                ("Сидоров Алексей Николаевич", "ул. Гагарина, 15")
            ]

            owner_ids = {}
            for фио, адрес in owners_data:
                result = self.db.execute_query(
                    "INSERT INTO Владелец (ФИО, Адрес) VALUES (%s, %s) RETURNING ID_Владельца",
                    (фио, адрес),
                    fetch=True
                )

                # Используем правильное имя колонки: id_Владельца
                if result and len(result) > 0:
                    owner_ids[фио] = result[0]['id_Владельца']
                    print(f"  Добавлен владелец: {фио} (ID: {owner_ids[фио]})")
                else:
                    raise Exception("Не удалось получить ID вставленного владельца")

            # 2. Автомобили
            print("Добавление автомобилей...")
            cars_data = [
                ("А123ВС77", "Toyota Camry", 2018, "Япония", "Иванов Сергей Петрович"),
                ("В456ОР77", "Lada Vesta", 2020, "Россия", "Петрова Анна Владимировна"),
                ("С789ТУ77", "Kia Rio", 2019, "Корея", "Сидоров Алексей Николаевич")
            ]

            car_ids = {}
            for номер, марка, год, изготовитель, владелец in cars_data:
                result = self.db.execute_query(
                    "INSERT INTO Автомобиль (Номер_госрегистрации, Марка, Год_выпуска, Изготовитель, ID_Владельца) VALUES (%s, %s, %s, %s, %s) RETURNING ID_Автомобиля",
                    (номер, марка, год, изготовитель, owner_ids[владелец]),
                    fetch=True
                )

                if result and len(result) > 0:
                    car_ids[номер] = result[0]['id_Автомобиля']
                    print(f"  Добавлен автомобиль: {марка} {номер} (ID: {car_ids[номер]})")
                else:
                    raise Exception(f"Не удалось получить ID вставленного автомобиля {номер}")

            # 3. Работники
            print("Добавление работников...")
            employees_data = [
                "Смирнов Алексей Иванович",
                "Козлова Мария Сергеевна",
                "Петров Дмитрий Викторович"
            ]

            employee_ids = {}
            for фио in employees_data:
                result = self.db.execute_query(
                    "INSERT INTO Работник (ФИО) VALUES (%s) RETURNING ID_Работника",
                    (фио,),
                    fetch=True
                )

                if result and len(result) > 0:
                    employee_ids[фио] = result[0]['id_Работника']
                    print(f"  Добавлен работник: {фио} (ID: {employee_ids[фио]})")
                else:
                    raise Exception(f"Не удалось получить ID вставленного работника {фио}")

            # 4. Неисправности
            print("Добавление неисправностей...")
            faults_data = [
                "Замена тормозных колодок",
                "Ремонт двигателя",
                "Замена масла",
                "Замена аккумулятора",
                "Балансировка колес"
            ]

            fault_ids = {}
            for неисправность in faults_data:
                result = self.db.execute_query(
                    "INSERT INTO Неисправность (Тип_неисправности) VALUES (%s) ON CONFLICT (Тип_неисправности) DO NOTHING RETURNING ID_Неисправности",
                    (неисправность,),
                    fetch=True
                )

                if result and len(result) > 0:
                    fault_ids[неисправность] = result[0]['id_Неисправности']
                    print(f"  Добавлена неисправность: {неисправность} (ID: {fault_ids[неисправность]})")
                else:
                    print(f"  Неисправность '{неисправность}' уже существует или не была добавлена")

            # 5. Факты ремонта
            print("Добавление фактов ремонта...")
            repairs_data = [
                ("А123ВС77", "Смирнов Алексей Иванович", "Замена тормозных колодок", "2024-01-15 10:00:00"),
                ("В456ОР77", "Козлова Мария Сергеевна", "Замена масла", "2024-01-16 14:30:00"),
                ("С789ТУ77", "Петров Дмитрий Викторович", "Ремонт двигателя", "2024-01-17 09:15:00"),
                ("А123ВС77", "Козлова Мария Сергеевна", "Замена аккумулятора", "2024-01-18 11:45:00")
            ]

            repair_count = 0
            for номер_авто, работник, неисправность, время in repairs_data:
                # Проверяем, что все необходимые ID существуют
                if (номер_авто in car_ids and работник in employee_ids and неисправность in fault_ids):
                    self.db.execute_query(
                        "INSERT INTO Факт_ремонта (ID_Автомобиля, ID_Работника, ID_Неисправности, Время_устранения) VALUES (%s, %s, %s, %s)",
                        (car_ids[номер_авто], employee_ids[работник], fault_ids[неисправность], время)
                    )
                    repair_count += 1
                    print(f"  Добавлен ремонт: {номер_авто} - {неисправность}")
                else:
                    print(f"  Пропущен ремонт: отсутствуют данные для {номер_авто}, {работник}, {неисправность}")

            print(f"✓ Тестовые данные успешно добавлены! Добавлено {repair_count} записей о ремонтах.")
            return True

        except Exception as e:
            print(f"✗ Ошибка при вставке тестовых данных: {e}")
            # Откатываем изменения при ошибке
            print("Откат изменений...")
            self.clear_test_data()
            return False

    def clear_test_data(self):
        """Очистка всех тестовых данных в правильном порядке (сначала дочерние, потом родительские)"""
        try:
            print("Очистка данных...")

            clear_queries = [
                "DELETE FROM Факт_ремонта",
                "DELETE FROM Автомобиль",
                "DELETE FROM Владелец",
                "DELETE FROM Работник",
                "DELETE FROM Неисправность"
            ]

            for query in clear_queries:
                try:
                    result = self.db.execute_query(query)
                    print(f"  Очищено: {query.split()[2]}")
                except Exception as e:
                    print(f"  Предупреждение при очистке {query.split()[2]}: {e}")

            print("Все тестовые данные очищены")
            return True
        except Exception as e:
            print(f"Ошибка при очистке данных: {e}")
            return False
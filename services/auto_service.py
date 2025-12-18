from config.database import Database
from datetime import datetime


class AutoService:
    def __init__(self):
        self.db = Database()

    # ОПЕРАЦИИ ИЗМЕНЕНИЯ ДАННЫХ

    def add_owner(self, фио, адрес):
        """Добавление информации о владельце"""
        query = "INSERT INTO Владелец (ФИО, Адрес) VALUES (%s, %s) RETURNING ID_Владельца"
        result = self.db.execute_query(query, (фио, адрес), fetch=True)
        # Используем правильное имя колонки: id_Владельца
        return f"Владелец '{фио}' успешно добавлен с ID: {result[0]['id_Владельца']}"

    def delete_employee(self, id_работника):
        """Удаление информации о работнике станции"""
        query = "DELETE FROM Работник WHERE ID_Работника = %s"
        self.db.execute_query(query, (id_работника,))
        return f"Работник с ID {id_работника} удален"

    def update_car_license(self, id_автомобиля, новый_номер):
        """Изменение номера автомобиля с полной проверкой"""
        # 1. Проверить существование авто
        check_query = "SELECT Номер_госрегистрации, Марка FROM Автомобиль WHERE ID_Автомобиля = %s"
        car = self.db.execute_query(check_query, (id_автомобиля,), fetch=True)

        if not car:
            raise ValueError(f"Автомобиль с ID={id_автомобиля} не найден")

        old_license = car[0]['Номер_госрегистрации']
        brand = car[0]['Марка']

        # 2. Проверка нового номера на уникальность (если изменился)
        if новый_номер != old_license:
            duplicate_query = """
            SELECT ID_Автомобиля, Марка 
            FROM Автомобиль 
            WHERE Номер_госрегистрации = %s AND ID_Автомобиля != %s
            """
            duplicate = self.db.execute_query(duplicate_query, (новый_номер, id_автомобиля), fetch=True)

            if duplicate:
                duplicate_id = duplicate[0]['id_Автомобиля']
                duplicate_brand = duplicate[0]['Марка']
                raise ValueError(
                    f"Номер '{новый_номер}' уже используется автомобилем "
                    f"ID={duplicate_id} ({duplicate_brand})"
                )

        update_query = "UPDATE Автомобиль SET Номер_госрегистрации = %s WHERE ID_Автомобиля = %s"

        try:
            rowcount = self.db.execute_query(update_query, (новый_номер, id_автомобиля))

            if rowcount == 0:
                # Технически сюда не должны попасть, т.к. уже проверили существование
                return {
                    'success': False,
                    'message': f"Автомобиль не был изменен",
                    'changed': False
                }
            else:
                return {
                    'success': True,
                    'message': f"Номер автомобиля {brand} изменен: {old_license} → {новый_номер}",
                    'changed': True,
                    'old_license': old_license,
                    'new_license': новый_номер,
                    'brand': brand
                }

        except Exception as e:
            # Обработка конкретных ошибок БД
            error_msg = str(e).lower()

            if "check constraint" in error_msg:
                raise ValueError(f"Номер '{новый_номер}' имеет неверный формат")
            elif "unique constraint" in error_msg:
                raise ValueError(f"Номер '{новый_номер}' уже используется другим автомобилем")
            elif "value too long" in error_msg:
                raise ValueError("Номер слишком длинный (макс. 15 символов)")
            else:
                raise Exception(f"Ошибка при обновлении номера: {str(e)}")

    def add_employee(self, фио):
        """Добавление работника"""
        query = "INSERT INTO Работник (ФИО) VALUES (%s) RETURNING ID_Работника"
        result = self.db.execute_query(query, (фио,), fetch=True)
        return f"Работник '{фио}' добавлен с ID: {result[0]['id_Работника']}"

    def add_fault(self, тип_неисправности):
        """Добавление типа неисправности с валидацией"""

        if not тип_неисправности or not тип_неисправности.strip():
            raise ValueError("Тип неисправности не может быть пустым")

        if len(тип_неисправности.strip()) > 100:
            raise ValueError("Тип неисправности слишком длинный (макс. 100 символов)")

        # Проверка существования
        check_query = "SELECT ID_Неисправности FROM Неисправность WHERE Тип_неисправности = %s"
        existing = self.db.execute_query(check_query, (тип_неисправности.strip(),), fetch=True)

        if existing:
            fault_id = existing[0]['id_Неисправности']
            return {
                'status': 'exists',
                'message': f"Неисправность '{тип_неисправности}' уже существует",
                'id': fault_id,
                'details': f"ID: {fault_id}"
            }

        insert_query = """
        INSERT INTO Неисправность (Тип_неисправности) 
        VALUES (%s) 
        RETURNING ID_Неисправности
        """

        try:
            result = self.db.execute_query(insert_query, (тип_неисправности.strip(),), fetch=True)
            fault_id = result[0]['id_Неисправности']
            return {
                'status': 'created',
                'message': f"Неисправность '{тип_неисправности}' добавлена",
                'id': fault_id,
                'details': f"ID: {fault_id}"
            }
        except Exception as e:
            raise Exception(f"Ошибка при добавлении неисправности: {str(e)}")

    # ЗАПРОСЫ ДЛЯ ДИСПЕТЧЕРА

    def get_owner_by_license(self, номер_госрегистрации):
        """ФИО и адрес владельца автомобиля с данным номером госрегистрации"""
        query = """
        SELECT в.ФИО, в.Адрес 
        FROM Владелец в
        JOIN Автомобиль а ON в.ID_Владельца = а.ID_Владельца
        WHERE а.Номер_госрегистрации = %s
        """
        return self.db.execute_query(query, (номер_госрегистрации,), fetch=True)

    def get_car_info_by_owner(self, фио_владельца):
        """Изготовитель, марка и год выпуска автомобиля данного владельца"""
        query = """
        SELECT а.Номер_госрегистрации, а.Марка, а.Год_выпуска, а.Изготовитель
        FROM Автомобиль а
        JOIN Владелец в ON а.ID_Владельца = в.ID_Владельца
        WHERE в.ФИО = %s
        """
        return self.db.execute_query(query, (фио_владельца,), fetch=True)

    def get_fixed_faults_by_owner(self, фио_владельца):
        """Перечень устраненных неисправностей автомобиля данного владельца"""
        query = """
        SELECT DISTINCT н.Тип_неисправности
        FROM Факт_ремонта фр
        JOIN Автомобиль а ON фр.ID_Автомобиля = а.ID_Автомобиля
        JOIN Владелец в ON а.ID_Владельца = в.ID_Владельца
        JOIN Неисправность н ON фр.ID_Неисправности = н.ID_Неисправности
        WHERE в.ФИО = %s
        ORDER BY н.Тип_неисправности
        """
        return self.db.execute_query(query, (фио_владельца,), fetch=True)

    def get_repair_details(self, фио_владельца, тип_неисправности):
        """ФИО работника и время устранения данной неисправности автомобиля данного владельца"""
        query = """
        SELECT р.ФИО as Работник, а.Номер_госрегистрации, фр.Время_устранения
        FROM Факт_ремонта фр
        JOIN Автомобиль а ON фр.ID_Автомобиля = а.ID_Автомобиля
        JOIN Владелец в ON а.ID_Владельца = в.ID_Владельца
        JOIN Работник р ON фр.ID_Работника = р.ID_Работника
        JOIN Неисправность н ON фр.ID_Неисправности = н.ID_Неисправности
        WHERE в.ФИО = %s AND н.Тип_неисправности = %s
        ORDER BY фр.Время_устранения DESC
        """
        return self.db.execute_query(query, (фио_владельца, тип_неисправности), fetch=True)

    def get_cars_repaired_by_employee(self, фио_работника):
        """Какие автомобили ремонтировал данный работник станции"""
        query = """
        SELECT DISTINCT а.Марка, а.Номер_госрегистрации, в.ФИО as Владелец, н.Тип_неисправности
        FROM Факт_ремонта фр
        JOIN Автомобиль а ON фр.ID_Автомобиля = а.ID_Автомобиля
        JOIN Владелец в ON а.ID_Владельца = в.ID_Владельца
        JOIN Работник р ON фр.ID_Работника = р.ID_Работника
        JOIN Неисправность н ON фр.ID_Неисправности = н.ID_Неисправности
        WHERE р.ФИО = %s
        ORDER BY а.Марка
        """
        return self.db.execute_query(query, (фио_работника,), fetch=True)

    def get_owners_by_fault_type(self, тип_неисправности):
        """ФИО владельцев автомобилей с указанным типом неисправности"""
        query = """
        SELECT DISTINCT в.ФИО, а.Номер_госрегистрации, а.Марка
        FROM Факт_ремонта фр
        JOIN Автомобиль а ON фр.ID_Автомобиля = а.ID_Автомобиля
        JOIN Владелец в ON а.ID_Владельца = в.ID_Владельца
        JOIN Неисправность н ON фр.ID_Неисправности = н.ID_Неисправности
        WHERE н.Тип_неисправности = %s
        ORDER BY в.ФИО
        """
        return self.db.execute_query(query, (тип_неисправности,), fetch=True)

    # СПРАВКИ И ОТЧЕТЫ

    def get_fault_report(self, фио_владельца=None):
        """Справка о наличии неисправности автомобиля любого владельца"""
        if фио_владельца:
            query = """
            SELECT в.ФИО, а.Марка, а.Номер_госрегистрации, 
                   н.Тип_неисправности, фр.Время_устранения
            FROM Факт_ремонта фр
            JOIN Автомобиль а ON фр.ID_Автомобиля = а.ID_Автомобиля
            JOIN Владелец в ON а.ID_Владельца = в.ID_Владельца
            JOIN Неисправность н ON фр.ID_Неисправности = н.ID_Неисправности
            WHERE в.ФИО = %s
            ORDER BY фр.Время_устранения DESC
            """
            return self.db.execute_query(query, (фио_владельца,), fetch=True)
        else:
            query = """
            SELECT в.ФИО, а.Марка, а.Номер_госрегистрации, 
                   н.Тип_неисправности, фр.Время_устранения
            FROM Факт_ремонта фр
            JOIN Автомобиль а ON фр.ID_Автомобиля = а.ID_Автомобиля
            JOIN Владелец в ON а.ID_Владельца = в.ID_Владельца
            JOIN Неисправность н ON фр.ID_Неисправности = н.ID_Неисправности
            ORDER BY в.ФИО, фр.Время_устранения DESC
            """
            return self.db.execute_query(query, fetch=True)

    def get_station_report(self):
        """Отчет о работе станции техобслуживания"""
        # Количество ремонтируемых автомобилей
        query1 = "SELECT COUNT(DISTINCT ID_Автомобиля) as total_cars FROM Факт_ремонта"
        total_cars = self.db.execute_query(query1, fetch=True)[0]['total_cars']

        # Детали ремонтов
        query2 = """
        SELECT а.Номер_госрегистрации, в.ФИО as Владелец, 
               р.ФИО as Работник, н.Тип_неисправности, фр.Время_устранения
        FROM Факт_ремонта фр
        JOIN Автомобиль а ON фр.ID_Автомобиля = а.ID_Автомобиля
        JOIN Владелец в ON а.ID_Владельца = в.ID_Владельца
        JOIN Работник р ON фр.ID_Работника = р.ID_Работника
        JOIN Неисправность н ON фр.ID_Неисправности = н.ID_Неисправности
        ORDER BY фр.Время_устранения DESC
        LIMIT 50
        """
        repair_details = self.db.execute_query(query2, fetch=True)

        # Неисправности по маркам
        query3 = """
        SELECT а.Марка, н.Тип_неисправности, COUNT(*) as Количество
        FROM Факт_ремонта фр
        JOIN Автомобиль а ON фр.ID_Автомобиля = а.ID_Автомобиля
        JOIN Неисправность н ON фр.ID_Неисправности = н.ID_Неисправности
        GROUP BY а.Марка, н.Тип_неисправности
        ORDER BY а.Марка, Количество DESC
        """
        faults_by_brand = self.db.execute_query(query3, fetch=True)

        # Статистика по работникам
        query4 = """
        SELECT р.ФИО, COUNT(*) as Количество_ремонтов
        FROM Факт_ремонта фр
        JOIN Работник р ON фр.ID_Работника = р.ID_Работника
        GROUP BY р.ФИО
        ORDER BY Количество_ремонтов DESC
        """
        employee_stats = self.db.execute_query(query4, fetch=True)

        return total_cars, repair_details, faults_by_brand, employee_stats

    def get_all_owners(self):
        """Получить всех владельцев"""
        return self.db.execute_query("SELECT * FROM Владелец ORDER BY ФИО", fetch=True)

    def get_all_employees(self):
        """Получить всех работников"""
        return self.db.execute_query("SELECT * FROM Работник ORDER BY ФИО", fetch=True)

    def get_all_cars(self):
        """Получить все автомобили"""
        return self.db.execute_query("SELECT * FROM Автомобиль ORDER BY Марка", fetch=True)

    def get_all_faults(self):
        """Получить все типы неисправностей"""
        return self.db.execute_query("SELECT * FROM Неисправность ORDER BY Тип_неисправности", fetch=True)
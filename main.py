from services.auto_service import AutoService
from models.models import AutoServiceModels
import os


def print_results(results, title):
    """Вспомогательная функция для красивого вывода результатов"""
    print(f"\n{'=' * 60}")
    print(f"{title:^60}")
    print(f"{'=' * 60}")

    if not results:
        print("Данные не найдены")
        return

    # Получаем названия колонок
    columns = list(results[0].keys())

    # Выводим заголовки
    header = " | ".join(str(col).ljust(20) for col in columns)
    print(header)
    print("-" * len(header))

    # Выводим данные
    for row in results:
        line = " | ".join(str(row[col]).ljust(20) for col in columns)
        print(line)


def print_simple_list(items, title):
    """Вывод простого списка"""
    print(f"\n{title}:")
    print("-" * 40)
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")


def wait_for_continue():
    """Ожидание нажатия Enter для продолжения"""
    input("\nНажмите Enter для продолжения...")


def test_data_menu(models, service):
    """Меню управления тестовыми данными"""
    while True:
        print("\n" + "=" * 50)
        print("УПРАВЛЕНИЕ ТЕСТОВЫМИ ДАННЫМИ")
        print("=" * 50)
        print("1 - Продолжить работу с текущими данными")
        print("2 - Добавить тестовые данные (очистить существующие)")
        print("3 - Очистить все данные")
        print("4 - Проверить состояние базы данных")
        print("0 - Выйти из программы")

        choice = input("\nВыберите действие: ").strip()

        if choice == '0':
            print("Выход из программы.")
            return False
        elif choice == '1':
            return True
        elif choice == '2':
            confirm = input("Вы уверены? Это очистит все существующие данные. (y/N): ")
            if confirm.lower() == 'y':
                models.clear_test_data()
                models.insert_test_data()
                print("Тестовые данные обновлены")
            wait_for_continue()
        elif choice == '3':
            confirm = input("Вы уверены? Это удалит ВСЕ данные из базы. (y/N): ")
            if confirm.lower() == 'y':
                models.clear_test_data()
                print("Все данные очищены")
            wait_for_continue()
        elif choice == '4':
            try:
                owners = service.get_all_owners()
                employees = service.get_all_employees()
                cars = service.get_all_cars()
                faults = service.get_all_faults()
                repairs = service.db.execute_query(
                    "SELECT COUNT(*) as count FROM Факт_ремонта",
                    fetch=True
                )

                print(f"\nСостояние базы данных:")
                print(f"  Владельцы: {len(owners)} записей")
                print(f"  Работники: {len(employees)} записей")
                print(f"  Автомобили: {len(cars)} записей")
                print(f"  Неисправности: {len(faults)} записей")
                print(f"  Факты ремонта: {repairs[0]['count']} записей")

                if len(owners) > 0:
                    print(f"\nПримеры данных:")
                    owner_name = owners[0].get('ФИО')
                    print(f"  Первый владелец: {owner_name}")
                if len(cars) > 0:
                    brand = cars[0].get('Марка')
                    license_plate = cars[0].get('Номер_госрегистрации')
                    print(f"  Первый автомобиль: {brand} ({license_plate})")
                if len(employees) > 0:
                    employee_name = employees[0].get('ФИО')
                    print(f"  Первый работник: {employee_name}")
                if len(faults) > 0:
                    fault_type = faults[0].get('Тип_неисправности')
                    print(f"  Первая неисправность: {fault_type}")

            except Exception as e:
                print(f"Ошибка при проверке состояния базы: {e}")
            wait_for_continue()
        else:
            print("Неверный выбор, попробуйте снова")


def operations_menu(service):
    """Меню операций с данными"""
    while True:
        print("\n" + "=" * 50)
        print("ОПЕРАЦИИ С ДАННЫМИ")
        print("=" * 50)
        print("1 - Добавить владельца")
        print("2 - Добавить работника")
        print("3 - Добавить неисправность")
        print("4 - Зарегистрировать ремонт")
        print("5 - Удалить работника")
        print("6 - Изменить номер автомобиля")
        print("0 - Назад в главное меню")

        choice = input("\nВыберите операцию: ").strip()

        if choice == '0':
            break

        elif choice == '1':
            print("\n--- ДОБАВЛЕНИЕ ВЛАДЕЛЬЦА ---")
            фио = input("ФИО владельца (0 - отмена): ")
            if фио == '0':
                continue
            адрес = input("Адрес: ")
            if адрес == '0':
                continue
            try:
                result = service.add_owner(фио, адрес)
                print(f"✓ {result}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif choice == '2':
            print("\n--- ДОБАВЛЕНИЕ РАБОТНИКА ---")
            фио = input("ФИО работника (0 - отмена): ")
            if фио == '0':
                continue
            try:
                result = service.add_employee(фио)
                print(f"✓ {result}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif choice == '3':
            print("\n--- ДОБАВЛЕНИЕ НЕИСПРАВНОСТИ ---")
            неисправность = input("Тип неисправности (0 - отмена): ")
            if неисправность == '0':
                continue
            try:
                result = service.add_fault(неисправность)
                print(f"✓ {result}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif choice == '4':
            print("\n--- РЕГИСТРАЦИЯ РЕМОНТА ---")
            номер_авто = input("Номер автомобиля (0 - отмена): ")
            if номер_авто == '0':
                continue
            фио_работника = input("ФИО работника (0 - отмена): ")
            if фио_работника == '0':
                continue
            тип_неисправности = input("Тип неисправности (0 - отмена): ")
            if тип_неисправности == '0':
                continue
            try:
                result = service.add_repair(номер_авто, фио_работника, тип_неисправности)
                print(f"✓ {result}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif choice == '5':
            print("\n--- УДАЛЕНИЕ РАБОТНИКА ---")
            try:
                # Покажем всех работников для удобства
                employees = service.get_all_employees()
                if employees:
                    print("\nСписок работников:")
                    for emp in employees:
                        # Используем правильные имена колонок из диагностики
                        employee_id = emp.get('id_Работника')
                        employee_name = emp.get('ФИО')
                        print(f"  ID: {employee_id} - {employee_name}")

                id_работника = input("\nID работника для удаления (0 - отмена): ")
                if id_работника == '0':
                    continue
                id_работника = int(id_работника)
                result = service.delete_employee(id_работника)
                print(f"✓ {result}")
            except ValueError:
                print("✗ Ошибка: введите числовой ID")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif choice == '6':
            print("\n--- ИЗМЕНЕНИЕ НОМЕРА АВТОМОБИЛЯ ---")
            try:
                # Покажем все автомобили для удобства
                cars = service.get_all_cars()
                if cars:
                    print("\nСписок автомобилей:")
                    for car in cars:
                        # Используем правильные имена колонок из диагностики
                        car_id = car.get('id_Автомобиля')
                        license_plate = car.get('Номер_госрегистрации')
                        brand = car.get('Марка')
                        print(f"  ID: {car_id} - {license_plate} ({brand})")

                id_авто = input("\nID автомобиля (0 - отмена): ")
                if id_авто == '0':
                    continue
                id_авто = int(id_авто)
                новый_номер = input("Новый номер: ")
                if новый_номер == '0':
                    continue
                result = service.update_car_license(id_авто, новый_номер)
                print(f"✓ {result}")
            except ValueError:
                print("✗ Ошибка: введите числовой ID")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        else:
            print("Неверный выбор, попробуйте снова")

def queries_menu(service):
    """Меню запросов диспетчера"""
    while True:
        print("\n--- ЗАПРОСЫ ДИСПЕТЧЕРА ---")
        print("1 - Владелец по номеру авто")
        print("2 - Информация об авто владельца")
        print("3 - Устраненные неисправности владельца")
        print("4 - Детали ремонта")
        print("5 - Авто работника")
        print("6 - Владельцы по типу неисправности")
        print("0 - Назад в главное меню")

        sub_choice = input("Выберите запрос: ")

        if sub_choice == '0':
            break

        elif sub_choice == '1':
            print("\n--- ВЛАДЕЛЕЦ ПО НОМЕРУ АВТО ---")
            номер = input("Номер госрегистрации (0 - отмена): ")
            if номер == '0':
                continue
            try:
                results = service.get_owner_by_license(номер)
                print_results(results, f"Владелец авто {номер}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '2':
            print("\n--- ИНФОРМАЦИЯ ОБ АВТО ВЛАДЕЛЬЦА ---")
            фио = input("ФИО владельца (0 - отмена): ")
            if фио == '0':
                continue
            try:
                results = service.get_car_info_by_owner(фио)
                print_results(results, f"Автомобили владельца {фио}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '3':
            print("\n--- УСТРАНЕННЫЕ НЕИСПРАВНОСТИ ВЛАДЕЛЬЦА ---")
            фио = input("ФИО владельца (0 - отмена): ")
            if фио == '0':
                continue
            try:
                results = service.get_fixed_faults_by_owner(фио)
                print_simple_list([row['тип_неисправности'] for row in results], f"Устраненные неисправности {фио}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '4':
            print("\n--- ДЕТАЛИ РЕМОНТА ---")
            фио = input("ФИО владельца (0 - отмена): ")
            if фио == '0':
                continue
            неисправность = input("Тип неисправности (0 - отмена): ")
            if неисправность == '0':
                continue
            try:
                results = service.get_repair_details(фио, неисправность)
                print_results(results, f"Детали ремонта {неисправность} для {фио}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '5':
            print("\n--- АВТОМОБИЛИ РАБОТНИКА ---")
            фио = input("ФИО работника (0 - отмена): ")
            if фио == '0':
                continue
            try:
                results = service.get_cars_repaired_by_employee(фио)
                print_results(results, f"Автомобили, отремонтированные {фио}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '6':
            print("\n--- ВЛАДЕЛЬЦЫ ПО ТИПУ НЕИСПРАВНОСТИ ---")
            неисправность = input("Тип неисправности (0 - отмена): ")
            if неисправность == '0':
                continue
            try:
                results = service.get_owners_by_fault_type(неисправность)
                print_results(results, f"Владельцы с неисправностью: {неисправность}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        else:
            print("Неверный выбор, попробуйте снова")


def reports_menu(service):
    """Меню справок и отчетов"""
    while True:
        print("\n--- СПРАВКИ И ОТЧЕТЫ ---")
        print("1 - Справка о неисправностях")
        print("2 - Полный отчет о работе станции")
        print("0 - Назад в главное меню")

        sub_choice = input("Выберите отчет: ")

        if sub_choice == '0':
            break

        elif sub_choice == '1':
            print("\n--- СПРАВКА О НЕИСПРАВНОСТЯХ ---")
            фио = input("ФИО владельца (Enter - все владельцы, 0 - отмена): ")
            if фио == '0':
                continue
            try:
                if фио.strip():
                    results = service.get_fault_report(фио)
                    print_results(results, f"Неисправности {фио}")
                else:
                    results = service.get_fault_report()
                    print_results(results, "Все неисправности")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '2':
            print("\n--- ПОЛНЫЙ ОТЧЕТ О РАБОТЕ СТАНЦИИ ---")
            try:
                total_cars, repairs, faults, employees = service.get_station_report()

                print(f"\n{'=' * 60}")
                print(f"{'ОТЧЕТ О РАБОТЕ СТАНЦИИ':^60}")
                print(f"{'=' * 60}")

                print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
                print(f"  Всего отремонтировано автомобилей: {total_cars}")

                print(f"\n👥 СТАТИСТИКА ПО РАБОТНИКАМ:")
                for emp in employees:
                    print(f"  {emp['фио']}: {emp['количество_ремонтов']} ремонтов")

                print(f"\n🚗 НЕИСПРАВНОСТИ ПО МАРКАМ АВТО:")
                for fault in faults:
                    print(f"  {fault['марка']}: {fault['тип_неисправности']} ({fault['количество']} раз)")

                print(f"\n🔧 ПОСЛЕДНИЕ РЕМОНТЫ (первые 10):")
                for repair in repairs[:10]:
                    print(
                        f"  {repair['номер_госрегистрации']} ({repair['владелец']}) - {repair['работник']}: {repair['тип_неисправности']} ({repair['время_устранения']})")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        else:
            print("Неверный выбор, попробуйте снова")


def view_data_menu(service):
    """Меню просмотра всех данных"""
    while True:
        print("\n--- ПРОСМОТР ВСЕХ ДАННЫХ ---")
        print("1 - Все владельцы")
        print("2 - Все работники")
        print("3 - Все автомобили")
        print("4 - Все неисправности")
        print("5 - Все факты ремонта")
        print("0 - Назад в главное меню")

        sub_choice = input("Выберите данные: ")

        if sub_choice == '0':
            break

        elif sub_choice == '1':
            try:
                results = service.get_all_owners()
                print_results(results, "ВСЕ ВЛАДЕЛЬЦЫ")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '2':
            try:
                results = service.get_all_employees()
                print_results(results, "ВСЕ РАБОТНИКИ")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '3':
            try:
                results = service.get_all_cars()
                print_results(results, "ВСЕ АВТОМОБИЛИ")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '4':
            try:
                results = service.get_all_faults()
                print_results(results, "ВСЕ НЕИСПРАВНОСТИ")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '5':
            try:
                # Используем правильные имена колонок
                results = service.db.execute_query("""
                    SELECT фр.id_Ремонта, в.ФИО as владелец, а.Номер_госрегистрации, а.Марка, 
                           р.ФИО as работник, н.Тип_неисправности, фр.Время_устранения
                    FROM Факт_ремонта фр
                    JOIN Автомобиль а ON фр.id_Автомобиля = а.id_Автомобиля
                    JOIN Владелец в ON а.id_Владельца = в.id_Владельца
                    JOIN Работник р ON фр.id_Работника = р.id_Работника
                    JOIN Неисправность н ON фр.id_Неисправности = н.id_Неисправности
                    ORDER BY фр.Время_устранения DESC
                """, fetch=True)
                print_results(results, "ВСЕ ФАКТЫ РЕМОНТА")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        else:
            print("Неверный выбор, попробуйте снова")


def main():
    # Инициализация базы данных
    print("Инициализация базы данных...")
    models = AutoServiceModels()

    # Диагностика структуры базы данных (опционально)
    # models.diagnose_database()

    # Диагностика подключения к БД
    try:
        conn = models.db.get_connection()
        db_info = conn.get_dsn_parameters()
        print(f"Подключение к БД: {db_info.get('dbname')} на {db_info.get('host')}:{db_info.get('port')}")
        conn.close()
    except Exception as e:
        print(f"Ошибка подключения: {e}")

    # Создание сервиса
    service = AutoService()

    print("\n" + "=" * 70)
    print("СИСТЕМА ДИСПЕТЧЕРА СТАНЦИИ ТЕХОБСЛУЖИВАНИЯ (PostgreSQL)")
    print("=" * 70)

    # УБИРАЕМ автоматическую вставку тестовых данных
    # Вместо этого предоставим пользователю выбор в меню

    # Добавим меню управления тестовыми данными
    if not test_data_menu(models, service):
        return

    # Основное меню программы
    while True:
        print("\n" + "=" * 50)
        print("ГЛАВНОЕ МЕНЮ")
        print("=" * 50)
        print("1 - Операции с данными")
        print("2 - Запросы диспетчера")
        print("3 - Справки и отчеты")
        print("4 - Просмотр всех данных")
        print("5 - Управление тестовыми данными")
        print("0 - Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == '0':
            print("\nВыход из программы. До свидания!")
            break

        elif choice == '1':
            operations_menu(service)

        elif choice == '2':
            queries_menu(service)

        elif choice == '3':
            reports_menu(service)

        elif choice == '4':
            view_data_menu(service)

        elif choice == '5':
            test_data_menu(models, service)

        else:
            print("Неверный выбор, попробуйте снова")

if __name__ == "__main__":
    main()
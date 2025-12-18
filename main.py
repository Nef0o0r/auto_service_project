# main.py
from services.auto_service import AutoService
from models.models import AutoServiceModels
from config.auth import AuthManager
from services.logger import Logger
from services.backup import BackupService
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


def admin_test_data_menu(models, service, logger, username):
    """Меню управления тестовыми данными"""
    while True:
        print("\n" + "=" * 50)
        print("УПРАВЛЕНИЕ ТЕСТОВЫМИ ДАННЫМИ")
        print("=" * 50)
        print("1 - Продолжить работу с текущими данными")
        print("2 - Добавить тестовые данные (очистить существующие)")
        print("3 - Очистить все данные")
        print("4 - Проверить состояние базы данных")
        print("0 - Назад")

        choice = input("\nВыберите действие: ").strip()

        if choice == '0':
            logger.log(username, "SYSTEM_EXIT", "User exited program")
            return False
        elif choice == '1':
            return True
        elif choice == '2':
            confirm = input("Вы уверены? Это очистит все существующие данные. (y/N): ")
            if confirm.lower() == 'y':
                models.clear_test_data()
                models.insert_test_data()
                logger.log(username, "TEST_DATA_ADD", "Test data added")
                print("Тестовые данные обновлены")
            wait_for_continue()
        elif choice == '3':
            confirm = input("Вы уверены? Это удалит ВСЕ данные из базы. (y/N): ")
            if confirm.lower() == 'y':
                models.clear_test_data()
                logger.log(username, "TEST_DATA_CLEAR", "All data cleared")
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


def operations_menu(service, logger, username):
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
                logger.log(username, "ADD_OWNER", f"ФИО={фио}, Адрес={адрес}")
                print(f"✓ {result}")
            except Exception as e:
                logger.log(username, "ERROR", f"ADD_OWNER failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif choice == '2':
            print("\n--- ДОБАВЛЕНИЕ РАБОТНИКА ---")
            фио = input("ФИО работника (0 - отмена): ")
            if фио == '0':
                continue
            try:
                result = service.add_employee(фио)
                logger.log(username, "ADD_EMPLOYEE", f"ФИО={фио}")
                print(f"✓ {result}")
            except Exception as e:
                logger.log(username, "ERROR", f"ADD_EMPLOYEE failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif choice == '3':
            print("\n--- ДОБАВЛЕНИЕ НЕИСПРАВНОСТИ ---")
            неисправность = input("Тип неисправности (0 - отмена): ")
            if неисправность == '0':
                continue
            try:
                result = service.add_fault(неисправность)
                logger.log(username, "ADD_FAULT", f"Тип={неисправность}")
                print(f"✓ {result}")
            except Exception as e:
                logger.log(username, "ERROR", f"ADD_FAULT failed: {str(e)}")
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
                logger.log(username, "ADD_REPAIR",
                           f"Авто={номер_авто}, Работник={фио_работника}, Неисправность={тип_неисправности}")
                print(f"✓ {result}")
            except Exception as e:
                logger.log(username, "ERROR", f"ADD_REPAIR failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif choice == '5':
            print("\n--- УДАЛЕНИЕ РАБОТНИКА ---")
            try:
                employees = service.get_all_employees()
                if employees:
                    print("\nСписок работников:")
                    for emp in employees:
                        employee_id = emp.get('id_Работника')
                        employee_name = emp.get('ФИО')
                        print(f"  ID: {employee_id} - {employee_name}")

                id_работника = input("\nID работника для удаления (0 - отмена): ")
                if id_работника == '0':
                    continue
                id_работника = int(id_работника)
                result = service.delete_employee(id_работника)
                logger.log(username, "DELETE_EMPLOYEE", f"ID={id_работника}")
                print(f"✓ {result}")
            except ValueError:
                print("✗ Ошибка: введите числовой ID")
            except Exception as e:
                logger.log(username, "ERROR", f"DELETE_EMPLOYEE failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif choice == '6':
            print("\n--- ИЗМЕНЕНИЕ НОМЕРА АВТОМОБИЛЯ ---")
            try:

                cars = service.get_all_cars()
                if cars:
                    print("\nСписок автомобилей:")
                    for car in cars:

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
                logger.log(username, "UPDATE_CAR_LICENSE", f"ID={id_авто}, Новый номер={новый_номер}")
                print(f"✓ {result}")
            except ValueError:
                print("✗ Ошибка: введите числовой ID")
            except Exception as e:
                logger.log(username, "ERROR", f"UPDATE_CAR_LICENSE failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        else:
            print("Неверный выбор, попробуйте снова")


def queries_menu(service, logger, username):
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
                logger.log(username, "QUERY_OWNER_BY_LICENSE", f"Номер={номер}")
                print_results(results, f"Владелец авто {номер}")
            except Exception as e:
                logger.log(username, "ERROR", f"QUERY_OWNER_BY_LICENSE failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '2':
            print("\n--- ИНФОРМАЦИЯ ОБ АВТО ВЛАДЕЛЬЦА ---")
            фио = input("ФИО владельца (0 - отмена): ")
            if фио == '0':
                continue
            try:
                results = service.get_car_info_by_owner(фио)
                logger.log(username, "QUERY_CAR_INFO", f"Владелец={фио}")
                print_results(results, f"Автомобили владельца {фио}")
            except Exception as e:
                logger.log(username, "ERROR", f"QUERY_CAR_INFO failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '3':
            print("\n--- УСТРАНЕННЫЕ НЕИСПРАВНОСТИ ВЛАДЕЛЬЦА ---")
            фио = input("ФИО владельца (0 - отмена): ")
            if фио == '0':
                continue
            try:
                results = service.get_fixed_faults_by_owner(фио)
                logger.log(username, "QUERY_FIXED_FAULTS", f"Владелец={фио}")
                print_simple_list([row['тип_неисправности'] for row in results], f"Устраненные неисправности {фио}")
            except Exception as e:
                logger.log(username, "ERROR", f"QUERY_FIXED_FAULTS failed: {str(e)}")
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
                logger.log(username, "QUERY_REPAIR_DETAILS", f"Владелец={фио}, Неисправность={неисправность}")
                print_results(results, f"Детали ремонта {неисправность} для {фио}")
            except Exception as e:
                logger.log(username, "ERROR", f"QUERY_REPAIR_DETAILS failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '5':
            print("\n--- АВТОМОБИЛИ РАБОТНИКА ---")
            фио = input("ФИО работника (0 - отмена): ")
            if фио == '0':
                continue
            try:
                results = service.get_cars_repaired_by_employee(фио)
                logger.log(username, "QUERY_CARS_BY_EMPLOYEE", f"Работник={фио}")
                print_results(results, f"Автомобили, отремонтированные {фио}")
            except Exception as e:
                logger.log(username, "ERROR", f"QUERY_CARS_BY_EMPLOYEE failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '6':
            print("\n--- ВЛАДЕЛЬЦЫ ПО ТИПУ НЕИСПРАВНОСТИ ---")
            неисправность = input("Тип неисправности (0 - отмена): ")
            if неисправность == '0':
                continue
            try:
                results = service.get_owners_by_fault_type(неисправность)
                logger.log(username, "QUERY_OWNERS_BY_FAULT", f"Неисправность={неисправность}")
                print_results(results, f"Владельцы с неисправностью: {неисправность}")
            except Exception as e:
                logger.log(username, "ERROR", f"QUERY_OWNERS_BY_FAULT failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        else:
            print("Неверный выбор, попробуйте снова")


def reports_menu(service, logger, username):
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
                    logger.log(username, "REPORT_FAULTS", f"Владелец={фио}")
                    print_results(results, f"Неисправности {фио}")
                else:
                    results = service.get_fault_report()
                    logger.log(username, "REPORT_ALL_FAULTS", "Все владельцы")
                    print_results(results, "Все неисправности")
            except Exception as e:
                logger.log(username, "ERROR", f"REPORT_FAULTS failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '2':
            print("\n--- ПОЛНЫЙ ОТЧЕТ О РАБОТЕ СТАНЦИИ ---")
            try:
                total_cars, repairs, faults, employees = service.get_station_report()
                logger.log(username, "REPORT_STATION", "Полный отчет")

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
                logger.log(username, "ERROR", f"REPORT_STATION failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        else:
            print("Неверный выбор, попробуйте снова")


def view_data_menu(service, logger, username):
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
                logger.log(username, "VIEW_ALL_OWNERS")
                print_results(results, "ВСЕ ВЛАДЕЛЬЦЫ")
            except Exception as e:
                logger.log(username, "ERROR", f"VIEW_ALL_OWNERS failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '2':
            try:
                results = service.get_all_employees()
                logger.log(username, "VIEW_ALL_EMPLOYEES")
                print_results(results, "ВСЕ РАБОТНИКИ")
            except Exception as e:
                logger.log(username, "ERROR", f"VIEW_ALL_EMPLOYEES failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '3':
            try:
                results = service.get_all_cars()
                logger.log(username, "VIEW_ALL_CARS")
                print_results(results, "ВСЕ АВТОМОБИЛИ")
            except Exception as e:
                logger.log(username, "ERROR", f"VIEW_ALL_CARS failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '4':
            try:
                results = service.get_all_faults()
                logger.log(username, "VIEW_ALL_FAULTS")
                print_results(results, "ВСЕ НЕИСПРАВНОСТИ")
            except Exception as e:
                logger.log(username, "ERROR", f"VIEW_ALL_FAULTS failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        elif sub_choice == '5':
            try:
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
                logger.log(username, "VIEW_ALL_REPAIRS")
                print_results(results, "ВСЕ ФАКТЫ РЕМОНТА")
            except Exception as e:
                logger.log(username, "ERROR", f"VIEW_ALL_REPAIRS failed: {str(e)}")
                print(f"✗ Ошибка: {e}")
            wait_for_continue()

        else:
            print("Неверный выбор, попробуйте снова")


def user_management_menu(auth, logger, admin_username):
    """Управление пользователями"""
    while True:
        print("\n--- УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ---")
        print("1 - Список пользователей")
        print("2 - Добавить пользователя")
        print("3 - Изменить пароль пользователя")
        print("0 - Назад")

        choice = input("Выберите действие: ").strip()

        if choice == '0':
            break

        elif choice == '1':
            print("\nСписок пользователей:")
            print("-" * 40)
            for user, info in auth.users.items():
                print(f"  {user}: {info['role']}")

        elif choice == '2':
            print("\n--- ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ ---")
            new_user = input("Имя пользователя: ").strip()
            new_pass = input("Пароль: ").strip()
            user_role = input("Роль (admin/dispatcher): ").strip().lower()

            if user_role not in ['admin', 'dispatcher']:
                user_role = 'dispatcher'

            if auth.create_user(new_user, new_pass, user_role):
                logger.log(admin_username, "USER_CREATE", f"user={new_user}, role={user_role}")
                print(f"✓ Пользователь {new_user} создан")
            else:
                print(f"✗ Пользователь {new_user} уже существует")

        elif choice == '3':
            print("\n--- ИЗМЕНЕНИЕ ПАРОЛЯ ---")
            target_user = input("Имя пользователя: ").strip()
            if target_user in auth.users:
                new_pass = input("Новый пароль: ").strip()
                if auth.change_password(target_user, new_pass):
                    logger.log(admin_username, "PASSWORD_CHANGE", f"user={target_user}")
                    print(f"✓ Пароль для {target_user} изменен")
                else:
                    print(f"✗ Ошибка изменения пароля")
            else:
                print(f"✗ Пользователь {target_user} не найден")

        else:
            print("Неверный выбор")


def backup_menu(backup_service, logger, username):
    """Меню резервного копирования"""
    while True:
        print("\n--- РЕЗЕРВНОЕ КОПИРОВАНИЕ ---")
        print("1 - Создать резервную копию")
        print("2 - Список резервных копий")
        print("3 - Восстановить из резервной копии")
        print("0 - Назад")

        choice = input("Выберите действие: ").strip()

        if choice == '0':
            break

        elif choice == '1':
            backup_folder = backup_service.create_backup()
            logger.log(username, "BACKUP_CREATE", f"folder={backup_folder}")
            print(f"✓ Резервная копия создана: {backup_folder}")
            wait_for_continue()

        elif choice == '2':
            backups = backup_service.list_backups()
            if backups:
                print("\nДоступные резервные копии:")
                for i, backup in enumerate(backups, 1):
                    print(f"  {i}. {backup['folder']} ({backup['timestamp']})")
            else:
                print("Резервные копии не найдены")
            wait_for_continue()

        elif choice == '3':
            backups = backup_service.list_backups()
            if backups:
                print("\nВыберите резервную копию для восстановления:")
                for i, backup in enumerate(backups, 1):
                    print(f"  {i}. {backup['folder']}")

                try:
                    choice_idx = int(input("Номер: ").strip()) - 1
                    if 0 <= choice_idx < len(backups):
                        confirm = input(f"Восстановить из {backups[choice_idx]['folder']}? (y/N): ").strip().lower()
                        if confirm == 'y':
                            if backup_service.restore_backup(backups[choice_idx]['path']):
                                logger.log(username, "BACKUP_RESTORE", f"folder={backups[choice_idx]['folder']}")
                                print("✓ Конфигурация восстановлена. Перезапустите программу.")
                                return True  # Выйти из программы для применения изменений
                            else:
                                print("✗ Ошибка восстановления")
                    else:
                        print("Неверный номер")
                except ValueError:
                    print("Введите число")
            else:
                print("Резервные копии не найдены")
            wait_for_continue()

        else:
            print("Неверный выбор")


def view_logs_menu(logger):
    """Просмотр логов"""
    while True:
        print("\n--- ПРОСМОТР ЛОГОВ ---")
        print("1 - Логи за сегодня")
        print("2 - Логи за конкретную дату")
        print("0 - Назад")

        choice = input("Выберите действие: ").strip()

        if choice == '0':
            break

        elif choice == '1':
            logs = logger.get_logs()
            if logs:
                print("\nЛоги за сегодня:")
                print("-" * 80)
                for log in logs:
                    print(log)
            else:
                print("Логи за сегодня отсутствуют")
            wait_for_continue()

        elif choice == '2':
            date_str = input("Дата (ГГГГ-ММ-ДД): ").strip()
            logs = logger.get_logs(date_str)
            if logs:
                print(f"\nЛоги за {date_str}:")
                print("-" * 80)
                for log in logs:
                    print(log)
            else:
                print(f"Логи за {date_str} отсутствуют")
            wait_for_continue()

        else:
            print("Неверный выбор")


def admin_menu(auth, logger, backup_service, models, service, username):
    """Меню администратора"""
    while True:
        print("\n" + "=" * 50)
        print("МЕНЮ АДМИНИСТРАТОРА")
        print("=" * 50)
        print("1 - Управление пользователями")
        print("2 - Резервное копирование")
        print("3 - Просмотр логов")
        print("4 - Перейти к работе с данными")
        print("5 - Тестовые данные")
        print("0 - Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == '0':
            break

        elif choice == '1':
            user_management_menu(auth, logger, username)

        elif choice == '2':
            if backup_menu(backup_service, logger, username):
                return True  # Выйти для перезапуска

        elif choice == '3':
            view_logs_menu(logger)

        elif choice == '4':
            main_dispatcher_menu(logger, service, username, "admin")

        elif choice == '5':
            admin_test_data_menu(models, service, logger, username)

        else:
            print("Неверный выбор")

    return False


def dispatcher_menu(logger, models, service, username):
    """Меню диспетчера"""
    logger.log(username, "DISPATCHER_SESSION_START", "Dispatcher session started")

    main_dispatcher_menu(logger, service, username, "dispatcher")
    return True


def main_dispatcher_menu(logger, service, username, role="dispatcher"):
    """Основное меню диспетчера"""
    while True:
        print("\n" + "=" * 50)
        if role == "admin":
            print("ГЛАВНОЕ МЕНЮ ДИСПЕТЧЕРА (версия АДМИНИСТРАТОРА)")
        else:
            print("ГЛАВНОЕ МЕНЮ ДИСПЕТЧЕРА")
        print("=" * 50)
        print("1 - Операции с данными")
        print("2 - Запросы диспетчера")
        print("3 - Справки и отчеты")
        print("4 - Просмотр всех данных")
        if role == "admin":
            print("0 - Назад")
        else:
            print("0 - Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == '0':
            break

        elif choice == '1':
            operations_menu(service, logger, username)

        elif choice == '2':
            queries_menu(service, logger, username)

        elif choice == '3':
            reports_menu(service, logger, username)

        elif choice == '4':
            view_data_menu(service, logger, username)

        else:
            print("Неверный выбор")

def main():
    # Инициализация систем
    auth = AuthManager()
    logger = Logger()
    backup_service = BackupService()

    # Аутентификация
    print("\n" + "=" * 70)
    print("СИСТЕМА ДИСПЕТЧЕРА СТАНЦИИ ТЕХОБСЛУЖИВАНИЯ - АВТОРИЗАЦИЯ")
    print("=" * 70)

    role = None
    while role is None:
        username = input("Логин: ").strip()
        password = input("Пароль: ").strip()

        role = auth.authenticate(username, password)
        if role is None:
            print("Неверный логин или пароль. Попробуйте снова.")

    # Логируем вход
    logger.log(username, "LOGIN", f"role={role}")
    print(f"\nДобро пожаловать, {username} ({role})!")

    # Инициализация базы данных
    print("\nИнициализация базы данных...")
    models = AutoServiceModels()
    service = AutoService()

    # Проверка подключения к БД
    try:
        conn = models.db.get_connection()
        db_info = conn.get_dsn_parameters()
        print(f"Подключение к БД: {db_info.get('dbname')} на {db_info.get('host')}:{db_info.get('port')}")
        conn.close()
    except Exception as e:
        print(f"Ошибка подключения: {e}")

    # Логируем инициализацию
    logger.log(username, "SYSTEM_INIT", "Database initialized")

    # Показываем меню в зависимости от роли
    if role == "admin":
        if admin_menu(auth, logger, backup_service, models, service, username):
            # Если нужно перезапустить (после восстановления бэкапа)
            print("\nПерезапустите программу для применения изменений.")
            return
    else:
        dispatcher_menu(logger, models, service, username)

    # Логируем выход
    logger.log(username, "LOGOUT", "Session ended")
    print("\nСеанс завершен. До свидания!")

if __name__ == "__main__":
    main()
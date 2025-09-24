"""
Пример использования отладки персонажей в PersonService.

Этот файл демонстрирует, как использовать новые отладочные функции
для анализа и мониторинга генерации персонажей.
"""

from services.person.person_service import PersonService


def example_persona_debug():
    """Пример использования отладочных функций PersonService."""
    
    person_service = PersonService()
    
    print("=== Примеры отладки персонажей ===\n")
    
    # 1. Проверка данных персонажей
    print("1. Статус данных персонажей:")
    data_status = person_service.get_persons_data_debug_info()
    print(f"   Данные загружены: {data_status['data_loaded']}")
    print(f"   Тип данных: {data_status.get('data_type', 'N/A')}")
    print(f"   Есть полы: {data_status.get('has_gender', False)}")
    print(f"   Есть темпераменты: {data_status.get('has_temperament', False)}")
    print(f"   Есть черты: {data_status.get('has_traits', False)}")
    print(f"   Всего черт: {data_status.get('total_traits', 0)}")
    
    # 2. Статистика персонажей
    print("\n2. Статистика персонажей:")
    stats = person_service.get_persona_statistics()
    if stats['available']:
        print(f"   Опций пола: {stats['gender_options']}")
        print(f"   Темпераментов: {stats['temperament_options']}")
        print(f"   Групп черт: {stats['trait_groups']}")
        print(f"   Всего черт: {stats['total_traits']}")
        print(f"   Возможных комбинаций: {stats['possible_combinations']}")
        
        print(f"\n   Детали темпераментов:")
        for temp_key, temp_info in stats['temperament_details'].items():
            print(f"     {temp_key}: {temp_info['description'][:50]}...")
        
        print(f"\n   Детали групп черт:")
        for group_name, group_info in stats['trait_group_details'].items():
            print(f"     {group_name}: {group_info['trait_count']} черт")
    else:
        print(f"   Ошибка: {stats.get('error', 'Неизвестная ошибка')}")
    
    # 3. Отладка генерации персонажа
    print("\n3. Отладка генерации персонажа:")
    debug_info = person_service.generate_persona_debug_info("male")
    
    if debug_info['generation_successful']:
        print(f"   Пол пользователя: {debug_info['user_gender']}")
        print(f"   Пол персонажа: {debug_info['persona_gender']}")
        print(f"   Выбранный темперамент: {debug_info['selected_temperament']['key']}")
        print(f"   Описание темперамента: {debug_info['selected_temperament']['text']}")
        print(f"   Количество групп черт: {debug_info['total_trait_groups']}")
        print(f"   Длина финального контента: {debug_info['final_content_length']} символов")
        
        print(f"\n   Выбранные черты:")
        for trait in debug_info['selected_traits']:
            print(f"     {trait['group']}: {trait['key']} - {trait['text'][:50]}...")
    else:
        print(f"   Ошибка генерации: {debug_info.get('error', 'Неизвестная ошибка')}")
    
    # 4. Сравнение разных генераций
    print("\n4. Сравнение генераций для разных полов:")
    
    for gender in ["male", "female"]:
        debug_info = person_service.generate_persona_debug_info(gender)
        if debug_info['generation_successful']:
            print(f"   {gender}: {debug_info['selected_temperament']['key']} "
                  f"({debug_info['final_content_length']} символов)")
        else:
            print(f"   {gender}: Ошибка генерации")


def example_telegram_bot_usage():
    """Пример использования в Telegram боте."""
    
    print("\n=== Пример использования в Telegram боте ===\n")
    
    # Симуляция обработки команд от админа
    admin_commands = [
        "/debug_msg persona",
        "/debug_msg persona_stats", 
        "/debug_msg persona_data"
    ]
    
    person_service = PersonService()
    
    for command in admin_commands:
        print(f"Команда: {command}")
        
        if "persona_stats" in command:
            # Статистика персонажей
            stats = person_service.get_persona_statistics()
            print(f"  Результат: Статистика с {stats.get('possible_combinations', 0)} комбинациями")
            
        elif "persona_data" in command:
            # Статус данных
            data_status = person_service.get_persons_data_debug_info()
            print(f"  Результат: Данные {'загружены' if data_status['data_loaded'] else 'не загружены'}")
            
        elif "persona" in command:
            # Полная отладка
            debug_info = person_service.generate_persona_debug_info("female")
            if debug_info['generation_successful']:
                print(f"  Результат: Персонаж {debug_info['persona_gender']} "
                      f"с темпераментом {debug_info['selected_temperament']['key']}")
            else:
                print(f"  Результат: Ошибка генерации")
        
        print()


def example_error_handling():
    """Пример обработки ошибок."""
    
    print("=== Пример обработки ошибок ===\n")
    
    person_service = PersonService()
    
    # Симуляция различных сценариев ошибок
    scenarios = [
        ("Нормальная генерация", "male"),
        ("Генерация для неизвестного пола", "unknown"),
    ]
    
    for scenario_name, gender in scenarios:
        print(f"Сценарий: {scenario_name}")
        
        try:
            debug_info = person_service.generate_persona_debug_info(gender)
            
            if debug_info['generation_successful']:
                print(f"  ✅ Успешно: {debug_info['persona_gender']} персонаж")
            else:
                print(f"  ❌ Ошибка: {debug_info.get('error', 'Неизвестная ошибка')}")
                
        except Exception as e:
            print(f"  💥 Исключение: {e}")
        
        print()


def example_performance_analysis():
    """Пример анализа производительности."""
    
    print("=== Анализ производительности ===\n")
    
    import time
    
    person_service = PersonService()
    
    # Тестируем производительность различных операций
    operations = [
        ("get_persons_data_debug_info", lambda: person_service.get_persons_data_debug_info()),
        ("get_persona_statistics", lambda: person_service.get_persona_statistics()),
        ("generate_persona_debug_info", lambda: person_service.generate_persona_debug_info("male")),
    ]
    
    for op_name, operation in operations:
        times = []
        
        # Выполняем операцию несколько раз для усреднения
        for _ in range(5):
            start_time = time.time()
            result = operation()
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        print(f"{op_name}: {avg_time:.4f} секунд (среднее из 5 попыток)")


if __name__ == "__main__":
    # Запускаем все примеры
    example_persona_debug()
    example_telegram_bot_usage()
    example_error_handling()
    example_performance_analysis()
    
    print("\n🎉 Все примеры выполнены успешно!")

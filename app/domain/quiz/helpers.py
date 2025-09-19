from typing import Dict, Any


# Функция анализа личности
def analyze_personality(answers: Dict[str, Any]) -> Dict[str, float]:
    """Анализирует ответы и определяет черты личности"""
    traits = {
        "adventurous": 0.0,  # авантюризм
        "analytical": 0.0,  # аналитичность
        "creative": 0.0,  # творчество
        "social": 0.0,  # общительность
        "introverted": 0.0,  # интроверсия
        "empathic": 0.0,  # эмпатия
        "practical": 0.0,  # практичность
        "free_spirited": 0.0,  # свободолюбие
    }

    # Анализ на основе выбора пейзажа
    landscape = answers.get("landscape", "")
    if landscape == "landscape_mountains":
        traits["adventurous"] += 0.8
        traits["free_spirited"] += 0.6
    elif landscape == "landscape_ocean":
        traits["free_spirited"] += 0.9
        traits["creative"] += 0.7
    elif landscape == "landscape_forest":
        traits["introverted"] += 0.8
        traits["analytical"] += 0.5
    elif landscape == "landscape_city":
        traits["social"] += 0.8
        traits["practical"] += 0.6

    # Анализ на основе суперспособности
    superpower = answers.get("superpower", "")
    if superpower == "superpower_mind_reading":
        traits["empathic"] += 0.9
        traits["analytical"] += 0.7
    elif superpower == "superpower_time_stop":
        traits["practical"] += 0.8
        traits["analytical"] += 0.6
    elif superpower == "superpower_teleport":
        traits["adventurous"] += 0.9
        traits["free_spirited"] += 0.8
    elif superpower == "superpower_immortality":
        traits["practical"] += 0.7
        traits["analytical"] += 0.6

    # Анализ времени суток
    time_of_day = answers.get("time_of_day", "")
    if time_of_day == "time_morning":
        traits["practical"] += 0.7
        traits["analytical"] += 0.5
    elif time_of_day == "time_day":
        traits["social"] += 0.6
        traits["practical"] += 0.5
    elif time_of_day == "time_evening":
        traits["creative"] += 0.8
        traits["social"] += 0.5
    elif time_of_day == "time_night":
        traits["introverted"] += 0.9
        traits["analytical"] += 0.6

    # Анализ выбора книги
    book = answers.get("book", "")
    if book == "book_encyclopedia":
        traits["analytical"] += 0.9
        traits["practical"] += 0.7
    elif book == "book_detective":
        traits["analytical"] += 0.8
        traits["creative"] += 0.6
    elif book == "book_novel":
        traits["creative"] += 0.8
        traits["empathic"] += 0.6
    elif book == "book_poetry":
        traits["creative"] += 0.9
        traits["introverted"] += 0.7

    # Анализ отдыха
    rest = answers.get("rest", "")
    if rest == "rest_party":
        traits["social"] += 0.9
        traits["free_spirited"] += 0.6
    elif rest == "rest_home":
        traits["introverted"] += 0.8
        traits["practical"] += 0.5
    elif rest == "rest_nature":
        traits["free_spirited"] += 0.8
        traits["adventurous"] += 0.6
    elif rest == "rest_reading":
        traits["introverted"] += 0.7
        traits["analytical"] += 0.6

    # Анализ животного
    animal = answers.get("animal", "")
    if animal == "animal_lion":
        traits["adventurous"] += 0.7
        traits["social"] += 0.8
    elif animal == "animal_fox":
        traits["analytical"] += 0.8
        traits["creative"] += 0.7
    elif animal == "animal_dolphin":
        traits["social"] += 0.9
        traits["empathic"] += 0.8
    elif animal == "animal_owl":
        traits["analytical"] += 0.9
        traits["introverted"] += 0.7

    return traits


# Функция сохранения профиля личности
async def save_personality_profile(user_id: int, personality_profile: Dict[str, float]):
    """Сохраняет профиль личности в базу данных"""
    # Import here to avoid circular imports
    from core.database import db_manager
    
    try:
        # Get database pool
        pool = await db_manager.get_pool()
        if not pool:
            raise Exception("Database pool not available")
        
        # Import UserService here to avoid circular imports
        from domain.user.services_cached import UserService
        user_service = UserService(pool)
        
        # Save personality profile
        await user_service.update_personality_profile(user_id, personality_profile)
        
    except Exception as e:
        # Log error but don't fail the quiz
        print(f"Error saving personality profile for user {user_id}: {e}")
        pass


# Функция форматирования результатов
def format_personality_results(personality_profile: Dict[str, float]) -> str:
    """Форматирует результаты анализа личности в читаемый текст"""
    # Определяем доминирующие черты
    dominant_traits = sorted(personality_profile.items(), key=lambda x: x[1], reverse=True)[
        :3
    ]  # Топ-3 черты

    result = ""
    for trait_name, trait_value in dominant_traits:
        if trait_value > 0:  # Only include traits with positive values
            if trait_name == "adventurous":
                result += "• Ты авантюрист и любишь новые вызовы\n"
            elif trait_name == "analytical":
                result += "• У тебя аналитический склад ума\n"
            elif trait_name == "creative":
                result += "• Ты творческая личность\n"
            elif trait_name == "social":
                result += "• Ты общительный и социальный человек\n"
            elif trait_name == "introverted":
                result += "• Ты ценишь уединение и самоанализ\n"
            elif trait_name == "empathic":
                result += "• Ты empathetic и понимаешь других людей\n"
            elif trait_name == "practical":
                result += "• Ты практичный и реалистичный человек\n"
            elif trait_name == "free_spirited":
                result += "• Ты свободолюбивая личность\n"

    return result

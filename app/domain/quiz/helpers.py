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

    # Анализ других ответов...
    # Добавьте логику для остальных вопросов

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
    for trait in dominant_traits:
        if trait == "adventurous":
            result += "• Ты авантюрист и любишь новые вызовы\n"
        elif trait == "analytical":
            result += "• У тебя аналитический склад ума\n"
        elif trait == "creative":
            result += "• Ты творческая личность\n"
        elif trait == "social":
            result += "• Ты общительный и социальный человек\n"
        elif trait == "introverted":
            result += "• Ты ценишь уединение и самоанализ\n"
        elif trait == "empathic":
            result += "• Ты empathetic и понимаешь других людей\n"
        elif trait == "practical":
            result += "• Ты практичный и реалистичный человек\n"
        elif trait == "free_spirited":
            result += "• Ты свободолюбивая личность\n"

    return result

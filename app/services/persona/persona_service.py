import random
<<<<<<< HEAD
from typing import Dict, Any
=======
from typing import Any, Dict, List

>>>>>>> 26c914549b6c9e95be38ffa9c16402f7d92f2d17
from shared.i18n import i18n


class PersonaService:
    """Сервис для генерации динамических персонажей на основе переводов"""

    def __init__(self):
        pass

    def generate_dynamic_persona(self, user_gender: str) -> Dict[str, str]:
        """
        Генерирует динамический персонаж на основе выбранного пола пользователя

        Args:
            user_gender: Пол пользователя ("male" или "female")

        Returns:
            Dict с системным промптом для персонажа
        """
        # Получаем данные персонажей из переводов
        persons_data = i18n.t("persons")

        # Проверяем, что данные получены корректно
        if not isinstance(persons_data, dict) or persons_data.startswith("["):
            # Fallback к простому промпту
            return {
                "role": "system",
                "content": "Ты дружелюбный AI-компаньон. Отвечай на русском языке.",
                "persona_gender": "unknown",
                "temperament": "unknown",
                "traits": [],
            }

        # Выбираем пол персонажа (противоположный пользователю)
        persona_gender = "female" if user_gender == "male" else "male"
        gender_texts = persons_data["gender"][persona_gender]
        gender_text = random.choice(gender_texts)

        # Выбираем темперамент
        temperament_key = random.choice(list(persons_data["temperament"].keys()))
        temperament_text = persons_data["temperament"][temperament_key]

        # Выбираем черты: по одной из каждой группы
        traits_texts = []
        for group_name, group in persons_data["traits"].items():
            trait_key = random.choice(list(group.keys()))
            traits_texts.append(group[trait_key])

        # Собираем системный промпт
        content = f"{gender_text}. {temperament_text} " + " ".join(traits_texts)

        return {
            "role": "system",
            "content": content,
            "persona_gender": persona_gender,
            "temperament": temperament_key,
            "traits": [trait for trait in traits_texts],
        }

    def get_persona_for_gender(self, user_gender: str) -> str:
        """
        Получает системный промпт персонажа для конкретного пола

        Args:
            user_gender: Пол пользователя ("male" или "female")

        Returns:
            Системный промпт персонажа
        """
        persona = self.generate_dynamic_persona(user_gender)
        return persona["content"]

    def get_persona_info(self, user_gender: str) -> Dict[str, Any]:
        """
        Получает полную информацию о персонаже

        Args:
            user_gender: Пол пользователя ("male" или "female")

        Returns:
            Словарь с информацией о персонаже
        """
        return self.generate_dynamic_persona(user_gender)

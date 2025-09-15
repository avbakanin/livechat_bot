import random
from typing import Dict, List, Any
from shared.middlewares.i18n_middleware import I18nMiddleware


class PersonaService:
    """Сервис для генерации динамических персонажей на основе переводов"""
    
    def __init__(self, i18n: I18nMiddleware):
        self.i18n = i18n
    
    def generate_dynamic_persona(self, user_gender: str) -> Dict[str, str]:
        """
        Генерирует динамический персонаж на основе выбранного пола пользователя
        
        Args:
            user_gender: Пол пользователя ("male" или "female")
            
        Returns:
            Dict с системным промптом для персонажа
        """
        # Получаем данные персонажей из переводов
        persons_data = self.i18n.t("persons")
        
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
            "traits": [trait for trait in traits_texts]
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

import random
from typing import Any, Dict, Literal, Optional

from shared.i18n import i18n
from shared.debug import AdminHelper, DebugTextHelper

# Alias literal gender type
UserGender = Literal["male", "female"]


class PersonService:
    """Сервис для генерации динамических персонажей на основе переводов"""

    def __init__(self):
        pass

    def generate_dynamic_persona(self, user_gender: UserGender) -> Dict[str, str]:
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

        content = f"{gender_text}. {temperament_text} " + " ".join(traits_texts)

        return {
            "role": "system",
            "content": content,
            "persona_gender": persona_gender,
            "temperament": temperament_key,
            "traits": [trait for trait in traits_texts],
        }

    def get_persona_for_gender(self, user_gender: UserGender) -> str:
        """
        Получает системный промпт персонажа для конкретного пола

        Return:
            Системный промпт персонажа
        """
        persona = self.generate_dynamic_persona(user_gender)
        return persona["content"]

    def get_persona_info(self, user_gender: UserGender) -> Dict[str, Any]:
        """
        Получает полную информацию о персонаже

        Return:
            Словарь с информацией о персонаже
        """
        return self.generate_dynamic_persona(user_gender)
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return AdminHelper.is_admin(user_id)
    
    def get_persons_data_debug_info(self) -> Dict[str, Any]:
        """
        Получает отладочную информацию о данных персонажей.
        
        Returns:
            Словарь с отладочной информацией
        """
        try:
            persons_data = i18n.t("persons")
            
            debug_info = {
                "data_loaded": True,
                "data_type": type(persons_data).__name__,
                "is_dict": isinstance(persons_data, dict),
                "has_gender": False,
                "has_temperament": False,
                "has_traits": False,
                "gender_options": [],
                "temperament_options": [],
                "trait_groups": [],
                "total_traits": 0
            }
            
            if isinstance(persons_data, dict):
                debug_info["has_gender"] = "gender" in persons_data
                debug_info["has_temperament"] = "temperament" in persons_data
                debug_info["has_traits"] = "traits" in persons_data
                
                if debug_info["has_gender"]:
                    debug_info["gender_options"] = list(persons_data["gender"].keys())
                
                if debug_info["has_temperament"]:
                    debug_info["temperament_options"] = list(persons_data["temperament"].keys())
                
                if debug_info["has_traits"]:
                    debug_info["trait_groups"] = list(persons_data["traits"].keys())
                    debug_info["total_traits"] = sum(len(group) for group in persons_data["traits"].values())
            
            return debug_info
            
        except Exception as e:
            return {
                "data_loaded": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def generate_persona_debug_info(self, user_gender: UserGender, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Генерирует отладочную информацию о создании персонажа.
        
        Args:
            user_gender: Пол пользователя
            user_id: ID пользователя (для проверки админа)
            
        Returns:
            Словарь с отладочной информацией
        """
        try:
            # Получаем данные персонажей
            persons_data = i18n.t("persons")
            
            debug_info = {
                "user_gender": user_gender,
                "persona_gender": "female" if user_gender == "male" else "male",
                "data_available": isinstance(persons_data, dict) and not persons_data.startswith("["),
                "generation_successful": False,
                "selected_temperament": None,
                "selected_traits": [],
                "total_trait_groups": 0,
                "final_content_length": 0,
                "error": None
            }
            
            if not debug_info["data_available"]:
                debug_info["error"] = "Persons data not available or invalid"
                return debug_info
            
            # Выбираем темперамент
            temperament_key = random.choice(list(persons_data["temperament"].keys()))
            temperament_text = persons_data["temperament"][temperament_key]
            debug_info["selected_temperament"] = {
                "key": temperament_key,
                "text": temperament_text
            }
            
            # Выбираем черты
            selected_traits = []
            for group_name, group in persons_data["traits"].items():
                trait_key = random.choice(list(group.keys()))
                trait_text = group[trait_key]
                selected_traits.append({
                    "group": group_name,
                    "key": trait_key,
                    "text": trait_text
                })
            
            debug_info["selected_traits"] = selected_traits
            debug_info["total_trait_groups"] = len(persons_data["traits"])
            
            # Генерируем контент
            persona_gender = "female" if user_gender == "male" else "male"
            gender_texts = persons_data["gender"][persona_gender]
            gender_text = random.choice(gender_texts)
            
            traits_texts = [trait["text"] for trait in selected_traits]
            content = f"{gender_text}. {temperament_text} " + " ".join(traits_texts)
            
            debug_info["final_content_length"] = len(content)
            debug_info["generation_successful"] = True
            
            return debug_info
            
        except Exception as e:
            return {
                "user_gender": user_gender,
                "generation_successful": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def get_persona_statistics(self) -> Dict[str, Any]:
        """
        Получает статистику по доступным персонажам.
        
        Returns:
            Словарь со статистикой
        """
        try:
            persons_data = i18n.t("persons")
            
            if not isinstance(persons_data, dict) or persons_data.startswith("["):
                return {
                    "available": False,
                    "error": "Persons data not available"
                }
            
            stats = {
                "available": True,
                "gender_options": len(persons_data.get("gender", {})),
                "temperament_options": len(persons_data.get("temperament", {})),
                "trait_groups": len(persons_data.get("traits", {})),
                "total_traits": 0,
                "possible_combinations": 1,
                "gender_details": {},
                "temperament_details": {},
                "trait_group_details": {}
            }
            
            # Детали по полам
            if "gender" in persons_data:
                for gender, texts in persons_data["gender"].items():
                    stats["gender_details"][gender] = {
                        "text_options": len(texts),
                        "sample_text": texts[0] if texts else "None"
                    }
            
            # Детали по темпераментам
            if "temperament" in persons_data:
                for temp_key, temp_text in persons_data["temperament"].items():
                    stats["temperament_details"][temp_key] = {
                        "description": temp_text,
                        "length": len(temp_text)
                    }
            
            # Детали по группам черт
            if "traits" in persons_data:
                for group_name, group in persons_data["traits"].items():
                    stats["trait_group_details"][group_name] = {
                        "trait_count": len(group),
                        "traits": list(group.keys())
                    }
                    stats["total_traits"] += len(group)
            
            # Вычисляем возможные комбинации
            if stats["gender_options"] > 0 and stats["temperament_options"] > 0:
                stats["possible_combinations"] = (
                    stats["gender_options"] * 
                    stats["temperament_options"] * 
                    stats["total_traits"]
                )
            
            return stats
            
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

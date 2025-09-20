"""
Personality-based prompt generation for AI responses.
"""

from typing import Dict, List, Optional, Tuple
from shared.i18n import i18n


class PersonalityPromptGenerator:
    """Generates AI prompts based on user personality traits."""
    
    def __init__(self):
        pass  # Теперь используем локализованные переводы
    
    def get_dominant_traits(self, personality_profile: Dict[str, float], limit: int = 3) -> List[Tuple[str, float]]:
        """Get top dominant personality traits."""
        if not personality_profile:
            return []
        
        # Сортируем по значению (от большего к меньшему)
        sorted_traits = sorted(personality_profile.items(), key=lambda x: x[1], reverse=True)
        
        # Берем только черты с положительными значениями
        positive_traits = [(trait, value) for trait, value in sorted_traits if value > 0]
        
        return positive_traits[:limit]
    
    def format_traits_for_prompt(self, dominant_traits: List[Tuple[str, float]], language: str = "en") -> str:
        """Format personality traits for AI prompt using localized translations (short format)."""
        if not dominant_traits:
            return ""
        
        # Временно устанавливаем язык для получения переводов
        original_language = i18n.get_language()
        i18n.set_language(language)
        
        trait_descriptions = []
        for trait, value in dominant_traits:
            try:
                # Получаем описание черты из переводов
                description = i18n.t(f"personality_traits.{trait}")
                
                # Получаем интенсивность из переводов
                if value >= 2.0:
                    intensity = i18n.t("personality_traits.intensity.very")
                elif value >= 1.0:
                    intensity = i18n.t("personality_traits.intensity.quite")
                else:
                    intensity = i18n.t("personality_traits.intensity.somewhat")
                
                # Короткий формат: "very social, quite creative"
                trait_descriptions.append(f"{intensity} {description}")
            except Exception:
                # Fallback если перевод не найден
                trait_descriptions.append(f"{trait} ({value})")
        
        # Восстанавливаем оригинальный язык
        i18n.set_language(original_language)
        
        # Объединяем через запятую для экономии токенов
        return ", ".join(trait_descriptions)
    
    def generate_personality_prompt(self, personality_profile: Optional[Dict[str, float]], 
                                  base_prompt: str, language: str = "en", gender_preference: str = "female") -> str:
        """Generate enhanced prompt with personality information using localized translations."""
        if not personality_profile:
            return base_prompt
        
        # Получаем доминирующие черты
        dominant_traits = self.get_dominant_traits(personality_profile)
        
        if not dominant_traits:
            return base_prompt
        
        # Форматируем черты для промпта
        traits_description = self.format_traits_for_prompt(dominant_traits, language)
        
        # Временно устанавливаем язык для получения переводов
        original_language = i18n.get_language()
        i18n.set_language(language)
        
        try:
            # Получаем переводы для пола
            if gender_preference == "female":
                gender = i18n.t("gender_translations.girl")
                gender_traits = i18n.t("gender_translations.sweet_empathetic_playful")
            else:
                gender = i18n.t("gender_translations.young_man")
                gender_traits = i18n.t("gender_translations.confident_empathetic_playful")
            
            # Получаем название языка
            language_name = i18n.t("language_names." + language)
            
            # Получаем локализованную секцию с персонажем и чертами личности
            personality_section = i18n.t("ai_prompts.personality_section_with_persona", 
                                       gender=gender, gender_traits=gender_traits, 
                                       language_name=language_name, traits_description=traits_description)
            
            # Восстанавливаем оригинальный язык
            i18n.set_language(original_language)
            
            return personality_section
            
        except Exception:
            # Fallback если перевод не найден
            i18n.set_language(original_language)
            return base_prompt
    
    def get_personality_summary(self, personality_profile: Optional[Dict[str, float]], 
                              language: str = "en") -> str:
        """Get a brief summary of user's personality for context using localized translations."""
        if not personality_profile:
            return ""
        
        dominant_traits = self.get_dominant_traits(personality_profile, limit=2)
        
        if not dominant_traits:
            return ""
        
        # Временно устанавливаем язык для получения переводов
        original_language = i18n.get_language()
        i18n.set_language(language)
        
        try:
            trait_names = []
            for trait, _ in dominant_traits:
                trait_names.append(i18n.t(f"personality_traits.{trait}"))
            
            # Восстанавливаем оригинальный язык
            i18n.set_language(original_language)
            
            if language == "en":
                return f"This user is {', '.join(trait_names)}."
            elif language == "ru":
                return f"Этот пользователь {', '.join(trait_names)}."
            else:
                # Для других языков используем базовый формат
                return f"User traits: {', '.join(trait_names)}."
                
        except Exception:
            # Fallback если перевод не найден
            i18n.set_language(original_language)
            return ""


# Глобальный экземпляр
personality_prompt_generator = PersonalityPromptGenerator()

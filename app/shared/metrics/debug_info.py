"""
Debug information utilities for troubleshooting and monitoring.
"""

from typing import Any, Dict, Optional, Union
from datetime import datetime
from shared.utils.datetime_utils import DateTimeUtils


class DebugInfoGenerator:
    """Генератор отладочной информации для различных объектов."""
    
    @staticmethod
    def format_user_debug_info(user_id: int, user: Optional[Any] = None, 
                             cached_user: Optional[Any] = None) -> str:
        """
        Генерирует отладочную информацию о пользователе.
        
        Args:
            user_id: ID пользователя
            user: Объект пользователя из БД
            cached_user: Объект пользователя из кэша
            
        Returns:
            Форматированная строка с отладочной информацией
        """
        debug_info = f"🔍 Debug информация для пользователя {user_id}:\n\n"
        
        # Информация из БД
        if user:
            debug_info += f"📊 Данные из БД:\n"
            debug_info += f"  ID: {user.id}\n"
            debug_info += f"  Username: {user.username}\n"
            debug_info += f"  First Name: {user.first_name}\n"
            debug_info += f"  Last Name: {user.last_name}\n"
            debug_info += f"  Language: {user.language}\n"
            debug_info += f"  Gender Preference: {user.gender_preference}\n"
            debug_info += f"  Subscription Status: {user.subscription_status}\n"
            debug_info += f"  Subscription Expires At: {user.subscription_expires_at}\n"
            debug_info += f"  Consent Given: {user.consent_given}\n"
            debug_info += f"  Created At: {user.created_at}\n"
            debug_info += f"  Updated At: {user.updated_at}\n"
            if hasattr(user, 'personality_profile') and user.personality_profile:
                debug_info += f"  Personality Profile: {user.personality_profile}\n"
            debug_info += "\n"
        else:
            debug_info += f"❌ Пользователь не найден в БД!\n\n"
        
        # Информация из кэша
        if cached_user:
            debug_info += f"💾 Данные из кэша:\n"
            debug_info += f"  Subscription Status: {cached_user.subscription_status}\n"
            debug_info += f"  Subscription Expires At: {cached_user.subscription_expires_at}\n"
            debug_info += f"  Consent Given: {cached_user.consent_given}\n"
            debug_info += f"  Language: {cached_user.language}\n"
            debug_info += f"  Gender Preference: {cached_user.gender_preference}\n"
            if hasattr(cached_user, 'personality_profile') and cached_user.personality_profile:
                debug_info += f"  Personality Profile: {cached_user.personality_profile}\n"
        else:
            debug_info += f"💾 Кэш пуст\n"
        
        return debug_info
    
    @staticmethod
    def format_subscription_debug_info(user_id: int, subscription_status: str, 
                                    expires_at: Optional[datetime] = None) -> str:
        """
        Генерирует отладочную информацию о подписке.
        
        Args:
            user_id: ID пользователя
            subscription_status: Статус подписки
            expires_at: Дата истечения подписки
            
        Returns:
            Форматированная строка с информацией о подписке
        """
        debug_info = f"💳 Debug информация о подписке для пользователя {user_id}:\n\n"
        debug_info += f"  Статус: {subscription_status}\n"
        
        if expires_at:
            debug_info += f"  Истекает: {expires_at}\n"
            debug_info += f"  Активна: {'Да' if not DateTimeUtils.is_expired(expires_at) else 'Нет'}\n"
        else:
            debug_info += f"  Истекает: Не установлено\n"
            debug_info += f"  Активна: {'Да' if subscription_status == 'premium' else 'Нет'}\n"
        
        return debug_info
    
    @staticmethod
    def format_personality_debug_info(user_id: int, personality_profile: Optional[Dict[str, float]]) -> str:
        """
        Генерирует отладочную информацию о профиле личности.
        
        Args:
            user_id: ID пользователя
            personality_profile: Профиль личности пользователя
            
        Returns:
            Форматированная строка с информацией о личности
        """
        debug_info = f"🧠 Debug информация о личности для пользователя {user_id}:\n\n"
        
        if personality_profile:
            debug_info += f"  Профиль найден: Да\n"
            debug_info += f"  Количество черт: {len(personality_profile)}\n\n"
            
            # Сортируем черты по значению
            sorted_traits = sorted(personality_profile.items(), key=lambda x: x[1], reverse=True)
            
            debug_info += f"  Топ-5 черт:\n"
            for i, (trait, value) in enumerate(sorted_traits[:5], 1):
                debug_info += f"    {i}. {trait}: {value:.2f}\n"
            
            if len(sorted_traits) > 5:
                debug_info += f"    ... и еще {len(sorted_traits) - 5} черт\n"
        else:
            debug_info += f"  Профиль найден: Нет\n"
        
        return debug_info
    
    @staticmethod
    def format_general_debug_info(title: str, data: Dict[str, Any]) -> str:
        """
        Генерирует общую отладочную информацию.
        
        Args:
            title: Заголовок отладочной информации
            data: Словарь с данными для отображения
            
        Returns:
            Форматированная строка с отладочной информацией
        """
        debug_info = f"🔍 {title}:\n\n"
        
        for key, value in data.items():
            if isinstance(value, dict):
                debug_info += f"  {key}:\n"
                for sub_key, sub_value in value.items():
                    debug_info += f"    {sub_key}: {sub_value}\n"
            elif isinstance(value, list):
                debug_info += f"  {key}: [{', '.join(map(str, value))}]\n"
            else:
                debug_info += f"  {key}: {value}\n"
        
        return debug_info
    
    @staticmethod
    def format_error_debug_info(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Генерирует отладочную информацию об ошибке.
        
        Args:
            error: Объект исключения
            context: Дополнительный контекст
            
        Returns:
            Форматированная строка с информацией об ошибке
        """
        debug_info = f"❌ Debug информация об ошибке:\n\n"
        debug_info += f"  Тип ошибки: {type(error).__name__}\n"
        debug_info += f"  Сообщение: {str(error)}\n"
        
        if context:
            debug_info += f"\n  Контекст:\n"
            for key, value in context.items():
                debug_info += f"    {key}: {value}\n"
        
        return debug_info


# Глобальный экземпляр для удобства использования
debug_info_generator = DebugInfoGenerator()


# Удобные функции для быстрого доступа
def get_user_debug_info(user_id: int, user: Optional[Any] = None, 
                       cached_user: Optional[Any] = None) -> str:
    """Быстрый доступ к генерации отладочной информации о пользователе."""
    return debug_info_generator.format_user_debug_info(user_id, user, cached_user)


def get_subscription_debug_info(user_id: int, subscription_status: str, 
                             expires_at: Optional[datetime] = None) -> str:
    """Быстрый доступ к генерации отладочной информации о подписке."""
    return debug_info_generator.format_subscription_debug_info(user_id, subscription_status, expires_at)


def get_personality_debug_info(user_id: int, personality_profile: Optional[Dict[str, float]]) -> str:
    """Быстрый доступ к генерации отладочной информации о личности."""
    return debug_info_generator.format_personality_debug_info(user_id, personality_profile)


def get_general_debug_info(title: str, data: Dict[str, Any]) -> str:
    """Быстрый доступ к генерации общей отладочной информации."""
    return debug_info_generator.format_general_debug_info(title, data)


def get_error_debug_info(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
    """Быстрый доступ к генерации отладочной информации об ошибке."""
    return debug_info_generator.format_error_debug_info(error, context)

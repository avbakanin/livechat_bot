"""
Common messages used across different domains.
"""
from aiogram.utils.markdown import hbold


def get_error_message(error_type: str = "general") -> str:
    """Get error message based on error type."""
    messages = {
        "general": "Произошла ошибка. Попробуйте позже.",
        "database": "Ошибка базы данных. Попробуйте позже.",
        "openai": "Ошибка при обработке сообщения. Попробуйте позже.",
        "validation": "Некорректные данные. Проверьте ввод.",
        "permission": "У вас нет прав для выполнения этого действия.",
        "limit": "Превышен лимит. Попробуйте позже."
    }
    return messages.get(error_type, messages["general"])


def get_success_message(action: str = "general") -> str:
    """Get success message based on action."""
    messages = {
        "general": "Операция выполнена успешно!",
        "saved": "Данные сохранены!",
        "updated": "Данные обновлены!",
        "deleted": "Данные удалены!",
        "sent": "Сообщение отправлено!"
    }
    return messages.get(action, messages["general"])


def get_help_text() -> str:
    """Get general help text."""
    return f"""
{hbold('🤖 Помощь по боту')}

{hbold('Доступные команды:')}
/start - Начать общение с ботом
/help - Показать эту справку
/choose_gender - Выбрать пол компаньона

{hbold('💬 Общение:')}
• Бесплатно: 100 сообщений в день
• Премиум: безлимитное общение

{hbold('🎭 Выбор компаньона:')}
• Девушка - милая и empathetic
• Молодой человек - уверенный и игривый

{hbold('💎 Премиум подписка:')}
Открывает безлимитное общение и дополнительные возможности

{hbold('❓ Частые вопросы:')}
• Бот запоминает контекст разговора
• Можно сменить пол компаньона в любое время
• Лимит сообщений сбрасывается каждый день

Для начала общения используйте {hbold('/start')}
"""


def get_privacy_info_text() -> str:
    """Get privacy policy text."""
    return ("🔐 <b>Политика конфиденциальности</b>\n\n"
            "Здесь ваш текст политики конфиденциальности...\n\n"
            "Полная версия: https://yourwebsite.com/privacy")

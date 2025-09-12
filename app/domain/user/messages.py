"""
User domain messages - text templates and responses.
"""
from config.openai import OPENAI_CONFIG


def get_consent_given_text() -> str:
    """Get text after consent is given."""
    return f"Спасибо за согласие! У тебя {OPENAI_CONFIG.get('FREE_MESSAGE_LIMIT', 100)} бесплатных сообщений в день. Выбери пол компаньона:"


def get_gender_change_warning_text() -> str:
    """Get gender change warning text."""
    return "⚠️ Вы уверены, что хотите сменить пол компаньона?\n\n" "Вся история переписки будет удалена!"


def get_gender_selection_text() -> str:
    """Get gender selection text."""
    return "Выбери пол компаньона:"

"""
Subscription domain messages - placeholder for future implementation.
"""
from aiogram.utils.markdown import hbold


def get_premium_info_text() -> str:
    """Get premium subscription info text."""
    return f"""
{hbold('💎 Премиум подписка')}

{hbold('Что дает премиум:')}
• ✅ Безлимитные сообщения
• ✅ Приоритетная обработка запросов
• ✅ Расширенная история диалога
• ✅ Специальные режимы общения

{hbold('Стоимость:')}
• 500 руб. / месяц

{hbold('Как приобрести:')}
Нажмите кнопку 'Купить премиум' в главном меню (/start)
"""

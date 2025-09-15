"""
Subscription domain messages - placeholder for future implementation.
"""

from aiogram.utils.markdown import hbold
from shared.i18n import i18n

# def get_premium_info_text() -> str:
#     """Get premium subscription info text."""
#     return f"""
# {hbold('💎 Премиум подписка')}

# {hbold('Что дает премиум:')}
# • ✅ Безлимитные сообщения
# • ✅ Приоритетная обработка запросов
# • ✅ Расширенная история диалога
# • ✅ Специальные режимы общения

# {hbold('Стоимость:')}
# • 500 руб. / месяц


# {hbold('Как приобрести:')}
# Нажмите кнопку 'Купить премиум' в главном меню (/start)
# """
def get_premium_info_text():
    return f"""
{hbold(i18n.t("premium.title"))}

{hbold(i18n.t("premium.benefits_title"))}
• {i18n.t("premium.benefits.unlimited")}
• {i18n.t("premium.benefits.priority")}
• {i18n.t("premium.benefits.history")}
• {i18n.t("premium.benefits.modes")}

{hbold(i18n.t("premium.price_title"))}
• {i18n.t("premium.price")}

{hbold(i18n.t("premium.howto_title"))}
{i18n.t("premium.howto")}
"""


def get_privacy_info_text():
    return (
        f"{i18n.t('privacy.title', hbold=hbold)}\n\n"
        f"{i18n.t('privacy.text')}\n\n"
        f"{i18n.t('privacy.full', url='https://yourwebsite.com/privacy')}"
    )

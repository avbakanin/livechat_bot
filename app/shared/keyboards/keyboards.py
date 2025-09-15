from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold
from shared.constants import APP_CONFIG
from shared.i18n import i18n


# ===== КЛАВИАТУРЫ ДЛЯ СОГЛАСИЯ С ПОЛИТИКОЙ =====
def get_consent_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.agree_privacy"), callback_data="consent_agree"
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.read_privacy"),
                    url="https://your-site.com/privacy",
                )
            ],
        ]
    )


# ===== КЛАВИАТУРЫ ОСНОВНАЯ ПОСЛЕ СТАРТА =====
def get_start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_female"), callback_data="gender_female"
                ),
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_male"), callback_data="gender_male"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.buy_premium"),
                    callback_data="subscribe_premium",
                )
            ],
        ]
    )


# ===== Текст для команды /start =====
def get_start_text():
    """Текст для команды /start"""
    return i18n.t("start.welcome", free_limit=APP_CONFIG["FREE_MESSAGE_LIMIT"])


# ===== Клавиатура после принятия согласия =====
def get_consent_given_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_female"), callback_data="gender_female"
                ),
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_male"), callback_data="gender_male"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.buy_premium"),
                    callback_data="subscribe_premium",
                )
            ],
        ]
    )


# ===== Текст после принятия согласия =====
def get_consent_given_text():
    return i18n.t("consent.agreed", free_limit=APP_CONFIG["FREE_MESSAGE_LIMIT"])


# ===== КЛАВИАТУРЫ ДЛЯ ВЫБОРА ПОЛА =====
def get_gender_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_female"), callback_data="gender_female"
                ),
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_male"), callback_data="gender_male"
                ),
            ]
        ]
    )


# ===== КЛАВИАТУРЫ ДЛЯ ПРЕМИУМА =====
def get_premium_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.buy_premium"),
                    callback_data="subscribe_premium",
                )
            ]
        ]
    )


# ===== КЛАВИАТУРЫ ДЛЯ КОМАНДА /help =====
def get_help_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_gender_help"),
                    callback_data="choose_gender_help",
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.premium_info_help"),
                    callback_data="premium_info_help",
                )
            ],
            # [InlineKeyboardButton(text="📝 Политика конфиденциальности", url="https://your-site.com/privacy")]
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.privacy_info_help"),
                    callback_data="privacy_info_help",
                )
            ],
        ]
    )


# ===== Текст для команды /help =====
def get_help_text():
    return f"""
{hbold(i18n.t("help.title"))}

{hbold(i18n.t("help.commands_title"))}
{i18n.t("help.start_command")}
{i18n.t("help.help_command")}
{i18n.t("help.gender_command")}

{hbold(i18n.t("help.communication_title"))}
{i18n.t("help.free_limit", free_limit=APP_CONFIG['FREE_MESSAGE_LIMIT'])}
{i18n.t("help.premiun_unlimited")}

{hbold(i18n.t("help.genders_title"))}
{i18n.t("help.female_description")}
{i18n.t("help.male_description")}

{hbold('💎 Премиум подписка:')}
{i18n.t("help.premium_description")}

{hbold(i18n.t("help.faq_title"))}
{i18n.t("help.context_memory")}
{i18n.t("help.gender_change")}
{i18n.t("help.limit_reset")}

{i18n.t("help.start_instructions", start_command=hbold('/start'))}
"""


# Для начала общения используйте {hbold('/start')}


# ===== Клавиатура для информации о премиуме =====
def get_premium_info_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.buy_premium"),
                    callback_data="subscribe_premium",
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.buy_premium"), callback_data="back_to_help"
                )
            ],
        ]
    )


def get_privacy_info_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.buy_premium"), callback_data="back_to_help"
                )
            ]
        ]
    )


# ===== Текст для информации о премиуме =====
def get_premium_info_text():
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


def get_privacy_info_text():
    return (
        "🔐 <b>Политика конфиденциальности</b>\n\n"
        "Здесь ваш текст политики конфиденциальности...\n\n"
        "Полная версия: https://yourwebsite.com/privacy"
    )


# ===== КЛАВИАТУРА ДЛЯ ЛИМИТА СООБЩЕНИЙ =====
def get_limit_exceeded_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.buy_premium"),
                    callback_data="subscribe_premium",
                )
            ]
        ]
    )


# ===== КЛАВИАТУРА ДЛЯ ПОДТВЕРЖДЕНИЯ СМЕНЫ ПОЛА =====
def get_gender_change_confirmation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.yes_change"),
                    callback_data="gender_change_confirm",
                ),
                InlineKeyboardButton(
                    text=i18n.t("buttons.cancel"), callback_data="gender_change_cancel"
                ),
            ]
        ]
    )

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold
from shared.constants import APP_CONFIG


# ===== КЛАВИАТУРЫ ДЛЯ СОГЛАСИЯ С ПОЛИТИКОЙ =====
def get_consent_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Согласен с политикой конфиденциальности", callback_data="consent_agree")],
            [InlineKeyboardButton(text="Читать политику", url="https://your-site.com/privacy")],
        ]
    )


# ===== КЛАВИАТУРЫ ОСНОВНАЯ ПОСЛЕ СТАРТА =====
def get_start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Выбрать девушку 😊", callback_data="gender_female"),
                InlineKeyboardButton(text="Выбрать молодого человека 😉", callback_data="gender_male"),
            ],
            [InlineKeyboardButton(text="Купить премиум 💳", callback_data="subscribe_premium")],
        ]
    )


# ===== Текст для команды /start =====
def get_start_text():
    """Текст для команды /start"""
    return f"Привет! У тебя {APP_CONFIG['FREE_MESSAGE_LIMIT']} бесплатных сообщений в день. Выбери пол компаньона:"


# ===== Клавиатура после принятия согласия =====
def get_consent_given_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Выбрать девушку 😊", callback_data="gender_female"),
                InlineKeyboardButton(text="Выбрать молодого человека 😉", callback_data="gender_male"),
            ],
            [InlineKeyboardButton(text="Купить премиум 💳", callback_data="subscribe_premium")],
        ]
    )


# ===== Текст после принятия согласия =====
def get_consent_given_text():
    return (
        f"Спасибо за согласие! У тебя {APP_CONFIG['FREE_MESSAGE_LIMIT']} бесплатных сообщений в день. Выбери пол компаньона:"
    )


# ===== КЛАВИАТУРЫ ДЛЯ ВЫБОРА ПОЛА =====
def get_gender_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Девушка 😊", callback_data="gender_female"),
                InlineKeyboardButton(text="Молодой человек 😉", callback_data="gender_male"),
            ]
        ]
    )


# ===== КЛАВИАТУРЫ ДЛЯ ПРЕМИУМА =====
def get_premium_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Купить премиум 💳", callback_data="subscribe_premium")]]
    )


# ===== КЛАВИАТУРЫ ДЛЯ КОМАНДА /help =====
def get_help_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎭 Выбрать пол компаньона", callback_data="choose_gender_help")],
            [InlineKeyboardButton(text="💎 Информация о премиуме", callback_data="premium_info_help")],
            # [InlineKeyboardButton(text="📝 Политика конфиденциальности", url="https://your-site.com/privacy")]
            [InlineKeyboardButton(text="📝 Политика конфиденциальности", callback_data="privacy_info_help")],
        ]
    )


# ===== Текст для команды /help =====
def get_help_text():
    return f"""
{hbold('🤖 Помощь по боту')}

{hbold('Доступные команды:')}
/start - Начать общение с ботом
/help - Показать эту справку
/choose_gender - Выбрать пол компаньона

{hbold('💬 Общение:')}
• Бесплатно: {APP_CONFIG['FREE_MESSAGE_LIMIT']} сообщений в день
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


# ===== Клавиатура для информации о премиуме =====
def get_premium_info_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Купить премиум", callback_data="subscribe_premium")],
            [InlineKeyboardButton(text="↩️ Назад к справке", callback_data="back_to_help")],
        ]
    )


def get_privacy_info_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="↩️ Назад к справке", callback_data="back_to_help")]]
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
        inline_keyboard=[[InlineKeyboardButton(text="Купить премиум 💳", callback_data="subscribe_premium")]]
    )


# ===== КЛАВИАТУРА ДЛЯ ПОДТВЕРЖДЕНИЯ СМЕНЫ ПОЛА =====
def get_gender_change_confirmation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, сменить пол", callback_data="gender_change_confirm"),
                InlineKeyboardButton(text="Отмена", callback_data="gender_change_cancel"),
            ]
        ]
    )

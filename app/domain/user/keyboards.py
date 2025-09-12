from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_consent_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Согласен с политикой конфиденциальности", callback_data="consent_agree")],
            [InlineKeyboardButton(text="Читать политику", url="https://your-site.com/privacy")],
        ]
    )


def get_consent_given_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Выбрать девушку 😊", callback_data="gender_female"),
                InlineKeyboardButton(text="Выбрать молодого человека 😉", callback_data="gender_male"),
            ],
            [InlineKeyboardButton(text="Купить премиум 💳", callback_data="subscribe_premium")],
        ]
    )


def get_gender_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Девушка 😊", callback_data="gender_female"),
                InlineKeyboardButton(text="Молодой человек 😉", callback_data="gender_male"),
            ]
        ]
    )


def get_gender_change_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, сменить пол", callback_data="gender_change_confirm"),
                InlineKeyboardButton(text="Отмена", callback_data="gender_change_cancel"),
            ]
        ]
    )


def get_help_keyboard(i18n_instance=None) -> InlineKeyboardMarkup:
    if i18n_instance is None:
        from shared.i18n import i18n

        i18n_instance = i18n

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=i18n_instance.t("buttons.choose_gender_help"), callback_data="choose_gender_help")],
            [InlineKeyboardButton(text=i18n_instance.t("buttons.premium_info_help"), callback_data="premium_info_help")],
            [InlineKeyboardButton(text=i18n_instance.t("buttons.privacy_info_help"), callback_data="privacy_info_help")],
        ]
    )


def get_privacy_info_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="↩️ Назад к справке", callback_data="back_to_help")]]
    )

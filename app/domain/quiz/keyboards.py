from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_quiz_start_keyboard(i18n) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=i18n.t("quiz.start_button"), callback_data="start_quiz")],
            [InlineKeyboardButton(text=i18n.t("buttons.back_to_help"), callback_data="back_to_help")]
        ]
    )


# Клавиатуры
def get_landscape_keyboard(i18n) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.landscape_mountains"), callback_data="landscape_mountains"),
                InlineKeyboardButton(text=i18n.t("quiz.options.landscape_ocean"), callback_data="landscape_ocean"),
            ],
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.landscape_forest"), callback_data="landscape_forest"),
                InlineKeyboardButton(text=i18n.t("quiz.options.landscape_city"), callback_data="landscape_city"),
            ],
        ]
    )


def get_superpower_keyboard(i18n) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.superpower_mind_reading"), callback_data="superpower_mind_reading"),
                InlineKeyboardButton(text=i18n.t("quiz.options.superpower_time_stop"), callback_data="superpower_time_stop"),
            ],
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.superpower_teleport"), callback_data="superpower_teleport"),
                InlineKeyboardButton(text=i18n.t("quiz.options.superpower_immortality"), callback_data="superpower_immortality"),
            ],
        ]
    )


def get_time_of_day_keyboard(i18n) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.time_morning"), callback_data="time_morning"),
                InlineKeyboardButton(text=i18n.t("quiz.options.time_day"), callback_data="time_day"),
            ],
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.time_evening"), callback_data="time_evening"),
                InlineKeyboardButton(text=i18n.t("quiz.options.time_night"), callback_data="time_night"),
            ],
        ]
    )


def get_book_keyboard(i18n) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.book_encyclopedia"), callback_data="book_encyclopedia"),
                InlineKeyboardButton(text=i18n.t("quiz.options.book_detective"), callback_data="book_detective"),
            ],
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.book_novel"), callback_data="book_novel"),
                InlineKeyboardButton(text=i18n.t("quiz.options.book_poetry"), callback_data="book_poetry"),
            ],
        ]
    )


def get_rest_keyboard(i18n) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.rest_party"), callback_data="rest_party"),
                InlineKeyboardButton(text=i18n.t("quiz.options.rest_home"), callback_data="rest_home"),
            ],
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.rest_nature"), callback_data="rest_nature"),
                InlineKeyboardButton(text=i18n.t("quiz.options.rest_reading"), callback_data="rest_reading"),
            ],
        ]
    )


def get_animal_keyboard(i18n) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.animal_lion"), callback_data="animal_lion"),
                InlineKeyboardButton(text=i18n.t("quiz.options.animal_fox"), callback_data="animal_fox"),
            ],
            [
                InlineKeyboardButton(text=i18n.t("quiz.options.animal_dolphin"), callback_data="animal_dolphin"),
                InlineKeyboardButton(text=i18n.t("quiz.options.animal_owl"), callback_data="animal_owl"),
            ],
        ]
    )


def get_completion_keyboard(i18n) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=i18n.t("quiz.messages.start_chatting_button"), callback_data="start_chatting")]
        ]
    )

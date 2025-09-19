from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_quiz_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Начать квиз ✨", callback_data="start_quiz")]]
    )


# Клавиатуры
def get_landscape_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏔️ Горные вершины", callback_data="landscape_mountains"),
                InlineKeyboardButton(text="🌊 Океанский берег", callback_data="landscape_ocean"),
            ],
            [
                InlineKeyboardButton(text="🏞️ Тихий лес", callback_data="landscape_forest"),
                InlineKeyboardButton(text="🌇 Городские огни", callback_data="landscape_city"),
            ],
        ]
    )


def get_superpower_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🧠 Чтение мыслей", callback_data="superpower_mind_reading"),
                InlineKeyboardButton(text="🕰️ Остановка времени", callback_data="superpower_time_stop"),
            ],
            [
                InlineKeyboardButton(text="✈️ Телепортация", callback_data="superpower_teleport"),
                InlineKeyboardButton(text="🐢 Бессмертие", callback_data="superpower_immortality"),
            ],
        ]
    )


def get_time_of_day_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌅 Раннее утро", callback_data="time_morning"),
                InlineKeyboardButton(text="☀️ День", callback_data="time_day"),
            ],
            [
                InlineKeyboardButton(text="🌇 Вечер", callback_data="time_evening"),
                InlineKeyboardButton(text="🌙 Ночь", callback_data="time_night"),
            ],
        ]
    )


def get_book_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Энциклопедия", callback_data="book_encyclopedia"),
                InlineKeyboardButton(text="📖 Детектив", callback_data="book_detective"),
            ],
            [
                InlineKeyboardButton(text="📙 Роман", callback_data="book_novel"),
                InlineKeyboardButton(text="📗 Поэзия", callback_data="book_poetry"),
            ],
        ]
    )


def get_rest_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎉 Вечеринка с друзьями", callback_data="rest_party"),
                InlineKeyboardButton(text="🎮 Игры/фильмы дома", callback_data="rest_home"),
            ],
            [
                InlineKeyboardButton(text="🏕️ Поход на природу", callback_data="rest_nature"),
                InlineKeyboardButton(text="📚 Чтение книги", callback_data="rest_reading"),
            ],
        ]
    )


def get_animal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🦁 Лев", callback_data="animal_lion"),
                InlineKeyboardButton(text="🦊 Лиса", callback_data="animal_fox"),
            ],
            [
                InlineKeyboardButton(text="🐬 Дельфин", callback_data="animal_dolphin"),
                InlineKeyboardButton(text="🦉 Сова", callback_data="animal_owl"),
            ],
        ]
    )


def get_completion_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Начать общение 💬", callback_data="start_chatting")]
        ]
    )

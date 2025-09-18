from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from domain.quiz.helpers import (
    analyze_personality,
    format_personality_results,
    save_personality_profile,
)
from domain.quiz.fsm import QuizStates

router = Router()

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


# Запуск квиза
@router.callback_query(F.data == "start_quiz")
async def process_start_quiz(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.waiting_for_landscape)
    await callback.message.edit_text(
        "1/7 Выбери пейзаж, который тебе ближе:",
        reply_markup=InlineKeyboardMarkup(
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
        ),
    )


# Вопрос 1: Пейзаж
@router.callback_query(QuizStates.waiting_for_landscape, F.data.startswith("landscape_"))
async def process_landscape(callback: CallbackQuery, state: FSMContext):
    await state.update_data(landscape=callback.data)
    await state.set_state(QuizStates.waiting_for_superpower)

    await callback.message.edit_text(
        "2/7 Какую суперспособность ты бы выбрал?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🧠 Чтение мыслей", callback_data="superpower_mind_reading"
                    ),
                    InlineKeyboardButton(
                        text="🕰️ Остановка времени", callback_data="superpower_time_stop"
                    ),
                ],
                [
                    InlineKeyboardButton(text="✈️ Телепортация", callback_data="superpower_teleport"),
                    InlineKeyboardButton(text="🐢 Бессмертие", callback_data="superpower_immortality"),
                ],
            ]
        ),
    )


# Вопрос 2: Суперспособность
@router.callback_query(QuizStates.waiting_for_superpower, F.data.startswith("superpower_"))
async def process_superpower(callback: CallbackQuery, state: FSMContext):
    await state.update_data(superpower=callback.data)
    await state.set_state(QuizStates.waiting_for_time_of_day)

    await callback.message.edit_text(
        "3/7 Какое время суток тебе ближе?",
        reply_markup=InlineKeyboardMarkup(
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
        ),
    )


# Вопрос 3: Время суток
@router.callback_query(QuizStates.waiting_for_time_of_day, F.data.startswith("time_"))
async def process_time_of_day(callback: CallbackQuery, state: FSMContext):
    await state.update_data(time_of_day=callback.data)
    await state.set_state(QuizStates.waiting_for_book)

    await callback.message.edit_text(
        "4/7 Какую книгу ты бы взял на необитаемый остров?",
        reply_markup=InlineKeyboardMarkup(
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
        ),
    )


# Вопрос 4: Книга
@router.callback_query(QuizStates.waiting_for_book, F.data.startswith("book_"))
async def process_book(callback: CallbackQuery, state: FSMContext):
    await state.update_data(book=callback.data)
    await state.set_state(QuizStates.waiting_for_three_words)

    await callback.message.edit_text("5/7 Опиши себя тремя словами (напиши ответ сообщением):")


# Вопрос 5: Три слова о себе
@router.message(QuizStates.waiting_for_three_words)
async def process_three_words(message: Message, state: FSMContext):
    if len(message.text.split()) < 2:  # Минимум 2 слова
        await message.answer("Пожалуйста, напиши хотя бы два слова для описания себя")
        return

    await state.update_data(three_words=message.text)
    await state.set_state(QuizStates.waiting_for_rest)

    await message.answer(
        "6/7 Что для тебя идеальный отдых?",
        reply_markup=InlineKeyboardMarkup(
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
        ),
    )


# Вопрос 6: Отдых
@router.callback_query(QuizStates.waiting_for_rest, F.data.startswith("rest_"))
async def process_rest(callback: CallbackQuery, state: FSMContext):
    await state.update_data(rest=callback.data)
    await state.set_state(QuizStates.waiting_for_animal)

    await callback.message.edit_text(
        "7/7 Какое животное тебе ближе по характеру?",
        reply_markup=InlineKeyboardMarkup(
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
        ),
    )


# Вопрос 7: Животное и завершение квиза
@router.callback_query(QuizStates.waiting_for_animal, F.data.startswith("animal_"))
async def process_animal(callback: CallbackQuery, state: FSMContext):
    await state.update_data(animal=callback.data)

    # Получаем все ответы
    data = await state.get_data()

    # Анализируем личностные черты
    personality_profile = analyze_personality(data)

    # Сохраняем в базу данных
    await save_personality_profile(callback.from_user.id, personality_profile)

    # Формируем ответ с результатами
    result_message = format_personality_results(personality_profile)

    await callback.message.edit_text(
        f"Спасибо за прохождение квиза! Вот что я узнал о тебе:\n\n{result_message}\n\n"
        "Эта информация поможет мне быть более полезным собеседником!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Начать общение 💬", callback_data="start_chatting")]
            ]
        ),
    )

    await state.clear()

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from shared.decorators import error_decorator
from shared.i18n import i18n

from .messages import get_quiz_texts
from .keyboards import (
    get_animal_keyboard,
    get_book_keyboard,
    get_completion_keyboard,
    get_landscape_keyboard,
    get_rest_keyboard,
    get_superpower_keyboard,
    get_time_of_day_keyboard,
)
from .helpers import (
    analyze_personality,
    format_personality_results,
    save_personality_profile,
)
from .fsm import QuizStates

router = Router()


# Запуск квиза
@router.callback_query(F.data == "start_quiz")
@error_decorator
async def process_start_quiz(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.waiting_for_landscape)
    texts = get_quiz_texts(i18n)
    await callback.message.edit_text(
        texts["start"],
        reply_markup=get_landscape_keyboard(i18n),
    )


# Вопрос 1: Пейзаж
@router.callback_query(QuizStates.waiting_for_landscape, F.data.startswith("landscape_"))
@error_decorator
async def process_landscape(callback: CallbackQuery, state: FSMContext):
    await state.update_data(landscape=callback.data)
    await state.set_state(QuizStates.waiting_for_superpower)
    texts = get_quiz_texts(i18n)

    await callback.message.edit_text(
        texts["superpower"],
        reply_markup=get_superpower_keyboard(i18n),
    )


# Вопрос 2: Суперспособность
@router.callback_query(QuizStates.waiting_for_superpower, F.data.startswith("superpower_"))
@error_decorator
async def process_superpower(callback: CallbackQuery, state: FSMContext):
    await state.update_data(superpower=callback.data)
    await state.set_state(QuizStates.waiting_for_time_of_day)
    texts = get_quiz_texts(i18n)

    await callback.message.edit_text(
        texts["time_of_day"],
        reply_markup=get_time_of_day_keyboard(i18n),
    )


# Вопрос 3: Время суток
@router.callback_query(QuizStates.waiting_for_time_of_day, F.data.startswith("time_"))
@error_decorator
async def process_time_of_day(callback: CallbackQuery, state: FSMContext):
    await state.update_data(time_of_day=callback.data)
    await state.set_state(QuizStates.waiting_for_book)
    texts = get_quiz_texts(i18n)

    await callback.message.edit_text(
        texts["book"],
        reply_markup=get_book_keyboard(i18n),
    )


# Вопрос 4: Книга
@router.callback_query(QuizStates.waiting_for_book, F.data.startswith("book_"))
@error_decorator
async def process_book(callback: CallbackQuery, state: FSMContext):
    await state.update_data(book=callback.data)
    await state.set_state(QuizStates.waiting_for_three_words)
    texts = get_quiz_texts(i18n)

    await callback.message.edit_text(texts["three_words"])


# Вопрос 5: Три слова о себе
@error_decorator
@router.message(QuizStates.waiting_for_three_words)
async def process_three_words(message: Message, state: FSMContext):
    texts = get_quiz_texts(i18n)

    if len(message.text.split()) < 2:
        await message.answer(texts["min_words"])
        return

    await state.update_data(three_words=message.text)
    await state.set_state(QuizStates.waiting_for_rest)

    await message.answer(
        texts["rest"],
        reply_markup=get_rest_keyboard(i18n),
    )


# Вопрос 6: Отдых
@router.callback_query(QuizStates.waiting_for_rest, F.data.startswith("rest_"))
@error_decorator
async def process_rest(callback: CallbackQuery, state: FSMContext):
    await state.update_data(rest=callback.data)
    await state.set_state(QuizStates.waiting_for_animal)
    texts = get_quiz_texts(i18n)

    await callback.message.edit_text(
        texts["animal"],
        reply_markup=get_animal_keyboard(i18n),
    )


# Вопрос 7: Животное и завершение квиза
@router.callback_query(QuizStates.waiting_for_animal, F.data.startswith("animal_"))
@error_decorator
async def process_animal(callback: CallbackQuery, state: FSMContext):
    await state.update_data(animal=callback.data)
    texts = get_quiz_texts(i18n)

    # Получаем все ответы
    data = await state.get_data()

    # Анализируем личностные черты
    personality_profile = analyze_personality(data)

    # Сохраняем в базу данных
    await save_personality_profile(callback.from_user.id, personality_profile)

    # Формируем ответ с результатами
    result_message = format_personality_results(personality_profile, i18n)

    await callback.message.edit_text(
        texts["completion"].format(result=result_message),
        reply_markup=get_completion_keyboard(i18n),
    )

    await state.clear()


# Обработчик кнопки "Начать общение"
@router.callback_query(F.data == "start_chatting")
@error_decorator
async def start_chatting_after_quiz(callback: CallbackQuery):
    texts = get_quiz_texts(i18n)
    await callback.message.edit_text(texts["start_chatting"])
    await callback.answer()

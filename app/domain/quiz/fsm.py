from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    waiting_for_landscape = State()
    waiting_for_superpower = State()
    waiting_for_time_of_day = State()
    waiting_for_book = State()
    waiting_for_three_words = State()
    waiting_for_rest = State()
    waiting_for_animal = State()

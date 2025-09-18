from aiogram import Dispatcher

from .user.handlers import router as user_router
from .user.callbacks import router as user_callbacks
from .message.handlers import router as message_router
from .payment.handlers import router as payment_router
from .quiz.handlers import router as quiz_router
from .quiz.callbacks import router as quiz_callbacks


def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(user_router)
    dp.include_router(user_callbacks)
    dp.include_router(message_router)
    dp.include_router(payment_router)
    dp.include_router(quiz_router)
    dp.include_router(quiz_callbacks)

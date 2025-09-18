from aiogram import Dispatcher

from .user.handlers import router as user_router
from .user.callbacks import router as user_callbacks
from .message.handlers import router as message_router
from .payment.handlers import router as payment_router


def setup_routers(dp: Dispatcher) -> None:
    """Register all domain routers."""
    dp.include_router(user_router)
    dp.include_router(user_callbacks)
    dp.include_router(message_router)
    dp.include_router(payment_router)

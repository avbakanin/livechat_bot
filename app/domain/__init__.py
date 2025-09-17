# Добавьте в файл c:\Users\User\Desktop\livechat_bot\app\domain\__init__.py
from aiogram import Dispatcher

from .message.handlers import router as message_router
from .payment.handlers import router as payment_router
from .user.handlers import router as user_router


def setup_routers(dp: Dispatcher) -> None:
    """Register all domain routers."""
    dp.include_router(user_router)
    dp.include_router(message_router)
    dp.include_router(payment_router)  # Domain modules for feature-based organization

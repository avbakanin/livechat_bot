from aiogram import Dispatcher
from shared.constants import TELEGRAM_CONFIG
from shared.middlewares.middlewares import AccessMiddleware

from .user.handlers import router as user_router
from .user.callbacks import router as user_callbacks
from .message.handlers import router as message_router
from .payment.handlers import router as payment_router
from .quiz.handlers import router as quiz_router
from .quiz.callbacks import router as quiz_callbacks


def setup_routers(dp: Dispatcher) -> None:
    setup_access_middleware()

    dp.include_router(quiz_router)
    dp.include_router(quiz_callbacks)
    dp.include_router(user_router)
    dp.include_router(user_callbacks)
    dp.include_router(message_router)
    dp.include_router(payment_router)


def setup_access_middleware() -> None:
    """Setup access middleware for restricted routers."""
    access_middleware = AccessMiddleware(TELEGRAM_CONFIG["allowed_user_ids"])

    # Router to handler type mapping
    router_config = {
        quiz_router: ["message", "callback_query"],
        quiz_callbacks: ["message", "callback_query"],
        user_router: ["message", "callback_query"],
        user_callbacks: ["message", "callback_query"],
        message_router: ["message"],
        payment_router: ["callback_query"],
    }

    # Apply middleware based on configuration
    for router, handler_types in router_config.items():
        for handler_type in handler_types:
            getattr(router, handler_type).middleware(access_middleware)

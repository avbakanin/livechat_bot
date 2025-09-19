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
    # Add AccessMiddleware only to restricted routers (not quiz)
    access_middleware = AccessMiddleware(TELEGRAM_CONFIG["allowed_user_ids"])
    
    # Restricted routers (require access control)
    user_router.message.middleware(access_middleware)
    user_router.callback_query.middleware(access_middleware)
    user_callbacks.message.middleware(access_middleware)
    user_callbacks.callback_query.middleware(access_middleware)
    message_router.message.middleware(access_middleware)
    payment_router.callback_query.middleware(access_middleware)
    
    # Quiz routers (no access restrictions)
    # quiz_router and quiz_callbacks remain unrestricted
    
    dp.include_router(user_router)
    dp.include_router(user_callbacks)
    dp.include_router(message_router)
    dp.include_router(payment_router)
    dp.include_router(quiz_router)
    dp.include_router(quiz_callbacks)

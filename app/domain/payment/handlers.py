"""
Payment domain handlers - placeholder for future implementation.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery
from shared.middlewares.i18n_middleware import I18nMiddleware
from shared.constants import Callbacks

router = Router()


@router.callback_query(F.data == Callbacks.SUBSCRIBE_PREMIUM)
async def premium_subscribe(callback: CallbackQuery, i18n: I18nMiddleware):
    """Handle premium subscription request."""
    await callback.message.edit_text(i18n.t("premium.unavailable"))
    await callback.answer()

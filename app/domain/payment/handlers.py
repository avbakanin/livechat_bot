"""
Payment domain handlers - placeholder for future implementation.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery
from shared.middlewares.i18n_middleware import I18nMiddleware

router = Router()


@router.callback_query(F.data == "subscribe_premium")
async def premium_subscribe(callback: CallbackQuery, i18n: I18nMiddleware):
    """Handle premium subscription request."""
    await callback.message.edit_text(i18n.t("premium.unavailable"))
    await callback.answer()

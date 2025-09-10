"""
Payment domain handlers - placeholder for future implementation.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "subscribe_premium")
async def premium_subscribe(callback: CallbackQuery):
    """Handle premium subscription request."""
    await callback.message.edit_text("Функция оплаты временно недоступна. Попробуйте позже.")
    await callback.answer()

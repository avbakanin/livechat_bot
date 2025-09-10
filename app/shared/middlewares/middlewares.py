# from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.dispatcher.middlewares.base import BaseMiddleware as LegacyBaseMiddleware
from aiogram import BaseMiddleware as V3BaseMiddleware

# class PoolMiddleware(BaseMiddleware):
class PoolMiddleware(LegacyBaseMiddleware):
    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def __call__(self, handler, event, data):
        data["pool"] = self.pool
        return await handler(event, data)


class AccessMiddleware(V3BaseMiddleware):
    def __init__(self, allowed_ids):
        super().__init__()
        self.allowed_ids = set(int(x) for x in allowed_ids)

    async def __call__(self, handler, event, data):
        user = getattr(event, 'from_user', None)
        if user is None:
            return await handler(event, data)

        if int(user.id) not in self.allowed_ids:
            # Try to notify user depending on event type
            try:
                if hasattr(event, 'answer') and callable(getattr(event, 'answer')):
                    await event.answer("Бот приватный. Доступ ограничен.")
            except Exception:
                pass
            return

        return await handler(event, data)

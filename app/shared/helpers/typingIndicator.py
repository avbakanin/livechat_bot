import asyncio

from aiogram import Bot


class TypingIndicator:
    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id
        self._task = None

    async def __aenter__(self):
        async def run():
            while True:  # бесконечный цикл на индикатор печати
                await self.bot.send_chat_action(self.chat_id, "typing")
                await asyncio.sleep(4)  # Telegram сбрасывает индикатор через ~5 секунд

        self._task = asyncio.create_task(run())
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

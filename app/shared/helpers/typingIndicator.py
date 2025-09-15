import asyncio
import logging

from aiogram import Bot


class TypingIndicator:
    """Context manager for showing typing indicator during long operations."""

    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id
        self._task = None

    async def __aenter__(self):
        """Start typing indicator."""

        async def run():
            while True:
                try:
                    await self.bot.send_chat_action(self.chat_id, "typing")
                    await asyncio.sleep(4)  # Telegram resets indicator after ~5 seconds
                except Exception as e:
                    logging.error(f"Error sending typing indicator: {e}")
                    break

        self._task = asyncio.create_task(run())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop typing indicator."""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logging.error(f"Error stopping typing indicator: {e}")

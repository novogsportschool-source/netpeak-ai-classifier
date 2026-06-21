import asyncio
import logging
from typing import List

import aiohttp

from config import settings

logger = logging.getLogger(__name__)


def split_text(text: str, chunk_size: int = 4000) -> List[str]:
    """Розбиває текст на частини (ліміт Telegram — 4096 символів)."""
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


async def _send_message(
    session: aiohttp.ClientSession,
    url: str,
    text: str,
    use_markdown: bool = True,
) -> bool:
    """Відправка одного повідомлення з fallback на випадок невалідного Markdown."""
    payload = {"chat_id": settings.TELEGRAM_CHAT_ID, "text": text}
    if use_markdown:
        payload["parse_mode"] = "Markdown"

    async with session.post(url, json=payload) as resp:
        if resp.status == 200:
            return True
        elif use_markdown:
            # Fallback: прибираємо Markdown і пробуємо знову
            logger.warning("Markdown невалідний, відправляю без форматування")
            return await _send_message(session, url, text, use_markdown=False)
        else:
            logger.error(f"Telegram API error: {await resp.text()}")
            return False


async def send_telegram_digest(report_text: str) -> None:
    """Відправка звіту в Telegram (з чанкінгом)."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials не знайдено. Пропускаю відправку.")
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    chunks = split_text(report_text)

    async with aiohttp.ClientSession() as session:
        for i, chunk in enumerate(chunks, 1):
            if await _send_message(session, url, chunk):
                logger.info(f"Telegram: чанк {i}/{len(chunks)} відправлено")
            if i < len(chunks):
                await asyncio.sleep(0.5)  # Захист від flood control
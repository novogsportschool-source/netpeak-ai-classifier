import asyncio
import logging
from typing import Optional

import instructor
from openai import AsyncOpenAI

from config import settings
from schemas import ProcessedRequest

logger = logging.getLogger(__name__)

# Обмеження паралельності
semaphore = asyncio.Semaphore(settings.SEM_LIMIT)

# Перемикаємо клієнт на DeepSeek API
client = instructor.from_openai(
    AsyncOpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    ),
    mode=instructor.Mode.JSON,  # JSON режим чудово працює з DeepSeek
)

CLASSIFICATION_PROMPT = """
Ти — AI-асистент, який класифікує вхідні запити від внутрішніх команд AI-юніту (Netpeak).
Проаналізуй текст запиту та заповни структуру.

=== КАТЕГОРІЇ (обери РІВНО ОДНУ) ===
- automation: просять автоматизувати рутинну задачу, створити скрипт, бота, парсер
- integration: просять з'єднати дві або більше систем, налаштувати обмін даними
- analytics: потрібні дані, звіти, таблиці, дашборди, аналітика, вибірки
- support: щось зламалося, не працює, потрібна технічна підтримка, баг
- consultation: просто питання, теоретичний запит, не вимагає конкретних дій
- out_of_scope: не стосується задач AI-юніту (закупівля техніки, подяки, оффтоп)

=== ПРИОРИТЕТИ (виводь з тону й змісту) ===
- low: не терміново, "не горить", теоретичне питання, "коли буде час"
- medium: стандартна задача, середній пріоритет, є дедлайн але не горить
- high: "горить", "терміново", "сьогодні до вечора", блокує роботу інших

=== ВІДДІЛИ (target_department) ===
Визнач за контекстом: marketing, sales, analytics, hr, content, support, 
finance, smm, ops, accounting, або null якщо не зрозуміло.

=== ОЗНАКИ needs_clarification = true ===
- Запит занадто розмитий ("потрібен бот", "табличку якусь")
- Не зрозуміло, що саме треба зробити
- Не вистачає критичних деталей для початку роботи
- Запит містить лише емоції без конкретики

=== requested_actions ===
Випиши СПИСОК конкретних дій, які просять виконати. 
Якщо дій немає (подяка, питання) — поверни порожній список.

=== ТЕКСТ ЗАПИТУ ===
"{text}"
"""


async def classify_request(
    request_id: str,
    text: str,
    channel: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> Optional[dict]:
    """
    Асинхронна класифікація одного запиту через LLM.
    Повертає dict або None у разі помилки.
    """
    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model=settings.MODEL_NAME,
                response_model=ProcessedRequest,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ти AI-асистент для класифікації запитів. "
                            "Відповідай строго структуровано згідно зі схемою."
                        ),
                    },
                    {"role": "user", "content": CLASSIFICATION_PROMPT.format(text=text)},
                ],
                temperature=0.1,
            )

            result = response.model_dump()
            result["id"] = request_id

            if channel:
                result["channel"] = channel
            if timestamp:
                result["timestamp"] = timestamp

            return result

        except Exception as e:
            logger.error(f"Помилка при обробці запиту ID {request_id}: {e}")
            return None
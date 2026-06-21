import asyncio
import json
import logging
import os
from typing import List

import pandas as pd

from config import settings
from classifier import classify_request
from reporter import generate_report
from sheets import write_to_google_sheets
from telegram import send_telegram_digest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def process_batch(df: pd.DataFrame) -> List[dict]:
    """Асинхронна батчева обробка всіх запитів з rate limiting."""
    tasks = []
    for _, row in df.iterrows():
        tasks.append(
            classify_request(
                request_id=str(row["id"]),
                text=str(row["raw_text"]),
                channel=row.get("channel"),
                timestamp=str(row.get("timestamp", "")),
            )
        )

    logger.info(
        f"Запущено {len(tasks)} задач з обмеженням "
        f"{settings.SEM_LIMIT} паралельних запитів"
    )
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


async def main() -> None:
    # 1. Читання CSV
    try:
        df = pd.read_csv(settings.INPUT_CSV)
    except FileNotFoundError:
        logger.error(f"Файл {settings.INPUT_CSV} не знайдено!")
        return
    except Exception as e:
        logger.error(f"Помилка читання CSV: {e}")
        return

    required = {"id", "raw_text"}
    if not required.issubset(df.columns):
        logger.error(f"CSV повинен містити колонки {required}. Знайдено: {set(df.columns)}")
        return

    logger.info(f"📥 Знайдено {len(df)} запитів. Починаю обробку...")

    # 2. Класифікація
    valid_results = await process_batch(df)
    failed = len(df) - len(valid_results)
    if failed:
        logger.warning(f"⚠️ Не вдалося обробити {failed} запитів")

    # 3. Збереження JSON
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    json_path = os.path.join(settings.OUTPUT_DIR, "output.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(valid_results, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 Результати збережено в {json_path} ({len(valid_results)} записів)")

    # 4. Звіт
    report_path = os.path.join(settings.OUTPUT_DIR, "report.md")
    report_text = generate_report(valid_results, report_path)

    # 5. Telegram
    await send_telegram_digest(report_text)

    # 6. Google Sheets
    write_to_google_sheets(valid_results)

    logger.info("✅ Обробку завершено!")


if __name__ == "__main__":
    asyncio.run(main())
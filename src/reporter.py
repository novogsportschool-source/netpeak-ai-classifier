import logging
from datetime import datetime
from typing import List

import pandas as pd

logger = logging.getLogger(__name__)

CATEGORY_MAP = {
    "automation": "🤖 Автоматизація",
    "integration": "🔗 Інтеграція",
    "analytics": "📊 Звіт/Аналітика",
    "support": "🐛 Баг/Підтримка",
    "consultation": "❓ Питання/Консультація",
    "out_of_scope": "🚫 Поза скоупом",
}

PRIORITY_MAP = {
    "low": "🟢 Низький",
    "medium": "🟡 Середній",
    "high": "🔴 Високий",
}


def generate_report(results: List[dict], output_path: str) -> str:
    """Формує markdown-звіт з агрегатами по категоріях, пріоритетах, відділах."""
    if not results:
        logger.warning("Немає результатів для звіту")
        return ""

    df = pd.DataFrame(results)
    lines: List[str] = []

    lines.append("# 📊 Звіт по обробці запитів\n")
    lines.append(f"**Дата генерації:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"**Всього оброблено:** {len(df)} запитів\n")

    # По категоріях
    lines.append("## 📂 Розподіл за категоріями\n")
    for cat, count in df["category"].value_counts().items():
        pretty = CATEGORY_MAP.get(cat, cat)
        pct = count / len(df) * 100
        lines.append(f"- {pretty}: **{count}** ({pct:.1f}%)")
    lines.append("")

    # По пріоритетах (фіксований порядок)
    lines.append("## ⚡ Розподіл за пріоритетами\n")
    for prio in ["high", "medium", "low"]:
        if prio in df["priority"].values:
            count = int((df["priority"] == prio).sum())
            pretty = PRIORITY_MAP.get(prio, prio)
            lines.append(f"- {pretty}: **{count}**")
    lines.append("")

    # По відділах
    if "target_department" in df.columns:
        dept_df = df[df["target_department"].notna()]
        if not dept_df.empty:
            lines.append("## 🏢 Розподіл за відділами\n")
            for dept, count in dept_df["target_department"].value_counts().items():
                lines.append(f"- **{dept}**: {count}")
            lines.append("")

    # Потребує уточнення
    lines.append("## ❓ Запити, що потребують уточнення\n")
    clar_df = df[df["needs_clarification"] == True]
    if not clar_df.empty:
        for _, row in clar_df.iterrows():
            lines.append(f"- **[{row['id']}]** {row['short_summary']}")
    else:
        lines.append("_Немає запитів, що потребують уточнення_ ✅")
    lines.append("")

    # Високий пріоритет
    lines.append("## 🔴 Запити з високим пріоритетом\n")
    high_df = df[df["priority"] == "high"]
    if not high_df.empty:
        for _, row in high_df.iterrows():
            lines.append(f"- **[{row['id']}]** {row['short_summary']}")
    else:
        lines.append("_Немає термінових запитів_ ✅")

    report_text = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    logger.info(f"Звіт збережено в {output_path}")

    return report_text
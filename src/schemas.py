from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class CategoryEnum(str, Enum):
    """Категорії запитів згідно з ТЗ"""
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    ANALYTICS = "analytics"
    SUPPORT = "support"
    CONSULTATION = "consultation"
    OUT_OF_SCOPE = "out_of_scope"


class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProcessedRequest(BaseModel):
    """
    Строга схема валідації відповіді LLM.
    Обов'язкові поля — з ТЗ.
    Додаткові поля (розширення) — для кращої аналітики та дебагу.
    """
    # === Обов'язкові з ТЗ ===
    id: str = Field(description="ID запиту з оригінального CSV")
    category: CategoryEnum = Field(description="Категорія запиту")
    target_department: Optional[str] = Field(
        description="Відділ-замовник. Якщо не зрозуміло — null",
        default=None,
    )
    priority: PriorityEnum = Field(description="Пріоритет задачі")
    short_summary: str = Field(description="Суть задачі в одному реченні")
    requested_actions: List[str] = Field(
        description="Список конкретних дій, які просять виконати",
        default_factory=list,
    )
    needs_clarification: bool = Field(
        description="Чи потрібні уточнення перед взяттям в роботу",
    )

    # === Розширення схеми (чому додано — див. README) ===
    suggested_language: str = Field(
        description="Мова оригінального запиту (uk, ru, en тощо)",
    )
    reasoning: Optional[str] = Field(
        description="Коротке пояснення логіки класифікації — для дебагу",
        default=None,
    )
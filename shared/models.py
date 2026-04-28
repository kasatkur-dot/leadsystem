from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


class RawLead(BaseModel):
    """Сырой лид — выходит из Агента 2 и Агента 6, идёт в Агент 3."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str                          # avito / profi / tender_email / tg_chat / vk / hh / yandex_services / hunter_tg / hunter_vk
    flow: Optional[Literal["A", "B"]]    # A=перепланировки, B=проектирование, None=не определён
    raw_text: str                        # исходный текст сообщения/объявления
    contact: Optional[str] = None        # телефон, email, telegram username
    author_name: Optional[str] = None
    city: Optional[str] = None
    source_url: Optional[str] = None     # ссылка на источник
    source_chat: Optional[str] = None    # название чата/группы (для TG/VK)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QualifiedLead(BaseModel):
    """Квалифицированный лид — выходит из Агента 3, идёт в Агент 5."""
    id: str
    raw_lead_id: str
    source: str
    flow: Literal["A", "B"]

    # Данные после обогащения
    contact: Optional[str] = None
    contact_type: Optional[Literal["phone", "email", "telegram"]] = None
    company_name: Optional[str] = None
    city: Optional[str] = None
    object_type: Optional[str] = None   # квартира / МКД / ТЦ / склад / ангар / ИЖС
    area_m2: Optional[float] = None

    # Скоринг
    score: Literal["hot", "warm", "cold", "off"]
    score_reason: str                   # почему такой скор

    # Оффер
    offer_text: str                     # что предложить этому лиду
    recommended_action: str             # позвонить сегодня / написать в течение дня

    # Мета
    source_url: Optional[str] = None
    raw_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class OutreachLead(BaseModel):
    """Лид из Агента 6 (аутрич) — человек ответил на наш комментарий."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: Literal["telegram", "vk", "forum"]
    chat_name: str
    original_post: str                  # пост на который мы ответили
    our_reply: str                      # наш ответ
    their_response: str                 # что ответил человек
    contact: Optional[str] = None
    flow: Optional[Literal["A", "B"]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

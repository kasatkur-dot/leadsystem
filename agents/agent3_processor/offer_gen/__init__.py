"""
Агент 3 — offer_gen
Claude API → персональный текст первого сообщения под источник и поток.
+ рекомендованное действие менеджеру.
Вызывается только для hot и warm лидов (cold — стандартный шаблон).
"""
from shared.models import RawLead
from shared.logger import get_logger
from shared.llm_client import complete_text

log = get_logger("offer_gen")

_SYSTEM = """Ты — Сергей Макеев, ГИП студии ВПП (Вектор Плюс-Про), Краснодар.
Пишешь первое сообщение человеку который написал о своей задаче.

Правила:
- Тон живой, без официоза, как пишут профессионалы в мессенджерах
- 2-3 предложения максимум
- Признай задачу человека, предложи следующий шаг (созвониться / прислать ТЗ)
- Не называй цены в сообщении
- Не используй: «рад помочь», «команда профессионалов», «качественно и в срок»
- Для Потока А: фокус на согласовании, безопасности сделки, полной цепочке до ЕГРН
- Для Потока Б: фокус на опыте МКД/ТЦ, стадиях П и Р, субподряде

Отвечай только текстом сообщения, без кавычек и пояснений."""

_COLD_TEMPLATE = {
    "A": "Здравствуйте! Занимаемся перепланировками под ключ — от проекта до ЕГРН. Если понадобится помощь, пишите.",
    "B": "Здравствуйте! Делаем инженерное проектирование МКД, ТЦ, складов — стадии П и Р. Если будет задача, готовы обсудить.",
}

_ACTION_MAP = {
    "hot": "позвонить сегодня",
    "warm": "написать в течение дня",
    "cold": "отправить при возможности",
    "off": "не связываться",
}


def generate(lead: RawLead, score: str, enriched: dict, *, raise_errors: bool = False) -> tuple[str, str]:
    """Возвращает (offer_text, recommended_action)."""
    action = _ACTION_MAP.get(score, "написать в течение дня")
    flow = lead.flow or "A"

    if score in ("cold", "off"):
        return _COLD_TEMPLATE.get(flow, _COLD_TEMPLATE["A"]), action

    context_parts = [
        f"Поток: {'А — перепланировки' if flow == 'A' else 'Б — инженерное проектирование'}",
        f"Источник: {lead.source}",
    ]
    if enriched.get("city"):
        context_parts.append(f"Город: {enriched['city']}")
    if enriched.get("object_type"):
        context_parts.append(f"Тип объекта: {enriched['object_type']}")
    if enriched.get("area_m2"):
        context_parts.append(f"Площадь: {enriched['area_m2']} м²")
    context_parts.append(f"Текст лида:\n{lead.raw_text[:800]}")

    try:
        offer = complete_text(
            task="offer",
            max_tokens=200,
            temperature=0.4,
            system=_SYSTEM,
            user="\n".join(context_parts),
        )
        log.info(f"оффер готов | lead={lead.id[:8]} | {offer[:60]}")
        return offer, action
    except Exception as e:
        log.error(f"offer_gen ошибка: {e}")
        if raise_errors:
            raise
        return _COLD_TEMPLATE.get(flow, _COLD_TEMPLATE["A"]), action

"""
Агент 3 — scorer
Claude API → оценка лида: hot / warm / cold / off + причина.
Использует общий LLM-router с промптом под каждый поток (А/Б).
"""
import json

from shared.models import RawLead
from shared.logger import get_logger
from shared.llm_client import complete_text

log = get_logger("scorer")

_SYSTEM = """Ты — квалификатор лидов для инженерно-проектной студии ВПП (Вектор Плюс-Про).

Поток А — Перепланировки под ключ (физлица, вся Россия):
  hot  = человек чётко описал задачу, есть контакт, срочность или конкретный объект
  warm = интерес есть, задача размытая или нет контакта
  cold = общий вопрос, нет срочности, пассивное «интересуюсь»
  off  = нецелевой (продаёт сам, аренда, другая тема, конкурент)

Поток Б — Инженерное проектирование (B2B: МКД, ТЦ, склады, ангары, стадии П и Р):
  hot  = конкретный объект + сроки + статус (застройщик, ГИП, архитектор)
  warm = проект есть но нет деталей, или нет контакта
  cold = общий запрос на субподряд без деталей
  off  = нецелевой (технологические разделы, линейные объекты, физлицо хочет ИЖС без проекта)

Отвечай ТОЛЬКО JSON без markdown:
{"score": "hot|warm|cold|off", "reason": "одно предложение почему"}"""


def score(lead: RawLead, *, raise_errors: bool = False) -> tuple[str, str]:
    """Возвращает (score, reason). При ошибке — ('cold', 'ошибка скоринга')."""
    flow_hint = f"Поток: {'А (перепланировки)' if lead.flow == 'A' else 'Б (инженерное проектирование)'}"
    user_msg = f"{flow_hint}\nИсточник: {lead.source}\n\nТекст лида:\n{lead.raw_text[:1500]}"

    try:
        raw = complete_text(
            task="scoring",
            max_tokens=120,
            temperature=0,
            system=_SYSTEM,
            user=user_msg,
        )
        data = json.loads(raw)
        s = data.get("score", "cold")
        r = data.get("reason", "")
        if s not in ("hot", "warm", "cold", "off"):
            s = "cold"
        log.info(f"score={s} | {r[:80]} | lead={lead.id[:8]}")
        return s, r
    except Exception as e:
        log.error(f"scorer ошибка: {e} | lead={lead.id[:8]}")
        if raise_errors:
            raise
        return "cold", "ошибка скоринга"

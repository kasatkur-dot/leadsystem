"""
Агент 6 — lead_detector
Определяет интерес в ответе на наш аутрич-сообщение.
handle_reply() вызывается из tg_monitor когда кто-то ответил на наше сообщение.
Если интерес → OutreachLead → leads:outreach → Агент 5.
"""
import json
from shared.logger import get_logger
from shared.redis_client import push_outreach
from shared.models import OutreachLead
from shared.llm_client import complete_text

log = get_logger("lead_detector")

_SYSTEM = """Ты определяешь есть ли интерес к услугам компании ВПП в ответе человека.
ВПП: перепланировки + инженерное проектирование.

Высокий интерес (true):
- Задаёт уточняющий вопрос про услугу
- Просит цену, сроки, контакты
- Говорит что ему это нужно / актуально
- Предлагает созвониться или написать в ЛС

Нет интереса (false):
- Просто поблагодарил
- Отрицательный ответ («не надо», «уже нашёл», «не актуально»)
- Флуд / оффтоп

Ответь строго JSON: {"interested": true/false, "reason": "одно предложение"}"""


def _is_interested(reply_text: str, our_reply: str, flow: str) -> tuple[bool, str]:
    prompt = (
        f"Поток: {flow}\n"
        f"Наш ответ был:\n«{our_reply}»\n\n"
        f"Человек ответил:\n«{reply_text}»"
    )
    try:
        raw = complete_text(
            task="lead_detector",
            max_tokens=100,
            temperature=0,
            system=_SYSTEM,
            user=prompt,
        )
        parsed = json.loads(raw)
        return bool(parsed["interested"]), parsed.get("reason", "")
    except Exception as e:
        log.warning(f"lead_detector parse error: {e}")
        return False, "parse error"


def handle_reply(tracking: dict, reply_text: str, contact: str | None) -> None:
    """
    Вызывается из tg_monitor когда кто-то ответил на наше сообщение.
    tracking — данные из outreach:sent hash.
    """
    if not reply_text.strip():
        return

    flow = tracking.get("flow", "A")
    our_reply = tracking.get("our_reply", "")
    chat_name = tracking.get("chat_name", "")

    interested, reason = _is_interested(reply_text, our_reply, flow)
    log.info(f"lead_detector: interested={interested} [{flow}] {chat_name}: {reason}")

    if not interested:
        return

    lead = OutreachLead(
        platform="telegram",
        chat_name=chat_name,
        original_post=tracking.get("original_post", ""),
        our_reply=our_reply,
        their_response=reply_text,
        contact=contact or tracking.get("contact"),
        flow=flow,
    )
    push_outreach(lead.model_dump(mode="json"))  # mode="json" — datetime → str
    log.info(f"Лид из аутрича передан в Агент 5: {lead.id} [{flow}] {contact}")

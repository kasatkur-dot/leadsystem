"""
Агент 6 — relevance
Оценивает кандидатов из outreach:candidates (Claude Haiku, дешевле).
Порог RELEVANCE_THRESHOLD (7). Прошёл порог → responder генерирует ответ → approver.
run_once() — одна итерация. Оркестратор вызывает каждые 2 мин.
"""
import json
import uuid
from shared.logger import get_logger
from shared.redis_client import pop_outreach_candidate, push_for_approval
from config.settings import RELEVANCE_THRESHOLD
from shared.llm_client import LLMConfigError, complete_text

log = get_logger("relevance")

_SYSTEM = """Ты оцениваешь сообщения из Telegram-чатов для компании ВПП (Вектор Плюс-Про).
ВПП занимается:
- Поток А: согласование перепланировок под ключ, вся Россия
- Поток Б: инженерное проектирование (МКД, ТЦ, склады, КР/КЖ/КМ/АР/АС/ПОС)

Оцени релевантность для аутрича — насколько уместно ответить от имени ВПП.

Высокая оценка (7–10):
- Человек явно ищет исполнителя («кто делает», «посоветуйте», «нужен проектировщик»)
- Описывает конкретную задачу входящую в компетенцию ВПП
- Признаки решения о покупке (купил квартиру, начинаем стройку, нужно согласовать)

Низкая оценка (0–4):
- Общий разговор без запроса на услуги
- Уже нашёл подрядчика
- Конкурент / риелтор / спам / реклама
- Тема не по профилю ВПП

Ответь строго JSON: {"score": 0-10, "reason": "одно предложение"}"""


def _score(candidate: dict) -> tuple[int, str]:
    prompt = (
        f"Поток: {candidate.get('flow', '?')}\n"
        f"Чат: {candidate.get('chat_name', '?')}\n"
        f"Сообщение:\n{candidate.get('raw_text', '')}"
    )
    raw = complete_text(
        task="relevance",
        max_tokens=100,
        temperature=0,
        system=_SYSTEM,
        user=prompt,
    )
    try:
        parsed = json.loads(raw)
        return int(parsed["score"]), parsed.get("reason", "")
    except Exception:
        log.warning(f"Не удалось распарсить ответ relevance: {raw!r}")
        return 0, "parse error"


def run_once() -> int:
    """Обрабатывает до 10 кандидатов за вызов. Возвращает кол-во отправленных на одобрение."""
    from agents.agent6_outreach.responder import generate_reply

    sent = 0
    for _ in range(10):
        candidate = pop_outreach_candidate()
        if not candidate:
            break

        contact = candidate.get("contact") or candidate.get("author_name") or "?"
        try:
            score, reason = _score(candidate)
        except LLMConfigError as e:
            log.warning(f"LLM не настроен — пропуск relevance: {e}")
            return sent
        log.info(f"score={score} [{candidate.get('flow')}] {contact[:30]}: {reason}")

        if score < RELEVANCE_THRESHOLD:
            continue

        reply_text = generate_reply(candidate, score)
        if not reply_text:
            continue

        approval_id = str(uuid.uuid4())
        payload = {
            "id": approval_id,
            "candidate": candidate,
            "reply_text": reply_text,
            "score": score,
            "score_reason": reason,
            "status": "pending",
        }
        push_for_approval(payload)
        sent += 1
        log.info(f"→ одобрение {approval_id} (score={score}): {reply_text[:60]}")

    return sent

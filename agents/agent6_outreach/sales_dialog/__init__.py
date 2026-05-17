"""
Агент 6 — sales_dialog
Ведёт диалог по стадиям когда человек ответил на наш аутрич.
Концепция: SalesGPT (filip-michalsky, 2.5k stars) — стадийная машина состояний.
Реализация: Claude API (не LangChain).
Approver подтверждает каждый ответ перед отправкой.
"""
from typing import Literal

from shared.logger import get_logger
from shared.llm_client import complete_text

log = get_logger("sales_dialog")

Stage = Literal["intro", "qualification", "proposal", "objection", "closing", "handoff"]

STAGE_PROMPTS: dict[Stage, str] = {
    "intro": (
        "Ты — Сергей, ГИП студии ВПП (Вектор Плюс-Про). "
        "Человек только что ответил на твой комментарий в чате. "
        "Твоя задача: тепло поздороваться, коротко объяснить чем занимаешься "
        "и задать один уточняющий вопрос о задаче человека. "
        "Пиши как живой человек, без официоза, 2-3 предложения максимум."
    ),
    "qualification": (
        "Ты — Сергей из ВПП. Тебе нужно понять: "
        "1) Что за объект (квартира / МКД / коммерция), "
        "2) Какой город, "
        "3) Есть ли уже проект или нужен с нуля. "
        "Задай один конкретный вопрос. Не давай консультаций пока — только уточняй."
    ),
    "proposal": (
        "Ты — Сергей из ВПП. Ты уже понял задачу человека. "
        "Предложи конкретное решение: что именно ВПП может сделать, "
        "примерные сроки и следующий шаг (созвон / отправить ТЗ). "
        "Без цен в переписке — только предложи созвониться для расчёта. "
        "3-4 предложения, живой тон."
    ),
    "objection": (
        "Ты — Сергей из ВПП. Человек возражает или сомневается. "
        "Признай возражение, ответь конкретно и предложи следующий шаг. "
        "Без давления. 2-3 предложения."
    ),
    "closing": (
        "Ты — Сергей из ВПП. Человек готов двигаться дальше. "
        "Зафиксируй договорённость, скажи что свяжешься или попроси контакт. "
        "Коротко, тепло, конкретно."
    ),
    "handoff": (
        "Ты — Сергей из ВПП. Передаёшь диалог менеджеру. "
        "Напиши человеку что с ним скоро свяжется коллега для уточнения деталей. "
        "1-2 предложения."
    ),
}

# Ключевые слова для автоперехода между стадиями
_PROPOSAL_TRIGGERS = ["квартира", "мкд", "здание", "объект", "площадь", "адрес", "город"]
_CLOSING_TRIGGERS = ["да", "договорились", "хорошо", "окей", "ок", "созвонимся", "пишите"]
_OBJECTION_TRIGGERS = ["дорого", "не нужно", "уже есть", "подумаю", "не уверен", "может быть"]


def _next_stage(current: Stage, user_text: str) -> Stage:
    text = user_text.lower()
    if current == "intro":
        return "qualification"
    if current == "qualification":
        if any(t in text for t in _PROPOSAL_TRIGGERS):
            return "proposal"
        return "qualification"
    if current == "proposal":
        if any(t in text for t in _CLOSING_TRIGGERS):
            return "closing"
        if any(t in text for t in _OBJECTION_TRIGGERS):
            return "objection"
        return "proposal"
    if current == "objection":
        if any(t in text for t in _CLOSING_TRIGGERS):
            return "closing"
        return "objection"
    if current == "closing":
        return "handoff"
    return current


def generate_reply(
    history: list[dict],  # [{"role": "user"/"assistant", "content": "..."}]
    current_stage: Stage,
    flow: str,
) -> tuple[str, Stage]:
    """
    Генерирует ответ для текущей стадии диалога.
    Возвращает (текст_ответа, следующая_стадия).
    """
    system = STAGE_PROMPTS[current_stage]
    if flow == "B":
        system += " Контекст: инженерное проектирование (МКД, ТЦ, склады, стадии П и Р)."
    else:
        system += " Контекст: перепланировки под ключ, согласование, Краснодар."

    try:
        reply_text = complete_text(
            task="sales_dialog",
            max_tokens=300,
            temperature=0.5,
            system=system,
            messages=history,
        )

        # Определяем следующую стадию по последнему сообщению пользователя
        last_user = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
        next_stage = _next_stage(current_stage, last_user)

        log.info(f"стадия {current_stage} → {next_stage} | ответ: {reply_text[:60]}")
        return reply_text, next_stage

    except Exception as e:
        log.error(f"generate_reply ошибка: {e}")
        return "Прошу прощения, сейчас немного занят — напишу чуть позже.", current_stage

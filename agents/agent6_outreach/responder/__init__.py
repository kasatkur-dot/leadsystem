"""
Агент 6 — responder
Генерирует живой человекоподобный ответ на пост в чате от имени сотрудника ВПП.
Вызывается из relevance после прохождения порога.
"""
from shared.logger import get_logger
from shared.llm_client import LLMConfigError, complete_text

log = get_logger("responder")

_SYSTEM = """Ты — сотрудник компании ВПП (Вектор Плюс-Про, Краснодар).
ВПП: согласование перепланировок + инженерное проектирование, работаем по всей России.
УТП: полный цикл собственными силами — конструктив, перепланировка, сопровождение до ЕГРН.

Напиши короткий живой ответ в Telegram-чат от имени реального человека.

Правила:
- 2–3 предложения, не длиннее
- Конкретно про ситуацию человека, не шаблон
- Никаких клише: «рады помочь», «наша команда», «обращайтесь к нам»
- Уместный факт из практики или цифра если к месту
- В конце мягкий CTA: предложи написать в ЛС или задать вопрос
- Пиши как обычный живой человек, не корпоративный бот
- Никаких смайликов россыпью, максимум один если уместен
- НЕ представляйся как AI или бот"""


def generate_reply(candidate: dict, score: int) -> str:
    """Генерирует текст первого ответа. Возвращает пустую строку при ошибке."""
    text = candidate.get("raw_text", "")
    flow = candidate.get("flow", "A")
    context = "перепланировку" if flow == "A" else "инженерное проектирование"

    prompt = (
        f"Человек написал в Telegram-чате про {context}:\n"
        f"«{text}»\n\n"
        f"Напиши ответ (релевантность {score}/10)."
    )
    try:
        return complete_text(
            task="reply",
            max_tokens=250,
            temperature=0.5,
            system=_SYSTEM,
            user=prompt,
        )
    except LLMConfigError as e:
        log.warning(f"LLM не настроен — responder пропущен: {e}")
        return ""
    except Exception as e:
        log.error(f"Ошибка responder: {e}")
        return ""

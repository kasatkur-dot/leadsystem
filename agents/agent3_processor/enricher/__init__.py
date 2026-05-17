"""
Агент 3 — enricher
Извлекает структурированные данные из raw_text без Claude API.
Regex + справочники → город, тип объекта, площадь, контакт.
Claude API для этого не нужен — экономим токены.
"""
import re
from shared.models import RawLead
from shared.logger import get_logger

log = get_logger("enricher")

# Крупные города России (топ-50 для быстрого поиска)
_CITIES = [
    "Москва", "Санкт-Петербург", "Краснодар", "Новосибирск", "Екатеринбург",
    "Казань", "Нижний Новгород", "Челябинск", "Самара", "Омск",
    "Ростов-на-Дону", "Уфа", "Красноярск", "Воронеж", "Пермь",
    "Волгоград", "Саратов", "Тюмень", "Тольятти", "Ижевск",
    "Барнаул", "Иркутск", "Хабаровск", "Ярославль", "Владивосток",
    "Махачкала", "Томск", "Оренбург", "Кемерово", "Новокузнецк",
    "Рязань", "Астрахань", "Набережные Челны", "Пенза", "Липецк",
    "Тула", "Киров", "Ульяновск", "Чебоксары", "Брянск",
    "Курск", "Иваново", "Магнитогорск", "Тверь", "Белгород",
    "Сочи", "Анапа", "Новороссийск", "Армавир", "Ставрополь",
]
_CITY_PAT = re.compile(
    r"\b(" + "|".join(re.escape(c) for c in _CITIES) + r")\b", re.IGNORECASE
)

# Типы объектов
_OBJECT_MAP = {
    "квартира": ["квартир", "квартал", "жил.помещ"],
    "МКД": ["мкд", "многоквартирн", "жилой дом", "многоэтажн"],
    "ТЦ": ["торговый центр", " тц ", "торгово-"],
    "склад": ["склад", "складской"],
    "ангар": ["ангар"],
    "офис": ["офис", "бизнес-центр", " бц "],
    "ИЖС": ["ижс", "частный дом", "коттедж", "индивидуальн"],
    "производство": ["производственн", "завод", "цех"],
}

_PHONE_PAT = re.compile(r"(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}")
_EMAIL_PAT = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_TG_PAT = re.compile(r"@[a-zA-Z0-9_]{5,}")
_AREA_PAT = re.compile(r"(\d+[\.,]?\d*)\s*(?:кв\.?\s*м|м²|m2)", re.IGNORECASE)


def enrich(lead: RawLead) -> dict:
    """Возвращает dict с извлечёнными полями для обновления QualifiedLead."""
    text = lead.raw_text

    result: dict = {}

    # Город
    if not lead.city:
        m = _CITY_PAT.search(text)
        if m:
            result["city"] = m.group(1).capitalize()

    # Тип объекта
    t = text.lower()
    for obj_type, patterns in _OBJECT_MAP.items():
        if any(p in t for p in patterns):
            result["object_type"] = obj_type
            break

    # Площадь
    m = _AREA_PAT.search(text)
    if m:
        try:
            result["area_m2"] = float(m.group(1).replace(",", "."))
        except ValueError:
            pass

    # Контакт (если не передан из источника)
    if not lead.contact:
        phone = _PHONE_PAT.search(text)
        if phone:
            result["contact"] = phone.group().replace(" ", "").replace("-", "")
            result["contact_type"] = "phone"
        else:
            email = _EMAIL_PAT.search(text)
            if email:
                result["contact"] = email.group()
                result["contact_type"] = "email"
            else:
                tg = _TG_PAT.search(text)
                if tg:
                    result["contact"] = tg.group()
                    result["contact_type"] = "telegram"
    else:
        # Определяем тип уже известного контакта
        if "@" in lead.contact and "." in lead.contact:
            result["contact_type"] = "email"
        elif lead.contact.startswith("@"):
            result["contact_type"] = "telegram"
        else:
            result["contact_type"] = "phone"

    return result

"""
Агент 5 — notifier
Отправляет TG-уведомление менеджеру при каждом новом QualifiedLead.
🔥 горячий / ⚡ тёплый / 🤝 холодный / ❌ нецелевой
"""
import telegram
from html import escape
from telegram.constants import ParseMode

from shared.models import QualifiedLead
from shared.logger import get_logger
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_MANAGER_CHAT_ID

log = get_logger("notifier")

_EMOJI = {"hot": "🔥", "warm": "⚡", "cold": "🤝", "off": "❌"}
_FLOW_LABEL = {"A": "Перепланировка", "B": "Проектирование"}
_SOURCE_LABEL = {
    "tender_email": "Тендер (email)",
    "avito": "Avito",
    "profi": "Profi.ru",
    "tg_chat": "Telegram чат",
    "vk": "ВКонтакте",
    "hh": "HeadHunter",
    "yandex_services": "Яндекс Услуги",
    "hunter_tg": "TG Охотник",
    "hunter_vk": "VK Охотник",
    "yandex_direct": "Яндекс.Директ",
    "google_ads": "Google Ads",
    "vk_ads": "VK Ads",
    "meta_ads": "Meta Ads",
    "telegram_ads": "Telegram Ads",
    "dzen_rsy": "Дзен/РСЯ",
    "influencer_tg": "Influencer-TG",
    "seo_organic": "SEO органика",
    "referral": "Реферал",
    "outbound": "Outbound",
    "outreach_telegram": "Аутрич Telegram",
    "outreach_vk": "Аутрич VK",
    "outreach_forum": "Аутрич форум",
    "outreach_max": "Аутрич MAX",
    "outreach_tenchat": "Аутрич TenChat",
    "outreach_yandex_q": "Аутрич Яндекс Кью",
    "outreach_email": "Аутрич email",
}


def _e(value: object) -> str:
    """Escape dynamic text for Telegram HTML parse mode."""
    return escape(str(value), quote=True)


def build_message(lead: QualifiedLead) -> str:
    """Собрать Telegram-уведомление без отправки сообщения."""
    emoji = _EMOJI.get(lead.score, "📋")
    flow = _e(_FLOW_LABEL.get(lead.flow, lead.flow))
    source = _e(_SOURCE_LABEL.get(lead.source, lead.source))

    lines = [
        f"{emoji} <b>{_e(lead.score.upper())}</b> — {flow}",
        f"📍 Источник: {source}",
    ]
    if lead.traffic_channel or lead.source_type:
        channel = _e(lead.traffic_channel or "не указан")
        source_type = _e(lead.source_type or "не указан")
        lines.append(f"🧭 Канал: {channel} / {source_type}")
    if lead.first_touch_channel:
        lines.append(f"👣 Первое касание: {_e(lead.first_touch_channel)}")
    if lead.utm_source or lead.utm_campaign:
        utm_source = _e(lead.utm_source or "-")
        utm_campaign = _e(lead.utm_campaign or "-")
        lines.append(f"🏷 UTM: {utm_source} / {utm_campaign}")
    if lead.city:
        lines.append(f"🏙 Город: {_e(lead.city)}")
    if lead.object_type:
        lines.append(f"🏗 Объект: {_e(lead.object_type)}")
    if lead.area_m2:
        lines.append(f"📐 Площадь: {_e(lead.area_m2)} м²")
    if lead.contact:
        lines.append(f"📞 Контакт: <code>{_e(lead.contact)}</code>")
    if lead.company_name:
        lines.append(f"🏢 Компания: {_e(lead.company_name)}")

    lines += [
        "",
        f"<b>Причина:</b> {_e(lead.score_reason)}",
        f"<b>Действие:</b> {_e(lead.recommended_action)}",
        "",
        f"<b>Оффер:</b>\n{_e(lead.offer_text)}",
    ]

    if lead.source_url:
        url = _e(lead.source_url)
        lines.append(f'\n🔗 <a href="{url}">Источник</a>')

    lines.append(f"\n<code>ID: {_e(lead.id[:8])}</code>")
    return "\n".join(lines)


_build_message = build_message


def notify(lead: QualifiedLead) -> bool:
    """Отправить уведомление менеджеру. Возвращает True при успехе."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_MANAGER_CHAT_ID:
        log.warning("TELEGRAM_BOT_TOKEN или TELEGRAM_MANAGER_CHAT_ID не заданы")
        return False

    if lead.score == "off":
        log.debug(f"off-лид {lead.id[:8]} — уведомление не отправляем")
        return True

    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        text = build_message(lead)
        import asyncio
        asyncio.run(
            bot.send_message(
                chat_id=TELEGRAM_MANAGER_CHAT_ID,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        )
        log.info(f"уведомление отправлено | {lead.score} | {lead.id[:8]}")
        return True
    except Exception as e:
        log.error(f"notifier ошибка: {e} | lead={lead.id[:8]}")
        return False

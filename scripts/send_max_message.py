"""
Отправить сообщение в MAX/Telegram-чат через открытую линию Bitrix24.

Использование:
  python scripts/send_max_message.py --contact "Анастасия" --message "Привет!"
  python scripts/send_max_message.py --lead-id 848 --message "Уточните детали проекта"
  python scripts/send_max_message.py --list-max-leads   # показать все лиды с открытой линией

Что делает:
  1. Через старый CRM-webhook ищет лид и извлекает CHAT_ID из поля IM
  2. Через imopenlines-webhook отправляет сообщение методом
     imopenlines.bot.session.message.send
  3. Никогда не выводит токены в логи

Ограничения:
  - Работает только если контакт сам написал через MAX или Telegram (HAS_IMOL=Y)
  - CHAT_ID хранится в поле IM лида в формате imol|telegrambot|2|{ext_id}|{chat_id}
  - Если диалог закрыт на стороне Bitrix24, отправка может быть отклонена
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from fast_bitrix24 import Bitrix
from config.settings import BITRIX24_WEBHOOK_URL, BITRIX24_IMOPENLINES_WEBHOOK_URL


def _get_crm_client() -> Bitrix:
    if not BITRIX24_WEBHOOK_URL:
        raise RuntimeError("BITRIX24_WEBHOOK_URL не задан в .env")
    return Bitrix(BITRIX24_WEBHOOK_URL)


def _get_imol_client() -> Bitrix:
    if not BITRIX24_IMOPENLINES_WEBHOOK_URL:
        raise RuntimeError("BITRIX24_IMOPENLINES_WEBHOOK_URL не задан в .env")
    return Bitrix(BITRIX24_IMOPENLINES_WEBHOOK_URL)


def extract_chat_id_from_lead(lead: dict) -> str | None:
    """Извлечь CHAT_ID из поля IM лида.

    Bitrix24 хранит MAX/Telegram-диалог в формате:
      imol|telegrambot|2|{external_user_id}|{chat_id}
    Последний сегмент — это числовой chat_id открытой линии.
    """
    im_fields = lead.get("IM") or []
    if isinstance(im_fields, dict):
        im_fields = [im_fields]
    for im in im_fields:
        value = (im.get("VALUE") or "").strip()
        if value.startswith("imol|"):
            parts = value.split("|")
            if len(parts) >= 5 and parts[-1].isdigit():
                return parts[-1]
    return None


def list_imol_leads(bx: Bitrix) -> list[dict]:
    """Вернуть все лиды с открытой линией (HAS_IMOL=Y, любой источник)."""
    all_leads = bx.get_all("crm.lead.list", {
        "filter": {"HAS_IMOL": "Y"},
        "select": ["ID", "NAME", "TITLE", "SOURCE_ID", "STATUS_ID", "IM"],
    })
    if not isinstance(all_leads, list):
        all_leads = [all_leads] if all_leads else []
    return all_leads


def find_leads_by_name(bx: Bitrix, name_query: str) -> list[dict]:
    """Найти лиды с открытой линией по части имени."""
    query = name_query.lower()
    all_imol = list_imol_leads(bx)
    matched = [
        l for l in all_imol
        if query in (l.get("NAME") or "").lower()
        or query in (l.get("TITLE") or "").lower()
    ]
    return matched


def get_imol_chat(crm_bx: Bitrix, lead_id: str) -> str | None:
    """Получить CHAT_ID для лида, читая его IM-поле через CRM-webhook."""
    try:
        lead = crm_bx.call("crm.lead.get", {
            "id": int(lead_id),
            "select": ["ID", "NAME", "IM"],
        })
        if not lead:
            return None
        chat_id = extract_chat_id_from_lead(lead)
        return chat_id
    except Exception as e:
        print(f"[warn] crm.lead.get failed: {e}", file=sys.stderr)
    return None


def send_message(imol_bx: Bitrix, chat_id: str, message: str) -> dict:
    """Отправить сообщение в открытую линию через imopenlines-webhook."""
    result = imol_bx.call("imopenlines.bot.session.message.send", {
        "CHAT_ID": int(chat_id),
        "MESSAGE": message,
    })
    return {"method": "imopenlines.bot.session.message.send", "chat_id": chat_id, "result": result}


def run_list(crm_bx: Bitrix) -> int:
    leads = list_imol_leads(crm_bx)
    if not leads:
        print("Лиды с открытой линией (HAS_IMOL=Y) не найдены.")
        return 0
    print(f"Лиды с открытой линией ({len(leads)}):")
    for lead in leads:
        chat_id = extract_chat_id_from_lead(lead)
        print(
            f"  ID={lead.get('ID'):>5}  "
            f"NAME={lead.get('NAME')!r:30}  "
            f"SOURCE={lead.get('SOURCE_ID') or '?':10}  "
            f"STATUS={lead.get('STATUS_ID') or '?':10}  "
            f"chat_id={chat_id or '?'}"
        )
    return 0


def run_send(crm_bx: Bitrix, imol_bx: Bitrix, lead_id: str | None, contact: str | None, message: str) -> int:
    # Определить lead_id
    if not lead_id:
        leads = find_leads_by_name(crm_bx, contact or "")
        if not leads:
            print(f"Лид не найден по имени {contact!r} среди контактов с открытой линией.")
            print("Попробуйте --list-max-leads чтобы посмотреть все доступные лиды.")
            return 1
        if len(leads) > 1:
            print(f"Найдено {len(leads)} лидов — уточните имя или используйте --lead-id:")
            for lead in leads:
                chat_id = extract_chat_id_from_lead(lead)
                print(f"  ID={lead.get('ID')}  NAME={lead.get('NAME')!r}  chat_id={chat_id or '?'}")
            return 1
        lead_id = str(leads[0]["ID"])
        chat_id = extract_chat_id_from_lead(leads[0])
        print(f"Найден лид ID={lead_id}  NAME={leads[0].get('NAME')!r}")
    else:
        chat_id = get_imol_chat(crm_bx, lead_id)

    if not chat_id:
        print(f"CHAT_ID для лида #{lead_id} не найден в поле IM.")
        print("Возможно диалог ещё не открыт или лид создан без MAX/Telegram.")
        return 1

    print(f"CHAT_ID: {chat_id}")

    # Отправить
    result = send_message(imol_bx, chat_id, message)
    if result.get("result"):
        print(f"send_status=OK  chat_id={chat_id}")
    else:
        print(f"send_status=UNKNOWN  result={result}")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Отправить сообщение в MAX/Telegram через открытую линию Bitrix24."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--contact", help="Часть имени контакта для поиска в Bitrix24")
    group.add_argument("--lead-id", help="ID лида в Bitrix24 (если уже известен)")
    group.add_argument("--list-max-leads", action="store_true", help="Показать все лиды с открытой линией")
    parser.add_argument("--message", "-m", help="Текст сообщения")
    args = parser.parse_args(argv)

    crm_bx = _get_crm_client()

    if args.list_max_leads:
        return run_list(crm_bx)

    if not args.message:
        parser.error("--message обязателен для отправки")

    if not args.contact and not args.lead_id:
        parser.error("Укажите --contact или --lead-id")

    imol_bx = _get_imol_client()
    return run_send(crm_bx, imol_bx, args.lead_id, args.contact, args.message)


if __name__ == "__main__":
    raise SystemExit(main())

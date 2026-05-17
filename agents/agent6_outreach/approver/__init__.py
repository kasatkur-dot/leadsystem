"""
Агент 6 — approver
TG-бот для одобрения аутрич-ответов менеджером.
✅ Отправить / ✏️ Изменить / ❌ Пропустить
Таймаут 30 мин — запрос удаляется из Redis автоматически через TTL.
run() — блокирующий. Оркестратор запускает в daemon-потоке.
"""
import asyncio
import html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CallbackQueryHandler, ContextTypes,
    MessageHandler, filters,
)
from shared.logger import get_logger
from shared.redis_client import (
    pop_for_approval, push_approved,
    set_approval, get_approval, delete_approval,
    set_bot_state, get_bot_state, delete_bot_state,
)
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_MANAGER_CHAT_ID

log = get_logger("approver")

APPROVAL_TTL = 1800  # 30 минут


def _e(text: str) -> str:
    """Экранирует строку для HTML parse_mode."""
    return html.escape(str(text))


async def _send_approval_message(bot, payload: dict) -> None:
    cand = payload["candidate"]
    contact = _e(cand.get("contact") or cand.get("author_name") or "неизвестный")
    flow = _e(cand.get("flow", "?"))
    chat_name = _e(cand.get("chat_name", "?"))
    original = _e(cand.get("raw_text", "")[:400])
    reply_text = _e(payload["reply_text"])
    approval_id = payload["id"]

    text = (
        f"🤝 <b>Аутрич [{flow}]</b> — одобрить ответ?\n\n"
        f"<b>Чат:</b> {chat_name}\n"
        f"<b>Автор:</b> {contact}\n\n"
        f"<b>Исходный пост:</b>\n{original}\n\n"
        f"<b>Предлагаемый ответ:</b>\n{reply_text}"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Отправить", callback_data=f"approve:{approval_id}"),
        InlineKeyboardButton("✏️ Изменить", callback_data=f"edit:{approval_id}"),
        InlineKeyboardButton("❌ Пропустить", callback_data=f"reject:{approval_id}"),
    ]])

    msg = await bot.send_message(
        chat_id=TELEGRAM_MANAGER_CHAT_ID,
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    payload["tg_message_id"] = msg.message_id
    set_approval(approval_id, payload, ttl=APPROVAL_TTL)
    log.info(f"Запрос одобрения отправлен: {approval_id} [{cand.get('flow')}] {cand.get('contact')}")


async def _callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action, approval_id = query.data.split(":", 1)

    payload = get_approval(approval_id)
    if not payload:
        await query.edit_message_text("⏰ Запрос истёк (30 мин).")
        return

    if action == "approve":
        payload["status"] = "approved"
        push_approved(payload)
        delete_approval(approval_id)
        await query.edit_message_text("✅ Одобрено — отправляем.")
        log.info(f"Одобрено: {approval_id}")

    elif action == "reject":
        delete_approval(approval_id)
        await query.edit_message_text("❌ Пропущено.")
        log.info(f"Отклонено: {approval_id}")

    elif action == "edit":
        set_bot_state(query.message.chat_id, {"action": "editing", "approval_id": approval_id})
        current_text = _e(payload["reply_text"])
        await query.edit_message_text(
            f"✏️ Отправь новый текст ответа (или /cancel чтобы отменить).\n\n"
            f"Текущий:\n{current_text}",
            parse_mode="HTML",
        )


async def _text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Ловит текст от менеджера когда бот ожидает отредактированный ответ."""
    if not update.message or not update.effective_chat:
        return
    chat_id = update.effective_chat.id

    state = get_bot_state(chat_id)
    if not state or state.get("action") != "editing":
        return

    approval_id = state["approval_id"]
    new_text = update.message.text.strip()

    if new_text == "/cancel":
        delete_bot_state(chat_id)
        await update.message.reply_text("Отменено.")
        return

    payload = get_approval(approval_id)
    if not payload:
        delete_bot_state(chat_id)
        await update.message.reply_text("⏰ Запрос истёк, нельзя изменить.")
        return

    payload["reply_text"] = new_text
    payload["status"] = "approved"
    push_approved(payload)
    delete_approval(approval_id)
    delete_bot_state(chat_id)
    await update.message.reply_text("✅ Сохранено — отправляем с новым текстом.")
    log.info(f"Отредактировано и одобрено: {approval_id}")


async def _queue_poller(bot) -> None:
    """Фоновая задача: перекачивает из Redis-очереди в TG."""
    while True:
        payload = pop_for_approval()
        if payload:
            try:
                await _send_approval_message(bot, payload)
            except Exception as e:
                log.error(f"Ошибка отправки одобрения: {e}")
        await asyncio.sleep(5)


def run() -> None:
    """Запускает TG-бота (блокирующий). Оркестратор вызывает в daemon-потоке."""
    if not TELEGRAM_BOT_TOKEN:
        log.warning("TELEGRAM_BOT_TOKEN не задан — approver не запущен")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(_callback_handler))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Chat(chat_id=TELEGRAM_MANAGER_CHAT_ID),
        _text_handler,
    ))

    async def post_init(application: Application) -> None:
        asyncio.create_task(_queue_poller(application.bot))

    app.post_init = post_init
    log.info("Approver бот запущен")
    app.run_polling(drop_pending_updates=True)

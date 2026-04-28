"""
Оркестратор — запускает всех агентов по расписанию.
Запуск: python orchestrator/scheduler.py
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR
from shared.logger import get_logger
from shared.db import init_db
from shared import redis_client

log = get_logger("orchestrator")
scheduler = BlockingScheduler(timezone="Europe/Moscow")


# ── Агент 2: Коллектор ───────────────────────────────────────────────────────

def run_tender_collector():
    log.info("Запуск тендерного субагента")
    from agents.agent2_collector.tender.collector import run
    run()

def run_avito_collector():
    log.info("Запуск Avito-субагента")
    # from agents.agent2_collector.avito.collector import run
    # run()

def run_profi_collector():
    log.info("Запуск Profi-субагента")


# ── Агент 3: Процессор ───────────────────────────────────────────────────────

def run_processor():
    log.info("Запуск процессора лидов")
    from agents.agent3_processor.processor import run
    run()


# ── Агент 5: CRM-роутер ──────────────────────────────────────────────────────

def run_crm_router():
    log.info("Запуск CRM-роутера")
    from agents.agent5_crm.router import run
    run()


# ── Агент 6: Аутрич + Hunter ─────────────────────────────────────────────────

def run_tg_monitor():
    log.info("Запуск TG-монитора (Агент 6)")
    # from agents.agent6_outreach.monitor.tg_monitor import run
    # run()

def run_hunter():
    log.info("Запуск Hunter-субагента (Агент 6)")


# ── Расписание ────────────────────────────────────────────────────────────────

def setup_schedule():
    # Тендеры — каждые 2 часа
    scheduler.add_job(run_tender_collector, "interval", hours=2, id="tender")

    # Процессор — каждые 30 минут (обрабатывает что накопилось в Redis)
    scheduler.add_job(run_processor, "interval", minutes=30, id="processor")

    # CRM-роутер — каждые 30 минут
    scheduler.add_job(run_crm_router, "interval", minutes=30, id="crm_router")

    # Avito — каждые 4 часа (Волна 2)
    # scheduler.add_job(run_avito_collector, "interval", hours=4, id="avito")

    # TG-монитор — непрерывный (запускается отдельно через asyncio)
    # Hunter — 1 раз в день в 9:00
    scheduler.add_job(run_hunter, "cron", hour=9, minute=0, id="hunter")


# ── Обработка ошибок ──────────────────────────────────────────────────────────

def on_error(event):
    log.error(f"Агент упал: {event.job_id} — {event.exception}")

scheduler.add_listener(on_error, EVENT_JOB_ERROR)


# ── Точка входа ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("Инициализация базы данных...")
    init_db()

    log.info(f"Redis: {'OK' if redis_client.ping() else 'НЕДОСТУПЕН — проверь Redis'}")
    log.info(f"Очереди: {redis_client.queue_sizes()}")

    setup_schedule()
    log.info("Оркестратор запущен. Агенты по расписанию.")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        log.info("Оркестратор остановлен.")

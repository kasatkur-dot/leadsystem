"""
Оркестратор — запускает всех агентов по расписанию.
Запуск: python -m orchestrator.scheduler
"""
import threading
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR
from shared.logger import get_logger
from shared.db import init_db
from shared import redis_client

log = get_logger("orchestrator")
scheduler = BlockingScheduler(timezone="Europe/Moscow")


# ── Агент 2: Коллектор ───────────────────────────────────────────────────────

def run_tender_collector():
    from agents.agent2_collector.tender_collector import run
    n = run()
    log.info(f"tender_collector: {n} новых лидов")

def run_avito_collector():
    pass  # Волна 2
    # from agents.agent2_collector.avito_collector import run; run()

def run_profi_collector():
    pass  # Волна 2


# ── Агент 3: Процессор ───────────────────────────────────────────────────────

def run_processor():
    from agents.agent3_processor import run
    n = run()
    log.info(f"processor: {n} лидов обработано")


# ── Агент 5: CRM-роутер ──────────────────────────────────────────────────────

def run_crm_router():
    from agents.agent5_crm import run
    n = run()
    log.info(f"crm_router: {n} лидов в Bitrix24")


# ── Агент 6: TG-мониторинг (отдельный поток, не APScheduler) ────────────────

def start_tg_monitor():
    """Запускает Telethon мониторинг в отдельном daemon-потоке."""
    def _target():
        try:
            from agents.agent6_outreach.tg_monitor import run
            run()
        except Exception as e:
            log.error(f"tg_monitor упал: {e}")

    t = threading.Thread(target=_target, name="tg_monitor", daemon=True)
    t.start()
    log.info("tg_monitor запущен в фоне")


def start_approver():
    """Запускает TG-бот одобрения аутрич-ответов в daemon-потоке."""
    def _target():
        try:
            from agents.agent6_outreach.approver import run
            run()
        except Exception as e:
            log.error(f"approver упал: {e}")

    t = threading.Thread(target=_target, name="approver", daemon=True)
    t.start()
    log.info("approver запущен в фоне")


def start_sender():
    """Запускает Telethon sender в daemon-потоке."""
    def _target():
        try:
            from agents.agent6_outreach.sender import run
            run()
        except Exception as e:
            log.error(f"sender упал: {e}")

    t = threading.Thread(target=_target, name="sender", daemon=True)
    t.start()
    log.info("sender запущен в фоне")


# ── Агент 6: Пайплайн оценки (APScheduler) ──────────────────────────────────

def run_relevance_pipeline():
    from agents.agent6_outreach.relevance import run_once
    n = run_once()
    if n:
        log.info(f"relevance: {n} кандидатов отправлено на одобрение")


# ── Расписание ────────────────────────────────────────────────────────────────

def setup_schedule():
    # Тендерные письма — каждые 15 минут
    scheduler.add_job(run_tender_collector, "interval", minutes=15, id="tender_collector")

    # Процессор лидов — каждые 5 минут
    scheduler.add_job(run_processor, "interval", minutes=5, id="processor")

    # CRM-роутер — каждые 5 минут (после процессора)
    scheduler.add_job(run_crm_router, "interval", minutes=5, id="crm_router")

    # Оценка кандидатов аутрича — каждые 2 минуты
    scheduler.add_job(run_relevance_pipeline, "interval", minutes=2, id="relevance_pipeline")

    # Avito — каждые 4 часа (Волна 2, раскомментировать позже)
    # scheduler.add_job(run_avito_collector, "interval", hours=4, id="avito_collector")


# ── Обработка ошибок ──────────────────────────────────────────────────────────

def on_error(event):
    log.error(f"агент упал: {event.job_id} — {event.exception}")

scheduler.add_listener(on_error, EVENT_JOB_ERROR)


# ── Точка входа ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("Инициализация базы данных...")
    init_db()

    redis_ok = redis_client.ping()
    log.info(f"Redis: {'OK' if redis_ok else 'НЕДОСТУПЕН — проверь Redis!'}")
    log.info(f"Очереди: {redis_client.queue_sizes()}")
    log.info(f"Blocklist: {redis_client.blocklist_size()} записей")

    start_tg_monitor()
    start_approver()
    start_sender()
    setup_schedule()

    log.info("Оркестратор запущен.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        log.info("Оркестратор остановлен.")

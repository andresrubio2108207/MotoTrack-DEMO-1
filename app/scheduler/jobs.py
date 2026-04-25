"""Scheduler de tareas: job diario para revisar mantenimientos y generar alertas."""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def check_maintenance_and_generate_alerts():
    """
    Job diario que revisa todos los mantenimientos programados
    y genera alertas automáticas cuando corresponde.
    """
    try:
        from app.database.engine import SessionLocal
        from app.services.alert_service import generate_alerts_all_motorcycles

        db = SessionLocal()
        try:
            count = generate_alerts_all_motorcycles(db)
            if count > 0:
                logger.info(f"Scheduler: {count} alerta(s) generada(s) automáticamente.")
            else:
                logger.debug("Scheduler: sin nuevas alertas que generar.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error en job de scheduler: {e}")


def start_scheduler():
    """Inicia el scheduler con el job de revisión diaria."""
    global _scheduler
    if _scheduler and _scheduler.running:
        logger.warning("El scheduler ya está en ejecución.")
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        func=check_maintenance_and_generate_alerts,
        trigger=IntervalTrigger(hours=24),
        id="daily_alert_check",
        name="Revisión diaria de mantenimientos",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler iniciado. Job diario registrado.")

    # Ejecutar inmediatamente al iniciar para capturar alertas pendientes
    check_maintenance_and_generate_alerts()


def stop_scheduler():
    """Detiene el scheduler de manera segura."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler detenido.")

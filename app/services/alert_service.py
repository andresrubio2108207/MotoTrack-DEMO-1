"""Servicio de alertas: creación, listado, resolución y generación automática."""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.maintenance import Maintenance
from app.models.motorcycle import Motorcycle


def create_alert(
    db: Session,
    motorcycle_id: int,
    message: str,
    due_date: Optional[datetime] = None,
    due_km: Optional[float] = None,
) -> Alert:
    """
    Crea una nueva alerta para una motocicleta.

    Args:
        db: Sesión de base de datos.
        motorcycle_id: ID de la motocicleta.
        message: Mensaje descriptivo de la alerta.
        due_date: Fecha límite para la alerta.
        due_km: Kilómetros límite para la alerta.

    Returns:
        El objeto Alert creado.
    """
    alert = Alert(
        motorcycle_id=motorcycle_id,
        message=message,
        due_date=due_date,
        due_km=due_km,
        resolved=False,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_active_alerts(db: Session, motorcycle_id: int) -> List[Alert]:
    """
    Retorna todas las alertas activas (no resueltas) de una motocicleta,
    ordenadas por fecha de creación descendente.
    """
    return (
        db.query(Alert)
        .filter(
            Alert.motorcycle_id == motorcycle_id,
            Alert.resolved == False,  # noqa: E712
        )
        .order_by(Alert.created_at.desc())
        .all()
    )


def get_all_alerts(db: Session, motorcycle_id: int) -> List[Alert]:
    """Retorna todas las alertas (activas y resueltas) de una motocicleta."""
    return (
        db.query(Alert)
        .filter(Alert.motorcycle_id == motorcycle_id)
        .order_by(Alert.created_at.desc())
        .all()
    )


def resolve_alert(db: Session, alert_id: int) -> Optional[Alert]:
    """
    Marca una alerta como resuelta.

    Returns:
        El objeto Alert actualizado o None si no existe.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
    alert.resolved = True
    db.commit()
    db.refresh(alert)
    return alert


def generate_alerts_for_motorcycle(db: Session, motorcycle_id: int) -> List[Alert]:
    """
    Genera alertas automáticas basadas en los mantenimientos programados.
    Revisa si la fecha o los km del próximo mantenimiento están próximos.

    Returns:
        Lista de alertas creadas.
    """
    created_alerts: List[Alert] = []
    now = datetime.utcnow()
    warning_days = 7   # Días de anticipación para alertar por fecha
    warning_km = 500   # Km de anticipación para alertar por km

    moto = db.query(Motorcycle).filter(Motorcycle.id == motorcycle_id).first()
    if not moto:
        return created_alerts

    # Obtener mantenimientos completados con próxima fecha/km programada
    maintenances = (
        db.query(Maintenance)
        .filter(
            Maintenance.motorcycle_id == motorcycle_id,
            Maintenance.completed == True,  # noqa: E712
        )
        .all()
    )

    for maint in maintenances:
        # Alerta por fecha próxima
        if maint.next_date and maint.next_date <= now + timedelta(days=warning_days):
            existing = db.query(Alert).filter(
                Alert.motorcycle_id == motorcycle_id,
                Alert.message.contains(maint.type),
                Alert.resolved == False,  # noqa: E712
            ).first()
            if not existing:
                alert = create_alert(
                    db=db,
                    motorcycle_id=motorcycle_id,
                    message=f"⏰ Próximo {maint.type} programado para {maint.next_date.strftime('%d/%m/%Y')}",
                    due_date=maint.next_date,
                )
                created_alerts.append(alert)

        # Alerta por km próximos
        if maint.next_km and moto.current_km >= maint.next_km - warning_km:
            existing = db.query(Alert).filter(
                Alert.motorcycle_id == motorcycle_id,
                Alert.message.contains(maint.type),
                Alert.resolved == False,  # noqa: E712
            ).first()
            if not existing:
                alert = create_alert(
                    db=db,
                    motorcycle_id=motorcycle_id,
                    message=f"🔧 {maint.type} requerido a los {maint.next_km:.0f} km (actual: {moto.current_km:.0f} km)",
                    due_km=maint.next_km,
                )
                created_alerts.append(alert)

    return created_alerts


def generate_alerts_all_motorcycles(db: Session) -> int:
    """
    Genera alertas para todas las motocicletas registradas.

    Returns:
        Número total de alertas creadas.
    """
    total = 0
    motorcycles = db.query(Motorcycle).all()
    for moto in motorcycles:
        alerts = generate_alerts_for_motorcycle(db, moto.id)
        total += len(alerts)
    return total

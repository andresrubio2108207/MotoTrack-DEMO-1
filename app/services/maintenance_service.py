"""Servicio de mantenimientos: creación, historial, completar y próximo mantenimiento."""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.maintenance import Maintenance
from app.models.motorcycle import Motorcycle

# Intervalos de mantenimiento por tipo (km y días)
MAINTENANCE_INTERVALS = {
    "Cambio de aceite": {"km": 3000, "days": 90},
    "Revisión de frenos": {"km": 5000, "days": 180},
    "Cambio de filtro de aire": {"km": 8000, "days": 365},
    "Revisión de cadena": {"km": 1500, "days": 30},
    "Cambio de bujías": {"km": 10000, "days": 365},
    "Revisión general": {"km": 10000, "days": 365},
    "Cambio de neumáticos": {"km": 20000, "days": 730},
}


def create_maintenance(
    db: Session,
    motorcycle_id: int,
    maintenance_type: str,
    km: float,
    description: str = "",
    date: Optional[datetime] = None,
) -> Maintenance:
    """
    Crea un nuevo registro de mantenimiento.

    Args:
        db: Sesión de base de datos.
        motorcycle_id: ID de la motocicleta.
        maintenance_type: Tipo de mantenimiento.
        km: Kilómetros actuales al momento del mantenimiento.
        description: Descripción adicional.
        date: Fecha del mantenimiento (por defecto: ahora).

    Returns:
        El objeto Maintenance creado.
    """
    maintenance_date = date or datetime.utcnow()
    interval = MAINTENANCE_INTERVALS.get(maintenance_type, {"km": 5000, "days": 180})

    next_km = km + interval["km"]
    next_date = maintenance_date + timedelta(days=interval["days"])

    maintenance = Maintenance(
        motorcycle_id=motorcycle_id,
        type=maintenance_type,
        date=maintenance_date,
        km=km,
        description=description,
        completed=True,
        next_km=next_km,
        next_date=next_date,
    )
    db.add(maintenance)

    # Actualizar km de la motocicleta
    moto = db.query(Motorcycle).filter(Motorcycle.id == motorcycle_id).first()
    if moto and km > moto.current_km:
        moto.current_km = km

    db.commit()
    db.refresh(maintenance)
    return maintenance


def get_maintenance_history(db: Session, motorcycle_id: int) -> List[Maintenance]:
    """
    Retorna el historial completo de mantenimientos de una motocicleta,
    ordenado por fecha descendente.
    """
    return (
        db.query(Maintenance)
        .filter(Maintenance.motorcycle_id == motorcycle_id)
        .order_by(Maintenance.date.desc())
        .all()
    )


def complete_maintenance(db: Session, maintenance_id: int) -> Optional[Maintenance]:
    """
    Marca un mantenimiento como completado.

    Returns:
        El Maintenance actualizado o None si no se encontró.
    """
    maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
    if not maintenance:
        return None
    maintenance.completed = True
    db.commit()
    db.refresh(maintenance)
    return maintenance


def calculate_next_maintenance(maintenance_type: str, last_km: float, last_date: datetime) -> dict:
    """
    Calcula cuándo debería realizarse el próximo mantenimiento.

    Returns:
        Diccionario con 'next_km' y 'next_date'.
    """
    interval = MAINTENANCE_INTERVALS.get(maintenance_type, {"km": 5000, "days": 180})
    return {
        "next_km": last_km + interval["km"],
        "next_date": last_date + timedelta(days=interval["days"]),
    }


def get_pending_maintenances(db: Session, motorcycle_id: int) -> List[Maintenance]:
    """Retorna mantenimientos pendientes (no completados) de una motocicleta."""
    return (
        db.query(Maintenance)
        .filter(
            Maintenance.motorcycle_id == motorcycle_id,
            Maintenance.completed == False,  # noqa: E712
        )
        .order_by(Maintenance.date.asc())
        .all()
    )

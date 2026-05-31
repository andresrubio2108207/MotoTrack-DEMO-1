from __future__ import annotations

from datetime import datetime
from typing import Any

from app.database.engine import session_scope
from app.models import Maintenance, Motorcycle


def _sync_motorcycle_km_from_history(session, motorcycle_id: int) -> None:
    motorcycle = session.get(Motorcycle, motorcycle_id)
    if motorcycle is None:
        return

    max_history_km = (
        session.query(Maintenance)
        .filter(Maintenance.motorcycle_id == motorcycle_id)
        .order_by(Maintenance.km_at_service.desc())
        .first()
    )
    if max_history_km is not None:
        motorcycle.current_km = max(float(motorcycle.current_km or 0), float(max_history_km.km_at_service or 0))


def create_maintenance(
    motorcycle_id: int,
    type: str,
    km_at_service: float,
    service_date: datetime,
    description: str | None = None,
    cost: float = 0.0,
    next_service_km: float | None = None,
    next_service_date: datetime | None = None,
) -> Maintenance:
    with session_scope() as session:
        motorcycle = session.get(Motorcycle, motorcycle_id)
        if motorcycle is None:
            raise ValueError("La motocicleta no existe.")

        maintenance = Maintenance(
            motorcycle_id=motorcycle_id,
            type=type.strip(),
            description=description.strip() if description else None,
            km_at_service=float(km_at_service),
            cost=float(cost),
            service_date=service_date,
            next_service_km=float(next_service_km) if next_service_km is not None else None,
            next_service_date=next_service_date,
        )
        session.add(maintenance)

        if motorcycle.current_km is None or float(km_at_service) > motorcycle.current_km:
            motorcycle.current_km = float(km_at_service)

        session.flush()
        session.refresh(maintenance)
        return maintenance


def list_maintenances(motorcycle_id: int) -> list[Maintenance]:
    with session_scope() as session:
        return (
            session.query(Maintenance)
            .filter(Maintenance.motorcycle_id == motorcycle_id)
            .order_by(Maintenance.service_date.desc(), Maintenance.id.desc())
            .all()
        )


def get_maintenance(maintenance_id: int) -> Maintenance | None:
    with session_scope() as session:
        return session.get(Maintenance, maintenance_id)


def update_maintenance(maintenance_id: int, **changes: Any) -> Maintenance:
    with session_scope() as session:
        maintenance = session.get(Maintenance, maintenance_id)
        if maintenance is None:
            raise ValueError("El mantenimiento no existe.")

        for field in (
            "type",
            "description",
            "km_at_service",
            "cost",
            "service_date",
            "next_service_km",
            "next_service_date",
        ):
            if field in changes:
                setattr(maintenance, field, changes[field])

        _sync_motorcycle_km_from_history(session, maintenance.motorcycle_id)

        session.flush()
        session.refresh(maintenance)
        return maintenance


def delete_maintenance(maintenance_id: int) -> bool:
    with session_scope() as session:
        maintenance = session.get(Maintenance, maintenance_id)
        if maintenance is None:
            return False
        motorcycle_id = maintenance.motorcycle_id
        session.delete(maintenance)
        session.flush()
        _sync_motorcycle_km_from_history(session, motorcycle_id)
        return True

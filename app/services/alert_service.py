from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.database.engine import session_scope
from app.models import Alert, Motorcycle


VALID_TRIGGER_TYPES = {"km", "date"}


def _as_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def create_alert(
    motorcycle_id: int,
    title: str,
    trigger_type: str,
    trigger_km: float | None = None,
    trigger_date: datetime | None = None,
    is_active: bool = True,
) -> Alert:
    normalized_trigger_type = trigger_type.strip().lower()
    if normalized_trigger_type not in VALID_TRIGGER_TYPES:
        raise ValueError("El tipo de alerta debe ser 'km' o 'date'.")

    with session_scope() as session:
        motorcycle = session.get(Motorcycle, motorcycle_id)
        if motorcycle is None:
            raise ValueError("La motocicleta no existe.")

        alert = Alert(
            motorcycle_id=motorcycle_id,
            title=title.strip(),
            trigger_type=normalized_trigger_type,
            trigger_km=float(trigger_km) if trigger_km is not None else None,
            trigger_date=trigger_date,
            is_active=is_active,
        )
        session.add(alert)
        session.flush()
        session.refresh(alert)
        return alert


def list_alerts(motorcycle_id: int | None = None, active_only: bool = False) -> list[Alert]:
    with session_scope() as session:
        query = session.query(Alert)
        if motorcycle_id is not None:
            query = query.filter(Alert.motorcycle_id == motorcycle_id)
        if active_only:
            query = query.filter(Alert.is_active.is_(True))
        return query.order_by(Alert.created_at.desc(), Alert.id.desc()).all()


def get_alert(alert_id: int) -> Alert | None:
    with session_scope() as session:
        return session.get(Alert, alert_id)


def update_alert(alert_id: int, **changes: Any) -> Alert:
    with session_scope() as session:
        alert = session.get(Alert, alert_id)
        if alert is None:
            raise ValueError("La alerta no existe.")

        if "trigger_type" in changes and changes["trigger_type"] is not None:
            normalized_trigger_type = str(changes["trigger_type"]).strip().lower()
            if normalized_trigger_type not in VALID_TRIGGER_TYPES:
                raise ValueError("El tipo de alerta debe ser 'km' o 'date'.")
            alert.trigger_type = normalized_trigger_type

        for field in ("title", "trigger_km", "trigger_date", "is_active", "is_fired"):
            if field in changes:
                setattr(alert, field, changes[field])

        session.flush()
        session.refresh(alert)
        return alert


def delete_alert(alert_id: int) -> bool:
    with session_scope() as session:
        alert = session.get(Alert, alert_id)
        if alert is None:
            return False
        session.delete(alert)
        return True


def evaluate_alerts(reference_date: datetime | None = None) -> list[Alert]:
    current_date = _as_utc_datetime(reference_date or datetime.now(timezone.utc))

    with session_scope() as session:
        alerts = (
            session.query(Alert)
            .join(Motorcycle, Motorcycle.id == Alert.motorcycle_id)
            .filter(Alert.is_active.is_(True), Alert.is_fired.is_(False))
            .all()
        )

        fired_alerts: list[Alert] = []
        for alert in alerts:
            should_fire = False

            if alert.trigger_type == "km" and alert.trigger_km is not None:
                should_fire = (alert.motorcycle.current_km or 0) >= alert.trigger_km
            elif alert.trigger_type == "date" and alert.trigger_date is not None:
                should_fire = _as_utc_datetime(alert.trigger_date) <= current_date

            if should_fire:
                alert.is_fired = True
                fired_alerts.append(alert)

        session.flush()
        for alert in fired_alerts:
            session.refresh(alert)
        return fired_alerts

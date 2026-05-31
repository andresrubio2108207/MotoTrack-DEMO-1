from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.database.engine import session_scope
from app.models import Alert, Motorcycle


VALID_TRIGGER_TYPES = {"km", "date", "both"}
MAINTENANCE_INTERVALS = {
    "Aceite y filtro de aceite": {"km": 3000, "icon": "OPACITY_ROUNDED", "color": "#E24B4A"},
    "Filtro de aire": {"km": 5000, "icon": "FILTER_ALT_ROUNDED", "color": "#BA7517"},
    "Líquido de frenos": {"km": 10000, "icon": "DISC_FULL_ROUNDED", "color": "#BA7517"},
    "Bujías": {"km": 8000, "icon": "BOLT_ROUNDED", "color": "#BA7517"},
    "Cadena (limpieza/ajuste)": {"km": 1000, "icon": "SETTINGS_INPUT_COMPONENT_ROUNDED", "color": "#1D9E75"},
    "Cadena (reemplazo)": {"km": 15000, "icon": "SETTINGS_INPUT_COMPONENT_ROUNDED", "color": "#E24B4A"},
    "Llantas": {"km": 20000, "icon": "TIRE_REPAIR_ROUNDED", "color": "#E24B4A"},
    "Revisión general": {"km": 6000, "icon": "BUILD_CIRCLE_OUTLINED", "color": "#1B5162"},
}

_INTERVAL_ALIASES = {
    "Aceite y filtro de aceite": ("aceite", "filtro de aceite"),
    "Filtro de aire": ("filtro de aire", "aire"),
    "Líquido de frenos": ("liquido de frenos", "líquido de frenos", "frenos"),
    "Bujías": ("bujia", "bujía", "bujias", "bujías"),
    "Cadena (limpieza/ajuste)": ("cadena", "limpieza", "ajuste"),
    "Cadena (reemplazo)": ("reemplazo de cadena", "cambio cadena", "cadena reemplazo"),
    "Llantas": ("llanta", "llantas", "neumatico", "neumático"),
    "Revisión general": ("revision", "revisión", "general"),
}


def _as_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_text(value: str) -> str:
    replacements = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")
    return value.translate(replacements).strip().lower()


def _history_item_value(item: Any, *names: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        for name in names:
            if name in item:
                return item[name]
        return default

    for name in names:
        if hasattr(item, name):
            return getattr(item, name)
    return default


def _matches_interval(maintenance_type: str, interval_name: str) -> bool:
    normalized_type = _normalize_text(maintenance_type)
    if _normalize_text(interval_name) in normalized_type:
        return True
    return any(_normalize_text(alias) in normalized_type for alias in _INTERVAL_ALIASES.get(interval_name, ()))


def calcular_alertas(
    km_actual: int,
    historial: list[dict],
    intervalos: dict = MAINTENANCE_INTERVALS,
) -> list[dict]:
    """
    Retorna alertas inteligentes por kilometraje para cada intervalo base.
    """
    alertas: list[dict] = []

    for tipo, config in intervalos.items():
        intervalo = int(config["km"])
        km_ultimo = 0

        for mantenimiento in historial:
            maintenance_type = str(_history_item_value(mantenimiento, "type", "tipo", "title", default=""))
            if not _matches_interval(maintenance_type, tipo):
                continue
            km_service = int(float(_history_item_value(mantenimiento, "km_at_service", "km", "km_ultimo", default=0) or 0))
            km_ultimo = max(km_ultimo, km_service)

        km_desde_ultimo = max(0, int(km_actual) - km_ultimo)
        km_restantes = intervalo - km_desde_ultimo

        if km_desde_ultimo >= intervalo:
            estado = "VENCIDO"
        elif km_desde_ultimo >= intervalo * 0.85:
            estado = "PRÓXIMO"
        else:
            estado = "AL DÍA"

        alertas.append(
            {
                "tipo": tipo,
                "estado": estado,
                "km_actual": int(km_actual),
                "km_ultimo": km_ultimo,
                "km_desde_ultimo": km_desde_ultimo,
                "km_restantes": int(km_restantes),
                "intervalo": intervalo,
                "icon": str(config["icon"]),
                "color": str(config["color"]),
            }
        )

    return alertas


def filtrar_alertas_activas(alertas: list[dict]) -> list[dict]:
    orden = {"VENCIDO": 0, "PRÓXIMO": 1}
    return sorted(
        [alerta for alerta in alertas if alerta.get("estado") in orden],
        key=lambda alerta: (orden[str(alerta["estado"])], int(alerta.get("km_restantes", 0))),
    )


def contar_por_estado(alertas: list[dict]) -> dict[str, int]:
    counts = {"VENCIDO": 0, "PRÓXIMO": 0, "AL DÍA": 0}
    for alerta in alertas:
        estado = str(alerta.get("estado", ""))
        if estado in counts:
            counts[estado] += 1
    return counts


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
        raise ValueError("El tipo de alerta debe ser 'km', 'date' o 'both'.")

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
                raise ValueError("El tipo de alerta debe ser 'km', 'date' o 'both'.")
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
            elif alert.trigger_type == "both":
                km_due = alert.trigger_km is not None and (alert.motorcycle.current_km or 0) >= alert.trigger_km
                date_due = alert.trigger_date is not None and _as_utc_datetime(alert.trigger_date) <= current_date
                should_fire = km_due or date_due

            if should_fire:
                alert.is_fired = True
                fired_alerts.append(alert)

        session.flush()
        for alert in fired_alerts:
            session.refresh(alert)
        return fired_alerts

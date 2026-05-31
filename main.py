from __future__ import annotations

import os
from datetime import datetime, timezone

import flet as ft
from dotenv import load_dotenv

from app.database.engine import configure_database, get_database_url, init_db
from app.database.seed import seed_database
from app.services.alert_service import (
    MAINTENANCE_INTERVALS,
    calcular_alertas,
    contar_por_estado,
    create_alert,
    delete_alert,
    evaluate_alerts,
    filtrar_alertas_activas,
    list_alerts,
    update_alert,
)
from app.services.auth_service import (
    add_motorcycle,
    authenticate_user,
    delete_motorcycle,
    get_user_by_id,
    list_user_motorcycles,
    register_user,
    update_motorcycle,
    update_motorcycle_km,
)
from app.services.export_service import export_maintenance_history_csv
from app.services.maintenance_service import create_maintenance, delete_maintenance, list_maintenances, update_maintenance
from app.state.session_state import SessionState
from ui.alerts.alerts_page import build_alert_form, build_alert_list, build_alert_summary
from ui.auth.login_page import build_login_card
from ui.auth.profile_page import build_profile_summary
from ui.auth.register_page import build_register_card
from ui.maintenance.detail_page import build_km_update_card, build_motorcycle_hero, build_suggestions_panel
from ui.maintenance.history_page import build_history_list
from ui.maintenance.new_maintenance_page import build_new_maintenance_form
from ui.shared.navbar import build_navbar
from ui.shared.snackbar import show_message
from ui.shared.theme import (
    ACCENT_COLOR,
    BG_COLOR,
    BORDER_COLOR,
    DANGER_COLOR,
    INFO_COLOR,
    MUTED_TEXT,
    PRIMARY_COLOR,
    PRIMARY_SOFT,
    SURFACE_ALT,
    SURFACE_COLOR,
    SUCCESS_COLOR,
    TEXT_COLOR,
    app_button_style,
    configure_page,
    empty_state,
    metric_tile,
    mobile_field,
    section_card,
    section_title,
)


load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def bootstrap_database(seed: bool | None = None, reset: bool = False) -> str:
    database_url = configure_database()
    init_db(drop_existing=reset)

    should_seed = _as_bool(os.getenv("AUTO_SEED_DATA"), default=True) if seed is None else seed
    if should_seed:
        seed_database(force_reset=False)
    return database_url


def _app_kwargs() -> dict:
    kwargs: dict = {}
    if os.getenv("PORT"):
        kwargs["port"] = int(os.getenv("PORT", "8550"))
    if _as_bool(os.getenv("FLET_WEB"), default=bool(os.getenv("PORT"))):
        kwargs["view"] = ft.AppView.WEB_BROWSER
    return kwargs


def _parse_optional_float(value: str) -> float | None:
    cleaned = value.strip()
    return float(cleaned) if cleaned else None


def _parse_datetime(value: str) -> datetime:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("La fecha es obligatoria.")

    parsed = datetime.fromisoformat(cleaned)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_datetime(value: datetime | None) -> str:
    if value is None:
        return "Sin fecha"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%d")


def _maintenance_history_payload(maintenances) -> list[dict]:
    return [
        {
            "type": item.type,
            "km_at_service": item.km_at_service,
            "service_date": item.service_date,
        }
        for item in maintenances
    ]


def _custom_alert_payload(alert) -> dict:
    if alert.trigger_type == "km" and alert.trigger_km is not None:
        meta = f"Personalizada | Limite: {alert.trigger_km:.0f} km"
    elif alert.trigger_type == "date" and alert.trigger_date is not None:
        meta = f"Personalizada | Fecha: {_format_datetime(alert.trigger_date)}"
    elif alert.trigger_type == "both":
        parts = []
        if alert.trigger_km is not None:
            parts.append(f"{alert.trigger_km:.0f} km")
        if alert.trigger_date is not None:
            parts.append(_format_datetime(alert.trigger_date))
        meta = "Personalizada | " + " | ".join(parts)
    else:
        meta = "Personalizada"

    return {
        "id": alert.id,
        "tipo": alert.title,
        "estado": "VENCIDO" if alert.is_fired else "AL DÍA",
        "meta": meta,
        "icon": "NOTIFICATIONS_ROUNDED",
        "color": DANGER_COLOR if alert.is_fired else SUCCESS_COLOR,
        "trigger_type": alert.trigger_type,
        "trigger_km": alert.trigger_km,
        "trigger_date": alert.trigger_date,
        "is_active": alert.is_active,
        "is_fired": alert.is_fired,
    }


def _history_items(maintenances) -> list[dict[str, str]]:
    return [
        {
            "id": item.id,
            "title": item.type,
            "meta": f"Fecha {_format_datetime(item.service_date)} | Km {item.km_at_service:.0f} | Costo {item.cost:.0f}",
            "description": item.description or "Sin descripcion adicional.",
            "type": item.type,
            "km_at_service": item.km_at_service,
            "cost": item.cost,
            "service_date": item.service_date,
            "next_service_km": item.next_service_km,
        }
        for item in maintenances
    ]


def _active_suggestions(active_alerts: list[dict]) -> list[str]:
    return [
        (
            f"[urgente] {alert['tipo']} vencido hace {abs(int(alert['km_restantes'])):,} km.".replace(",", ".")
            if alert["estado"] == "VENCIDO"
            else f"[advertencia] {alert['tipo']} está próximo. Faltan {int(alert['km_restantes']):,} km.".replace(",", ".")
        )
        for alert in active_alerts[:4]
    ]


def run_app(page: ft.Page) -> None:
    configure_page(page)
    page.title = os.getenv("APP_NAME", "MotoTrack")

    session_state = SessionState()
    selected_motorcycle_id: int | None = None
    current_tab = 0
    last_vencidas_notice: tuple[int, int] | None = None
    km_field_dirty = False
    km_field_motorcycle_id: int | None = None

    login_email = mobile_field("Correo electrónico", "demo@mototrack.local", keyboard=ft.KeyboardType.EMAIL)
    login_password = mobile_field("Contraseña", "********", password=True)
    login_email.value = "demo@mototrack.local"
    login_password.value = "demo1234"

    register_name = mobile_field("Nombre completo", "Carlos Ruiz")
    register_email = mobile_field("Correo electrónico", "cliente@email.com", keyboard=ft.KeyboardType.EMAIL)
    register_password = mobile_field("Contraseña", "Mínimo 8 caracteres", password=True)

    moto_brand = mobile_field("Marca", "Honda")
    moto_model = mobile_field("Modelo", "CB125F")
    moto_year = mobile_field("Año", "2025", keyboard=ft.KeyboardType.NUMBER)
    moto_plate = mobile_field("Placa", "ABC123")
    moto_km = mobile_field("Kilometraje actual", "0", keyboard=ft.KeyboardType.NUMBER)
    moto_km.value = "0"

    km_update_field = mobile_field("Kilometraje actual", "24350", keyboard=ft.KeyboardType.NUMBER)

    maintenance_type = mobile_field("Tipo de mantenimiento", "Cambio de aceite")
    maintenance_km = mobile_field("Km del servicio", "9500", keyboard=ft.KeyboardType.NUMBER)
    maintenance_cost = mobile_field("Costo", "0", keyboard=ft.KeyboardType.NUMBER)
    maintenance_cost.value = "0"
    maintenance_date = mobile_field("Fecha ISO", "2026-05-06T10:30:00+00:00")
    maintenance_next_km = mobile_field("Próximo servicio km", "12000", keyboard=ft.KeyboardType.NUMBER)
    maintenance_description = mobile_field("Descripción", "Notas del servicio")
    maintenance_description.multiline = True
    maintenance_description.min_lines = 2
    maintenance_description.max_lines = 4

    alert_title = mobile_field("Titulo", "SOAT o cambio de aceite")
    alert_trigger_type = ft.Dropdown(
        label="Tipo",
        value="km",
        border_radius=16,
        filled=True,
        bgcolor=SURFACE_COLOR,
        border_color=BORDER_COLOR,
        focused_border_color=PRIMARY_COLOR,
        label_style=ft.TextStyle(color=MUTED_TEXT, size=12),
        text_style=ft.TextStyle(color=TEXT_COLOR, size=14),
        options=[
            ft.dropdown.Option("km", text="Por km"),
            ft.dropdown.Option("date", text="Por fecha"),
            ft.dropdown.Option("both", text="Ambos"),
        ],
    )
    alert_trigger_km = mobile_field("Km objetivo", "10000", keyboard=ft.KeyboardType.NUMBER)
    alert_trigger_date = mobile_field("Fecha ISO", "2026-06-01T00:00:00+00:00")

    alert_date_picker = ft.DatePicker(
        field_label_text="Fecha limite",
        help_text="Selecciona la fecha limite",
        confirm_text="Usar fecha",
        cancel_text="Cancelar",
    )
    maintenance_date_picker = ft.DatePicker(
        field_label_text="Fecha del servicio",
        help_text="Selecciona la fecha del mantenimiento",
        confirm_text="Usar fecha",
        cancel_text="Cancelar",
    )

    auth_panel = ft.Column(spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)
    dashboard_panel = ft.Column(spacing=0, expand=True, visible=False)
    navbar_host = ft.Container(margin=ft.margin.Margin.symmetric(horizontal=16, vertical=14))
    content_host = ft.Container(expand=True)

    def is_compact() -> bool:
        return (page.width or 390) < 560

    def notify(message: str, tone: str = "info") -> None:
        show_message(page, message, tone=tone)

    def mark_km_field_dirty(_e) -> None:
        nonlocal km_field_dirty
        km_field_dirty = True

    km_update_field.on_change = mark_km_field_dirty

    def handle_alert_date_picker_change(e) -> None:
        picked = getattr(e.control, "value", None)
        if picked is not None:
            alert_trigger_date.value = picked.isoformat()
            page.update()

    def handle_maintenance_date_picker_change(e) -> None:
        picked = getattr(e.control, "value", None)
        if picked is not None:
            maintenance_date.value = picked.isoformat()
            page.update()

    alert_date_picker.on_change = handle_alert_date_picker_change
    maintenance_date_picker.on_change = handle_maintenance_date_picker_change
    if hasattr(page, "overlay"):
        page.overlay.append(alert_date_picker)
        page.overlay.append(maintenance_date_picker)

    def open_alert_date_picker(_e) -> None:
        alert_date_picker.open = True
        page.update()

    def open_maintenance_date_picker(_e) -> None:
        maintenance_date_picker.open = True
        page.update()

    def close_dialog(_e=None) -> None:
        dialog = getattr(page, "dialog", None)
        if dialog is not None:
            dialog.open = False
        page.update()

    def show_info_dialog(title: str, lines: list[str]) -> None:
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
            content=ft.Column([ft.Text(line, size=13, color=TEXT_COLOR) for line in lines], spacing=8, tight=True),
            actions=[ft.TextButton("Cerrar", on_click=close_dialog)],
        )
        page.dialog.open = True
        page.update()

    def show_confirm_dialog(title: str, message: str, on_confirm) -> None:
        def confirm(e) -> None:
            close_dialog()
            on_confirm(e)

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
            content=ft.Text(message, size=13, color=TEXT_COLOR),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Confirmar", on_click=confirm, style=app_button_style(DANGER_COLOR)),
            ],
        )
        page.dialog.open = True
        page.update()

    def show_motorcycle_editor(motorcycle) -> None:
        brand_field = mobile_field("Marca", "Honda")
        model_field = mobile_field("Modelo", "CB125F")
        year_field = mobile_field("Año", "2025", keyboard=ft.KeyboardType.NUMBER)
        plate_field = mobile_field("Placa", "ABC123")
        km_field = mobile_field("Kilometraje actual", "0", keyboard=ft.KeyboardType.NUMBER)
        brand_field.value = motorcycle.brand
        model_field.value = motorcycle.model
        year_field.value = str(motorcycle.year)
        plate_field.value = motorcycle.plate
        km_field.value = str(int(motorcycle.current_km or 0))

        def save(_e) -> None:
            try:
                update_motorcycle(
                    motorcycle.id,
                    brand=brand_field.value or "",
                    model=model_field.value or "",
                    year=int(year_field.value or "0"),
                    plate=plate_field.value or "",
                    current_km=float(km_field.value or "0"),
                )
            except ValueError as exc:
                notify(str(exc), tone="error")
                return
            close_dialog()
            notify("Motocicleta actualizada.", tone="success")
            refresh_dashboard()

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar motocicleta", weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
            content=ft.Column([brand_field, model_field, year_field, plate_field, km_field], spacing=10, tight=True, width=360),
            actions=[ft.TextButton("Cancelar", on_click=close_dialog), ft.ElevatedButton("Guardar", on_click=save, style=app_button_style())],
        )
        page.dialog.open = True
        page.update()

    def show_maintenance_editor(item: dict) -> None:
        type_field = mobile_field("Tipo", "Cambio de aceite")
        km_field = mobile_field("Km del servicio", "9500", keyboard=ft.KeyboardType.NUMBER)
        cost_field = mobile_field("Costo", "0", keyboard=ft.KeyboardType.NUMBER)
        date_field = mobile_field("Fecha ISO", "2026-05-06T10:30:00+00:00")
        next_km_field = mobile_field("Próximo servicio km", "12000", keyboard=ft.KeyboardType.NUMBER)
        description_field = mobile_field("Descripción", "Notas del servicio")
        description_field.multiline = True
        description_field.min_lines = 2
        description_field.max_lines = 4
        type_field.value = str(item.get("type") or item.get("title") or "")
        km_field.value = f"{float(item.get('km_at_service') or 0):.0f}"
        cost_field.value = f"{float(item.get('cost') or 0):.0f}"
        date_field.value = _format_datetime(item.get("service_date"))
        next_km = item.get("next_service_km")
        next_km_field.value = "" if next_km is None else f"{float(next_km):.0f}"
        description_field.value = str(item.get("description") or "")

        def save(_e) -> None:
            try:
                update_maintenance(
                    int(item["id"]),
                    type=type_field.value or "",
                    km_at_service=float(km_field.value or "0"),
                    cost=float(cost_field.value or "0"),
                    service_date=_parse_datetime(date_field.value or ""),
                    next_service_km=_parse_optional_float(next_km_field.value or ""),
                    description=description_field.value or None,
                )
            except ValueError as exc:
                notify(str(exc), tone="error")
                return
            close_dialog()
            notify("Mantenimiento actualizado.", tone="success")
            refresh_dashboard()

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar mantenimiento", weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
            content=ft.Column(
                [type_field, km_field, cost_field, date_field, next_km_field, description_field],
                spacing=10,
                tight=True,
                width=380,
            ),
            actions=[ft.TextButton("Cancelar", on_click=close_dialog), ft.ElevatedButton("Guardar", on_click=save, style=app_button_style())],
        )
        page.dialog.open = True
        page.update()

    def show_alert_editor(item: dict) -> None:
        title_field = mobile_field("Título", "SOAT o cambio de aceite")
        trigger_type_field = ft.Dropdown(
            label="Tipo",
            value=str(item.get("trigger_type") or "km"),
            border_radius=16,
            filled=True,
            bgcolor=SURFACE_COLOR,
            border_color=BORDER_COLOR,
            focused_border_color=PRIMARY_COLOR,
            options=[
                ft.dropdown.Option("km", text="Por km"),
                ft.dropdown.Option("date", text="Por fecha"),
                ft.dropdown.Option("both", text="Ambos"),
            ],
        )
        km_field = mobile_field("Km objetivo", "10000", keyboard=ft.KeyboardType.NUMBER)
        date_field = mobile_field("Fecha ISO", "2026-06-01T00:00:00+00:00")
        active_field = ft.Checkbox(label="Activa", value=bool(item.get("is_active", True)), active_color=PRIMARY_COLOR)
        title_field.value = str(item.get("tipo") or "")
        km_value = item.get("trigger_km")
        km_field.value = "" if km_value is None else f"{float(km_value):.0f}"
        date_field.value = _format_datetime(item.get("trigger_date")) if item.get("trigger_date") else ""

        def save(_e) -> None:
            try:
                trigger_type = trigger_type_field.value or "km"
                update_alert(
                    int(item["id"]),
                    title=title_field.value or "",
                    trigger_type=trigger_type,
                    trigger_km=_parse_optional_float(km_field.value or "") if trigger_type in {"km", "both"} else None,
                    trigger_date=_parse_datetime(date_field.value or "") if trigger_type in {"date", "both"} else None,
                    is_active=bool(active_field.value),
                    is_fired=False,
                )
            except ValueError as exc:
                notify(str(exc), tone="error")
                return
            close_dialog()
            notify("Alerta actualizada.", tone="success")
            refresh_dashboard()

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar alerta", weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
            content=ft.Column([title_field, trigger_type_field, km_field, date_field, active_field], spacing=10, tight=True, width=360),
            actions=[ft.TextButton("Cancelar", on_click=close_dialog), ft.ElevatedButton("Guardar", on_click=save, style=app_button_style())],
        )
        page.dialog.open = True
        page.update()

    def current_user():
        if not session_state.user_id:
            return None
        return get_user_by_id(session_state.user_id)

    def user_motorcycles():
        user = current_user()
        return list_user_motorcycles(user.id) if user is not None else []  # type: ignore

    def ensure_selected_motorcycle() -> None:
        nonlocal selected_motorcycle_id
        motorcycles = user_motorcycles()
        if motorcycles and (selected_motorcycle_id is None or all(m.id != selected_motorcycle_id for m in motorcycles)):
            selected_motorcycle_id = motorcycles[0].id  # type: ignore
        if not motorcycles:
            selected_motorcycle_id = None

    def selected_motorcycle():
        ensure_selected_motorcycle()
        for motorcycle in user_motorcycles():
            if motorcycle.id == selected_motorcycle_id:
                return motorcycle
        return None

    def require_selected_motorcycle() -> int:
        if selected_motorcycle_id is None:
            raise ValueError("Primero selecciona una motocicleta.")
        return selected_motorcycle_id

    def motorcycle_context(motorcycle) -> tuple[list, list, list[dict], list[dict], dict[str, int]]:
        history = list_maintenances(motorcycle.id)  # type: ignore
        custom_alerts = list_alerts(motorcycle.id)  # type: ignore
        smart_alerts = calcular_alertas(int(motorcycle.current_km or 0), _maintenance_history_payload(history))
        active_smart_alerts = filtrar_alertas_activas(smart_alerts)
        counts = contar_por_estado(smart_alerts)
        return history, custom_alerts, smart_alerts, active_smart_alerts, counts

    def global_counts() -> tuple[int, int, int, int]:
        motorcycles = user_motorcycles()
        total_services = 0
        custom_alerts = 0
        fired_custom = 0
        active_smart = 0

        for motorcycle in motorcycles:
            history = list_maintenances(motorcycle.id)  # type: ignore
            alerts = list_alerts(motorcycle.id)  # type: ignore
            smart_alerts = calcular_alertas(int(motorcycle.current_km or 0), _maintenance_history_payload(history))
            total_services += len(history)
            custom_alerts += len(alerts)
            fired_custom += len([alert for alert in alerts if alert.is_fired])
            active_smart += len(filtrar_alertas_activas(smart_alerts))

        return total_services, custom_alerts, fired_custom, active_smart

    def active_alert_count() -> int:
        _services, _custom, fired_custom, active_smart = global_counts()
        return fired_custom + active_smart

    def refresh_top_nav() -> None:
        navbar_host.content = build_navbar(
            title=str(page.title),
            subtitle="Seguimiento claro para motos cuidadas.",
            user_name=session_state.user_name,
            alertas_activas=active_alert_count(),
            compact=is_compact(),
            on_alerts_click=lambda _e: switch_tab(1),
            on_profile_click=lambda _e: switch_tab(4),
        )

    def motorcycle_card(motorcycle) -> ft.Container:
        active = motorcycle.id == selected_motorcycle_id
        actions = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.Icons.EDIT_ROUNDED,
                    icon_color=ACCENT_COLOR if active else PRIMARY_COLOR,
                    tooltip="Editar motocicleta",
                    on_click=lambda _e, moto=motorcycle: show_motorcycle_editor(moto),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.DELETE_OUTLINE_ROUNDED,
                    icon_color=DANGER_COLOR,
                    tooltip="Eliminar motocicleta",
                    on_click=lambda _e, moto=motorcycle: confirm_delete_motorcycle(moto),
                ),
            ],
            spacing=0,
            tight=True,
        )
        return ft.Container(
            bgcolor="#FFF4EC" if active else SURFACE_COLOR,
            border_radius=18,
            border=ft.border.all(1.5 if active else 1, ACCENT_COLOR if active else BORDER_COLOR),
            padding=14,
            on_click=lambda _e, moto_id=motorcycle.id: select_motorcycle(moto_id),
            content=ft.Row(
                [
                    ft.Container(
                        width=44,
                        height=44,
                        border_radius=15,
                        bgcolor="#F7D9C6" if active else SURFACE_ALT,
                        alignment=ft.alignment.Alignment.CENTER,
                        content=ft.Icon(
                            ft.icons.Icons.TWO_WHEELER_ROUNDED,
                            color=ACCENT_COLOR if active else PRIMARY_COLOR,
                            size=23,
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(f"{motorcycle.brand} {motorcycle.model}", size=15, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                            ft.Text(f"{motorcycle.plate} | {motorcycle.year}", size=11, color=MUTED_TEXT),
                            ft.Text(f"{motorcycle.current_km:.0f} km registrados", size=12, color=TEXT_COLOR),
                        ],
                        spacing=2,
                        tight=True,
                        expand=True,
                    ),
                    actions,
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def confirm_delete_motorcycle(motorcycle) -> None:
        def delete(_e) -> None:
            nonlocal selected_motorcycle_id
            if delete_motorcycle(motorcycle.id):
                if selected_motorcycle_id == motorcycle.id:
                    selected_motorcycle_id = None
                notify("Motocicleta eliminada.", tone="success")
                refresh_dashboard()
            else:
                notify("No se encontró la motocicleta.", tone="error")

        show_confirm_dialog(
            "Eliminar motocicleta",
            "Se eliminarán también sus mantenimientos y alertas. Esta acción no se puede deshacer.",
            delete,
        )

    def confirm_delete_maintenance(_e, item: dict) -> None:
        def delete(_event) -> None:
            if delete_maintenance(int(item["id"])):
                notify("Mantenimiento eliminado.", tone="success")
                refresh_dashboard()
            else:
                notify("No se encontró el mantenimiento.", tone="error")

        show_confirm_dialog("Eliminar mantenimiento", "Esta acción no se puede deshacer.", delete)

    def confirm_delete_alert(_e, item: dict) -> None:
        def delete(_event) -> None:
            if delete_alert(int(item["id"])):
                notify("Alerta eliminada.", tone="success")
                refresh_dashboard()
            else:
                notify("No se encontró la alerta.", tone="error")

        show_confirm_dialog("Eliminar alerta", "Esta acción no se puede deshacer.", delete)

    def show_alert_detail(_e, item: dict) -> None:
        lines = [
            f"Estado: {item.get('estado', 'Pendiente')}",
            f"Referencia: {item.get('tipo', 'Alerta')}",
        ]
        if "km_restantes" in item:
            lines.extend(
                [
                    f"Km actual: {int(item.get('km_actual', 0)):,}".replace(",", "."),
                    f"Último servicio relacionado: {int(item.get('km_ultimo', 0)):,} km".replace(",", "."),
                    f"Intervalo base: cada {int(item.get('intervalo', 0)):,} km".replace(",", "."),
                    f"Km restantes: {int(item.get('km_restantes', 0)):,}".replace(",", "."),
                ]
            )
        else:
            lines.append(str(item.get("meta", "Alerta personalizada.")))
            if item.get("trigger_km") is not None:
                lines.append(f"Km objetivo: {float(item['trigger_km']):.0f}")
            if item.get("trigger_date") is not None:
                lines.append(f"Fecha objetivo: {_format_datetime(item.get('trigger_date'))}")
        if item.get("estado") == "VENCIDO":
            lines.append("Acción sugerida: programa el mantenimiento o actualiza el punto de partida.")
        elif item.get("estado") in {"PRÓXIMO", "PROXIMO"}:
            lines.append("Acción sugerida: prepara el próximo servicio.")
        else:
            lines.append("Acción sugerida: mantener seguimiento normal.")
        show_info_dialog("Detalle de alerta", lines)

    def export_history_for_selected_motorcycle(_e) -> None:
        motorcycle = selected_motorcycle()
        if motorcycle is None:
            notify("Selecciona una motocicleta para exportar.", tone="error")
            return
        history = list_maintenances(motorcycle.id)  # type: ignore
        output_path = export_maintenance_history_csv(motorcycle, history)
        notify(f"Historial exportado: {output_path}", tone="success")

    def view_shell(controls: list[ft.Control]) -> ft.Column:
        return ft.Column(
            controls,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def build_home_view() -> ft.Column:
        ensure_selected_motorcycle()
        motorcycles = user_motorcycles()
        total_services, custom_alerts, fired_custom, active_smart = global_counts()
        compact = is_compact()

        motorcycle_controls: list[ft.Control] = (
            [motorcycle_card(motorcycle) for motorcycle in motorcycles]
            if motorcycles
            else [
                empty_state("Sin motocicletas", "Agrega la primera moto para empezar el seguimiento."),
                section_card(
                    ft.Column(
                        [
                            section_title("Primeros pasos", "Completa este flujo para activar el seguimiento.", ft.icons.Icons.ROUTE_ROUNDED),
                            ft.Text("1. Registra marca, modelo, placa y kilometraje actual.", size=12, color=TEXT_COLOR),
                            ft.Text("2. Abre Servicio para cargar el primer mantenimiento.", size=12, color=TEXT_COLOR),
                            ft.Text("3. Revisa Alertas para ver el plan sugerido por kilometraje.", size=12, color=TEXT_COLOR),
                        ],
                        spacing=8,
                    )
                ),
            ]
        )

        return view_shell(
            [
                ft.Container(
                    margin=ft.margin.Margin.symmetric(horizontal=16),
                    content=ft.Column(
                        [
                            metric_tile("Motos", str(len(motorcycles)), ft.icons.Icons.TWO_WHEELER_ROUNDED, color=PRIMARY_COLOR),
                            metric_tile("Servicios", str(total_services), ft.icons.Icons.BUILD_ROUNDED, color=ACCENT_COLOR),
                        ],
                        spacing=10,
                    )
                    if compact
                    else ft.Row(
                        [
                            metric_tile("Motos", str(len(motorcycles)), ft.icons.Icons.TWO_WHEELER_ROUNDED, color=PRIMARY_COLOR),
                            metric_tile("Servicios", str(total_services), ft.icons.Icons.BUILD_ROUNDED, color=ACCENT_COLOR),
                        ],
                        spacing=10,
                    ),
                ),
                ft.Container(
                    margin=ft.margin.Margin.symmetric(horizontal=16),
                    content=ft.Column(
                        [
                            metric_tile("Alertas", str(active_smart + custom_alerts), ft.icons.Icons.NOTIFICATIONS_ROUNDED, color=INFO_COLOR),
                            metric_tile(
                                "Criticas",
                                str(active_smart + fired_custom),
                                ft.icons.Icons.PRIORITY_HIGH_ROUNDED,
                                color=DANGER_COLOR if active_smart + fired_custom else SUCCESS_COLOR,
                            ),
                        ],
                        spacing=10,
                    )
                    if compact
                    else ft.Row(
                        [
                            metric_tile("Alertas", str(active_smart + custom_alerts), ft.icons.Icons.NOTIFICATIONS_ROUNDED, color=INFO_COLOR),
                            metric_tile(
                                "Criticas",
                                str(active_smart + fired_custom),
                                ft.icons.Icons.PRIORITY_HIGH_ROUNDED,
                                color=DANGER_COLOR if active_smart + fired_custom else SUCCESS_COLOR,
                            ),
                        ],
                        spacing=10,
                    ),
                ),
                ft.Container(
                    margin=ft.margin.Margin.symmetric(horizontal=16),
                    padding=16,
                    bgcolor=SURFACE_COLOR,
                    border_radius=20,
                    border=ft.border.all(1, BORDER_COLOR),
                    content=ft.Column(
                        [
                            section_title("Mis motocicletas", "Toca una moto para abrir Servicio.", ft.icons.Icons.GARAGE_ROUNDED),
                            *motorcycle_controls,
                        ],
                        spacing=12,
                    ),
                ),
                ft.Container(
                    margin=ft.margin.Margin.symmetric(horizontal=16),
                    content=section_card(
                        ft.Column(
                            [
                                section_title(
                                    "Registrar motocicleta",
                                    "Agrega motos del cliente y administra su progreso.",
                                    ft.icons.Icons.ADD_ROAD_ROUNDED,
                                ),
                                moto_brand,
                                moto_model,
                                ft.Column([moto_year, moto_plate], spacing=10)
                                if compact
                                else ft.Row(
                                    [ft.Container(content=moto_year, expand=1), ft.Container(content=moto_plate, expand=1)],
                                    spacing=10,
                                ),
                                moto_km,
                                ft.ElevatedButton("Agregar motocicleta", on_click=handle_add_motorcycle, style=app_button_style()),
                            ],
                            spacing=12,
                        )
                    ),
                ),
                ft.Container(height=80),
            ]
        )

    def build_alerts_view() -> ft.Column:
        motorcycle = selected_motorcycle()
        if motorcycle is None:
            return view_shell(
                [
                    ft.Container(margin=ft.margin.Margin.symmetric(horizontal=16), content=empty_state("Sin moto seleccionada", "Registra o selecciona una moto desde Inicio.")),
                    ft.Container(height=80),
                ]
            )

        _history, custom_alerts, smart_alerts, _active_smart_alerts, counts = motorcycle_context(motorcycle)
        custom_alert_items = [_custom_alert_payload(alert) for alert in custom_alerts]

        return view_shell(
            [
                build_alert_summary(counts),
                build_alert_list(
                    [*smart_alerts, *custom_alert_items],
                    compact=is_compact(),
                    on_detail=show_alert_detail,
                    on_edit=lambda e, item: show_alert_editor(item),
                    on_delete=confirm_delete_alert,
                ),
                build_alert_form(
                    alert_title,
                    alert_trigger_type,
                    alert_trigger_km,
                    alert_trigger_date,
                    handle_add_alert,
                    open_alert_date_picker,
                ),
                ft.Container(height=80),
            ]
        )

    def build_service_view() -> ft.Column:
        nonlocal km_field_dirty, km_field_motorcycle_id, last_vencidas_notice
        motorcycle = selected_motorcycle()
        if motorcycle is None:
            return view_shell(
                [
                    ft.Container(margin=ft.margin.Margin.symmetric(horizontal=16), content=empty_state("Sin moto seleccionada", "Registra o selecciona una moto desde Inicio.")),
                    ft.Container(height=80),
                ]
            )

        fired_now = evaluate_alerts()
        relevant_fired = [alert for alert in fired_now if alert.motorcycle_id == motorcycle.id]  # type: ignore
        if relevant_fired:
            notify(f"Se actualizaron {len(relevant_fired)} alertas personalizadas.", tone="warning")

        history, custom_alerts, _smart_alerts, active_smart_alerts, counts = motorcycle_context(motorcycle)
        if counts["VENCIDO"] and last_vencidas_notice != (motorcycle.id, counts["VENCIDO"]):
            last_vencidas_notice = (motorcycle.id, counts["VENCIDO"])
            notify(f"{counts['VENCIDO']} mantenimiento(s) vencido(s) por kilometraje.", tone="error")

        if km_field_motorcycle_id != motorcycle.id or not km_field_dirty:
            km_update_field.value = f"{int(motorcycle.current_km or 0)}"
            km_field_motorcycle_id = motorcycle.id  # type: ignore
            km_field_dirty = False

        stats = [
            ("Placa", motorcycle.plate),
            ("Año", str(motorcycle.year)),
            ("Km", f"{motorcycle.current_km:.0f}"),
            ("Alertas", str(len(active_smart_alerts) + len([alert for alert in custom_alerts if alert.is_fired]))),
        ]

        suggestions = _active_suggestions(active_smart_alerts)
        if not suggestions:
            suggestions = ["[ok] Todo al dia. No hay vencimientos cercanos."]

        return view_shell(
            [
                build_motorcycle_hero(
                    title=f"{motorcycle.brand} {motorcycle.model}",
                    subtitle="Moto seleccionada para servicio y kilometraje.",
                    stats=stats,
                ),
                build_km_update_card(km_update_field, handle_update_km, confirm_release_alerts),
                build_suggestions_panel(suggestions),
                build_new_maintenance_form(
                    maintenance_type,
                    maintenance_km,
                    maintenance_cost,
                    maintenance_date,
                    maintenance_next_km,
                    maintenance_description,
                    handle_add_maintenance,
                    open_maintenance_date_picker,
                    compact=is_compact(),
                ),
                ft.Container(height=80),
            ]
        )

    def build_history_view() -> ft.Column:
        motorcycle = selected_motorcycle()
        if motorcycle is None:
            return view_shell(
                [
                    ft.Container(margin=ft.margin.Margin.symmetric(horizontal=16), content=empty_state("Sin moto seleccionada", "Registra o selecciona una moto desde Inicio.")),
                    ft.Container(height=80),
                ]
            )

        history = list_maintenances(motorcycle.id)  # type: ignore
        return view_shell(
            [
                ft.Container(
                    margin=ft.margin.Margin.symmetric(horizontal=16),
                    content=ft.ElevatedButton(
                        "Exportar historial CSV",
                        icon=ft.icons.Icons.DOWNLOAD_ROUNDED,
                        on_click=export_history_for_selected_motorcycle,
                        style=app_button_style(ACCENT_COLOR),
                    ),
                ),
                build_history_list(
                    _history_items(history),
                    on_edit=lambda e, item: show_maintenance_editor(item),
                    on_delete=confirm_delete_maintenance,
                ),
                ft.Container(height=80),
            ]
        )

    def build_profile_view() -> ft.Column:
        motorcycles = user_motorcycles()
        return view_shell(
            [
                build_profile_summary(session_state.user_name, session_state.user_email, len(motorcycles), compact=is_compact()),
                ft.Container(
                    margin=ft.margin.Margin.symmetric(horizontal=16),
                    content=ft.ElevatedButton(
                        "Cerrar sesión",
                        icon=ft.icons.Icons.LOGOUT_ROUNDED,
                        on_click=handle_logout,
                        style=ft.ButtonStyle(
                            bgcolor=DANGER_COLOR,
                            color="#FFFFFF",
                            padding=ft.padding.Padding.symmetric(vertical=15, horizontal=16),
                            shape=ft.RoundedRectangleBorder(radius=16),
                        ),
                    ),
                ),
                ft.Container(height=80),
            ]
        )

    def build_navigation_bar(alertas_activas: int = 0) -> ft.NavigationBar:
        alert_badge = ft.Badge(label=str(min(alertas_activas, 9)), bgcolor=DANGER_COLOR, text_color="#FFFFFF") if alertas_activas > 0 else None
        return ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.icons.Icons.HOME_OUTLINED, selected_icon=ft.icons.Icons.HOME_ROUNDED, label="Inicio"),
                ft.NavigationBarDestination(
                    icon=ft.icons.Icons.NOTIFICATIONS_OUTLINED,
                    selected_icon=ft.icons.Icons.NOTIFICATIONS_ROUNDED,
                    label="Alertas",
                    badge=alert_badge,
                ),
                ft.NavigationBarDestination(icon=ft.icons.Icons.BUILD_OUTLINED, selected_icon=ft.icons.Icons.BUILD_ROUNDED, label="Servicio"),
                ft.NavigationBarDestination(icon=ft.icons.Icons.HISTORY_OUTLINED, selected_icon=ft.icons.Icons.HISTORY_ROUNDED, label="Historial"),
                ft.NavigationBarDestination(icon=ft.icons.Icons.PERSON_OUTLINED, selected_icon=ft.icons.Icons.PERSON_ROUNDED, label="Perfil"),
            ],
            selected_index=current_tab,
            on_change=lambda e: switch_tab(e.control.selected_index),
            bgcolor=SURFACE_COLOR,
            indicator_color=PRIMARY_SOFT,
            label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        )

    def switch_tab(index: int) -> None:
        nonlocal current_tab
        current_tab = index
        ensure_selected_motorcycle()
        refresh_top_nav()

        views = {
            0: build_home_view,
            1: build_alerts_view,
            2: build_service_view,
            3: build_history_view,
            4: build_profile_view,
        }
        content_host.content = ft.Container(content=views[index](), expand=True, padding=ft.padding.Padding.only(bottom=80))
        page.navigation_bar = build_navigation_bar(active_alert_count())
        page.update()

    def refresh_dashboard() -> None:
        switch_tab(current_tab)

    def handle_resize(_e) -> None:
        if dashboard_panel.visible:
            refresh_dashboard()

    page.on_resize = handle_resize

    def show_auth_view() -> None:
        auth_panel.visible = True
        dashboard_panel.visible = False
        page.navigation_bar = None
        page.update()

    def show_dashboard_view() -> None:
        auth_panel.visible = False
        dashboard_panel.visible = True
        switch_tab(0)

    def select_motorcycle(moto_id: int) -> None:
        nonlocal km_field_dirty, km_field_motorcycle_id, selected_motorcycle_id
        selected_motorcycle_id = moto_id
        km_field_dirty = False
        km_field_motorcycle_id = None
        switch_tab(2)

    def handle_login(_e) -> None:
        user = authenticate_user(login_email.value or "", login_password.value or "")
        if user is None:
            notify("Credenciales invalidas.", tone="error")
            return

        session_state.login(user)
        login_password.value = ""
        notify(f"Bienvenido, {user.name}.", tone="success")
        show_dashboard_view()

    def handle_register(_e) -> None:
        try:
            user = register_user(register_name.value or "", register_email.value or "", register_password.value or "")
        except ValueError as exc:
            notify(str(exc), tone="error")
            return

        session_state.login(user)
        register_name.value = ""
        register_email.value = ""
        register_password.value = ""
        notify("Cuenta creada correctamente.", tone="success")
        show_dashboard_view()

    def handle_logout(_e) -> None:
        nonlocal selected_motorcycle_id, current_tab
        selected_motorcycle_id = None
        current_tab = 0
        session_state.logout()
        notify("Sesion cerrada.", tone="info")
        show_auth_view()

    def handle_add_motorcycle(_e) -> None:
        nonlocal selected_motorcycle_id
        try:
            if session_state.user_id is None:
                raise ValueError("No hay una sesión activa.")

            motorcycle = add_motorcycle(
                session_state.user_id,
                moto_brand.value or "",
                moto_model.value or "",
                int(moto_year.value or "0"),
                moto_plate.value or "",
                float(moto_km.value or "0"),
            )
        except ValueError as exc:
            notify(str(exc), tone="error")
            return

        selected_motorcycle_id = motorcycle.id  # type: ignore
        moto_brand.value = ""
        moto_model.value = ""
        moto_year.value = ""
        moto_plate.value = ""
        moto_km.value = "0"
        notify("Motocicleta registrada.", tone="success")
        switch_tab(0)

    def handle_update_km(_e) -> None:
        nonlocal km_field_dirty, km_field_motorcycle_id
        try:
            motorcycle_id = require_selected_motorcycle()
            new_km = int(float(km_update_field.value or "0"))
            if new_km < 0:
                raise ValueError("El kilometraje no puede ser negativo.")

            motorcycle = update_motorcycle_km(motorcycle_id, new_km)
            history = list_maintenances(motorcycle.id)  # type: ignore
            smart_alerts = calcular_alertas(int(motorcycle.current_km or 0), _maintenance_history_payload(history))
            active_count = len(filtrar_alertas_activas(smart_alerts))
        except ValueError as exc:
            notify(str(exc), tone="error")
            return

        notify(f"Kilometraje actualizado. {active_count} alerta(s) activas.", tone="success")
        km_field_dirty = False
        km_field_motorcycle_id = motorcycle_id
        switch_tab(2)

    def confirm_release_alerts(_e) -> None:
        show_confirm_dialog(
            "Tomar km como punto de partida",
            "Se crearán registros de mantenimiento para las alertas activas usando el kilometraje escrito. Úsalo cuando quieras reiniciar el plan desde este km.",
            handle_release_alerts,
        )

    def handle_release_alerts(_e) -> None:
        nonlocal km_field_dirty, km_field_motorcycle_id, last_vencidas_notice
        try:
            motorcycle_id = require_selected_motorcycle()
            current_km = int(float(km_update_field.value or "0"))
            if current_km < 0:
                raise ValueError("El kilometraje no puede ser negativo.")

            motorcycle = update_motorcycle_km(motorcycle_id, current_km)
            history = list_maintenances(motorcycle.id)  # type: ignore
            smart_alerts = calcular_alertas(int(motorcycle.current_km or 0), _maintenance_history_payload(history))
            active_alerts = filtrar_alertas_activas(smart_alerts)

            for alert in active_alerts:
                interval = MAINTENANCE_INTERVALS[alert["tipo"]]["km"]
                create_maintenance(
                    motorcycle_id=motorcycle.id,
                    type=alert["tipo"],
                    km_at_service=float(current_km),
                    service_date=datetime.now(timezone.utc),
                    description="Punto de partida del plan de alertas.",
                    cost=0,
                    next_service_km=float(current_km + interval),
                )
        except ValueError as exc:
            notify(str(exc), tone="error")
            return

        last_vencidas_notice = None
        notify(f"Plan iniciado desde {current_km} km. {len(active_alerts)} alerta(s) liberadas.", tone="success")
        km_field_dirty = False
        km_field_motorcycle_id = motorcycle_id
        switch_tab(2)

    def handle_add_maintenance(_e) -> None:
        try:
            create_maintenance(
                motorcycle_id=require_selected_motorcycle(),
                type=maintenance_type.value or "",
                km_at_service=float(maintenance_km.value or "0"),
                service_date=_parse_datetime(maintenance_date.value or ""),
                description=maintenance_description.value or None,
                cost=float(maintenance_cost.value or "0"),
                next_service_km=_parse_optional_float(maintenance_next_km.value or ""),
            )
        except ValueError as exc:
            notify(str(exc), tone="error")
            return

        maintenance_type.value = ""
        maintenance_km.value = ""
        maintenance_cost.value = "0"
        maintenance_date.value = ""
        maintenance_next_km.value = ""
        maintenance_description.value = ""
        notify("Mantenimiento guardado.", tone="success")
        switch_tab(2)

    def handle_add_alert(_e) -> None:
        try:
            trigger_type = alert_trigger_type.value or "km"
            trigger_km = _parse_optional_float(alert_trigger_km.value or "") if trigger_type in {"km", "both"} else None
            trigger_date = _parse_datetime(alert_trigger_date.value or "") if trigger_type in {"date", "both"} else None
            create_alert(
                motorcycle_id=require_selected_motorcycle(),
                title=alert_title.value or "",
                trigger_type=trigger_type,
                trigger_km=trigger_km,
                trigger_date=trigger_date,
            )
        except ValueError as exc:
            notify(str(exc), tone="error")
            return

        alert_title.value = ""
        alert_trigger_km.value = ""
        alert_trigger_date.value = ""
        notify("Alerta creada.", tone="success")
        switch_tab(1)

    def show_login_form(_e=None) -> None:
        login_card_host.visible = True
        register_card_host.visible = False
        page.update()

    def show_register_form(_e=None) -> None:
        login_card_host.visible = False
        register_card_host.visible = True
        page.update()

    login_card_host = ft.Container(
        margin=ft.margin.Margin.symmetric(horizontal=16),
        content=build_login_card(login_email, login_password, handle_login, show_register_form),
    )
    register_card_host = ft.Container(
        margin=ft.margin.Margin.symmetric(horizontal=16),
        content=build_register_card(register_name, register_email, register_password, handle_register, show_login_form),
        visible=False,
    )

    auth_panel.controls = [
        ft.Container(height=10),
        login_card_host,
        register_card_host,
        ft.Container(height=24),
    ]
    dashboard_panel.controls = [navbar_host, content_host]

    page.add(auth_panel, dashboard_panel)
    show_auth_view()


if __name__ == "__main__":
    bootstrap_database(seed=None)
    ft.app(target=run_app, **_app_kwargs())

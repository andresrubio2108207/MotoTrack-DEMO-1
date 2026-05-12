from __future__ import annotations

import os
from datetime import datetime, timezone

import flet as ft
from dotenv import load_dotenv

from app.database.engine import configure_database, get_database_url, init_db
from app.database.seed import seed_database
from app.services.alert_service import create_alert, evaluate_alerts, list_alerts
from app.services.auth_service import (
    add_motorcycle,
    authenticate_user,
    get_user_by_id,
    list_user_motorcycles,
    register_user,
)
from app.services.maintenance_service import create_maintenance, list_maintenances
from app.state.session_state import SessionState
from ui.alerts.alerts_page import build_alert_form, build_alert_list
from ui.auth.login_page import build_login_card
from ui.auth.profile_page import build_auth_header, build_profile_summary
from ui.auth.register_page import build_register_card
from ui.maintenance.detail_page import build_motorcycle_hero, build_suggestions_panel
from ui.maintenance.history_page import build_history_list
from ui.maintenance.new_maintenance_page import build_new_maintenance_form
from ui.shared.navbar import build_navbar
from ui.shared.snackbar import show_message
from ui.shared.theme import (
    ACCENT_COLOR,
    BORDER_COLOR,
    DANGER_COLOR,
    INFO_COLOR,
    MUTED_TEXT,
    PRIMARY_COLOR,
    SURFACE_ALT,
    SURFACE_COLOR,
    SUCCESS_COLOR,
    TEXT_COLOR,
    app_button_style,
    configure_page,
    empty_state,
    metric_tile,
    mobile_field,
    section_title,
    section_card,
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


def _build_suggestions(motorcycle, maintenances, alerts) -> list[str]:
    suggestions: list[str] = []
    current_km = motorcycle.current_km or 0

    if maintenances:
        latest = maintenances[0]
        if latest.next_service_km is not None:
            remaining_km = latest.next_service_km - current_km
            if remaining_km <= 0:
                suggestions.append(
                    f"El proximo mantenimiento ya esta vencido por kilometraje. Objetivo: {latest.next_service_km:.0f} km."
                )
            elif remaining_km <= 500:
                suggestions.append(
                    f"Programa el siguiente servicio pronto. Faltan aproximadamente {remaining_km:.0f} km."
                )

        if latest.next_service_date is not None:
            due_date = latest.next_service_date.astimezone(timezone.utc)
            days_left = (due_date.date() - datetime.now(timezone.utc).date()).days
            if days_left < 0:
                suggestions.append("Hay un mantenimiento con fecha objetivo vencida. Conviene priorizarlo.")
            elif days_left <= 10:
                suggestions.append(f"El siguiente servicio por fecha vence en {days_left} dias.")

    fired_alerts = [alert for alert in alerts if alert.is_fired]
    if fired_alerts:
        suggestions.append(f"Tienes {len(fired_alerts)} alerta(s) disparada(s) que ya requieren seguimiento.")

    if current_km >= 20000 and not suggestions:
        suggestions.append("La moto ya acumula bastante kilometraje. Vale la pena revisar aceite, frenos y transmision.")

    return suggestions[:3]


def run_app(page: ft.Page) -> None:
    configure_page(page)
    page.title = os.getenv("APP_NAME", "MotoTrack")
    session_state = SessionState()
    selected_motorcycle_id: int | None = None

    login_email = mobile_field("Correo electronico", "demo@mototrack.local", keyboard=ft.KeyboardType.EMAIL)
    login_password = mobile_field("Contrasena", "********", password=True)

    register_name = mobile_field("Nombre completo", "Carlos Ruiz")
    register_email = mobile_field("Correo electronico", "cliente@email.com", keyboard=ft.KeyboardType.EMAIL)
    register_password = mobile_field("Contrasena", "Minimo 8 caracteres", password=True)

    moto_brand = mobile_field("Marca", "Honda")
    moto_model = mobile_field("Modelo", "CB125F")
    moto_year = mobile_field("Ano", "2025", keyboard=ft.KeyboardType.NUMBER)
    moto_plate = mobile_field("Placa", "ABC123")
    moto_km = mobile_field("Kilometraje actual", "0", keyboard=ft.KeyboardType.NUMBER)
    moto_km.value = "0"

    maintenance_type = mobile_field("Tipo de mantenimiento", "Cambio de aceite")
    maintenance_km = mobile_field("Km del servicio", "9500", keyboard=ft.KeyboardType.NUMBER)
    maintenance_cost = mobile_field("Costo", "0", keyboard=ft.KeyboardType.NUMBER)
    maintenance_cost.value = "0"
    maintenance_date = mobile_field("Fecha ISO", "2026-05-06T10:30:00+00:00")
    maintenance_next_km = mobile_field("Proximo servicio km", "12000", keyboard=ft.KeyboardType.NUMBER)
    maintenance_description = mobile_field("Descripcion", "Notas del servicio")
    maintenance_description.multiline = True
    maintenance_description.min_lines = 2
    maintenance_description.max_lines = 4

    alert_title = mobile_field("Titulo", "SOAT o cambio de aceite")
    alert_trigger_type = ft.Dropdown(
        label="Tipo",
        value="km",
        border_radius=8,
        filled=True,
        bgcolor="#FFFFFF",
        border_color=BORDER_COLOR,
        focused_border_color=PRIMARY_COLOR,
        label_style=ft.TextStyle(color=MUTED_TEXT, size=12),
        text_style=ft.TextStyle(color=TEXT_COLOR, size=14),
        options=[ft.dropdown.Option("km"), ft.dropdown.Option("date")],
    )
    alert_trigger_km = mobile_field("Km objetivo", "10000", keyboard=ft.KeyboardType.NUMBER)
    alert_trigger_date = mobile_field("Fecha ISO", "2026-06-01T00:00:00+00:00")

    auth_panel = ft.Column(spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)
    dashboard_panel = ft.Column(spacing=16, scroll=ft.ScrollMode.AUTO, expand=True, visible=False)
    navbar_host = ft.Container()
    overview_column = ft.Column(spacing=10)

    motorcycles_column = ft.Column(spacing=12)
    detail_column = ft.Column(spacing=16)
    db_label = ft.Text("", size=12, color=MUTED_TEXT)

    def notify(message: str, tone: str = "info") -> None:
        show_message(page, message, tone=tone)

    def current_user():
        if not session_state.user_id:
            return None
        return get_user_by_id(session_state.user_id)

    def require_selected_motorcycle() -> int:
        if selected_motorcycle_id is None:
            raise ValueError("Primero selecciona una motocicleta.")
        return selected_motorcycle_id

    def render_motorcycle_cards(motorcycles) -> None:
        motorcycles_column.controls.clear()

        if not motorcycles:
            motorcycles_column.controls.append(
                empty_state(
                    "Sin motocicletas registradas",
                    "Agrega la primera moto del cliente para comenzar a construir historial y alertas.",
                )
            )
            return

        for motorcycle in motorcycles:
            active = motorcycle.id == selected_motorcycle_id
            motorcycles_column.controls.append(
                ft.Container(
                    bgcolor="#FFF4EC" if active else "#FFFFFF",
                    border_radius=8,
                    border=ft.border.all(1.5 if active else 1, ACCENT_COLOR if active else BORDER_COLOR),
                    padding=14,
                    on_click=lambda _e, moto_id=motorcycle.id: select_motorcycle(moto_id),
                    content=ft.Row(
                        [
                            ft.Container(
                                width=44,
                                height=44,
                                border_radius=8,
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
                                    ft.Text(
                                        f"{motorcycle.brand} {motorcycle.model}",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_COLOR,
                                    ),
                                    ft.Text(f"{motorcycle.plate} | {motorcycle.year}", size=11, color=MUTED_TEXT),
                                    ft.Text(f"{motorcycle.current_km:.0f} km registrados", size=12, color=TEXT_COLOR),
                                ],
                                spacing=2,
                                tight=True,
                                expand=True,
                            ),
                            ft.Icon(
                                ft.icons.Icons.CHEVRON_RIGHT_ROUNDED,
                                color=ACCENT_COLOR if active else MUTED_TEXT,
                                size=22,
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )

    def render_motorcycle_detail() -> None:
        nonlocal selected_motorcycle_id
        detail_column.controls.clear()

        user = current_user()
        if user is None:
            return

        motorcycles = {m.id: m for m in list_user_motorcycles(user.id)}  # type: ignore
        if selected_motorcycle_id is None or selected_motorcycle_id not in motorcycles:
            detail_column.controls.append(
                empty_state(
                    "Selecciona una moto",
                    "El panel de detalle mostrara historial, alertas y sugerencias cuando elijas una motocicleta.",
                )
            )
            return

        motorcycle = motorcycles[selected_motorcycle_id]  # type: ignore
        fired_now = evaluate_alerts()
        relevant_fired = [alert for alert in fired_now if alert.motorcycle_id == motorcycle.id]  # type: ignore
        if relevant_fired:
            notify(f"Se actualizaron {len(relevant_fired)} alertas pendientes para esta moto.", tone="warning")

        history = list_maintenances(motorcycle.id)  # type: ignore
        alerts = list_alerts(motorcycle.id)  # type: ignore
        stats = [
            ("Placa", motorcycle.plate),
            ("Kilometraje", f"{motorcycle.current_km:.0f} km"),
            ("Servicios", str(len(history))),
            ("Alertas", str(len(alerts))),
        ]
        subtitle = "Sigue el estado del vehiculo, registra servicios y detecta proximos pendientes."

        history_items = [
            {
                "title": item.type,
                "meta": f"Fecha { _format_datetime(item.service_date) } | Km {item.km_at_service:.0f} | Costo {item.cost:.0f}",  # type: ignore
                "description": item.description or "Sin descripcion adicional.",
            }
            for item in history
        ]

        alert_items = []
        for alert in alerts:
            trigger_text = (
                f"Objetivo por km: {alert.trigger_km:.0f}"
                if alert.trigger_type == "km" and alert.trigger_km is not None  # type: ignore
                else f"Objetivo por fecha: {_format_datetime(alert.trigger_date)}"  # type: ignore
            )
            alert_items.append(
                {
                    "title": alert.title,
                    "meta": f"Tipo {alert.trigger_type} | {trigger_text}",
                    "status": "Disparada" if alert.is_fired else "Pendiente",  # type: ignore
                }
            )

        suggestions = _build_suggestions(motorcycle, history, alerts)

        detail_column.controls.extend(
            [
                build_motorcycle_hero(
                    title=f"{motorcycle.brand} {motorcycle.model}",
                    subtitle=subtitle,
                    stats=stats,
                ),
                build_profile_summary(session_state.user_name, session_state.user_email, len(motorcycles)),
                build_suggestions_panel(suggestions),
                build_new_maintenance_form(
                    maintenance_type,
                    maintenance_km,
                    maintenance_cost,
                    maintenance_date,
                    maintenance_next_km,
                    maintenance_description,
                    handle_add_maintenance,
                ),
                build_history_list(history_items),
                build_alert_form(
                    alert_title,
                    alert_trigger_type,
                    alert_trigger_km,
                    alert_trigger_date,
                    handle_add_alert,
                ),
                build_alert_list(alert_items),
            ]
        )

    def refresh_dashboard() -> None:
        nonlocal selected_motorcycle_id
        user = current_user()
        if user is None:
            return

        navbar_host.content = build_navbar(
            title=str(page.title),
            subtitle="Interfaz pensada para seguimiento preventivo y atencion clara al cliente.",
            user_name=session_state.user_name,
            on_logout=handle_logout,
        )
        db_label.value = f"Base de datos activa: {get_database_url()}"
        motorcycles = list_user_motorcycles(user.id)  # type: ignore
        total_alerts = 0
        fired_alerts = 0
        total_services = 0
        for motorcycle in motorcycles:
            moto_alerts = list_alerts(motorcycle.id)  # type: ignore
            total_alerts += len(moto_alerts)
            fired_alerts += len([alert for alert in moto_alerts if alert.is_fired])
            total_services += len(list_maintenances(motorcycle.id))  # type: ignore

        overview_column.controls = [
            ft.Container(
                margin=ft.margin.Margin.symmetric(horizontal=16),
                content=ft.Row(
                    [
                                    metric_tile("Motos", str(len(motorcycles)), ft.icons.Icons.TWO_WHEELER_ROUNDED, color=PRIMARY_COLOR),
                                    metric_tile("Servicios", str(total_services), ft.icons.Icons.BUILD_ROUNDED, color=ACCENT_COLOR),
                    ],
                    spacing=10,
                ),
            ),
            ft.Container(
                margin=ft.margin.Margin.symmetric(horizontal=16),
                content=ft.Row(
                    [
                        metric_tile("Alertas", str(total_alerts), ft.icons.Icons.NOTIFICATIONS_ROUNDED, color=INFO_COLOR),
                        metric_tile("Criticas", str(fired_alerts), ft.icons.Icons.PRIORITY_HIGH_ROUNDED, color=DANGER_COLOR if fired_alerts else SUCCESS_COLOR),
                    ],
                    spacing=10,
                ),
            ),
        ]
        if motorcycles and (selected_motorcycle_id is None or all(m.id != selected_motorcycle_id for m in motorcycles)):
            selected_motorcycle_id = motorcycles[0].id  # type: ignore
        if not motorcycles:
            selected_motorcycle_id = None

        render_motorcycle_cards(motorcycles)
        render_motorcycle_detail()
        page.update()

    def show_auth_view() -> None:
        auth_panel.visible = True
        dashboard_panel.visible = False
        page.update()

    def show_dashboard_view() -> None:
        auth_panel.visible = False
        dashboard_panel.visible = True
        refresh_dashboard()

    def select_motorcycle(moto_id: int) -> None:
        nonlocal selected_motorcycle_id
        selected_motorcycle_id = moto_id
        refresh_dashboard()

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
            user = register_user(
                register_name.value or "",
                register_email.value or "",
                register_password.value or "",
            )
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
        nonlocal selected_motorcycle_id
        selected_motorcycle_id = None
        session_state.logout()
        notify("Sesion cerrada.", tone="info")
        show_auth_view()

    def handle_add_motorcycle(_e) -> None:
        try:
            if session_state.user_id is None:
                raise ValueError("No hay una sesion activa.")

            add_motorcycle(
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

        moto_brand.value = ""
        moto_model.value = ""
        moto_year.value = ""
        moto_plate.value = ""
        moto_km.value = "0"
        notify("Motocicleta registrada.", tone="success")
        refresh_dashboard()

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
        refresh_dashboard()

    def handle_add_alert(_e) -> None:
        try:
            trigger_type = alert_trigger_type.value or "km"
            create_alert(
                motorcycle_id=require_selected_motorcycle(),
                title=alert_title.value or "",
                trigger_type=trigger_type,
                trigger_km=_parse_optional_float(alert_trigger_km.value or "") if trigger_type == "km" else None,
                trigger_date=_parse_datetime(alert_trigger_date.value or "") if trigger_type == "date" else None,
            )
        except ValueError as exc:
            notify(str(exc), tone="error")
            return

        alert_title.value = ""
        alert_trigger_km.value = ""
        alert_trigger_date.value = ""
        notify("Alerta creada.", tone="success")
        refresh_dashboard()

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

    dashboard_panel.controls = [
        ft.Container(margin=ft.margin.Margin.symmetric(horizontal=16, vertical=16), content=navbar_host),
        overview_column,
            ft.Container(
            margin=ft.margin.Margin.symmetric(horizontal=16),
            content=section_card(
                ft.Column(
                    [
                        section_title(
                            "Registrar motocicleta",
                            "Agrega motos del cliente y administra su progreso desde el panel.",
                            ft.icons.Icons.ADD_ROAD_ROUNDED,
                        ),
                        moto_brand,
                        moto_model,
                        ft.Row([ft.Container(content=moto_year, expand=1), ft.Container(content=moto_plate, expand=1)], spacing=10),
                        moto_km,
                        ft.ElevatedButton(
                            "Agregar motocicleta",
                            on_click=handle_add_motorcycle,
                            style=app_button_style(),
                        ),
                        db_label,
                    ],
                    spacing=12,
                )
            ),
        ),
        ft.Container(
            margin=ft.margin.Margin.symmetric(horizontal=16),
            bgcolor=SURFACE_COLOR,
            border_radius=8,
            border=ft.border.all(1, BORDER_COLOR),
            padding=16,
            content=ft.Column(
                [
                    section_title(
                        "Mis motocicletas",
                        "Selecciona una moto para ver historial, alertas y sugerencias.",
                        ft.icons.Icons.GARAGE_ROUNDED,
                    ),
                    motorcycles_column,
                ],
                spacing=12,
            ),
        ),
        detail_column,
        ft.Container(height=24),
    ]

    page.add(auth_panel, dashboard_panel)
    show_auth_view()


if __name__ == "__main__":
    bootstrap_database(seed=None)
    ft.app(target=run_app)

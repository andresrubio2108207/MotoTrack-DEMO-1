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


def run_app(page: ft.Page) -> None:
    session_state = SessionState()
    selected_motorcycle_id: int | None = None

    page.title = os.getenv("APP_NAME", "MotoTrack")
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 860
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#f4efe6"
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#204b57",
            secondary="#d96c3d",
            surface="#fffaf3",
            background="#f4efe6",
        )
    )

    login_email = ft.TextField(label="Correo", width=320)
    login_password = ft.TextField(label="Contrasena", password=True, can_reveal_password=True, width=320)

    register_name = ft.TextField(label="Nombre completo", width=320)
    register_email = ft.TextField(label="Correo", width=320)
    register_password = ft.TextField(label="Contrasena", password=True, can_reveal_password=True, width=320)

    moto_brand = ft.TextField(label="Marca", width=180)
    moto_model = ft.TextField(label="Modelo", width=180)
    moto_year = ft.TextField(label="Ano", width=120)
    moto_plate = ft.TextField(label="Placa", width=150)
    moto_km = ft.TextField(label="Kilometraje actual", width=160, value="0")

    maintenance_type = ft.TextField(label="Tipo de mantenimiento", width=260)
    maintenance_km = ft.TextField(label="Km del servicio", width=150)
    maintenance_cost = ft.TextField(label="Costo", width=140, value="0")
    maintenance_date = ft.TextField(label="Fecha ISO", width=220, hint_text="2026-05-06T10:30:00+00:00")
    maintenance_next_km = ft.TextField(label="Proximo servicio km", width=170)
    maintenance_description = ft.TextField(label="Descripcion", multiline=True, min_lines=2, max_lines=3, width=500)

    alert_title = ft.TextField(label="Titulo de alerta", width=250)
    alert_trigger_type = ft.Dropdown(
        label="Tipo",
        width=150,
        value="km",
        options=[ft.dropdown.Option("km"), ft.dropdown.Option("date")],
    )
    alert_trigger_km = ft.TextField(label="Km objetivo", width=150)
    alert_trigger_date = ft.TextField(label="Fecha ISO", width=220, hint_text="2026-06-01T00:00:00+00:00")

    auth_panel = ft.Column(spacing=18)
    dashboard_panel = ft.Column(spacing=20, visible=False)

    motorcycles_column = ft.Column(spacing=12)
    maintenances_column = ft.Column(spacing=10)
    alerts_column = ft.Column(spacing=10)
    selected_motorcycle_label = ft.Text("Selecciona una moto para ver el detalle.", size=16, weight=ft.FontWeight.W_600)
    db_label = ft.Text("", size=12, color="#51646a")

    def notify(message: str, color: str = "#204b57") -> None:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.colors.WHITE),
            bgcolor=color,
            open=True,
        )
        page.update()

    def current_user():
        if not session_state.user_id:
            return None
        return get_user_by_id(session_state.user_id)

    def require_selected_motorcycle() -> int:
        if selected_motorcycle_id is None:
            raise ValueError("Primero selecciona una motocicleta.")
        return selected_motorcycle_id

    def render_motorcycle_detail() -> None:
        nonlocal selected_motorcycle_id

        maintenances_column.controls.clear()
        alerts_column.controls.clear()

        if selected_motorcycle_id is None:
            selected_motorcycle_label.value = "Selecciona una moto para ver el detalle."
            return

        user = current_user()
        if user is None:
            selected_motorcycle_id = None
            selected_motorcycle_label.value = "Selecciona una moto para ver el detalle."
            return

        motorcycles = {m.id: m for m in list_user_motorcycles(user.id)}
        motorcycle = motorcycles.get(selected_motorcycle_id)
        if motorcycle is None:
            selected_motorcycle_id = None
            selected_motorcycle_label.value = "Selecciona una moto para ver el detalle."
            return

        selected_motorcycle_label.value = (
            f"{motorcycle.brand} {motorcycle.model} | placa {motorcycle.plate} | {motorcycle.current_km:.0f} km"
        )

        history = list_maintenances(motorcycle.id)
        if history:
            for item in history:
                maintenances_column.controls.append(
                    ft.Container(
                        bgcolor="#fffaf3",
                        border=ft.border.all(1, "#d7c8b1"),
                        border_radius=14,
                        padding=14,
                        content=ft.Column(
                            [
                                ft.Text(item.type, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    f"Fecha: {item.service_date} | Km: {item.km_at_service:.0f} | Costo: {item.cost:.0f}"
                                ),
                                ft.Text(item.description or "Sin descripcion", color="#6b7280"),
                            ],
                            spacing=4,
                        ),
                    )
                )
        else:
            maintenances_column.controls.append(ft.Text("Aun no hay mantenimientos registrados."))

        fired_now = evaluate_alerts()
        alert_rows = list_alerts(motorcycle.id)
        if alert_rows:
            if fired_now:
                relevant = [alert for alert in fired_now if alert.motorcycle_id == motorcycle.id]
                if relevant:
                    notify(f"Se actualizaron {len(relevant)} alertas pendientes para esta moto.", "#d96c3d")

            for alert in alert_rows:
                trigger_text = (
                    f"Km objetivo: {alert.trigger_km:.0f}"
                    if alert.trigger_type == "km" and alert.trigger_km is not None
                    else f"Fecha objetivo: {alert.trigger_date}"
                )
                status = "Disparada" if alert.is_fired else "Pendiente"
                alerts_column.controls.append(
                    ft.Container(
                        bgcolor="#fffaf3",
                        border=ft.border.all(1, "#d7c8b1"),
                        border_radius=14,
                        padding=14,
                        content=ft.Column(
                            [
                                ft.Text(alert.title, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Tipo: {alert.trigger_type} | {trigger_text}"),
                                ft.Text(f"Estado: {status}", color="#d96c3d" if alert.is_fired else "#51646a"),
                            ],
                            spacing=4,
                        ),
                    )
                )
        else:
            alerts_column.controls.append(ft.Text("Aun no hay alertas para esta moto."))

    def refresh_dashboard() -> None:
        nonlocal selected_motorcycle_id

        motorcycles_column.controls.clear()
        user = current_user()
        if user is None:
            return

        db_label.value = f"Base de datos activa: {get_database_url()}"
        motos = list_user_motorcycles(user.id)

        if not motos:
            selected_motorcycle_id = None
            motorcycles_column.controls.append(ft.Text("Todavia no tienes motocicletas registradas."))
        else:
            if selected_motorcycle_id is None or all(m.id != selected_motorcycle_id for m in motos):
                selected_motorcycle_id = motos[0].id

            for motorcycle in motos:
                motorcycles_column.controls.append(
                    ft.Container(
                        bgcolor="#fffaf3" if motorcycle.id != selected_motorcycle_id else "#f8d9c4",
                        border=ft.border.all(1, "#d7c8b1"),
                        border_radius=16,
                        padding=16,
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            f"{motorcycle.brand} {motorcycle.model}",
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.ElevatedButton(
                                            "Ver detalle",
                                            on_click=lambda _e, moto_id=motorcycle.id: select_motorcycle(moto_id),
                                            style=ft.ButtonStyle(
                                                bgcolor="#204b57",
                                                color=ft.colors.WHITE,
                                            ),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Text(
                                    f"Placa {motorcycle.plate} | Ano {motorcycle.year} | {motorcycle.current_km:.0f} km"
                                ),
                            ],
                            spacing=6,
                        ),
                    )
                )

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
            notify("Credenciales invalidas.", "#b42318")
            return

        session_state.login(user)
        login_password.value = ""
        notify(f"Bienvenido, {user.name}.")
        show_dashboard_view()

    def handle_register(_e) -> None:
        try:
            user = register_user(
                register_name.value or "",
                register_email.value or "",
                register_password.value or "",
            )
        except ValueError as exc:
            notify(str(exc), "#b42318")
            return

        session_state.login(user)
        register_name.value = ""
        register_email.value = ""
        register_password.value = ""
        notify("Cuenta creada correctamente.")
        show_dashboard_view()

    def handle_logout(_e) -> None:
        nonlocal selected_motorcycle_id
        selected_motorcycle_id = None
        session_state.logout()
        notify("Sesion cerrada.")
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
            notify(str(exc), "#b42318")
            return

        moto_brand.value = ""
        moto_model.value = ""
        moto_year.value = ""
        moto_plate.value = ""
        moto_km.value = "0"
        notify("Motocicleta registrada.")
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
            notify(str(exc), "#b42318")
            return

        maintenance_type.value = ""
        maintenance_km.value = ""
        maintenance_cost.value = "0"
        maintenance_date.value = ""
        maintenance_next_km.value = ""
        maintenance_description.value = ""
        notify("Mantenimiento guardado.")
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
            notify(str(exc), "#b42318")
            return

        alert_title.value = ""
        alert_trigger_km.value = ""
        alert_trigger_date.value = ""
        notify("Alerta creada.")
        refresh_dashboard()

    auth_panel.controls = [
        ft.Container(
            bgcolor="#204b57",
            border_radius=28,
            padding=32,
            content=ft.Column(
                [
                    ft.Text(page.title, size=34, weight=ft.FontWeight.BOLD, color="#fffaf3"),
                    ft.Text("Controla motos, mantenimientos y alertas desde SQLite + SQLAlchemy.", color="#d9e7ea"),
                    ft.Row(
                        [
                            ft.Container(
                                expand=True,
                                bgcolor="#fffaf3",
                                border_radius=20,
                                padding=24,
                                content=ft.Column(
                                    [
                                        ft.Text("Iniciar sesion", size=22, weight=ft.FontWeight.BOLD),
                                        login_email,
                                        login_password,
                                        ft.ElevatedButton(
                                            "Entrar",
                                            on_click=handle_login,
                                            style=ft.ButtonStyle(bgcolor="#d96c3d", color=ft.colors.WHITE),
                                        ),
                                    ],
                                    spacing=14,
                                ),
                            ),
                            ft.Container(
                                expand=True,
                                bgcolor="#fffaf3",
                                border_radius=20,
                                padding=24,
                                content=ft.Column(
                                    [
                                        ft.Text("Crear cuenta", size=22, weight=ft.FontWeight.BOLD),
                                        register_name,
                                        register_email,
                                        register_password,
                                        ft.ElevatedButton(
                                            "Registrarme",
                                            on_click=handle_register,
                                            style=ft.ButtonStyle(bgcolor="#204b57", color=ft.colors.WHITE),
                                        ),
                                    ],
                                    spacing=14,
                                ),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Text(
                        "Demo listo. Si activaste AUTO_SEED_DATA, puedes usar demo@mototrack.local / demo1234",
                        size=12,
                        color="#d9e7ea",
                    ),
                ],
                spacing=22,
            ),
        )
    ]

    dashboard_panel.controls = [
        ft.Container(
            bgcolor="#fffaf3",
            border_radius=24,
            padding=24,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(page.title, size=30, weight=ft.FontWeight.BOLD),
                                    ft.Text("Panel principal conectado a SQLite y SQLAlchemy.", color="#51646a"),
                                    db_label,
                                ],
                                spacing=4,
                            ),
                            ft.OutlinedButton("Cerrar sesion", on_click=handle_logout),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                col={"sm": 12, "md": 5},
                                content=ft.Column(
                                    [
                                        ft.Text("Mis motocicletas", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Row([moto_brand, moto_model], wrap=True),
                                        ft.Row([moto_year, moto_plate, moto_km], wrap=True),
                                        ft.ElevatedButton(
                                            "Agregar motocicleta",
                                            on_click=handle_add_motorcycle,
                                            style=ft.ButtonStyle(bgcolor="#204b57", color=ft.colors.WHITE),
                                        ),
                                        motorcycles_column,
                                    ],
                                    spacing=14,
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 7},
                                content=ft.Column(
                                    [
                                        selected_motorcycle_label,
                                        ft.Divider(),
                                        ft.Text("Registrar mantenimiento", size=18, weight=ft.FontWeight.BOLD),
                                        ft.Row([maintenance_type, maintenance_km, maintenance_cost], wrap=True),
                                        ft.Row([maintenance_date, maintenance_next_km], wrap=True),
                                        maintenance_description,
                                        ft.ElevatedButton(
                                            "Guardar mantenimiento",
                                            on_click=handle_add_maintenance,
                                            style=ft.ButtonStyle(bgcolor="#d96c3d", color=ft.colors.WHITE),
                                        ),
                                        ft.Text("Historial", size=18, weight=ft.FontWeight.BOLD),
                                        maintenances_column,
                                        ft.Divider(),
                                        ft.Text("Nueva alerta", size=18, weight=ft.FontWeight.BOLD),
                                        ft.Row([alert_title, alert_trigger_type, alert_trigger_km, alert_trigger_date], wrap=True),
                                        ft.ElevatedButton(
                                            "Crear alerta",
                                            on_click=handle_add_alert,
                                            style=ft.ButtonStyle(bgcolor="#204b57", color=ft.colors.WHITE),
                                        ),
                                        ft.Text("Alertas", size=18, weight=ft.FontWeight.BOLD),
                                        alerts_column,
                                    ],
                                    spacing=14,
                                ),
                            ),
                        ]
                    ),
                ],
                spacing=18,
            ),
        )
    ]

    page.add(auth_panel, dashboard_panel)
    show_auth_view()


if __name__ == "__main__":
    bootstrap_database(seed=None)
    ft.app(target=run_app)

"""Página de detalle de un mantenimiento específico."""

import flet as ft
from app.database.engine import SessionLocal
from app.models.maintenance import Maintenance
from app.services.maintenance_service import complete_maintenance
from app.state.session_state import session_state
from ui.shared.theme import (
    BACKGROUND, SURFACE_VARIANT, PRIMARY, ON_SURFACE, ON_SURFACE_MUTED,
    SUCCESS, WARNING, BORDER, primary_button_style,
)
from ui.shared.snackbar import show_snackbar
from ui.shared.navbar import build_navbar


def detail_page(page: ft.Page, maintenance_id: int):
    """Construye y muestra el detalle de un mantenimiento."""
    page.title = "MotoTrack PRO - Detalle"
    page.bgcolor = BACKGROUND
    page.padding = 0

    if not session_state.is_authenticated:
        page.go("/login")
        return

    db = SessionLocal()
    maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
    db.close()

    if not maintenance:
        show_snackbar(page, "Mantenimiento no encontrado", "error")
        page.go("/maintenance")
        return

    def do_complete(e):
        db = SessionLocal()
        result = complete_maintenance(db, maintenance_id)
        db.close()
        if result:
            show_snackbar(page, "Mantenimiento marcado como completado ✅", "success")
            detail_page(page, maintenance_id)  # Refrescar
        else:
            show_snackbar(page, "No se pudo actualizar el mantenimiento", "error")

    def info_row(icon, label, value: str) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(icon, color=PRIMARY, size=18),
                        bgcolor=ft.Colors.with_opacity(0.1, PRIMARY),
                        border_radius=8,
                        padding=ft.padding.all(6),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(label, size=11, color=ON_SURFACE_MUTED),
                            ft.Text(value or "—", size=14, color=ON_SURFACE, weight=ft.FontWeight.W_500),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=12,
            ),
            bgcolor=SURFACE_VARIANT,
            border_radius=12,
            padding=ft.padding.all(14),
        )

    status_color = SUCCESS if maintenance.completed else WARNING
    status_text = "Completado" if maintenance.completed else "Pendiente"
    status_icon = ft.Icons.CHECK_CIRCLE_ROUNDED if maintenance.completed else ft.Icons.PENDING_ROUNDED

    content = ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_ROUNDED,
                            icon_color=ON_SURFACE,
                            on_click=lambda e: page.go("/maintenance"),
                        ),
                        ft.Text("Detalle", size=22, weight=ft.FontWeight.BOLD, color=ON_SURFACE),
                    ],
                    spacing=8,
                ),

                ft.Divider(height=8, color="transparent"),

                # Tipo y estado
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.BUILD_ROUNDED, color=PRIMARY, size=28),
                                bgcolor=ft.Colors.with_opacity(0.1, PRIMARY),
                                border_radius=14,
                                padding=ft.padding.all(10),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(maintenance.type, size=18, weight=ft.FontWeight.BOLD, color=ON_SURFACE),
                                    ft.Row(
                                        controls=[
                                            ft.Icon(status_icon, color=status_color, size=14),
                                            ft.Text(status_text, size=12, color=status_color),
                                        ],
                                        spacing=4,
                                    ),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                        ],
                        spacing=14,
                    ),
                    bgcolor=SURFACE_VARIANT,
                    border_radius=16,
                    padding=ft.padding.all(18),
                ),

                ft.Divider(height=12, color="transparent"),

                # Detalles
                ft.Text("Información", size=14, weight=ft.FontWeight.W_600, color=ON_SURFACE_MUTED),
                ft.Divider(height=6, color="transparent"),
                info_row(ft.Icons.CALENDAR_TODAY_ROUNDED, "Fecha", maintenance.date.strftime("%d/%m/%Y %H:%M") if maintenance.date else "—"),
                ft.Divider(height=6, color="transparent"),
                info_row(ft.Icons.SPEED_ROUNDED, "Kilómetros", f"{maintenance.km:.0f} km"),
                ft.Divider(height=6, color="transparent"),
                info_row(ft.Icons.NOTES_ROUNDED, "Descripción", maintenance.description or "Sin descripción"),
                ft.Divider(height=6, color="transparent"),
                info_row(
                    ft.Icons.UPDATE_ROUNDED,
                    "Próximo mantenimiento (km)",
                    f"{maintenance.next_km:.0f} km" if maintenance.next_km else "—",
                ),
                ft.Divider(height=6, color="transparent"),
                info_row(
                    ft.Icons.EVENT_ROUNDED,
                    "Próxima fecha",
                    maintenance.next_date.strftime("%d/%m/%Y") if maintenance.next_date else "—",
                ),

                ft.Divider(height=20, color="transparent"),

                # Botón completar (solo si no está completado)
                ft.ElevatedButton(
                    text="Marcar como Completado",
                    icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
                    style=primary_button_style(),
                    on_click=do_complete,
                    expand=True,
                    visible=not maintenance.completed,
                ),
            ],
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=24),
        expand=True,
        bgcolor=BACKGROUND,
    )

    page.controls.clear()
    page.navigation_bar = build_navbar(page, active_index=0)
    page.add(content)
    page.update()

"""Página de historial de mantenimientos."""

import flet as ft
from app.database.engine import SessionLocal
from app.services.maintenance_service import get_maintenance_history
from app.state.session_state import session_state
from ui.shared.theme import (
    BACKGROUND, SURFACE_VARIANT, PRIMARY, ON_SURFACE, ON_SURFACE_MUTED,
    SUCCESS, WARNING, BORDER,
)
from ui.shared.navbar import build_navbar


def _status_chip(completed: bool) -> ft.Container:
    color = SUCCESS if completed else WARNING
    text = "Completado" if completed else "Pendiente"
    icon = ft.Icons.CHECK_CIRCLE_ROUNDED if completed else ft.Icons.PENDING_ROUNDED
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, color=color, size=12),
                ft.Text(text, size=11, color=color),
            ],
            spacing=4,
            tight=True,
        ),
        bgcolor=ft.Colors.with_opacity(0.12, color),
        border_radius=8,
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
    )


def _maintenance_card(page: ft.Page, m, on_tap) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.BUILD_ROUNDED, color=PRIMARY, size=20),
                            bgcolor=ft.Colors.with_opacity(0.1, PRIMARY),
                            border_radius=10,
                            padding=ft.padding.all(8),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(m.type, size=15, weight=ft.FontWeight.W_600, color=ON_SURFACE),
                                ft.Text(
                                    m.date.strftime("%d/%m/%Y") if m.date else "—",
                                    size=12,
                                    color=ON_SURFACE_MUTED,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        _status_chip(m.completed),
                    ],
                    spacing=12,
                ),
                ft.Divider(height=10, color=BORDER),
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SPEED_ROUNDED, color=ON_SURFACE_MUTED, size=14),
                                ft.Text(f"{m.km:.0f} km", size=12, color=ON_SURFACE_MUTED),
                            ],
                            spacing=4,
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color=ON_SURFACE_MUTED, size=14),
                            ],
                            spacing=4,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=4,
        ),
        bgcolor=SURFACE_VARIANT,
        border_radius=16,
        padding=ft.padding.all(16),
        on_click=lambda e: on_tap(m.id),
        ink=True,
        border=ft.border.all(1, BORDER),
        animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )


def history_page(page: ft.Page):
    """Construye y muestra la página de historial de mantenimientos."""
    page.title = "MotoTrack PRO - Mantenimientos"
    page.bgcolor = BACKGROUND
    page.padding = 0

    if not session_state.is_authenticated:
        page.go("/login")
        return

    moto = session_state.current_motorcycle
    user = session_state.current_user

    def on_tap(maintenance_id: int):
        page.go(f"/maintenance/{maintenance_id}")

    def refresh():
        page.controls.clear()
        page.navigation_bar = build_navbar(page, active_index=0)

        if not moto:
            page.add(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.TWO_WHEELER_ROUNDED, size=64, color=ON_SURFACE_MUTED),
                            ft.Text("Sin motocicleta registrada", size=16, color=ON_SURFACE_MUTED),
                            ft.Text("Regístra una moto para comenzar.", size=13, color=ON_SURFACE_MUTED),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                    bgcolor=BACKGROUND,
                )
            )
            page.update()
            return

        db = SessionLocal()
        records = get_maintenance_history(db, moto.id)
        db.close()

        cards = [_maintenance_card(page, m, on_tap) for m in records]

        body = ft.Container(
            content=ft.Column(
                controls=[
                    # Header
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Column(
                                            controls=[
                                                ft.Text("Mantenimientos", size=24, weight=ft.FontWeight.BOLD, color=ON_SURFACE),
                                                ft.Text(f"{moto.brand} {moto.model} · {moto.current_km:.0f} km", size=13, color=ON_SURFACE_MUTED),
                                            ],
                                            spacing=4,
                                            expand=True,
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.ADD_CIRCLE_ROUNDED,
                                            icon_color=PRIMARY,
                                            icon_size=32,
                                            tooltip="Nuevo mantenimiento",
                                            on_click=lambda e: page.go("/maintenance/new"),
                                        ),
                                    ],
                                    spacing=8,
                                ),
                            ],
                            spacing=4,
                        ),
                        padding=ft.padding.only(top=16, bottom=8),
                    ),

                    # Lista
                    *(cards if cards else [
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.BUILD_CIRCLE_OUTLINED, size=56, color=ON_SURFACE_MUTED),
                                    ft.Text("Sin mantenimientos registrados", size=15, color=ON_SURFACE_MUTED),
                                    ft.Text("Registra el primer mantenimiento con el botón +", size=12, color=ON_SURFACE_MUTED, text_align=ft.TextAlign.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=12,
                            ),
                            alignment=ft.alignment.center,
                            padding=ft.padding.all(40),
                        )
                    ]),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            expand=True,
            bgcolor=BACKGROUND,
        )

        page.add(body)
        page.update()

    refresh()

"""Barra de navegación inferior compartida."""

import flet as ft
from ui.shared.theme import PRIMARY, SURFACE, BORDER, ON_SURFACE_MUTED


def build_navbar(page: ft.Page, active_index: int = 0) -> ft.NavigationBar:
    """
    Construye la barra de navegación inferior.

    Args:
        page: La página Flet.
        active_index: Índice de la pestaña activa (0=Mantenimientos, 1=Alertas, 2=Perfil).

    Returns:
        Un NavigationBar configurado.
    """

    def on_change(e):
        idx = e.control.selected_index
        if idx == 0:
            page.go("/maintenance")
        elif idx == 1:
            page.go("/alerts")
        elif idx == 2:
            page.go("/profile")

    return ft.NavigationBar(
        selected_index=active_index,
        bgcolor=SURFACE,
        indicator_color=ft.Colors.with_opacity(0.15, PRIMARY),
        shadow_color=ft.Colors.BLACK,
        surface_tint_color=PRIMARY,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.BUILD_OUTLINED,
                selected_icon=ft.Icons.BUILD_ROUNDED,
                label="Mantenimientos",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                selected_icon=ft.Icons.NOTIFICATIONS_ROUNDED,
                label="Alertas",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.PERSON_OUTLINE_ROUNDED,
                selected_icon=ft.Icons.PERSON_ROUNDED,
                label="Perfil",
            ),
        ],
        on_change=on_change,
        animation_duration=200,
    )

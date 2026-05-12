from __future__ import annotations

import flet as ft

from ui.shared.theme import ACCENT_COLOR, BORDER_COLOR, PRIMARY_COLOR, SURFACE_COLOR, TEXT_COLOR, translucent


def build_navbar(
    *,
    title: str,
    subtitle: str,
    user_name: str | None,
    on_logout,
) -> ft.Container:
    initials = (user_name or "?")[0].upper()

    return ft.Container(
        padding=ft.padding.Padding.symmetric(horizontal=14, vertical=12),
        border_radius=20,
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment.TOP_LEFT,
            end=ft.alignment.Alignment.BOTTOM_RIGHT,
            colors=[PRIMARY_COLOR, "#236478"],
        ),
        content=ft.Row(
            [
                ft.Container(
                    width=40,
                    height=40,
                    border_radius=15,
                    bgcolor=translucent(SURFACE_COLOR, "24"),
                    alignment=ft.alignment.Alignment.CENTER,
                    content=ft.Icon(ft.icons.Icons.TWO_WHEELER_ROUNDED, color=SURFACE_COLOR, size=22),
                ),
                ft.Column(
                    [
                        ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=SURFACE_COLOR),
                        ft.Text(subtitle, size=11, color="#D8EEF3"),
                    ],
                    spacing=1,
                    tight=True,
                    expand=True,
                ),
                ft.Container(
                    width=34,
                    height=34,
                    border_radius=13,
                    bgcolor=SURFACE_COLOR,
                    border=ft.border.all(1, BORDER_COLOR),
                    alignment=ft.alignment.Alignment.CENTER,
                    content=ft.Text(initials, size=13, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.LOGOUT_ROUNDED,
                    icon_color=SURFACE_COLOR,
                    icon_size=21,
                    tooltip="Cerrar sesion",
                    on_click=on_logout,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

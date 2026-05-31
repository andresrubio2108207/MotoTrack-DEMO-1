from __future__ import annotations

import flet as ft

from ui.shared.theme import BORDER_COLOR, DANGER_COLOR, PRIMARY_COLOR, SURFACE_COLOR, TEXT_COLOR, translucent


def build_navbar(
    *,
    title: str,
    subtitle: str,
    user_name: str | None,
    alertas_activas: int = 0,
    compact: bool = False,
    on_alerts_click=None,
    on_profile_click=None,
    on_logout=None,
) -> ft.Container:
    initials = (user_name or "?")[0].upper()
    title_size = 16 if compact else 18
    subtitle_size = 10 if compact else 11

    return ft.Container(
        padding=ft.padding.Padding.symmetric(horizontal=12 if compact else 14, vertical=10 if compact else 12),
        border_radius=18 if compact else 20,
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment.TOP_LEFT,
            end=ft.alignment.Alignment.BOTTOM_RIGHT,
            colors=[PRIMARY_COLOR, "#236478"],
        ),
        content=ft.Row(
            [
                ft.Container(
                    width=38 if compact else 42,
                    height=38 if compact else 42,
                    border_radius=14 if compact else 16,
                    bgcolor=translucent(SURFACE_COLOR, "24"),
                    alignment=ft.alignment.Alignment.CENTER,
                    content=ft.Icon(ft.icons.Icons.TWO_WHEELER_ROUNDED, color=SURFACE_COLOR, size=21 if compact else 23),
                ),
                ft.Column(
                    [
                        ft.Text(title, size=title_size, weight=ft.FontWeight.BOLD, color=SURFACE_COLOR, max_lines=1),
                        ft.Text(subtitle, size=subtitle_size, color="#D8EEF3", max_lines=1),
                    ],
                    spacing=1,
                    tight=True,
                    expand=True,
                ),
                _alerts_icon(alertas_activas, on_click=on_alerts_click),
                ft.Container(
                    width=34 if compact else 36,
                    height=34 if compact else 36,
                    border_radius=13 if compact else 14,
                    bgcolor=SURFACE_COLOR,
                    border=ft.border.all(1, BORDER_COLOR),
                    alignment=ft.alignment.Alignment.CENTER,
                    on_click=on_profile_click,
                    ink=True,
                    content=ft.Text(initials, size=13, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                ),
            ],
            spacing=8 if compact else 10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def _alerts_icon(alertas_activas: int, on_click=None) -> ft.Control:
    bell = ft.Icon(ft.icons.Icons.NOTIFICATIONS_ROUNDED, color=SURFACE_COLOR, size=22)
    if alertas_activas <= 0:
        return ft.Container(
            width=36,
            height=36,
            border_radius=14,
            bgcolor=translucent(SURFACE_COLOR, "14"),
            alignment=ft.alignment.Alignment.CENTER,
            on_click=on_click,
            ink=True,
            content=bell,
        )

    return ft.Stack(
        [
            ft.Container(
                width=36,
                height=36,
                border_radius=14,
                bgcolor=translucent(SURFACE_COLOR, "18"),
                alignment=ft.alignment.Alignment.CENTER,
                on_click=on_click,
                ink=True,
                content=bell,
            ),
            ft.Container(
                right=0,
                top=0,
                width=18,
                height=18,
                border_radius=9,
                bgcolor=DANGER_COLOR,
                alignment=ft.alignment.Alignment.CENTER,
                content=ft.Text(str(min(alertas_activas, 9)), size=10, color="#FFFFFF", weight=ft.FontWeight.BOLD),
            ),
        ],
        width=36,
        height=36,
    )

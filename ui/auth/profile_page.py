from __future__ import annotations

import flet as ft

from ui.shared.theme import (
    ACCENT_COLOR,
    ACCENT_SOFT,
    BORDER_COLOR,
    MUTED_TEXT,
    PRIMARY_COLOR,
    PRIMARY_LIGHT,
    SUCCESS_COLOR,
    SURFACE_COLOR,
    TEXT_COLOR,
    pill,
    section_card,
    status_badge,
    translucent,
)


def _feature_chip(icon: str, label: str) -> ft.Container:
    return ft.Container(
        bgcolor=translucent("#FFFFFF", "24"),
        border_radius=999,
        padding=ft.padding.Padding.symmetric(horizontal=10, vertical=6),
        content=ft.Row(
            [
                ft.Icon(icon, color="#FFFFFF", size=14),
                ft.Text(label, size=11, color="#FFFFFF", weight=ft.FontWeight.W_600),
            ],
            spacing=5,
            tight=True,
        ),
    )


def build_auth_header() -> ft.Container:
    return ft.Container(
        margin=ft.margin.Margin.symmetric(horizontal=16),
        padding=18,
        border_radius=20,
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment.TOP_LEFT,
            end=ft.alignment.Alignment.BOTTOM_RIGHT,
            colors=[PRIMARY_COLOR, "#236478", ACCENT_COLOR],
        ),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            width=56,
                            height=56,
                            border_radius=18,
                            bgcolor=translucent("#FFFFFF", "24"),
                            alignment=ft.alignment.Alignment.CENTER,
                            content=ft.Icon(ft.icons.Icons.TWO_WHEELER_ROUNDED, color="#FFFFFF", size=31),
                        ),
                        ft.Column(
                            [
                                ft.Text("MotoTrack", size=27, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                ft.Text("Mantenimiento premium para motos cuidadas.", size=12, color="#FCE9DC"),
                            ],
                            spacing=3,
                            tight=True,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        _feature_chip(ft.icons.Icons.HISTORY_ROUNDED, "Historial"),
                        _feature_chip(ft.icons.Icons.NOTIFICATIONS_ROUNDED, "Alertas"),
                        _feature_chip(ft.icons.Icons.BUILD_ROUNDED, "Servicios"),
                    ],
                    spacing=8,
                    wrap=True,
                ),
            ],
            spacing=14,
        ),
    )


def build_profile_summary(user_name: str | None, user_email: str | None, total_motos: int) -> ft.Container:
    initials = "".join(word[0].upper() for word in (user_name or "U").split()[:2])

    return ft.Container(
        margin=ft.margin.Margin.symmetric(horizontal=16),
        content=section_card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                width=54,
                                height=54,
                                border_radius=18,
                                bgcolor=PRIMARY_LIGHT,
                                border=ft.border.all(1, BORDER_COLOR),
                                alignment=ft.alignment.Alignment.CENTER,
                                content=ft.Text(initials, size=19, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        user_name or "Usuario activo",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_COLOR,
                                    ),
                                    ft.Text(user_email or "Sin correo disponible", size=12, color=MUTED_TEXT),
                                ],
                                spacing=3,
                                tight=True,
                                expand=True,
                            ),
                            status_badge("Activo", color=SUCCESS_COLOR),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            pill("Motos registradas", str(total_motos), tone=ACCENT_SOFT),
                            pill("Estado", "Al dia", tone=PRIMARY_LIGHT),
                        ],
                        spacing=10,
                        wrap=True,
                    ),
                ],
                spacing=14,
            )
        ),
    )

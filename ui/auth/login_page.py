from __future__ import annotations

import flet as ft

from ui.shared.theme import (
    ACCENT_COLOR,
    MUTED_TEXT,
    PRIMARY_COLOR,
    PRIMARY_LIGHT,
    SURFACE_COLOR,
    TEXT_COLOR,
    primary_button,
    section_card,
    translucent,
)


def build_login_card(email_field: ft.TextField, password_field: ft.TextField, on_login, on_go_register=None) -> ft.Container:
    hero = ft.Container(
        padding=ft.padding.Padding.only(left=20, right=20, top=28, bottom=24),
        border_radius=20,
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment.TOP_LEFT,
            end=ft.alignment.Alignment.BOTTOM_RIGHT,
            colors=[PRIMARY_COLOR, "#236478"],
        ),
        content=ft.Column(
            [
                ft.Container(
                    width=54,
                    height=54,
                    border_radius=18,
                    bgcolor=translucent(SURFACE_COLOR, "24"),
                    alignment=ft.alignment.Alignment.CENTER,
                    content=ft.Icon(ft.icons.Icons.TWO_WHEELER_ROUNDED, color=SURFACE_COLOR, size=30),
                ),
                ft.Text("MotoTrack", size=30, weight=ft.FontWeight.BOLD, color=SURFACE_COLOR),
                ft.Text(
                    "Mantenimiento, alertas y vida util de tu moto en un solo lugar.",
                    size=13,
                    color="#D8EEF3",
                ),
            ],
            spacing=10,
            tight=True,
        ),
    )

    form = section_card(
        ft.Column(
            [
                ft.Text("Iniciar sesion", size=20, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                ft.Text("Accede al panel de seguimiento preventivo.", size=12, color=MUTED_TEXT),
                email_field,
                password_field,
                primary_button("Entrar al panel", on_click=on_login),
                ft.Container(
                    bgcolor=PRIMARY_LIGHT,
                    border_radius=16,
                    padding=ft.padding.Padding.symmetric(horizontal=14, vertical=11),
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.Icons.INFO_OUTLINE_ROUNDED, color=PRIMARY_COLOR, size=16),
                            ft.Text(
                                "Demo: demo@mototrack.local / demo1234",
                                size=11,
                                color=PRIMARY_COLOR,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
                ft.Row(
                    [
                        ft.Text("No tienes cuenta?", size=13, color=MUTED_TEXT),
                        ft.TextButton(
                            "Registrate",
                            on_click=on_go_register,
                            style=ft.ButtonStyle(color=ACCENT_COLOR),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    tight=True,
                ),
            ],
            spacing=12,
        ),
        padding=18,
    )

    return ft.Container(
        content=ft.Column([hero, ft.Container(height=12), form], spacing=0),
        bgcolor=SURFACE_COLOR,
        border_radius=22,
        padding=8,
    )

from __future__ import annotations

import flet as ft

from ui.shared.theme import (
    accent_button,
    MUTED_TEXT,
    PRIMARY_COLOR,
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
                ft.Row(
                    [
                        ft.Container(
                            width=58,
                            height=58,
                            border_radius=20,
                            bgcolor=translucent(SURFACE_COLOR, "22"),
                            alignment=ft.alignment.Alignment.CENTER,
                            content=ft.Icon(ft.icons.Icons.TWO_WHEELER_ROUNDED, color=SURFACE_COLOR, size=31),
                        ),
                        ft.Column(
                            [
                                ft.Text("MotoTrack", size=30, weight=ft.FontWeight.BOLD, color=SURFACE_COLOR),
                                ft.Text("Cuidado preventivo para tu moto.", size=12, color="#D8EEF3"),
                            ],
                            spacing=2,
                            tight=True,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(
                    bgcolor=translucent(SURFACE_COLOR, "14"),
                    border_radius=16,
                    padding=ft.padding.Padding.symmetric(horizontal=12, vertical=10),
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.Icons.VERIFIED_ROUNDED, color=SURFACE_COLOR, size=17),
                            ft.Text(
                                "Historial, kilometraje y alertas inteligentes en un panel.",
                                size=12,
                                color=SURFACE_COLOR,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
            ],
            spacing=14,
            tight=True,
        ),
    )

    form = section_card(
        ft.Column(
            [
                ft.Text("Iniciar sesión", size=20, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                ft.Text("Accede al panel de seguimiento preventivo.", size=12, color=MUTED_TEXT),
                email_field,
                password_field,
                primary_button("Entrar al panel", on_click=on_login),
                accent_button("Crear cuenta", on_click=on_go_register),
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

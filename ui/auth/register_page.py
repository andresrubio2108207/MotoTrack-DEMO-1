from __future__ import annotations

import flet as ft

from ui.shared.theme import (
    ACCENT_COLOR,
    ACCENT_SOFT,
    MUTED_TEXT,
    PRIMARY_COLOR,
    SURFACE_COLOR,
    TEXT_COLOR,
    accent_button,
    section_card,
    translucent,
)


def build_register_card(
    name_field: ft.TextField,
    email_field: ft.TextField,
    password_field: ft.TextField,
    on_register,
    on_go_login=None,
) -> ft.Container:
    hero = ft.Container(
        padding=ft.padding.Padding.only(left=20, right=20, top=28, bottom=24),
        border_radius=20,
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment.TOP_LEFT,
            end=ft.alignment.Alignment.BOTTOM_RIGHT,
            colors=[ACCENT_COLOR, "#B05A26"],
        ),
        content=ft.Column(
            [
                ft.Container(
                    width=54,
                    height=54,
                    border_radius=18,
                    bgcolor=translucent("#FFFFFF", "24"),
                    alignment=ft.alignment.Alignment.CENTER,
                    content=ft.Icon(ft.icons.Icons.PERSON_ADD_ROUNDED, color="#FFFFFF", size=29),
                ),
                ft.Text("Crear cuenta", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Text("Empieza a construir el historial completo de tu moto.", size=13, color="#FFE5D5"),
            ],
            spacing=10,
            tight=True,
        ),
    )

    form = section_card(
        ft.Column(
            [
                ft.Text("Datos de acceso", size=20, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                ft.Text("Tu cuenta queda lista para guardar motos y mantenimientos.", size=12, color=MUTED_TEXT),
                name_field,
                email_field,
                password_field,
                accent_button("Crear cuenta", on_click=on_register),
                ft.Container(
                    bgcolor=ACCENT_SOFT,
                    border_radius=16,
                    padding=ft.padding.Padding.symmetric(horizontal=14, vertical=11),
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.Icons.LOCK_OUTLINE_ROUNDED, color=ACCENT_COLOR, size=16),
                            ft.Text(
                                "Tu contrasena se almacena protegida con hash.",
                                size=11,
                                color=ACCENT_COLOR,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
                ft.Row(
                    [
                        ft.Text("Ya tienes cuenta?", size=13, color=MUTED_TEXT),
                        ft.TextButton("Inicia sesion", on_click=on_go_login, style=ft.ButtonStyle(color=PRIMARY_COLOR)),
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

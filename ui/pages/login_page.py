from __future__ import annotations

import flet as ft

from ui.shared.theme import (
    ACCENT_COLOR,
    MUTED_TEXT,
    PRIMARY_COLOR,
    PRIMARY_LIGHT,
    SURFACE_COLOR,
    TEXT_COLOR,
    mobile_field,
    primary_button,
    section_card,
    translucent,
)


def build_login_page(
    on_login,
    on_go_register,
) -> tuple[ft.Column, ft.TextField, ft.TextField]:
    email_field = mobile_field("Correo electronico", "demo@mototrack.local", keyboard=ft.KeyboardType.EMAIL)
    password_field = mobile_field("Contrasena", "********", password=True)

    hero = ft.Container(
        padding=ft.padding.Padding.only(left=24, right=24, top=52, bottom=32),
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
                ft.Text("Tu historial de mantenimiento, siempre al dia.", size=13, color="#D8EEF3"),
            ],
            spacing=10,
            tight=True,
        ),
    )

    card = ft.Container(
        margin=ft.margin.Margin.symmetric(horizontal=16),
        content=section_card(
            ft.Column(
                [
                    ft.Text("Iniciar sesion", size=20, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                    ft.Text("Accede a tus motos, mantenimientos y alertas.", size=12, color=MUTED_TEXT),
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
        ),
    )

    root = ft.Column(
        [hero, ft.Container(height=12), card, ft.Container(height=24)],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
    )

    return root, email_field, password_field

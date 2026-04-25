"""Página de perfil del usuario."""

import flet as ft
from app.state.session_state import session_state
from app.services.auth_service import logout
from ui.shared.theme import (
    BACKGROUND, SURFACE_VARIANT, PRIMARY, ON_SURFACE, ON_SURFACE_MUTED,
    BORDER, SUCCESS, ERROR,
)
from ui.shared.navbar import build_navbar
from ui.shared.snackbar import show_snackbar


def profile_page(page: ft.Page):
    """Construye y muestra la página de perfil."""
    page.title = "MotoTrack PRO - Perfil"
    page.bgcolor = BACKGROUND
    page.padding = 0

    user = session_state.current_user
    moto = session_state.current_motorcycle

    if not user:
        page.go("/login")
        return

    def do_logout(e):
        logout()
        show_snackbar(page, "Sesión cerrada correctamente.", "info")
        page.go("/login")

    # Avatar
    avatar = ft.Container(
        content=ft.Text(
            user.username[0].upper(),
            size=32,
            weight=ft.FontWeight.BOLD,
            color=PRIMARY,
        ),
        width=72,
        height=72,
        border_radius=36,
        bgcolor=ft.Colors.with_opacity(0.15, PRIMARY),
        alignment=ft.alignment.center,
    )

    def info_row(icon, label, value):
        return ft.Row(
            controls=[
                ft.Icon(icon, color=PRIMARY, size=18),
                ft.Column(
                    controls=[
                        ft.Text(label, size=11, color=ON_SURFACE_MUTED),
                        ft.Text(value or "—", size=14, color=ON_SURFACE, weight=ft.FontWeight.W_500),
                    ],
                    spacing=2,
                ),
            ],
            spacing=12,
        )

    # Motocicletas del usuario
    motos = user.motorcycles if user.motorcycles else []
    moto_cards = []
    for m in motos:
        is_active = moto and moto.id == m.id
        moto_cards.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.TWO_WHEELER_ROUNDED, color=PRIMARY, size=24),
                        ft.Column(
                            controls=[
                                ft.Text(f"{m.brand} {m.model}", size=15, weight=ft.FontWeight.W_600, color=ON_SURFACE),
                                ft.Text(f"{m.year or '—'} · {m.current_km:.0f} km", size=12, color=ON_SURFACE_MUTED),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Text("Activa", size=10, color=SUCCESS),
                            bgcolor=ft.Colors.with_opacity(0.1, SUCCESS),
                            border_radius=8,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            visible=is_active,
                        ),
                    ],
                    spacing=12,
                ),
                bgcolor=SURFACE_VARIANT,
                border_radius=12,
                padding=ft.padding.all(14),
                border=ft.border.all(1, PRIMARY if is_active else BORDER),
            )
        )

    content = ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Perfil", size=24, weight=ft.FontWeight.BOLD, color=ON_SURFACE),
                            ft.Text("Tu cuenta y motocicletas", size=13, color=ON_SURFACE_MUTED),
                        ],
                        spacing=4,
                    ),
                    padding=ft.padding.only(top=16, bottom=8),
                ),

                # Tarjeta de usuario
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    avatar,
                                    ft.Column(
                                        controls=[
                                            ft.Text(user.username, size=18, weight=ft.FontWeight.BOLD, color=ON_SURFACE),
                                            ft.Text(user.email, size=13, color=ON_SURFACE_MUTED),
                                        ],
                                        spacing=4,
                                        expand=True,
                                    ),
                                ],
                                spacing=16,
                            ),
                            ft.Divider(height=16, color=BORDER),
                            info_row(ft.Icons.BADGE_ROUNDED, "Usuario", user.username),
                            ft.Divider(height=8, color="transparent"),
                            info_row(ft.Icons.EMAIL_ROUNDED, "Email", user.email),
                            ft.Divider(height=8, color="transparent"),
                            info_row(ft.Icons.TWO_WHEELER_ROUNDED, "Motocicletas", str(len(motos))),
                        ],
                        spacing=4,
                    ),
                    bgcolor=SURFACE_VARIANT,
                    border_radius=16,
                    padding=ft.padding.all(20),
                ),

                ft.Divider(height=16, color="transparent"),

                # Mis motocicletas
                ft.Text("Mis Motocicletas", size=16, weight=ft.FontWeight.W_600, color=ON_SURFACE),
                ft.Divider(height=8, color="transparent"),
                *(moto_cards if moto_cards else [
                    ft.Container(
                        content=ft.Text("No hay motocicletas registradas.", color=ON_SURFACE_MUTED, text_align=ft.TextAlign.CENTER),
                        alignment=ft.alignment.center,
                        padding=ft.padding.all(24),
                    )
                ]),

                ft.Divider(height=24, color="transparent"),

                # Logout
                ft.ElevatedButton(
                    text="Cerrar Sesión",
                    icon=ft.Icons.LOGOUT_ROUNDED,
                    style=ft.ButtonStyle(
                        bgcolor=ERROR,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=ft.padding.symmetric(horizontal=24, vertical=14),
                    ),
                    on_click=do_logout,
                    expand=True,
                ),
            ],
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=8),
        expand=True,
        bgcolor=BACKGROUND,
    )

    page.controls.clear()
    page.add(
        ft.Column(
            controls=[content],
            expand=True,
            spacing=0,
        )
    )
    page.navigation_bar = build_navbar(page, active_index=2)
    page.update()

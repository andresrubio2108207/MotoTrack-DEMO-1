"""Página de inicio de sesión."""

import flet as ft
from app.database.engine import SessionLocal
from app.services.auth_service import login_user
from app.state.session_state import session_state
from ui.shared.theme import (
    BACKGROUND, SURFACE_VARIANT, PRIMARY, ON_SURFACE, ON_SURFACE_MUTED,
    input_style, primary_button_style, secondary_button_style,
)
from ui.shared.snackbar import show_snackbar


def login_page(page: ft.Page):
    """Construye y muestra la página de login."""
    page.title = "MotoTrack PRO - Login"
    page.bgcolor = BACKGROUND
    page.padding = 0

    username_field = ft.TextField(
        label="Usuario",
        hint_text="Ingresa tu usuario",
        prefix_icon=ft.Icons.PERSON_ROUNDED,
        **input_style(),
    )
    password_field = ft.TextField(
        label="Contraseña",
        hint_text="Ingresa tu contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_ROUNDED,
        **input_style(),
    )
    loading = ft.ProgressRing(width=20, height=20, stroke_width=2, color=PRIMARY, visible=False)

    def do_login(e):
        # Limpiar errores
        username_field.error_text = None
        password_field.error_text = None

        username = username_field.value.strip()
        password = password_field.value.strip()

        # Validaciones locales
        if not username:
            username_field.error_text = "El usuario es requerido"
            page.update()
            return
        if not password:
            password_field.error_text = "La contraseña es requerida"
            page.update()
            return

        loading.visible = True
        page.update()

        try:
            db = SessionLocal()
            result = login_user(db, username, password)
            db.close()

            session_state.set_user(result["user"], result["access_token"])

            # Seleccionar primera motocicleta si existe
            if result["user"].motorcycles:
                session_state.set_motorcycle(result["user"].motorcycles[0])

            show_snackbar(page, f"¡Bienvenido, {result['user'].username}! 🏍️", "success")
            page.go("/maintenance")

        except ValueError as ex:
            show_snackbar(page, str(ex), "error")
        except Exception as ex:
            show_snackbar(page, f"Error inesperado: {ex}", "error")
        finally:
            loading.visible = False
            page.update()

    def go_register(e):
        page.go("/register")

    content = ft.Container(
        content=ft.Column(
            controls=[
                # Logo / Header
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.TWO_WHEELER_ROUNDED,
                                    color=PRIMARY,
                                    size=64,
                                ),
                                bgcolor=ft.Colors.with_opacity(0.1, PRIMARY),
                                border_radius=20,
                                padding=ft.padding.all(16),
                                alignment=ft.alignment.center,
                            ),
                            ft.Text(
                                "MotoTrack PRO",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=ON_SURFACE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Gestiona tu motocicleta con inteligencia",
                                size=13,
                                color=ON_SURFACE_MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    alignment=ft.alignment.center,
                ),

                ft.Divider(height=24, color="transparent"),

                # Formulario
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Iniciar Sesión", size=20, weight=ft.FontWeight.BOLD, color=ON_SURFACE),
                            ft.Text("Accede a tu cuenta", size=13, color=ON_SURFACE_MUTED),
                            ft.Divider(height=16, color="transparent"),
                            username_field,
                            ft.Divider(height=8, color="transparent"),
                            password_field,
                            ft.Divider(height=16, color="transparent"),
                            ft.Row(
                                controls=[
                                    loading,
                                    ft.ElevatedButton(
                                        text="Iniciar Sesión",
                                        icon=ft.Icons.LOGIN_ROUNDED,
                                        style=primary_button_style(),
                                        on_click=do_login,
                                        expand=True,
                                    ),
                                ],
                                spacing=12,
                            ),
                            ft.Divider(height=8, color="transparent"),
                            ft.TextButton(
                                content=ft.Text(
                                    "¿No tienes cuenta? Regístrate",
                                    color=ON_SURFACE_MUTED,
                                    size=13,
                                ),
                                on_click=go_register,
                            ),
                        ],
                        spacing=4,
                    ),
                    bgcolor=SURFACE_VARIANT,
                    border_radius=20,
                    padding=ft.padding.all(24),
                ),

                # Demo hint
                ft.Container(
                    content=ft.Text(
                        "Demo: usuario demo / contraseña demo1234",
                        size=11,
                        color=ON_SURFACE_MUTED,
                        text_align=ft.TextAlign.CENTER,
                        italic=True,
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(top=8),
                ),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=48),
        expand=True,
        alignment=ft.alignment.center,
        bgcolor=BACKGROUND,
    )

    page.controls.clear()
    page.add(content)
    page.update()

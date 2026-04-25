"""Página de registro de usuario y motocicleta."""

import flet as ft
from app.database.engine import SessionLocal
from app.services.auth_service import register_user
from app.models.motorcycle import Motorcycle
from app.state.session_state import session_state
from ui.shared.theme import (
    BACKGROUND, SURFACE_VARIANT, PRIMARY, ON_SURFACE, ON_SURFACE_MUTED,
    input_style, primary_button_style, secondary_button_style,
)
from ui.shared.snackbar import show_snackbar


def register_page(page: ft.Page):
    """Construye y muestra la página de registro."""
    page.title = "MotoTrack PRO - Registro"
    page.bgcolor = BACKGROUND
    page.padding = 0

    # Campos de usuario
    username_field = ft.TextField(label="Usuario", prefix_icon=ft.Icons.PERSON_ROUNDED, **input_style())
    email_field = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL_ROUNDED, keyboard_type=ft.KeyboardType.EMAIL, **input_style())
    password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK_ROUNDED, **input_style())
    confirm_password_field = ft.TextField(label="Confirmar contraseña", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK_OUTLINE, **input_style())

    # Campos de motocicleta
    brand_field = ft.TextField(label="Marca", prefix_icon=ft.Icons.TWO_WHEELER_ROUNDED, **input_style())
    model_field = ft.TextField(label="Modelo", prefix_icon=ft.Icons.DIRECTIONS_BIKE_ROUNDED, **input_style())
    year_field = ft.TextField(label="Año", prefix_icon=ft.Icons.CALENDAR_TODAY_ROUNDED, keyboard_type=ft.KeyboardType.NUMBER, **input_style())
    km_field = ft.TextField(label="Kilometraje actual", prefix_icon=ft.Icons.SPEED_ROUNDED, keyboard_type=ft.KeyboardType.NUMBER, value="0", **input_style())

    loading = ft.ProgressRing(width=20, height=20, stroke_width=2, color=PRIMARY, visible=False)

    def do_register(e):
        # Limpiar errores
        for field in [username_field, email_field, password_field, confirm_password_field, brand_field, model_field]:
            field.error_text = None

        username = username_field.value.strip()
        email = email_field.value.strip()
        password = password_field.value.strip()
        confirm = confirm_password_field.value.strip()
        brand = brand_field.value.strip()
        model = model_field.value.strip()
        year_str = year_field.value.strip()
        km_str = km_field.value.strip() or "0"

        # Validaciones
        errors = False
        if not username:
            username_field.error_text = "Requerido"
            errors = True
        if not email or "@" not in email:
            email_field.error_text = "Email inválido"
            errors = True
        if len(password) < 6:
            password_field.error_text = "Mínimo 6 caracteres"
            errors = True
        if password != confirm:
            confirm_password_field.error_text = "Las contraseñas no coinciden"
            errors = True
        if not brand:
            brand_field.error_text = "Requerido"
            errors = True
        if not model:
            model_field.error_text = "Requerido"
            errors = True

        if errors:
            page.update()
            return

        loading.visible = True
        page.update()

        try:
            db = SessionLocal()
            user = register_user(db, username, email, password)

            # Registrar motocicleta
            year = int(year_str) if year_str.isdigit() else None
            km = float(km_str) if km_str else 0.0
            moto = Motorcycle(
                user_id=user.id,
                brand=brand,
                model=model,
                year=year,
                current_km=km,
            )
            db.add(moto)
            db.commit()
            db.refresh(user)
            db.refresh(moto)
            db.close()

            session_state.set_user(user, "")
            session_state.set_motorcycle(moto)

            show_snackbar(page, "¡Cuenta creada con éxito! 🎉", "success")
            page.go("/maintenance")

        except ValueError as ex:
            show_snackbar(page, str(ex), "error")
        except Exception as ex:
            show_snackbar(page, f"Error inesperado: {ex}", "error")
        finally:
            loading.visible = False
            page.update()

    def go_login(e):
        page.go("/login")

    content = ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_ROUNDED,
                            icon_color=ON_SURFACE,
                            on_click=go_login,
                        ),
                        ft.Text("Crear Cuenta", size=22, weight=ft.FontWeight.BOLD, color=ON_SURFACE),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=8, color="transparent"),

                # Datos de usuario
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.PERSON_ADD_ROUNDED, color=PRIMARY, size=20),
                                    ft.Text("Datos de usuario", size=16, weight=ft.FontWeight.W_600, color=ON_SURFACE),
                                ],
                                spacing=8,
                            ),
                            ft.Divider(height=8, color="transparent"),
                            username_field,
                            email_field,
                            password_field,
                            confirm_password_field,
                        ],
                        spacing=10,
                    ),
                    bgcolor=SURFACE_VARIANT,
                    border_radius=16,
                    padding=ft.padding.all(20),
                ),

                ft.Divider(height=12, color="transparent"),

                # Datos de motocicleta
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.TWO_WHEELER_ROUNDED, color=PRIMARY, size=20),
                                    ft.Text("Tu motocicleta", size=16, weight=ft.FontWeight.W_600, color=ON_SURFACE),
                                ],
                                spacing=8,
                            ),
                            ft.Divider(height=8, color="transparent"),
                            ft.Row(controls=[brand_field, model_field], spacing=10, expand=True),
                            ft.Row(controls=[year_field, km_field], spacing=10, expand=True),
                        ],
                        spacing=10,
                    ),
                    bgcolor=SURFACE_VARIANT,
                    border_radius=16,
                    padding=ft.padding.all(20),
                ),

                ft.Divider(height=16, color="transparent"),
                ft.Row(
                    controls=[
                        loading,
                        ft.ElevatedButton(
                            text="Registrarme",
                            icon=ft.Icons.APP_REGISTRATION_ROUNDED,
                            style=primary_button_style(),
                            on_click=do_register,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                ),
                ft.TextButton(
                    content=ft.Text("¿Ya tienes cuenta? Inicia sesión", color=ON_SURFACE_MUTED, size=13),
                    on_click=go_login,
                ),
            ],
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=32),
        expand=True,
        bgcolor=BACKGROUND,
    )

    page.controls.clear()
    page.add(content)
    page.update()

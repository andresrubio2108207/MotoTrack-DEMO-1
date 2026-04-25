"""Página para agregar un nuevo mantenimiento."""

import flet as ft
from datetime import datetime
from app.database.engine import SessionLocal
from app.services.maintenance_service import create_maintenance, MAINTENANCE_INTERVALS
from app.state.session_state import session_state
from ui.shared.theme import (
    BACKGROUND, SURFACE_VARIANT, PRIMARY, ON_SURFACE, ON_SURFACE_MUTED,
    input_style, primary_button_style,
)
from ui.shared.snackbar import show_snackbar


def new_maintenance_page(page: ft.Page):
    """Construye y muestra el formulario para nuevo mantenimiento."""
    page.title = "MotoTrack PRO - Nuevo Mantenimiento"
    page.bgcolor = BACKGROUND
    page.padding = 0

    if not session_state.is_authenticated:
        page.go("/login")
        return

    moto = session_state.current_motorcycle
    if not moto:
        show_snackbar(page, "No hay motocicleta seleccionada", "error")
        page.go("/maintenance")
        return

    maintenance_types = list(MAINTENANCE_INTERVALS.keys())

    type_dropdown = ft.Dropdown(
        label="Tipo de mantenimiento",
        options=[ft.dropdown.Option(t) for t in maintenance_types],
        value=maintenance_types[0],
        filled=True,
        fill_color=SURFACE_VARIANT,
        border_color=PRIMARY,
        focused_border_color=PRIMARY,
        border_radius=12,
        text_style=ft.TextStyle(color=ON_SURFACE),
        label_style=ft.TextStyle(color=ON_SURFACE_MUTED),
        prefix_icon=ft.Icons.BUILD_ROUNDED,
    )

    km_field = ft.TextField(
        label="Kilómetros actuales",
        prefix_icon=ft.Icons.SPEED_ROUNDED,
        keyboard_type=ft.KeyboardType.NUMBER,
        value=str(int(moto.current_km)),
        **input_style(),
    )

    date_field = ft.TextField(
        label="Fecha (DD/MM/AAAA)",
        prefix_icon=ft.Icons.CALENDAR_TODAY_ROUNDED,
        value=datetime.now().strftime("%d/%m/%Y"),
        **input_style(),
    )

    description_field = ft.TextField(
        label="Descripción / Notas",
        prefix_icon=ft.Icons.NOTES_ROUNDED,
        multiline=True,
        min_lines=2,
        max_lines=4,
        **input_style(),
    )

    loading = ft.ProgressRing(width=20, height=20, stroke_width=2, color=PRIMARY, visible=False)

    def do_save(e):
        km_field.error_text = None
        date_field.error_text = None

        km_str = km_field.value.strip()
        date_str = date_field.value.strip()

        errors = False
        try:
            km = float(km_str)
        except ValueError:
            km_field.error_text = "Kilómetros inválidos"
            errors = True
            km = 0.0

        try:
            date = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            date_field.error_text = "Formato inválido (DD/MM/AAAA)"
            errors = True
            date = datetime.utcnow()

        if errors:
            page.update()
            return

        loading.visible = True
        page.update()

        try:
            db = SessionLocal()
            create_maintenance(
                db=db,
                motorcycle_id=moto.id,
                maintenance_type=type_dropdown.value,
                km=km,
                description=description_field.value.strip(),
                date=date,
            )
            # Actualizar km en la sesión
            moto.current_km = max(moto.current_km, km)
            db.close()

            show_snackbar(page, "Mantenimiento registrado exitosamente ✅", "success")
            page.go("/maintenance")
        except Exception as ex:
            show_snackbar(page, f"Error al guardar: {ex}", "error")
        finally:
            loading.visible = False
            page.update()

    content = ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_ROUNDED,
                            icon_color=ON_SURFACE,
                            on_click=lambda e: page.go("/maintenance"),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Nuevo Mantenimiento", size=20, weight=ft.FontWeight.BOLD, color=ON_SURFACE),
                                ft.Text(f"{moto.brand} {moto.model}", size=12, color=ON_SURFACE_MUTED),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=8,
                ),

                ft.Divider(height=12, color="transparent"),

                # Formulario
                ft.Container(
                    content=ft.Column(
                        controls=[
                            type_dropdown,
                            ft.Divider(height=8, color="transparent"),
                            ft.Row(controls=[km_field, date_field], spacing=10, expand=True),
                            ft.Divider(height=8, color="transparent"),
                            description_field,
                        ],
                        spacing=4,
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
                            text="Guardar Mantenimiento",
                            icon=ft.Icons.SAVE_ROUNDED,
                            style=primary_button_style(),
                            on_click=do_save,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                ),
            ],
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=24),
        expand=True,
        bgcolor=BACKGROUND,
    )

    page.controls.clear()
    page.navigation_bar = None
    page.add(content)
    page.update()

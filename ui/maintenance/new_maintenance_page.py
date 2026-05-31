from __future__ import annotations

import flet as ft

from ui.shared.theme import BORDER_COLOR, SURFACE_COLOR, TEXT_COLOR, accent_button, section_title, translucent


def build_new_maintenance_form(
    type_field: ft.TextField,
    km_field: ft.TextField,
    cost_field: ft.TextField,
    date_field: ft.TextField,
    next_km_field: ft.TextField,
    description_field: ft.TextField,
    on_submit,
    on_pick_date=None,
    compact: bool = False,
) -> ft.Container:
    date_controls: list[ft.Control] = [ft.Container(content=date_field, expand=1)]
    if on_pick_date is not None:
        date_controls.append(
            ft.IconButton(
                icon=ft.icons.Icons.CALENDAR_MONTH_ROUNDED,
                icon_color="#1B5162",
                tooltip="Elegir fecha",
                on_click=on_pick_date,
            )
        )

    service_fields: ft.Control = (
        ft.Column([type_field, km_field], spacing=10)
        if compact
        else ft.Row(
            [
                ft.Container(content=type_field, expand=2),
                ft.Container(content=km_field, expand=1),
            ],
            spacing=10,
        )
    )
    money_date_fields: ft.Control = (
        ft.Column([cost_field, ft.Row(date_controls, spacing=6)], spacing=10)
        if compact
        else ft.Row(
            [
                ft.Container(content=cost_field, expand=1),
                ft.Container(content=ft.Row(date_controls, spacing=6), expand=1),
            ],
            spacing=10,
        )
    )

    return ft.Container(
        margin=ft.margin.Margin.symmetric(horizontal=16),
        padding=16,
        bgcolor=SURFACE_COLOR,
        border_radius=20,
        border=ft.border.all(1, BORDER_COLOR),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=12, color=translucent(TEXT_COLOR, "12"), offset=ft.Offset(0, 6)),
        content=ft.Column(
            [
                section_title(
                    "Registrar mantenimiento",
                    "Guarda el servicio y programa la próxima intervención.",
                    ft.icons.Icons.BUILD_CIRCLE_OUTLINED,
                ),
                service_fields,
                money_date_fields,
                next_km_field,
                description_field,
                accent_button("Guardar mantenimiento", on_click=on_submit),
            ],
            spacing=12,
        ),
    )

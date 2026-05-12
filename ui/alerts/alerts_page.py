from __future__ import annotations

import flet as ft

from ui.shared.theme import (
    ACCENT_SOFT,
    BORDER_COLOR,
    DANGER_COLOR,
    MUTED_TEXT,
    SUCCESS_COLOR,
    SURFACE_COLOR,
    TEXT_COLOR,
    WARNING_COLOR,
    app_button_style,
    empty_state,
    section_title,
    status_badge,
    translucent,
)


def build_alert_form(
    title_field: ft.TextField,
    trigger_type_field: ft.Dropdown,
    trigger_km_field: ft.TextField,
    trigger_date_field: ft.TextField,
    on_submit,
) -> ft.Container:
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
                    "Nueva alerta",
                    "Recordatorios por kilometraje o fecha.",
                    ft.icons.Icons.ADD_ALERT_ROUNDED,
                ),
                title_field,
                trigger_type_field,
                trigger_km_field,
                trigger_date_field,
                ft.ElevatedButton("Guardar alerta", on_click=on_submit, style=app_button_style()),
            ],
            spacing=12,
        ),
    )


def _alert_icon_and_color(status: str) -> tuple[str, str, str]:
    if status == "Disparada":
        return ft.icons.Icons.NOTIFICATION_IMPORTANT_ROUNDED, "#FCE3E2", DANGER_COLOR
    if status == "Proxima":
        return ft.icons.Icons.SCHEDULE_ROUNDED, "#F9E7CB", WARNING_COLOR
    return ft.icons.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, "#DCF3EC", SUCCESS_COLOR


def build_alert_list(alerts: list[dict[str, str]]) -> ft.Column:
    header = ft.Container(
        padding=ft.padding.Padding.only(left=16, right=16, top=4, bottom=0),
        content=section_title(
            "Alertas del vehiculo",
            "Estado actual de cada recordatorio.",
            ft.icons.Icons.NOTIFICATIONS_ACTIVE_ROUNDED,
        ),
    )

    if not alerts:
        return ft.Column(
            [
                header,
                ft.Container(
                    margin=ft.margin.Margin.symmetric(horizontal=16),
                    content=empty_state("Sin alertas", "Cuando registres una alerta aparecera aqui."),
                ),
            ],
            spacing=12,
        )

    items: list[ft.Control] = [header]
    for alert in alerts:
        icon_name, icon_bg, icon_color = _alert_icon_and_color(alert["status"])
        fired = alert["status"] == "Disparada"
        items.append(
            ft.Container(
                margin=ft.margin.Margin.symmetric(horizontal=16),
                padding=ft.padding.Padding.symmetric(horizontal=14, vertical=13),
                bgcolor=SURFACE_COLOR,
                border_radius=18,
                border=ft.border.all(1.4 if fired else 1, icon_color if fired else BORDER_COLOR),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=translucent(TEXT_COLOR, "0D"), offset=ft.Offset(0, 5)),
                content=ft.Row(
                    [
                        ft.Container(
                            width=42,
                            height=42,
                            border_radius=15,
                            bgcolor=icon_bg,
                            alignment=ft.alignment.Alignment.CENTER,
                            content=ft.Icon(icon_name, color=icon_color, size=21),
                        ),
                        ft.Column(
                            [
                                ft.Text(alert["title"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                ft.Text(alert["meta"], size=11, color=MUTED_TEXT),
                            ],
                            spacing=3,
                            tight=True,
                            expand=True,
                        ),
                        status_badge(alert["status"], color=icon_color, bg=icon_bg),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        )

    return ft.Column(items, spacing=10)

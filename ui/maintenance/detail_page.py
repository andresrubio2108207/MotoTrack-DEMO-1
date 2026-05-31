from __future__ import annotations

import flet as ft

from ui.shared.theme import (
    BORDER_COLOR,
    DANGER_COLOR,
    MUTED_TEXT,
    PRIMARY_COLOR,
    PRIMARY_LIGHT,
    SUCCESS_COLOR,
    SURFACE_COLOR,
    TEXT_COLOR,
    WARNING_COLOR,
    accent_button,
    outline_button,
    pill,
    section_title,
    translucent,
)


def build_motorcycle_hero(
    *,
    title: str,
    subtitle: str,
    stats: list[tuple[str, str]],
) -> ft.Container:
    return ft.Container(
        margin=ft.margin.Margin.symmetric(horizontal=16),
        padding=18,
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
                            width=50,
                            height=50,
                            border_radius=17,
                            bgcolor=translucent("#FFFFFF", "24"),
                            alignment=ft.alignment.Alignment.CENTER,
                            content=ft.Icon(ft.icons.Icons.TWO_WHEELER_ROUNDED, color="#FFFFFF", size=28),
                        ),
                        ft.Column(
                            [
                                ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                ft.Text(subtitle, size=12, color="#D8EEF3"),
                            ],
                            spacing=3,
                            tight=True,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row([pill(label, value, tone="#FFFFFF") for label, value in stats], wrap=True, spacing=8, run_spacing=8),
            ],
            spacing=16,
        ),
    )


def build_km_update_card(km_field: ft.TextField, on_update_km, on_release_alerts=None) -> ft.Container:
    km_field.text_align = ft.TextAlign.CENTER
    km_field.text_size = 28
    km_field.keyboard_type = ft.KeyboardType.NUMBER
    km_field.suffix_text = "km"

    return ft.Container(
        margin=ft.margin.Margin.symmetric(horizontal=16),
        padding=18,
        bgcolor=SURFACE_COLOR,
        border_radius=20,
        border=ft.border.all(1, BORDER_COLOR),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=translucent(TEXT_COLOR, "0D"), offset=ft.Offset(0, 5)),
        content=ft.Column(
            [
                section_title(
                    "Kilometraje actual",
                    "Actualiza el odómetro para recalcular alertas.",
                    ft.icons.Icons.TWO_WHEELER_ROUNDED,
                ),
                km_field,
                accent_button("Actualizar kilometraje", on_click=on_update_km),
                outline_button("Tomar este km como punto de partida", on_click=on_release_alerts),
            ],
            spacing=12,
        ),
    )


_URGENCY_STYLES: dict[str, tuple[str, str, str]] = {
    "urgente": (DANGER_COLOR, "#FCE3E2", ft.icons.Icons.PRIORITY_HIGH),
    "advertencia": (WARNING_COLOR, "#F9E7CB", ft.icons.Icons.WARNING_AMBER_ROUNDED),
    "ok": (SUCCESS_COLOR, "#DCF3EC", ft.icons.Icons.CHECK_ROUNDED),
}


def _suggestion_card(text: str) -> ft.Container:
    lower = text.lower()
    if text.startswith("[urgente]"):
        key = "urgente"
        body = text[9:].strip()
    elif text.startswith("[advertencia]"):
        key = "advertencia"
        body = text[13:].strip()
    else:
        key = "ok"
        body = text.replace("[ok]", "").strip()

    if "vencid" in lower or "urgente" in lower or "superad" in lower:
        key = "urgente"
    elif "proxim" in lower or "revisar" in lower or "pronto" in lower:
        key = "advertencia"

    color, bg, icon_name = _URGENCY_STYLES[key]
    return ft.Container(
        margin=ft.margin.Margin.symmetric(horizontal=16),
        bgcolor=SURFACE_COLOR,
        border_radius=18,
        border=ft.border.all(1, BORDER_COLOR),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=translucent(TEXT_COLOR, "0D"), offset=ft.Offset(0, 5)),
        content=ft.Row(
            [
                ft.Container(
                    width=5,
                    bgcolor=color,
                    border_radius=ft.border_radius.BorderRadius.only(top_left=18, bottom_left=18),
                ),
                ft.Container(
                    width=38,
                    height=38,
                    border_radius=14,
                    bgcolor=bg,
                    alignment=ft.alignment.Alignment.CENTER,
                    content=ft.Icon(icon_name, color=color, size=18),
                ),
                ft.Text(body, size=13, color=TEXT_COLOR, expand=True),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.Padding.only(top=12, right=14, bottom=12),
    )


def build_suggestions_panel(items: list[str]) -> ft.Column:
    header = ft.Container(
        padding=ft.padding.Padding.only(left=16, right=16, top=4, bottom=0),
        content=section_title(
            "Sugerencias",
            "Próximas acciones recomendadas.",
            ft.icons.Icons.TIPS_AND_UPDATES_ROUNDED,
        ),
    )

    if not items:
        no_items = ft.Container(
            margin=ft.margin.Margin.symmetric(horizontal=16),
            padding=14,
            bgcolor=PRIMARY_LIGHT,
            border_radius=18,
            content=ft.Row(
                [
                    ft.Icon(ft.icons.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color=SUCCESS_COLOR, size=20),
                    ft.Text("Todo al dia. No hay vencimientos cercanos.", size=13, color=TEXT_COLOR, expand=True),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        return ft.Column([header, no_items], spacing=10)

    return ft.Column([header, *[_suggestion_card(item) for item in items]], spacing=10)

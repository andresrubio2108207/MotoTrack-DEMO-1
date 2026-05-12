from __future__ import annotations

import flet as ft

from ui.shared.theme import ACCENT_COLOR, ACCENT_SOFT, BORDER_COLOR, MUTED_TEXT, SURFACE_COLOR, TEXT_COLOR, empty_state, section_title, translucent


_TYPE_ICONS: dict[str, str] = {
    "aceite": ft.icons.Icons.OPACITY_ROUNDED,
    "frenos": ft.icons.Icons.DISC_FULL_ROUNDED,
    "cadena": ft.icons.Icons.SETTINGS_INPUT_COMPONENT_ROUNDED,
    "llanta": ft.icons.Icons.TIRE_REPAIR_ROUNDED,
    "bujia": ft.icons.Icons.BOLT_ROUNDED,
    "filtro": ft.icons.Icons.FILTER_ALT_ROUNDED,
    "revision": ft.icons.Icons.BUILD_CIRCLE_OUTLINED,
}


def _icon_for_title(title: str) -> str:
    low = title.lower()
    for key, icon in _TYPE_ICONS.items():
        if key in low:
            return icon
    return ft.icons.Icons.BUILD_OUTLINED


def build_history_list(items: list[dict[str, str]]) -> ft.Column:
    header = ft.Container(
        padding=ft.padding.Padding.only(left=16, right=16, top=4, bottom=0),
        content=section_title(
            "Historial",
            "Servicios registrados, kilometraje y notas.",
            ft.icons.Icons.HISTORY_ROUNDED,
        ),
    )

    if not items:
        return ft.Column(
            [
                header,
                ft.Container(
                    margin=ft.margin.Margin.symmetric(horizontal=16),
                    content=empty_state("Aun no hay mantenimientos", "Cuando registres un servicio aparecera aqui."),
                ),
            ],
            spacing=12,
        )

    cards: list[ft.Control] = [header]
    for item in items:
        icon_name = _icon_for_title(item["title"])
        cards.append(
            ft.Container(
                margin=ft.margin.Margin.symmetric(horizontal=16),
                padding=ft.padding.Padding.symmetric(horizontal=14, vertical=13),
                bgcolor=SURFACE_COLOR,
                border_radius=18,
                border=ft.border.all(1, BORDER_COLOR),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=translucent(TEXT_COLOR, "0D"), offset=ft.Offset(0, 5)),
                content=ft.Row(
                    [
                        ft.Container(
                            width=42,
                            height=42,
                            border_radius=15,
                            bgcolor=ACCENT_SOFT,
                            alignment=ft.alignment.Alignment.CENTER,
                            content=ft.Icon(icon_name, color=ACCENT_COLOR, size=20),
                        ),
                        ft.Column(
                            [
                                ft.Text(item["title"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                ft.Text(item["meta"], size=11, color=MUTED_TEXT),
                                ft.Text(item["description"], size=12, color=TEXT_COLOR),
                            ],
                            spacing=3,
                            tight=True,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            )
        )

    return ft.Column(cards, spacing=10)

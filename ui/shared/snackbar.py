from __future__ import annotations

import flet as ft

from ui.shared.theme import ACCENT_COLOR, DANGER_COLOR, PRIMARY_COLOR, SUCCESS_COLOR, SURFACE_COLOR


def show_message(page: ft.Page, message: str, *, tone: str = "info") -> None:
    colors = {
        "info": PRIMARY_COLOR,
        "success": SUCCESS_COLOR,
        "warning": ACCENT_COLOR,
        "error": DANGER_COLOR,
    }
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color=SURFACE_COLOR, size=14),
        bgcolor=colors.get(tone, PRIMARY_COLOR),
        duration=2800,
        open=True,
    )
    page.update()

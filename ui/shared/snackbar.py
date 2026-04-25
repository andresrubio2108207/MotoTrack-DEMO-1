"""SnackBar utilitario para mensajes de éxito y error."""

import flet as ft
from ui.shared.theme import SUCCESS, ERROR, WARNING


def show_snackbar(
    page: ft.Page,
    message: str,
    kind: str = "info",
    duration: int = 3000,
):
    """
    Muestra un SnackBar con estilo según el tipo de mensaje.

    Args:
        page: La página Flet actual.
        message: Texto a mostrar.
        kind: "success", "error", "warning" o "info".
        duration: Duración en milisegundos.
    """
    color_map = {
        "success": SUCCESS,
        "error": ERROR,
        "warning": WARNING,
        "info": "#1E88E5",
    }
    icon_map = {
        "success": ft.Icons.CHECK_CIRCLE_ROUNDED,
        "error": ft.Icons.ERROR_ROUNDED,
        "warning": ft.Icons.WARNING_ROUNDED,
        "info": ft.Icons.INFO_ROUNDED,
    }

    bgcolor = color_map.get(kind, color_map["info"])
    icon = icon_map.get(kind, icon_map["info"])

    snack = ft.SnackBar(
        content=ft.Row(
            controls=[
                ft.Icon(icon, color=ft.Colors.WHITE, size=20),
                ft.Text(message, color=ft.Colors.WHITE, size=14, expand=True),
            ],
            spacing=12,
        ),
        bgcolor=bgcolor,
        duration=duration,
        behavior=ft.SnackBarBehavior.FLOATING,
        shape=ft.RoundedRectangleBorder(radius=12),
        margin=ft.margin.only(bottom=80, left=16, right=16),
    )
    page.open(snack)
    page.update()

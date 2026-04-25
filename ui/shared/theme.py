"""Tema oscuro moderno para MotoTrack PRO."""

import flet as ft

# ─── Paleta de colores ────────────────────────────────────────────────────────
PRIMARY = "#FF6B35"          # Naranja vibrante
PRIMARY_DARK = "#E55A25"     # Naranja oscuro (hover)
SECONDARY = "#1E88E5"        # Azul eléctrico
BACKGROUND = "#0D0D0D"       # Negro profundo
SURFACE = "#1A1A1A"          # Gris muy oscuro
SURFACE_VARIANT = "#242424"  # Gris oscuro (cards)
ON_SURFACE = "#E0E0E0"       # Texto claro
ON_SURFACE_MUTED = "#9E9E9E" # Texto secundario
SUCCESS = "#4CAF50"          # Verde éxito
WARNING = "#FFC107"          # Amarillo advertencia
ERROR = "#F44336"            # Rojo error
BORDER = "#2A2A2A"           # Bordes sutiles
SHADOW = "#000000"           # Sombras


def get_theme() -> ft.Theme:
    """Retorna el tema oscuro configurado para MotoTrack PRO."""
    return ft.Theme(
        color_scheme_seed=PRIMARY,
        color_scheme=ft.ColorScheme(
            primary=PRIMARY,
            primary_container=PRIMARY_DARK,
            secondary=SECONDARY,
            background=BACKGROUND,
            surface=SURFACE,
            on_primary=ft.Colors.WHITE,
            on_secondary=ft.Colors.WHITE,
            on_background=ON_SURFACE,
            on_surface=ON_SURFACE,
            error=ERROR,
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )


def card_style() -> dict:
    """Estilo base para tarjetas (cards)."""
    return {
        "bgcolor": SURFACE_VARIANT,
        "border_radius": 16,
        "padding": ft.padding.all(16),
    }


def input_style() -> dict:
    """Estilo base para campos de texto."""
    return {
        "border_color": BORDER,
        "focused_border_color": PRIMARY,
        "fill_color": SURFACE,
        "filled": True,
        "border_radius": 12,
        "text_style": ft.TextStyle(color=ON_SURFACE),
        "label_style": ft.TextStyle(color=ON_SURFACE_MUTED),
        "cursor_color": PRIMARY,
    }


def primary_button_style() -> ft.ButtonStyle:
    """Estilo para botones primarios."""
    return ft.ButtonStyle(
        bgcolor=PRIMARY,
        color=ft.Colors.WHITE,
        shape=ft.RoundedRectangleBorder(radius=12),
        elevation=4,
        overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        animation_duration=200,
    )


def secondary_button_style() -> ft.ButtonStyle:
    """Estilo para botones secundarios."""
    return ft.ButtonStyle(
        bgcolor=SURFACE_VARIANT,
        color=ON_SURFACE,
        shape=ft.RoundedRectangleBorder(radius=12),
        side=ft.BorderSide(1, BORDER),
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        animation_duration=200,
    )


def danger_button_style() -> ft.ButtonStyle:
    """Estilo para botones de peligro/eliminar."""
    return ft.ButtonStyle(
        bgcolor=ERROR,
        color=ft.Colors.WHITE,
        shape=ft.RoundedRectangleBorder(radius=12),
        elevation=2,
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        animation_duration=200,
    )

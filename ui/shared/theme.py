from __future__ import annotations

import flet as ft

if not hasattr(ft.icons, "Icons"):
    class _IconsCompat:
        def __getattr__(self, name: str) -> str:
            return getattr(ft.icons, name)

    ft.icons.Icons = _IconsCompat()  # type: ignore[attr-defined]

if not hasattr(ft.border, "all") and hasattr(ft.border, "Border"):
    ft.border.all = ft.border.Border.all  # type: ignore[attr-defined]


PRIMARY_COLOR = "#1B5162"
PRIMARY_DEEP = "#123A46"
PRIMARY_LIGHT = "#D9EBEF"
ACCENT_COLOR = "#D4723A"
ACCENT_DEEP = "#B05A26"
ACCENT_SOFT = "#F6DED0"
BG_COLOR = "#F2EDE4"
SURFACE_COLOR = "#FDFAF4"
SURFACE_ALT = "#EFE5D7"
TEXT_COLOR = "#17303A"
MUTED_TEXT = "#5C6E73"
BORDER_COLOR = "#D8C8B0"
SUCCESS_COLOR = "#1D9E75"
DANGER_COLOR = "#E24B4A"
WARNING_COLOR = "#BA7517"
INFO_COLOR = PRIMARY_COLOR
PRIMARY_SOFT = PRIMARY_LIGHT


def translucent(color: str, alpha: str = "18") -> str:
    return f"#{alpha}{color.lstrip('#')}"


def configure_page(page: ft.Page) -> None:
    page.title = "MotoTrack"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.scroll = ft.ScrollMode.HIDDEN
    page.bgcolor = BG_COLOR
    page.fonts = {}
    try:
        color_scheme = ft.ColorScheme(
            primary=PRIMARY_COLOR,
            secondary=ACCENT_COLOR,
            background=BG_COLOR,
            surface=SURFACE_COLOR,
        )
    except TypeError:
        color_scheme = ft.ColorScheme(primary=PRIMARY_COLOR, secondary=ACCENT_COLOR)
    page.theme = ft.Theme(color_scheme=color_scheme)


def _gradient(start: str, end: str) -> ft.LinearGradient:
    return ft.LinearGradient(
        begin=ft.alignment.Alignment.TOP_LEFT,
        end=ft.alignment.Alignment.BOTTOM_RIGHT,
        colors=[start, end],
    )


def mobile_field(
    label: str,
    hint: str = "",
    *,
    password: bool = False,
    keyboard: ft.KeyboardType = ft.KeyboardType.TEXT,
) -> ft.TextField:
    return ft.TextField(
        label=label,
        hint_text=hint,
        password=password,
        can_reveal_password=password,
        keyboard_type=keyboard,
        filled=True,
        bgcolor=SURFACE_COLOR,
        border_radius=16,
        border_color=BORDER_COLOR,
        focused_border_color=PRIMARY_COLOR,
        cursor_color=PRIMARY_COLOR,
        label_style=ft.TextStyle(color=MUTED_TEXT, size=12),
        text_style=ft.TextStyle(color=TEXT_COLOR, size=14),
        content_padding=ft.padding.Padding.symmetric(horizontal=14, vertical=13),
    )


def app_button_style(color: str = PRIMARY_COLOR) -> ft.ButtonStyle:
    return ft.ButtonStyle(
        bgcolor=color,
        color="#FFFFFF",
        padding=ft.padding.Padding.symmetric(vertical=15, horizontal=16),
        shape=ft.RoundedRectangleBorder(radius=16),
        text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_700),
    )


def secondary_button_style(color: str = ACCENT_COLOR) -> ft.ButtonStyle:
    return app_button_style(color)


def primary_button(text: str, on_click=None, *, bgcolor: str = PRIMARY_COLOR) -> ft.ElevatedButton:
    return ft.ElevatedButton(text, on_click=on_click, style=app_button_style(bgcolor), width=float("inf"))


def accent_button(text: str, on_click=None) -> ft.ElevatedButton:
    return primary_button(text, on_click=on_click, bgcolor=ACCENT_COLOR)


def outline_button(text: str, on_click=None) -> ft.OutlinedButton:
    return ft.OutlinedButton(
        text,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=PRIMARY_COLOR,
            side=ft.BorderSide(1, BORDER_COLOR),
            padding=ft.padding.Padding.symmetric(vertical=14, horizontal=16),
            shape=ft.RoundedRectangleBorder(radius=16),
            text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_700),
        ),
        width=float("inf"),
    )


def section_card(
    content: ft.Control,
    *,
    padding: int = 16,
    expand: bool | None = None,
) -> ft.Container:
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=SURFACE_COLOR,
        border_radius=20,
        border=ft.border.all(1, BORDER_COLOR),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=12, color=translucent(TEXT_COLOR, "14"), offset=ft.Offset(0, 6)),
        expand=expand,
    )


def pill(label: str, value: str, *, tone: str = PRIMARY_LIGHT) -> ft.Container:
    return ft.Container(
        bgcolor=tone,
        border_radius=14,
        padding=ft.padding.Padding.symmetric(horizontal=10, vertical=8),
        content=ft.Column(
            [
                ft.Text(label.upper(), size=9, color=MUTED_TEXT, weight=ft.FontWeight.W_700),
                ft.Text(value, size=13, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            ],
            spacing=1,
            tight=True,
        ),
    )


def status_badge(text: str, *, color: str = SUCCESS_COLOR, bg: str = "") -> ft.Container:
    return ft.Container(
        bgcolor=bg or translucent(color),
        border_radius=999,
        padding=ft.padding.Padding.symmetric(horizontal=10, vertical=6),
        content=ft.Text(text, size=11, color=color, weight=ft.FontWeight.W_700),
    )


def empty_state(title: str, body: str) -> ft.Container:
    return section_card(
        ft.Column(
            [
                ft.Container(
                    width=52,
                    height=52,
                    border_radius=18,
                    bgcolor=PRIMARY_LIGHT,
                    alignment=ft.alignment.Alignment.CENTER,
                    content=ft.Icon(ft.icons.Icons.INBOX_OUTLINED, color=PRIMARY_COLOR, size=28),
                ),
                ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=TEXT_COLOR, text_align=ft.TextAlign.CENTER),
                ft.Text(body, size=12, color=MUTED_TEXT, text_align=ft.TextAlign.CENTER),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
    )


def page_header(title: str, subtitle: str = "") -> ft.Container:
    controls: list[ft.Control] = [ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)]
    if subtitle:
        controls.append(ft.Text(subtitle, size=12, color=MUTED_TEXT))
    return ft.Container(
        padding=ft.padding.Padding.only(left=16, right=16, top=16, bottom=8),
        content=ft.Column(controls, spacing=4, tight=True),
    )


def section_title(title: str, subtitle: str = "", icon: str | None = None) -> ft.Row:
    leading: list[ft.Control] = []
    if icon:
        leading.append(
            ft.Container(
                width=34,
                height=34,
                border_radius=13,
                bgcolor=PRIMARY_LIGHT,
                alignment=ft.alignment.Alignment.CENTER,
                content=ft.Icon(icon, color=PRIMARY_COLOR, size=18),
            )
        )

    return ft.Row(
        [
            *leading,
            ft.Column(
                [
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                    ft.Text(subtitle, size=11, color=MUTED_TEXT) if subtitle else ft.Container(height=0),
                ],
                spacing=2,
                tight=True,
                expand=True,
            ),
        ],
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def metric_tile(label: str, value: str, icon: str, *, color: str = PRIMARY_COLOR) -> ft.Container:
    return section_card(
        ft.Row(
            [
                ft.Container(
                    width=40,
                    height=40,
                    border_radius=15,
                    bgcolor=translucent(color),
                    alignment=ft.alignment.Alignment.CENTER,
                    content=ft.Icon(icon, color=color, size=20),
                ),
                ft.Column(
                    [
                        ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                        ft.Text(label, size=11, color=MUTED_TEXT),
                    ],
                    spacing=1,
                    tight=True,
                    expand=True,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=12,
        expand=True,
    )


def divider() -> ft.Divider:
    return ft.Divider(height=1, color=BORDER_COLOR, thickness=0.8)

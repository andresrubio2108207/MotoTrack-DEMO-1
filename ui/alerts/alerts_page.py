from __future__ import annotations

import flet as ft

from ui.shared.theme import (
    BORDER_COLOR,
    DANGER_COLOR,
    MUTED_TEXT,
    PRIMARY_COLOR,
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


def _icon(icon_name: str) -> str:
    return getattr(ft.icons.Icons, icon_name, ft.icons.Icons.NOTIFICATIONS_ROUNDED)


def build_alert_form(
    title_field: ft.TextField,
    trigger_type_field: ft.Dropdown,
    trigger_km_field: ft.TextField,
    trigger_date_field: ft.TextField,
    on_submit,
    on_pick_date=None,
) -> ft.Container:
    date_row_controls: list[ft.Control] = [ft.Container(content=trigger_date_field, expand=True)]
    if on_pick_date is not None:
        date_row_controls.append(
            ft.IconButton(
                icon=ft.icons.Icons.CALENDAR_MONTH_ROUNDED,
                icon_color=PRIMARY_COLOR,
                tooltip="Elegir fecha",
                on_click=on_pick_date,
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
                    "Alerta personalizada",
                    "Crea recordatorios fuera del plan base.",
                    ft.icons.Icons.ADD_ALERT_ROUNDED,
                ),
                title_field,
                trigger_type_field,
                trigger_km_field,
                ft.Row(date_row_controls, spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.ElevatedButton("Guardar alerta", on_click=on_submit, style=app_button_style()),
            ],
            spacing=12,
        ),
    )


def build_alert_summary(counts: dict[str, int]) -> ft.Container:
    cards = [
        ("Vencidos", counts.get("VENCIDO", 0), DANGER_COLOR, ft.icons.Icons.PRIORITY_HIGH_ROUNDED),
        ("Próximos", counts.get("PRÓXIMO", 0), WARNING_COLOR, ft.icons.Icons.SCHEDULE_ROUNDED),
        ("Al día", counts.get("AL DÍA", 0), SUCCESS_COLOR, ft.icons.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED),
    ]
    return ft.Container(
        height=112,
        content=ft.Row(
            [
                ft.Container(
                    width=120,
                    padding=14,
                    bgcolor=SURFACE_COLOR,
                    border_radius=18,
                    border=ft.border.all(1, BORDER_COLOR),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(icon, color=color, size=21),
                                    ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Text(label, size=12, color=MUTED_TEXT, weight=ft.FontWeight.W_600),
                        ],
                        spacing=8,
                        tight=True,
                    ),
                )
                for label, value, color, icon in cards
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        ),
        padding=ft.padding.Padding.only(left=16, right=16),
    )


def _alert_style(status: str, color: str | None = None) -> tuple[str, str, str]:
    normalized = status.upper()
    if normalized in {"VENCIDO", "DISPARADA"}:
        return ft.icons.Icons.NOTIFICATION_IMPORTANT_ROUNDED, "#FCE3E2", DANGER_COLOR
    if normalized in {"PRÓXIMO", "PROXIMO", "PROXIMA"}:
        return ft.icons.Icons.SCHEDULE_ROUNDED, "#F9E7CB", WARNING_COLOR
    if normalized in {"AL DÍA", "AL DIA", "PENDIENTE"}:
        return ft.icons.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, "#DCF3EC", color or SUCCESS_COLOR
    return ft.icons.Icons.NOTIFICATIONS_ROUNDED, "#DDEDF1", color or PRIMARY_COLOR


def _distance_text(alert: dict) -> str:
    if "km_restantes" not in alert:
        return alert.get("meta", "")

    remaining = int(alert["km_restantes"])
    if remaining < 0:
        return f"Vencido hace {abs(remaining):,} km".replace(",", ".")
    if remaining == 0:
        return "Vence ahora"
    return f"Faltan {remaining:,} km".replace(",", ".")


def _smart_alert_card(
    alert: dict,
    *,
    compact: bool = False,
    on_detail=None,
    on_edit=None,
    on_delete=None,
) -> ft.Container:
    status = str(alert.get("estado", alert.get("status", "Pendiente")))
    icon_name, icon_bg, icon_color = _alert_style(status, str(alert.get("color", "")) or None)
    display_icon = _icon(str(alert.get("icon", ""))) if alert.get("icon") else icon_name

    title = str(alert.get("tipo", alert.get("title", "Alerta")))
    meta = (
        f"Ultimo: {int(alert.get('km_ultimo', 0)):,} km · Intervalo: cada {int(alert.get('intervalo', 0)):,} km"
        if "intervalo" in alert
        else str(alert.get("meta", ""))
    ).replace(",", ".")

    leading = ft.Container(
        width=44,
        height=44,
        border_radius=15,
        bgcolor=icon_bg,
        alignment=ft.alignment.Alignment.CENTER,
        content=ft.Icon(display_icon, color=icon_color, size=22),
    )
    text_block = ft.Column(
        [
            ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR, max_lines=2),
            ft.Text(meta, size=11, color=MUTED_TEXT, max_lines=2),
            ft.Text(_distance_text(alert), size=12, color=icon_color, weight=ft.FontWeight.W_600, max_lines=2),
        ],
        spacing=3,
        tight=True,
        expand=True,
    )
    badge = status_badge(status, color=icon_color, bg=icon_bg)
    actions = [
        ft.IconButton(
            icon=ft.icons.Icons.INFO_OUTLINE_ROUNDED,
            icon_color=PRIMARY_COLOR,
            tooltip="Detalle",
            on_click=lambda e, item=alert: on_detail(e, item),
        )
    ] if on_detail else []
    if alert.get("id") and on_edit:
        actions.append(
            ft.IconButton(
                icon=ft.icons.Icons.EDIT_ROUNDED,
                icon_color=PRIMARY_COLOR,
                tooltip="Editar alerta",
                on_click=lambda e, item=alert: on_edit(e, item),
            )
        )
    if alert.get("id") and on_delete:
        actions.append(
            ft.IconButton(
                icon=ft.icons.Icons.DELETE_OUTLINE_ROUNDED,
                icon_color=DANGER_COLOR,
                tooltip="Eliminar alerta",
                on_click=lambda e, item=alert: on_delete(e, item),
            )
        )
    actions_row = ft.Row(actions, spacing=0, tight=True) if actions else ft.Container(width=0)
    content: ft.Control

    if compact:
        content = ft.Column(
            [
                ft.Row(
                    [leading, text_block],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Row([badge, actions_row], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ],
            spacing=8,
        )
    else:
        content = ft.Row(
            [leading, text_block, badge, actions_row],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    return ft.Container(
        margin=ft.margin.Margin.symmetric(horizontal=16),
        padding=ft.padding.Padding.symmetric(horizontal=14, vertical=13),
        bgcolor=SURFACE_COLOR,
        border_radius=18,
        border=ft.border.all(1, BORDER_COLOR),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=translucent(TEXT_COLOR, "0D"), offset=ft.Offset(0, 5)),
        content=content,
    )


def build_alert_list(alerts: list[dict], *, compact: bool = False, on_detail=None, on_edit=None, on_delete=None) -> ft.Column:
    header = ft.Container(
        padding=ft.padding.Padding.only(left=16, right=16, top=4, bottom=0),
        content=section_title(
            "Lista completa de alertas",
            "Plan base y alertas personalizadas.",
            ft.icons.Icons.NOTIFICATIONS_ACTIVE_ROUNDED,
        ),
    )

    if not alerts:
        return ft.Column(
            [
                header,
                ft.Container(
                    margin=ft.margin.Margin.symmetric(horizontal=16),
                    content=empty_state("Sin alertas", "Cuando registres mantenimientos o alertas apareceran aqui."),
                ),
            ],
            spacing=12,
        )

    return ft.Column(
        [
            header,
            *[
                _smart_alert_card(
                    alert,
                    compact=compact,
                    on_detail=on_detail,
                    on_edit=on_edit,
                    on_delete=on_delete,
                )
                for alert in alerts
            ],
        ],
        spacing=10,
    )

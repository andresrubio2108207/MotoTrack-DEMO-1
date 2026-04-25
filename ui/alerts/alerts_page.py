"""Página de alertas activas y resueltas."""

import flet as ft
from app.database.engine import SessionLocal
from app.services.alert_service import get_active_alerts, get_all_alerts, resolve_alert
from app.state.session_state import session_state
from ui.shared.theme import (
    BACKGROUND, SURFACE_VARIANT, PRIMARY, ON_SURFACE, ON_SURFACE_MUTED,
    SUCCESS, ERROR, WARNING, BORDER,
)
from ui.shared.navbar import build_navbar
from ui.shared.snackbar import show_snackbar


def _alert_card(alert, on_resolve) -> ft.Container:
    """Construye una tarjeta para una alerta."""
    if alert.resolved:
        icon = ft.Icons.CHECK_CIRCLE_ROUNDED
        icon_color = SUCCESS
        bg_color = ft.Colors.with_opacity(0.08, SUCCESS)
        border_color = ft.Colors.with_opacity(0.3, SUCCESS)
    elif alert.due_km:
        icon = ft.Icons.SPEED_ROUNDED
        icon_color = WARNING
        bg_color = ft.Colors.with_opacity(0.08, WARNING)
        border_color = ft.Colors.with_opacity(0.3, WARNING)
    else:
        icon = ft.Icons.NOTIFICATIONS_ACTIVE_ROUNDED
        icon_color = ERROR
        bg_color = ft.Colors.with_opacity(0.08, ERROR)
        border_color = ft.Colors.with_opacity(0.3, ERROR)

    due_info = None
    if alert.due_date:
        due_info = ft.Text(f"Vence: {alert.due_date.strftime('%d/%m/%Y')}", size=11, color=ON_SURFACE_MUTED)
    elif alert.due_km:
        due_info = ft.Text(f"Km límite: {alert.due_km:.0f} km", size=11, color=ON_SURFACE_MUTED)

    controls = [
        ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(icon, color=icon_color, size=20),
                    bgcolor=bg_color,
                    border_radius=10,
                    padding=ft.padding.all(8),
                ),
                ft.Column(
                    controls=[
                        ft.Text(alert.message, size=13, color=ON_SURFACE, expand=True),
                        *([ due_info ] if due_info else []),
                        ft.Text(
                            alert.created_at.strftime("%d/%m/%Y") if alert.created_at else "",
                            size=10,
                            color=ON_SURFACE_MUTED,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            spacing=12,
        ),
    ]

    if not alert.resolved:
        controls.append(
            ft.Container(
                content=ft.TextButton(
                    text="Resolver",
                    icon=ft.Icons.CHECK_ROUNDED,
                    style=ft.ButtonStyle(color=SUCCESS),
                    on_click=lambda e, aid=alert.id: on_resolve(aid),
                ),
                alignment=ft.alignment.center_right,
            )
        )

    return ft.Container(
        content=ft.Column(controls=controls, spacing=8),
        bgcolor=SURFACE_VARIANT,
        border_radius=16,
        padding=ft.padding.all(16),
        border=ft.border.all(1, border_color),
        animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )


def alerts_page(page: ft.Page):
    """Construye y muestra la página de alertas."""
    page.title = "MotoTrack PRO - Alertas"
    page.bgcolor = BACKGROUND
    page.padding = 0

    if not session_state.is_authenticated:
        page.go("/login")
        return

    moto = session_state.current_motorcycle

    def on_resolve(alert_id: int):
        db = SessionLocal()
        result = resolve_alert(db, alert_id)
        db.close()
        if result:
            show_snackbar(page, "Alerta resuelta ✅", "success")
            alerts_page(page)  # Refrescar
        else:
            show_snackbar(page, "No se pudo resolver la alerta", "error")

    page.controls.clear()
    page.navigation_bar = build_navbar(page, active_index=1)

    if not moto:
        page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.NOTIFICATIONS_OFF_ROUNDED, size=64, color=ON_SURFACE_MUTED),
                        ft.Text("Sin motocicleta registrada", size=16, color=ON_SURFACE_MUTED),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=BACKGROUND,
            )
        )
        page.update()
        return

    db = SessionLocal()
    active = get_active_alerts(db, moto.id)
    all_alerts = get_all_alerts(db, moto.id)
    resolved = [a for a in all_alerts if a.resolved]
    db.close()

    active_cards = [_alert_card(a, on_resolve) for a in active]
    resolved_cards = [_alert_card(a, on_resolve) for a in resolved]

    content = ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Alertas", size=24, weight=ft.FontWeight.BOLD, color=ON_SURFACE),
                            ft.Text(f"{moto.brand} {moto.model} · {len(active)} activa(s)", size=13, color=ON_SURFACE_MUTED),
                        ],
                        spacing=4,
                    ),
                    padding=ft.padding.only(top=16, bottom=8),
                ),

                # Activas
                ft.Text("🔴 Alertas Activas", size=15, weight=ft.FontWeight.W_600, color=ON_SURFACE),
                ft.Divider(height=6, color="transparent"),
                *(active_cards if active_cards else [
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(ft.Icons.NOTIFICATIONS_NONE_ROUNDED, size=48, color=ON_SURFACE_MUTED),
                                ft.Text("No hay alertas activas", size=14, color=ON_SURFACE_MUTED),
                                ft.Text("Tu moto está al día 🎉", size=12, color=ON_SURFACE_MUTED),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        alignment=ft.alignment.center,
                        padding=ft.padding.all(32),
                    )
                ]),

                ft.Divider(height=16, color=BORDER),

                # Resueltas
                ft.Text("✅ Alertas Resueltas", size=15, weight=ft.FontWeight.W_600, color=ON_SURFACE_MUTED),
                ft.Divider(height=6, color="transparent"),
                *(resolved_cards if resolved_cards else [
                    ft.Container(
                        content=ft.Text("Sin alertas resueltas aún.", size=13, color=ON_SURFACE_MUTED),
                        padding=ft.padding.all(16),
                    )
                ]),
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=8),
        expand=True,
        bgcolor=BACKGROUND,
    )

    page.add(content)
    page.update()

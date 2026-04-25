"""
MotoTrack PRO - Punto de entrada principal.
Inicializa la base de datos, el scheduler y arranca la aplicación Flet.
"""

import logging
import re

import flet as ft

from app.database.engine import init_db
from app.database.seed import seed_database
from app.scheduler.jobs import start_scheduler, stop_scheduler
from app.state.session_state import session_state
from ui.shared.theme import get_theme, BACKGROUND

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main(page: ft.Page):
    """Función principal de la aplicación Flet."""

    # ─── Configuración de la página ───────────────────────────────────────────
    page.title = "MotoTrack PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = get_theme()
    page.dark_theme = get_theme()
    page.bgcolor = BACKGROUND
    page.padding = 0
    page.window.width = 400
    page.window.height = 780
    page.window.resizable = True

    # ─── Router ───────────────────────────────────────────────────────────────
    def route_change(e: ft.RouteChangeEvent):
        """Maneja los cambios de ruta y carga la pantalla correspondiente."""
        page.navigation_bar = None
        route = e.route

        # Rutas protegidas: redirige al login si no hay sesión
        protected = ["/maintenance", "/alerts", "/profile"]
        is_protected = any(route.startswith(p) for p in protected)
        if is_protected and not session_state.is_authenticated:
            page.go("/login")
            return

        if route == "/" or route == "/login":
            from ui.auth.login_page import login_page
            login_page(page)

        elif route == "/register":
            from ui.auth.register_page import register_page
            register_page(page)

        elif route == "/profile":
            from ui.auth.profile_page import profile_page
            profile_page(page)

        elif route == "/maintenance":
            from ui.maintenance.history_page import history_page
            history_page(page)

        elif route == "/maintenance/new":
            from ui.maintenance.new_maintenance_page import new_maintenance_page
            new_maintenance_page(page)

        elif re.match(r"^/maintenance/\d+$", route):
            maintenance_id = int(route.split("/")[-1])
            from ui.maintenance.detail_page import detail_page
            detail_page(page, maintenance_id)

        elif route == "/alerts":
            from ui.alerts.alerts_page import alerts_page
            alerts_page(page)

        else:
            # Ruta no encontrada → redirigir
            logger.warning(f"Ruta desconocida: {route}")
            page.go("/login")

    def view_pop(e: ft.ViewPopEvent):
        """Maneja la navegación hacia atrás."""
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # ─── Pantalla inicial ─────────────────────────────────────────────────────
    page.go("/login")


if __name__ == "__main__":
    logger.info("🏍️  Iniciando MotoTrack PRO...")

    # Inicializar base de datos
    logger.info("Inicializando base de datos...")
    init_db()

    # Insertar datos de ejemplo
    logger.info("Cargando datos de ejemplo...")
    seed_database()

    # Iniciar scheduler de tareas
    logger.info("Iniciando scheduler...")
    start_scheduler()

    try:
        # Lanzar aplicación Flet
        ft.app(target=main)
    finally:
        stop_scheduler()
        logger.info("MotoTrack PRO cerrado correctamente.")

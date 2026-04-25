"""Estado global de sesión: usuario actual y motocicleta seleccionada."""

from typing import Optional


class SessionState:
    """
    Maneja el estado de sesión de la aplicación.
    Almacena el usuario autenticado y la motocicleta actualmente seleccionada.
    """

    def __init__(self):
        self.current_user = None          # Objeto User de SQLAlchemy
        self.current_motorcycle = None    # Objeto Motorcycle de SQLAlchemy
        self.access_token: Optional[str] = None

    @property
    def is_authenticated(self) -> bool:
        """Retorna True si hay un usuario autenticado."""
        return self.current_user is not None

    def set_user(self, user, token: str = ""):
        """Establece el usuario actual y su token."""
        self.current_user = user
        self.access_token = token

    def set_motorcycle(self, motorcycle):
        """Establece la motocicleta actualmente seleccionada."""
        self.current_motorcycle = motorcycle

    def clear(self):
        """Limpia toda la sesión (logout)."""
        self.current_user = None
        self.current_motorcycle = None
        self.access_token = None

    def __repr__(self) -> str:
        user_info = self.current_user.username if self.current_user else "None"
        moto_info = str(self.current_motorcycle) if self.current_motorcycle else "None"
        return f"<SessionState user={user_info} motorcycle={moto_info}>"


# Instancia global de sesión (singleton)
session_state = SessionState()

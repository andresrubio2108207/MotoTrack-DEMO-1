from __future__ import annotations

from dataclasses import dataclass

from app.models import User


@dataclass
class SessionState:
    user_id: int | None = None
    user_name: str | None = None
    user_email: str | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None

    def login(self, user: User) -> None:
        self.user_id = user.id
        self.user_name = user.name
        self.user_email = user.email

    def logout(self) -> None:
        self.user_id = None
        self.user_name = None
        self.user_email = None

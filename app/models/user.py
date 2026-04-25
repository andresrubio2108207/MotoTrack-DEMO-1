"""Modelo de Usuario."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base import Base


class User(Base):
    """Modelo ORM para usuarios de la aplicación."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)

    # Relación con motocicletas
    motorcycles = relationship("Motorcycle", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"

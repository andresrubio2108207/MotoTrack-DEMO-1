"""Modelo de Motocicleta."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Motorcycle(Base):
    """Modelo ORM para motocicletas registradas."""

    __tablename__ = "motorcycles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=True)
    current_km = Column(Float, default=0.0, nullable=False)

    # Relaciones
    owner = relationship("User", back_populates="motorcycles")
    maintenances = relationship("Maintenance", back_populates="motorcycle", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="motorcycle", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Motorcycle id={self.id} brand={self.brand!r} model={self.model!r}>"

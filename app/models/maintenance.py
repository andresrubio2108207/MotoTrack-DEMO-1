"""Modelo de Mantenimiento."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Maintenance(Base):
    """Modelo ORM para registros de mantenimiento."""

    __tablename__ = "maintenances"

    id = Column(Integer, primary_key=True, index=True)
    motorcycle_id = Column(Integer, ForeignKey("motorcycles.id"), nullable=False)
    type = Column(String(100), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    km = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    next_km = Column(Float, nullable=True)  # Km para el próximo mantenimiento
    next_date = Column(DateTime, nullable=True)  # Fecha para el próximo mantenimiento

    # Relación con motocicleta
    motorcycle = relationship("Motorcycle", back_populates="maintenances")

    def __repr__(self) -> str:
        return f"<Maintenance id={self.id} type={self.type!r} completed={self.completed}>"

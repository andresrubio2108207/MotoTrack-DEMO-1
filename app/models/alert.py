"""Modelo de Alerta."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Alert(Base):
    """Modelo ORM para alertas de mantenimiento."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    motorcycle_id = Column(Integer, ForeignKey("motorcycles.id"), nullable=False)
    message = Column(Text, nullable=False)
    due_date = Column(DateTime, nullable=True)
    due_km = Column(Float, nullable=True)
    resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relación con motocicleta
    motorcycle = relationship("Motorcycle", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert id={self.id} resolved={self.resolved} message={self.message[:30]!r}>"

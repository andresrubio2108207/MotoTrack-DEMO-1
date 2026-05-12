from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class Maintenance(Base):
    __tablename__ = "maintenances"

    id = Column(Integer, primary_key=True, autoincrement=True)  # type: ignore
    motorcycle_id = Column(Integer, ForeignKey("motorcycles.id", ondelete="CASCADE"), nullable=False)  # type: ignore
    type = Column(String, nullable=False)  # type: ignore
    description = Column(Text, nullable=True)  # type: ignore
    km_at_service = Column(Float, nullable=False)  # type: ignore
    cost = Column(Float, default=0.0)  # type: ignore
    service_date = Column(DateTime, nullable=False)  # type: ignore
    next_service_km = Column(Float, nullable=True)  # type: ignore
    next_service_date = Column(DateTime, nullable=True)  # type: ignore
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # type: ignore

    motorcycle = relationship("Motorcycle", back_populates="maintenances")
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)  # type: ignore
    motorcycle_id = Column(Integer, ForeignKey("motorcycles.id", ondelete="CASCADE"), nullable=False)  # type: ignore
    title = Column(String, nullable=False)  # type: ignore
    trigger_type = Column(String, nullable=False)  # type: ignore
    trigger_km = Column(Float, nullable=True)  # type: ignore
    trigger_date = Column(DateTime, nullable=True)  # type: ignore
    is_active = Column(Boolean, default=True)  # type: ignore
    is_fired = Column(Boolean, default=False)  # type: ignore
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # type: ignore

    motorcycle = relationship("Motorcycle", back_populates="alerts")
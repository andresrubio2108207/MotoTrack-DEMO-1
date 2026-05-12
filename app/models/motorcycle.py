from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Motorcycle(Base):
    __tablename__ = "motorcycles"

    id = Column(Integer, primary_key=True, autoincrement=True)  # type: ignore
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # type: ignore
    brand = Column(String, nullable=False)  # type: ignore
    model = Column(String, nullable=False)  # type: ignore
    year = Column(Integer, nullable=False)  # type: ignore
    plate = Column(String, unique=True, nullable=False)  # type: ignore
    current_km = Column(Float, default=0.0)  # type: ignore
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # type: ignore

    owner        = relationship("User", back_populates="motorcycles")
    maintenances = relationship(
        "Maintenance",
        back_populates="motorcycle",
        cascade="all, delete-orphan"
    )
    alerts       = relationship(
        "Alert",
        back_populates="motorcycle",
        cascade="all, delete-orphan"
    )
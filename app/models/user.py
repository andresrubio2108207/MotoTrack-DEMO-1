from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)  # type: ignore
    name = Column(String, nullable=False)  # type: ignore
    email = Column(String, unique=True, nullable=False, index=True)  # type: ignore
    password = Column(String, nullable=False)  # type: ignore
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # type: ignore

    motorcycles = relationship(
        "Motorcycle",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
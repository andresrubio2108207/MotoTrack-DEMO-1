from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.base import Base

class Motorcycle(Base):
    __tablename__ = "motorcycles"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    brand      = Column(String, nullable=False)
    model      = Column(String, nullable=False)
    year       = Column(Integer, nullable=False)
    plate      = Column(String, unique=True, nullable=False)
    current_km = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

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
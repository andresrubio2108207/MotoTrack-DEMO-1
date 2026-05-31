from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class Maintenance(Base):
    __tablename__ = "maintenances"

    id = Column(Integer, primary_key=True, autoincrement=True)  
    motorcycle_id = Column(Integer, ForeignKey("motorcycles.id", ondelete="CASCADE"), nullable=False)  
    type = Column(String, nullable=False)  
    description = Column(Text, nullable=True)  
    km_at_service = Column(Float, nullable=False)  
    cost = Column(Float, default=0.0)  
    service_date = Column(DateTime, nullable=False)  
    next_service_km = Column(Float, nullable=True)  
    next_service_date = Column(DateTime, nullable=True)  
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  

    motorcycle = relationship("Motorcycle", back_populates="maintenances")
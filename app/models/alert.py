from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    motorcycle_id = Column(Integer, ForeignKey("motorcycles.id", ondelete="CASCADE"), nullable=False)
    title         = Column(String, nullable=False)
    trigger_type  = Column(String, nullable=False)   
    trigger_km    = Column(Float, nullable=True)
    trigger_date  = Column(DateTime, nullable=True)
    is_active     = Column(Boolean, default=True)
    is_fired      = Column(Boolean, default=False)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    motorcycle = relationship("Motorcycle", back_populates="alerts")
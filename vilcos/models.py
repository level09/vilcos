from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from vilcos.database import Base

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class Table(BaseModel):
    __tablename__ = "tables"

    table_number = Column(Integer, unique=True, index=True)
    capacity = Column(Integer)
    location = Column(String)  # e.g., 'window', 'bar', 'patio'
    reservations = relationship("Reservation", back_populates="table")

class TimeSlot(BaseModel):
    __tablename__ = "time_slots"

    start_time = Column(Time, index=True)
    end_time = Column(Time)
    is_lunch = Column(Boolean)
    is_dinner = Column(Boolean)

class Reservation(BaseModel):
    __tablename__ = "reservations"

    table_id = Column(Integer, ForeignKey("tables.id"))
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"))
    reservation_date = Column(DateTime, index=True)
    party_size = Column(Integer)
    status = Column(String)  # e.g., 'confirmed', 'cancelled', 'completed'
    customer_name = Column(String)
    customer_email = Column(String)
    customer_phone = Column(String)
    special_requests = Column(String)
    
    table = relationship("Table", back_populates="reservations")
    time_slot = relationship("TimeSlot")


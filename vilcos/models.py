from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table as SQLAlchemyTable
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Numeric
from vilcos.database import Base


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)


class DiningTable(BaseModel):
    __tablename__ = "tables"

    table_number = Column(Integer, unique=True, index=True)
    capacity = Column(Integer)
    location = Column(String)  # e.g., 'window', 'bar', 'patio'
    reservations = relationship("Reservation", back_populates="table")


class TimeSlot(BaseModel):
    __tablename__ = "time_slots"

    duration = Column(Integer, index=True)  # Duration in minutes


# Association table for many-to-many relationship between Reservation and Item
reservation_items = SQLAlchemyTable(
    'reservation_items', Base.metadata,
    Column('reservation_id', Integer, ForeignKey('reservations.id'), primary_key=True),
    Column('item_id', Integer, ForeignKey('items.id'), primary_key=True)
)

class Category(BaseModel):
    __tablename__ = "categories"
    
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    items = relationship("Item", back_populates="category")

class Item(BaseModel):
    __tablename__ = "items"

    item_number = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    name_korean = Column(String)
    description = Column(String)
    dietary_info = Column(String)  # e.g., 'A / C / F / K'
    price = Column(Numeric(10, 2))  # Store price as a numeric field
    category_id = Column(Integer, ForeignKey('categories.id'))  # Add ForeignKey for category
    category = relationship("Category", back_populates="items")
    reservations = relationship("Reservation", secondary=reservation_items, back_populates="items")

class Reservation(BaseModel):
    __tablename__ = "reservations"

    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)  # Nullable for pickup orders
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"))
    reservation_date = Column(DateTime, index=True)
    party_size = Column(Integer)
    status = Column(String)  # e.g., 'confirmed', 'cancelled', 'completed'
    customer_name = Column(String)
    customer_email = Column(String)
    customer_phone = Column(String)
    special_requests = Column(String)

    table = relationship("DiningTable", back_populates="reservations")
    time_slot = relationship("TimeSlot")
    items = relationship("Item", secondary=reservation_items, back_populates="reservations")

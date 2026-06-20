from .base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

class VendorProfile(SQLAlchemyBase):
    __tablename__ = "vendor_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=True, index=True, comment="Foreign key to the accounts table.")
    Maps_id = Column(String, nullable=True, comment="Google Maps Place ID for the vendor.")
    country = Column(String, nullable=True)
    address = Column(String, nullable=True)
    name = Column(String, nullable=False)
    government= Column(String, nullable=False)
    area = Column(String, nullable=False)
    description = Column(String, nullable=False)
    lattitude = Column(String)
    longitude = Column(String)
    geofence_radius = Column(Integer)
    address_url = Column(String, nullable=True, comment="URL to the location on a map, e.g., Google Maps link.")
    working_hours = Column(JSONB, nullable=True, comment="JSON object describing opening hours.")
    category_id = Column(Integer, nullable=True, comment="Foreign key to a categories table for vendors.")
    is_approved = Column(Boolean, default=False, nullable=False, comment="Whether the vendor is approved and visible.")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    reviews = relationship("VendorReview", back_populates="vendor", cascade="all, delete-orphan")
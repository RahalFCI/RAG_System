from .base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class VendorReview(SQLAlchemyBase):
    __tablename__ = 'vendor_reviews'

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey('vendor_profiles.id'), nullable=False, index=True)
    author = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    vendor = relationship("VendorProfile", back_populates="reviews")

from .base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, Text , DateTime , func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

class places_reviews(SQLAlchemyBase):
    __tablename__ = "places_reviews"
    id = Column(Integer, primary_key=True, index=True)
    review_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    place_id = Column(Integer, nullable=False)
    explorer_id = Column(Integer, nullable=False)
    comment = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    Created_at = Column(DateTime( timezone=True),default=func.now() ,nullable=False)
    Updated_at = Column(DateTime( timezone=True),default=func.now() , onupdate=func.now() ,nullable=False)
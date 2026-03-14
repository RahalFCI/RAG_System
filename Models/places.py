from .base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, Text , DateTime , func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

class Place(SQLAlchemyBase):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    place_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)
    government= Column(String, nullable=False)
    address = Column(String, nullable=False)
    description = Column(String, nullable=False)
    lattitude = Column(String)
    longitude = Column(String)
    geofence_radius = Column(Integer)
    Created_at = Column(DateTime( timezone=True),default=func.now() ,nullable=False)
    Updated_at = Column(DateTime( timezone=True),default=func.now() , onupdate=func.now() ,nullable=False)

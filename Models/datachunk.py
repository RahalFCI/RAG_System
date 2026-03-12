from sqlalchemy import Column, Integer, String, Float, DateTime, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid
from sqlalchemy.orm import relationship
from .base import SQLAlchemyBase







class DataChunk(SQLAlchemyBase):
    __tablename__ = "chunks"

    chunk_id = Column(Integer, primary_key=True, index=True)

    chunk_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    chunk_text = Column(String, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)
    chunk_order = Column(Integer, nullable=False)

    chunk_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    chunk_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)


    Created_at = Column(DateTime( timezone=True),default=func.now() ,nullable=False)
    Updated_at = Column(DateTime( timezone=True),default=func.now() , onupdate=func.now() ,nullable=False)

    project = relationship("Project", back_populates="chunks" )
    asset = relationship("Asset", back_populates="chunks" )



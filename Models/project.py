from .base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, Text , DateTime , func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid



class Project(SQLAlchemyBase):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)

    project_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    Created_at = Column(DateTime( timezone=True),default=func.now() ,nullable=False)
    Updated_at = Column(DateTime( timezone=True),default=func.now() , onupdate=func.now() ,nullable=False)

    chunks = relationship("DataChunk", back_populates="project" )
    assets = relationship("Asset", back_populates="project" )   

    
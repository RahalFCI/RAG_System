from .base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, Text, DateTime, func, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

class UserProfile(SQLAlchemyBase):
    __tablename__ = "explorer_profiles"

    # Fields from your provided schema
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=True, index=True) # Assuming this links to an accounts table
    bio = Column(Text, nullable=True)
    country_code = Column(String, nullable=True)
    gender = Column(String(255), nullable=True)
    available_xp = Column(Integer, nullable=False, default=0)
    cumulative_xp = Column(Integer, nullable=False, default=0)
    current_level = Column(Integer, nullable=False, default=1)
    is_public = Column(Boolean, default=True, nullable=False)
    is_premium = Column(Boolean, nullable=False, default=False)
    plan_tier_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # --- Suggested fields for enhanced personalization ---
    interest_tags = Column(ARRAY(String), nullable=True, comment="User's selected interests like 'history', 'foodie', 'outdoors'.")
    budget_preference = Column(String, nullable=True, comment="User's budget preference, e.g., 'low', 'medium', 'high'.")
    preferred_travel_style = Column(String, nullable=True, comment="e.g., 'solo', 'family', 'couple', 'group'.")
    home_city = Column(String, nullable=True, comment="User's home city for 'near me' features.")
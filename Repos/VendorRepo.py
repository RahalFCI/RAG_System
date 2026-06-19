from .BaseRepo import BaseRepo
from RAG_System.Models import VendorProfile, VendorReview
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)


class VendorRepo(BaseRepo):
    """Repository for managing VendorProfile records in database."""
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client
    
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance
    
    async def create_vendor(self, vendor: VendorProfile):
        """Create a new vendor profile record."""
        try:
            async with self.db_client() as session:
                async with session.begin():
                    session.add(vendor)
                await session.commit()
                await session.refresh(vendor)
            return vendor
        except Exception as e:
            logger.error(f"Error creating vendor: {str(e)}")
            raise
    
    async def get_vendor_by_id(self, vendor_id: str):
        """Get a vendor by its ID."""
        try:
            async with self.db_client() as session:
                stmt = select(VendorProfile).where(VendorProfile.id == vendor_id)
                result = await session.execute(stmt)
                vendor = result.scalar_one_or_none()
            return vendor
        except Exception as e:
            logger.error(f"Error fetching vendor {vendor_id}: {str(e)}")
            return None
    
    async def get_vendors_by_area(self, area: str):
        """Get all vendors in a specific area."""
        try:
            async with self.db_client() as session:
                stmt = select(VendorProfile).where(VendorProfile.area == area)
                result = await session.execute(stmt)
                vendors = result.scalars().all()
            return vendors
        except Exception as e:
            logger.error(f"Error fetching vendors for area {area}: {str(e)}")
            return []
    
    async def get_vendors_by_government(self, government: str):
        """Get all vendors in a specific government/region."""
        try:
            async with self.db_client() as session:
                stmt = select(VendorProfile).where(VendorProfile.government == government)
                result = await session.execute(stmt)
                vendors = result.scalars().all()
            return vendors
        except Exception as e:
            logger.error(f"Error fetching vendors for government {government}: {str(e)}")
            return []
    
    async def get_approved_vendors(self):
        """Get all approved vendors."""
        try:
            async with self.db_client() as session:
                stmt = select(VendorProfile).where(VendorProfile.is_approved == True)
                result = await session.execute(stmt)
                vendors = result.scalars().all()
            return vendors
        except Exception as e:
            logger.error(f"Error fetching approved vendors: {str(e)}")
            return []
    
    async def get_all_vendors(self):
        """Get all vendors."""
        try:
            async with self.db_client() as session:
                stmt = select(VendorProfile)
                result = await session.execute(stmt)
                vendors = result.scalars().all()
            return vendors
        except Exception as e:
            logger.error(f"Error fetching all vendors: {str(e)}")
            return []
    
    async def update_vendor(self, vendor_id: str, update_data: dict):
        """Update a vendor profile record."""
        try:
            async with self.db_client() as session:
                async with session.begin():
                    vendor = await session.get(VendorProfile, vendor_id)
                    if vendor:
                        for key, value in update_data.items():
                            if hasattr(vendor, key):
                                setattr(vendor, key, value)
                await session.commit()
            return vendor
        except Exception as e:
            logger.error(f"Error updating vendor {vendor_id}: {str(e)}")
            raise
    
    async def delete_vendor(self, vendor_id: str):
        """Delete a vendor profile record."""
        try:
            async with self.db_client() as session:
                async with session.begin():
                    vendor = await session.get(VendorProfile, vendor_id)
                    if vendor:
                        await session.delete(vendor)
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting vendor {vendor_id}: {str(e)}")
            return False


class VendorReviewRepo(BaseRepo):
    """Repository for managing VendorReview records in database."""
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client
    
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance
    
    async def create_review(self, review: VendorReview):
        """Create a new vendor review record."""
        try:
            async with self.db_client() as session:
                async with session.begin():
                    session.add(review)
                await session.commit()
                await session.refresh(review)
            return review
        except Exception as e:
            logger.error(f"Error creating vendor review: {str(e)}")
            raise
    
    async def get_reviews_for_vendor(self, vendor_id: str):
        """Get all reviews for a specific vendor."""
        try:
            async with self.db_client() as session:
                stmt = select(VendorReview).where(VendorReview.vendor_id == vendor_id)
                result = await session.execute(stmt)
                reviews = result.scalars().all()
            return reviews
        except Exception as e:
            logger.error(f"Error fetching reviews for vendor {vendor_id}: {str(e)}")
            return []
    
    async def get_reviews_by_rating(self, vendor_id: str, min_rating: int = 0):
        """Get vendor reviews with a minimum rating."""
        try:
            async with self.db_client() as session:
                stmt = select(VendorReview).where(
                    (VendorReview.vendor_id == vendor_id) & 
                    (VendorReview.rating >= min_rating)
                )
                result = await session.execute(stmt)
                reviews = result.scalars().all()
            return reviews
        except Exception as e:
            logger.error(f"Error fetching rated reviews for vendor {vendor_id}: {str(e)}")
            return []
    
    async def delete_review(self, review_id: int):
        """Delete a vendor review record."""
        try:
            async with self.db_client() as session:
                async with session.begin():
                    review = await session.get(VendorReview, review_id)
                    if review:
                        await session.delete(review)
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting review {review_id}: {str(e)}")
            return False

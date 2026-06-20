from .BaseRepo import BaseRepo
from RAG_System.Models import Place
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)


class PlaceRepo(BaseRepo):
    """Repository for managing Place records in database."""
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client
    
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance
    
    async def create_place(self, place: Place):
        """Create a new place record."""
        try:
            async with self.db_client() as session:
                async with session.begin():
                    session.add(place)
                await session.commit()
                await session.refresh(place)
            return place
        except Exception as e:
            logger.error(f"Error creating place: {str(e)}")
            raise
    
    async def get_place_by_id(self, place_id: int):
        """Get a place by its ID."""
        try:
            async with self.db_client() as session:
                stmt = select(Place).where(Place.id == place_id)
                result = await session.execute(stmt)
                place = result.scalar_one_or_none()
            return place
        except Exception as e:
            logger.error(f"Error fetching place {place_id}: {str(e)}")
            return None
    
    async def get_places_by_area(self, area: str):
        """Get all places in a specific area."""
        try:
            async with self.db_client() as session:
                stmt = select(Place).where(Place.area == area)
                result = await session.execute(stmt)
                places = result.scalars().all()
            return places
        except Exception as e:
            logger.error(f"Error fetching places for area {area}: {str(e)}")
            return []
    
    async def get_places_by_government(self, government: str):
        """Get all places in a specific government/region."""
        try:
            async with self.db_client() as session:
                stmt = select(Place).where(Place.government == government)
                result = await session.execute(stmt)
                places = result.scalars().all()
            return places
        except Exception as e:
            logger.error(f"Error fetching places for government {government}: {str(e)}")
            return []
    
    async def get_all_places(self):
        """Get all places."""
        try:
            async with self.db_client() as session:
                stmt = select(Place)
                result = await session.execute(stmt)
                places = result.scalars().all()
            return places
        except Exception as e:
            logger.error(f"Error fetching all places: {str(e)}")
            return []
    
    async def update_place(self, place_id: int, update_data: dict):
        """Update a place record."""
        try:
            async with self.db_client() as session:
                async with session.begin():
                    place = await session.get(Place, place_id)
                    if place:
                        for key, value in update_data.items():
                            if hasattr(place, key):
                                setattr(place, key, value)
                await session.commit()
            return place
        except Exception as e:
            logger.error(f"Error updating place {place_id}: {str(e)}")
            raise
    
    async def delete_place(self, place_id: int):
        """Delete a place record."""
        try:
            async with self.db_client() as session:
                async with session.begin():
                    place = await session.get(Place, place_id)
                    if place:
                        await session.delete(place)
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting place {place_id}: {str(e)}")
            return False

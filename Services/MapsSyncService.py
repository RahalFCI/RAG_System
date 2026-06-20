from RAG_System.helpers.Data.Maps import MapsDataProvider
from RAG_System.Repos.PlaceRepo import PlaceRepo
from RAG_System.Repos.VendorRepo import VendorRepo, VendorReviewRepo
from RAG_System.Models.places import Place
from RAG_System.Models.vendor import VendorProfile
from RAG_System.Models.vendor_reviews import VendorReview
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MapsSyncService:
    """Service to sync data from Google Maps API to local database."""
    
    def __init__(self, api_key: str, db_client: object):
        """
        Initialize the sync service.
        
        Args:
            api_key: Google Maps API key
            db_client: Database client
        """
        self.maps_provider = MapsDataProvider(api_key)
        self.db_client = db_client
    
    async def sync_places(self, latitude: float, longitude: float, 
                         government: str, area: str,
                         search_type: str = "tourist_attraction",
                         radius: int = 5000) -> List[Place]:
        """
        Fetch places from Google Maps API and save to database.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            government: Government/state name
            area: Area/neighborhood name
            search_type: Type of place to search
            radius: Search radius in meters
            
        Returns:
            List of created Place records
        """
        try:
            # Fetch data from Maps API
            maps_places = self.maps_provider.get_places_nearby(
                latitude, longitude, search_type, radius
            )
            
            # Initialize repository
            place_repo = await PlaceRepo.create_instance(self.db_client)
            
            created_places = []
            for maps_place in maps_places:
                # Create Place model instance
                place = Place(
                    name=maps_place.get('name', ''),
                    government=government,
                    address=maps_place.get('address', ''),
                    area=area,
                    description=self._get_place_description(maps_place),
                    lattitude=str(maps_place.get('latitude', '')),
                    longitude=str(maps_place.get('longitude', '')),
                    geofence_radius=radius
                )
                
                # Save to database
                created_place = await place_repo.create_place(place)
                created_places.append(created_place)
                logger.info(f"Created place: {place.name}")
            
            logger.info(f"Synced {len(created_places)} places for {area}, {government}")
            return created_places
            
        except Exception as e:
            logger.error(f"Error syncing places: {str(e)}")
            return []
    
    async def sync_vendors(self, latitude: float, longitude: float,
                          government: str, area: str,
                          radius: int = 5000) -> List[VendorProfile]:
        """
        Fetch vendors/businesses from Google Maps API and save to database.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            government: Government/state name
            area: Area/neighborhood name
            radius: Search radius in meters
            
        Returns:
            List of created VendorProfile records
        """
        try:
            # Fetch data from Maps API
            maps_vendors = self.maps_provider.get_vendors_nearby(latitude, longitude, radius)
            
            # Initialize repository
            vendor_repo = await VendorRepo.create_instance(self.db_client)
            
            created_vendors = []
            for maps_vendor in maps_vendors:
                # Create VendorProfile model instance
                vendor = VendorProfile(
                    Maps_id=maps_vendor.get('place_id', ''),
                    name=maps_vendor.get('name', ''),
                    government=government,
                    address=maps_vendor.get('address', ''),
                    area=area,
                    description=self._get_place_description(maps_vendor),
                    lattitude=str(maps_vendor.get('latitude', '')),
                    longitude=str(maps_vendor.get('longitude', '')),
                    geofence_radius=radius,
                    address_url=self._build_maps_url(
                        maps_vendor.get('latitude'),
                        maps_vendor.get('longitude')
                    )
                )
                
                # Save to database
                created_vendor = await vendor_repo.create_vendor(vendor)
                created_vendors.append(created_vendor)
                
                # Fetch and sync reviews for this vendor
                await self._sync_vendor_reviews(
                    maps_vendor.get('place_id'),
                    created_vendor.id
                )
                
                logger.info(f"Created vendor: {vendor.name}")
            
            logger.info(f"Synced {len(created_vendors)} vendors for {area}, {government}")
            return created_vendors
            
        except Exception as e:
            logger.error(f"Error syncing vendors: {str(e)}")
            return []
    
    async def _sync_vendor_reviews(self, place_id: str, vendor_id: str):
        """
        Fetch reviews for a specific vendor and save to database.
        
        Args:
            place_id: Google Maps place ID
            vendor_id: Local vendor ID
        """
        try:
            # Fetch reviews from Maps API
            maps_reviews = self.maps_provider.get_place_reviews(place_id)
            
            # Initialize repository
            review_repo = await VendorReviewRepo.create_instance(self.db_client)
            
            for maps_review in maps_reviews:
                logger.info(f"Syncing review by {maps_review.get('author', 'Anonymous')} for vendor {vendor_id}")   
                review = VendorReview(
                    vendor_id=vendor_id,
                    author=maps_review.get('author', 'Anonymous'),
                    rating=maps_review.get('rating', 0),
                    content=maps_review.get('text', '')
                )
                
                await review_repo.create_review(review)
            
            logger.info(f"Synced {len(maps_reviews)} reviews for vendor {vendor_id}")
            
        except Exception as e:
            logger.error(f"Error syncing reviews for vendor {vendor_id}: {str(e)}")
    
    async def search_and_sync_places(self, query: str, government: str, 
                                    area: str, latitude: float = None,
                                    longitude: float = None) -> List[Place]:
        """
        Search for places by query and sync to database.
        
        Args:
            query: Search query (e.g., "museums in Cairo")
            government: Government/state name
            area: Area/neighborhood name
            latitude: Optional center latitude for location bias
            longitude: Optional center longitude for location bias
            
        Returns:
            List of created Place records
        """
        try:
            # Search on Maps API
            maps_places = self.maps_provider.search_places_by_query(
                query, latitude, longitude
            )
            
            # Initialize repository
            place_repo = await PlaceRepo.create_instance(self.db_client)
            
            created_places = []
            for maps_place in maps_places:
                place = Place(
                    name=maps_place.get('name', ''),
                    government=government,
                    address=maps_place.get('address', ''),
                    area=area,
                    description=query,
                    lattitude=str(maps_place.get('latitude', '')),
                    longitude=str(maps_place.get('longitude', '')),
                    geofence_radius=5000
                )
                
                created_place = await place_repo.create_place(place)
                created_places.append(created_place)
            
            logger.info(f"Synced {len(created_places)} places from query: {query}")
            return created_places
            
        except Exception as e:
            logger.error(f"Error searching and syncing places: {str(e)}")
            return []
    
    def _get_place_description(self, maps_place: Dict[str, Any]) -> str:
        """
        Generate description from place data.
        
        Args:
            maps_place: Place data from Google Maps
            
        Returns:
            Description string
        """
        parts = []
        
        if maps_place.get('rating'):
            parts.append(f"Rating: {maps_place['rating']}")
        
        if 'types' in maps_place and maps_place['types']:
            place_type = maps_place['types'][0].replace('_', ' ').title()
            parts.append(f"Type: {place_type}")
        
        if maps_place.get('business_status'):
            parts.append(f"Status: {maps_place['business_status']}")
        
        return " | ".join(parts) if parts else "No description available"
    
    def _build_maps_url(self, latitude: float, longitude: float) -> str:
        """
        Build a Google Maps URL for a location.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            Google Maps URL
        """
        if latitude and longitude:
            return f"https://maps.google.com/?q={latitude},{longitude}"
        return ""
    
    async def sync_all_vendor_reviews(self): 
        # sync reviews for all vendors in the database
        try:
            vendor_repo = await VendorRepo.create_instance(self.db_client)
            all_vendors = await vendor_repo.get_all_vendors()
            
            for vendor in all_vendors:
                await self._sync_vendor_reviews(vendor.Maps_id, vendor.id)
            
            logger.info(f"Synced reviews for {len(all_vendors)} vendors")
        except Exception as e:
            logger.error(f"Error syncing all vendor reviews: {str(e)}")

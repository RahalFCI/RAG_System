"""
Example script showing how to use Google Maps API integration.

Run this after setting up:
1. GOOGLE_MAPS_API_KEY in .env
2. Database is running
3. All models and repositories are initialized
"""

import asyncio
import logging
from RAG_System.Services.MapsSyncService import MapsSyncService
from RAG_System.Repos.PlaceRepo import PlaceRepo
from RAG_System.Repos.VendorRepo import VendorRepo, VendorReviewRepo
from RAG_System.helpers.Config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_sync_places(service: MapsSyncService, db_client):
    """
    Example 1: Sync tourist attractions in Giza.
    """
    logger.info("=" * 50)
    logger.info("Example 1: Syncing Places")
    logger.info("=" * 50)
    
    places = await service.sync_places(
        latitude=30.0089,      # Giza Plateau
        longitude=31.2097,
        government="Cairo",
        area="Giza",
        search_type="tourist_attraction",
        radius=5000
    )
    
    logger.info(f"✓ Synced {len(places)} tourist attractions in Giza")
    
    # Query the places we just saved
    place_repo = await PlaceRepo.create_instance(db_client)
    all_giza_places = await place_repo.get_places_by_area("Giza")
    logger.info(f"✓ Total places in Giza database: {len(all_giza_places)}")
    
    return places


async def example_sync_vendors(service: MapsSyncService, db_client):
    """
    Example 2: Sync vendors/businesses and their reviews in Downtown Cairo.
    """
    logger.info("\n" + "=" * 50)
    logger.info("Example 2: Syncing Vendors with Reviews")
    logger.info("=" * 50)
    
    vendors = await service.sync_vendors(
        latitude=30.0626,      # Downtown Cairo
        longitude=31.2453,
        government="Cairo",
        area="Downtown",
        radius=3000
    )
    
    logger.info(f"✓ Synced {len(vendors)} vendors with reviews in Downtown Cairo")
    
    # Query vendors
    vendor_repo = await VendorRepo.create_instance(db_client)
    all_vendors = await vendor_repo.get_vendors_by_area("Downtown")
    logger.info(f"✓ Total vendors in Downtown database: {len(all_vendors)}")
    
    return vendors


async def example_query_reviews(db_client, vendor_id):
    """
    Example 3: Query reviews for a specific vendor.
    """
    logger.info("\n" + "=" * 50)
    logger.info("Example 3: Querying Vendor Reviews")
    logger.info("=" * 50)
    
    review_repo = await VendorReviewRepo.create_instance(db_client)
    
    # Get all reviews
    all_reviews = await review_repo.get_reviews_for_vendor(vendor_id)
    logger.info(f"✓ Total reviews for vendor: {len(all_reviews)}")
    
    # Get high-rated reviews (4+ stars)
    high_rated = await review_repo.get_reviews_by_rating(vendor_id, min_rating=4)
    logger.info(f"✓ High-rated reviews (4+ stars): {len(high_rated)}")
    
    # Print sample reviews
    for i, review in enumerate(all_reviews[:3]):
        logger.info(f"\n  Review {i+1}:")
        logger.info(f"    Author: {review.author}")
        logger.info(f"    Rating: {review.rating}/5")
        logger.info(f"    Content: {review.content[:100]}...")


async def example_search_places(service: MapsSyncService, db_client):
    """
    Example 4: Search for specific types of places.
    """
    logger.info("\n" + "=" * 50)
    logger.info("Example 4: Searching for Specific Places")
    logger.info("=" * 50)
    
    queries = [
        "museums Cairo",
        "restaurants Giza",
        "ancient sites Cairo"
    ]
    
    for query in queries:
        places = await service.search_and_sync_places(
            query=query,
            government="Cairo",
            area=query.split()[-1].title(),
            latitude=30.0444,
            longitude=31.2357
        )
        logger.info(f"✓ Found {len(places)} results for: {query}")


async def example_get_approved_vendors(db_client):
    """
    Example 5: Get approved vendors and their stats.
    """
    logger.info("\n" + "=" * 50)
    logger.info("Example 5: Getting Approved Vendors Stats")
    logger.info("=" * 50)
    
    vendor_repo = await VendorRepo.create_instance(db_client)
    review_repo = await VendorReviewRepo.create_instance(db_client)
    
    approved_vendors = await vendor_repo.get_approved_vendors()
    logger.info(f"✓ Total approved vendors: {len(approved_vendors)}")
    
    # Print stats for each vendor
    for vendor in approved_vendors[:5]:  # Show first 5
        reviews = await review_repo.get_reviews_for_vendor(vendor.id)
        avg_rating = (
            sum(r.rating for r in reviews if r.rating) / len(reviews)
            if reviews else 0
        )
        
        logger.info(f"\n  {vendor.name}:")
        logger.info(f"    Location: {vendor.area}, {vendor.government}")
        logger.info(f"    Reviews: {len(reviews)}")
        logger.info(f"    Avg Rating: {avg_rating:.1f}/5")
        logger.info(f"    URL: {vendor.address_url}")


async def example_filter_by_area(db_client):
    """
    Example 6: Filter places by area and government.
    """
    logger.info("\n" + "=" * 50)
    logger.info("Example 6: Filtering by Area and Government")
    logger.info("=" * 50)
    
    place_repo = await PlaceRepo.create_instance(db_client)
    vendor_repo = await VendorRepo.create_instance(db_client)
    
    # Places in Giza
    giza_places = await place_repo.get_places_by_area("Giza")
    logger.info(f"✓ Places in Giza: {len(giza_places)}")
    
    # Places in Downtown
    downtown_places = await place_repo.get_places_by_area("Downtown")
    logger.info(f"✓ Places in Downtown: {len(downtown_places)}")
    
    # Vendors by government
    cairo_vendors = await vendor_repo.get_vendors_by_government("Cairo")
    logger.info(f"✓ Vendors in Cairo government: {len(cairo_vendors)}")


async def main():
    """Run all examples."""
    
    logger.info("Starting Google Maps API Integration Examples...")
    
    # Get settings and initialize service
    settings = get_settings()
    api_key = settings.OPENAI_API_KEY  # Replace with GOOGLE_MAPS_API_KEY
    
    if not api_key:
        logger.error("ERROR: Google Maps API key not configured in .env")
        return
    
    # Initialize service
    # Note: Replace None with your actual db_client
    service = MapsSyncService(api_key=api_key, db_client=None)
    
    try:
        # Example 1: Sync places
        places = await example_sync_places(service, db_client=None)
        
        # Example 2: Sync vendors with reviews
        vendors = await example_sync_vendors(service, db_client=None)
        
        # Example 3: Query reviews (use first vendor from list)
        if vendors:
            await example_query_reviews(db_client=None, vendor_id=vendors[0].id)
        
        # Example 4: Search for specific places
        await example_search_places(service, db_client=None)
        
        # Example 5: Get approved vendors stats
        await example_get_approved_vendors(db_client=None)
        
        # Example 6: Filter by area
        await example_filter_by_area(db_client=None)
        
        logger.info("\n" + "=" * 50)
        logger.info("✓ All examples completed successfully!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Error running examples: {str(e)}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())

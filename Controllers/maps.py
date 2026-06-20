from fastapi import APIRouter, Depends, HTTPException, Query, Request
from RAG_System.helpers.Config import get_settings, Settings
from RAG_System.Services.MapsSyncService import MapsSyncService
from typing import List
import logging

logger = logging.getLogger(__name__)

maps_router = APIRouter(
    prefix="/api/v1/maps",
    tags=["maps"],
)


def get_maps_sync_service(request: Request, app_settings: Settings) -> MapsSyncService:
    """Get MapsSyncService instance with API key from settings."""
    api_key = getattr(app_settings, 'GOOGLE_MAPS_API_KEY', None)
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Google Maps API key not configured in settings"
        )
    return MapsSyncService(api_key=api_key, db_client=request.app.db_client)


@maps_router.post("/sync-places")
async def sync_places(
    request: Request,
    app_settings: Settings = Depends(get_settings),
    latitude: float = Query(..., description="Center latitude"),
    longitude: float = Query(..., description="Center longitude"),
    government: str = Query(..., description="Government/state name"),
    area: str = Query(..., description="Area/neighborhood name"),
    search_type: str = Query("tourist_attraction", description="Type of place to search"),
    radius: int = Query(5000, description="Search radius in meters"),
):
    """
    Sync places from Google Maps API to database.
    
    Example: /api/v1/maps/sync-places?latitude=30.0444&longitude=31.2357&government=Cairo&area=Giza&search_type=tourist_attraction
    """
    try:
        service = get_maps_sync_service(request, app_settings)
        
        places = await service.sync_places(
            latitude=latitude,
            longitude=longitude,
            government=government,
            area=area,
            search_type=search_type,
            radius=radius
        )
        
        return {
            "status": "success",
            "message": f"Synced {len(places)} places",
            "count": len(places)
        }
    except Exception as e:
        logger.error(f"Error syncing places: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@maps_router.post("/sync-vendors")
async def sync_vendors(
    request: Request,
    app_settings: Settings = Depends(get_settings),
    latitude: float = Query(..., description="Center latitude"),
    longitude: float = Query(..., description="Center longitude"),
    government: str = Query(..., description="Government/state name"),
    area: str = Query(..., description="Area/neighborhood name"),
    radius: int = Query(5000, description="Search radius in meters"),
):
    """
    Sync vendors/businesses from Google Maps API to database.
    
    Example: /api/v1/maps/sync-vendors?latitude=30.0444&longitude=31.2357&government=Cairo&area=Giza
    """
    try:
        service = get_maps_sync_service(request, app_settings)
        
        vendors = await service.sync_vendors(
            latitude=latitude,
            longitude=longitude,
            government=government,
            area=area,
            radius=radius
        )
        
        return {
            "status": "success",
            "message": f"Synced {len(vendors)} vendors with reviews",
            "count": len(vendors)
        }
    except Exception as e:
        logger.error(f"Error syncing vendors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    


@maps_router.post("/sync-vendor-reviews") #sync reviews for all vendors in the database
async def sync_vendor_reviews(request:Request,  app_settings: Settings = Depends(get_settings)):
    """
    Sync reviews for all vendors in the database.
    
    Example: /api/v1/maps/sync-vendor-reviews
    """
    try:
        service = get_maps_sync_service(request, app_settings)
        
        synced_reviews_count = await service.sync_all_vendor_reviews()
        
        return {
            "status": "success",
            "message": f"Synced reviews for {synced_reviews_count} vendors",
            "count": synced_reviews_count
        }
    except Exception as e:
        logger.error(f"Error syncing vendor reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@maps_router.post("/search-places")
async def search_places(
    request: Request,
    app_settings: Settings = Depends(get_settings),
    query: str = Query(..., description="Search query (e.g., 'museums in Cairo')"),
    government: str = Query(..., description="Government/state name"),
    area: str = Query(..., description="Area/neighborhood name"),
    latitude: float = Query(None, description="Optional center latitude"),
    longitude: float = Query(None, description="Optional center longitude"),
):
    """
    Search for places by query and sync to database.
    
    Example: /api/v1/maps/search-places?query=restaurants+in+Cairo&government=Cairo&area=Giza
    """
    try:
        service = get_maps_sync_service(request, app_settings)
        
        places = await service.search_and_sync_places(
            query=query,
            government=government,
            area=area,
            latitude=latitude,
            longitude=longitude
        )
        
        return {
            "status": "success",
            "message": f"Found and synced {len(places)} places for query: {query}",
            "count": len(places)
        }
    except Exception as e:
        logger.error(f"Error searching places: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@maps_router.get("/health")
async def health_check():
    """Check if Maps API integration is configured."""
    return {
        "status": "healthy",
        "service": "Maps Sync Service",
        "note": "Ensure GOOGLE_MAPS_API_KEY is set in .env file"
    }

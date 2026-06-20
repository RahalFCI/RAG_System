# Google Maps API Integration Guide

This guide explains how to use the Google Maps API integration to fetch places, vendors, and reviews for your RAG System.

## Setup

### 1. Update .env File

Add your Google Maps API key to `.env`:

```env
GOOGLE_MAPS_API_KEY="your_google_maps_api_key_here"
```

### 2. Install Dependencies

Ensure `googlemaps` package is in your requirements:

```bash
pip install googlemaps
```

### 3. Update Config.py

Add the Google Maps API key to your Settings class in `helpers/Config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    GOOGLE_MAPS_API_KEY: str = None
```

### 4. Register Routes

Update your `main.py` to include the maps router:

```python
from RAG_System.Controllers.maps import maps_router

app.include_router(maps_router)
```

## API Endpoints

### 1. Sync Places

**Endpoint:** `POST /api/v1/maps/sync-places`

Fetch nearby places from Google Maps and save to database.

**Parameters:**
- `latitude` (float, required): Center latitude (e.g., 30.0444 for Cairo)
- `longitude` (float, required): Center longitude (e.g., 31.2357 for Cairo)
- `government` (str, required): Government/state name (e.g., "Cairo")
- `area` (str, required): Area/neighborhood (e.g., "Giza")
- `search_type` (str, optional): Type of place - "tourist_attraction", "museum", "restaurant", "hotel", "shopping_mall" (default: "tourist_attraction")
- `radius` (int, optional): Search radius in meters (default: 5000)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/maps/sync-places?latitude=30.0444&longitude=31.2357&government=Cairo&area=Giza&search_type=museum&radius=5000"
```

**Response:**
```json
{
  "status": "success",
  "message": "Synced 25 places",
  "count": 25
}
```

### 2. Sync Vendors

**Endpoint:** `POST /api/v1/maps/sync-vendors`

Fetch nearby businesses/vendors and their reviews from Google Maps.

**Parameters:**
- `latitude` (float, required): Center latitude
- `longitude` (float, required): Center longitude
- `government` (str, required): Government/state name
- `area` (str, required): Area/neighborhood
- `radius` (int, optional): Search radius in meters (default: 5000)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/maps/sync-vendors?latitude=30.0444&longitude=31.2357&government=Cairo&area=Giza"
```

**Response:**
```json
{
  "status": "success",
  "message": "Synced 15 vendors with reviews",
  "count": 15
}
```

### 3. Search Places

**Endpoint:** `POST /api/v1/maps/search-places`

Search for places by query string and sync to database.

**Parameters:**
- `query` (str, required): Search query (e.g., "restaurants in Cairo", "museums")
- `government` (str, required): Government/state name
- `area` (str, required): Area/neighborhood
- `latitude` (float, optional): Center latitude for location bias
- `longitude` (float, optional): Center longitude for location bias

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/maps/search-places?query=restaurants&government=Cairo&area=Giza&latitude=30.0444&longitude=31.2357"
```

**Response:**
```json
{
  "status": "success",
  "message": "Found and synced 20 places for query: restaurants",
  "count": 20
}
```

## Python Usage Examples

### Direct Service Usage

```python
from RAG_System.Services.MapsSyncService import MapsSyncService
from RAG_System.helpers.Config import get_settings

settings = get_settings()
service = MapsSyncService(
    api_key=settings.GOOGLE_MAPS_API_KEY,
    db_client=your_db_client
)

# Sync places
places = await service.sync_places(
    latitude=30.0444,
    longitude=31.2357,
    government="Cairo",
    area="Giza",
    search_type="tourist_attraction"
)

# Sync vendors (businesses)
vendors = await service.sync_vendors(
    latitude=30.0444,
    longitude=31.2357,
    government="Cairo",
    area="Giza"
)

# Search specific places
museums = await service.search_and_sync_places(
    query="museums",
    government="Cairo",
    area="Giza",
    latitude=30.0444,
    longitude=31.2357
)
```

### Querying Synced Data

```python
from RAG_System.Repos.PlaceRepo import PlaceRepo
from RAG_System.Repos.VendorRepo import VendorRepo, VendorReviewRepo

# Initialize repositories
place_repo = await PlaceRepo.create_instance(db_client)
vendor_repo = await VendorRepo.create_instance(db_client)
review_repo = await VendorReviewRepo.create_instance(db_client)

# Get all places in an area
places = await place_repo.get_places_by_area("Giza")

# Get vendors by government
vendors = await vendor_repo.get_vendors_by_government("Cairo")

# Get only approved vendors
approved = await vendor_repo.get_approved_vendors()

# Get reviews for a vendor
reviews = await review_repo.get_reviews_for_vendor(vendor_id)

# Get highly rated reviews
high_rated = await review_repo.get_reviews_by_rating(vendor_id, min_rating=4)
```

## Data Models

### Place Model
- `id`: Primary key
- `place_uuid`: Unique UUID
- `name`: Place name
- `government`: Government/state
- `address`: Full address
- `area`: Neighborhood/area
- `description`: Place description
- `latitude`: GPS latitude
- `longitude`: GPS longitude
- `geofence_radius`: Search radius
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### VendorProfile Model
- `id`: UUID primary key
- `name`: Vendor name
- `government`: Government/state
- `address`: Full address
- `area`: Neighborhood/area
- `description`: Business description
- `latitude`: GPS latitude
- `longitude`: GPS longitude
- `geofence_radius`: Search radius
- `address_url`: Google Maps link
- `working_hours`: JSON object with opening hours
- `is_approved`: Approval status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### VendorReview Model
- `id`: Primary key
- `vendor_id`: Foreign key to vendor
- `author`: Review author name
- `rating`: Rating (1-5)
- `content`: Review text
- `created_at`: Creation timestamp

## Common Use Cases

### 1. Populate Initial Database

```python
# Get all tourist attractions in Giza
areas = [
    {"name": "Giza", "lat": 30.0444, "lon": 31.2357},
    {"name": "Downtown", "lat": 30.0626, "lon": 31.2453},
    {"name": "Heliopolis", "lat": 30.0956, "lon": 31.3422}
]

for area in areas:
    await service.sync_places(
        latitude=area["lat"],
        longitude=area["lon"],
        government="Cairo",
        area=area["name"],
        search_type="tourist_attraction"
    )
```

### 2. Filter Places by User Query

```python
# When user searches for "Egyptian museums"
museums = await service.search_and_sync_places(
    query="Egyptian museums Cairo",
    government="Cairo",
    area="Various"
)

# Query all museums
all_museums = await place_repo.get_places_by_area("Various")
```

### 3. Get Recommended Vendors

```python
# Get approved vendors with high ratings
vendors = await vendor_repo.get_approved_vendors()

for vendor in vendors:
    reviews = await review_repo.get_reviews_by_rating(vendor.id, min_rating=4)
    if len(reviews) > 5:  # At least 5 high-rated reviews
        print(f"Recommended: {vendor.name} - {len(reviews)} high reviews")
```

## Data for Cairo & Giza

### Coordinates
- **Cairo Center**: 30.0626, 31.2453
- **Giza Plateau**: 30.0089, 31.2097
- **Downtown Cairo**: 30.0626, 31.2453
- **Heliopolis**: 30.0956, 31.3422

### Popular Search Types for Egypt
- `museum` - Museums
- `tourist_attraction` - Tourist sites
- `historical_site` - Historical locations
- `restaurant` - Restaurants
- `hotel` - Hotels
- `shopping_mall` - Shopping centers
- `cafe` - Cafes
- `bar` - Bars/Nightlife

## Error Handling

```python
try:
    places = await service.sync_places(
        latitude=30.0444,
        longitude=31.2357,
        government="Cairo",
        area="Giza"
    )
except Exception as e:
    logger.error(f"Failed to sync places: {str(e)}")
    # Handle error appropriately
```

## Rate Limiting

Google Maps API has rate limits. The `MapsDataProvider` includes a 2-second delay between paginated requests to respect API limits.

## Security Notes

1. Never commit your API key to version control
2. Use environment variables (.env file)
3. Implement API key rotation in production
4. Monitor API usage in Google Cloud Console

## Troubleshooting

### "Google Maps API key not configured"
- Ensure `GOOGLE_MAPS_API_KEY` is set in `.env`
- Restart your application after updating .env

### No results from API
- Check coordinates are correct
- Verify place type exists in that area
- Increase search radius
- Check API quota in Google Cloud Console

### Database errors
- Ensure PostgreSQL is running
- Check database connection string
- Verify Place and VendorProfile tables exist

## References

- [Google Maps API Documentation](https://developers.google.com/maps)
- [Places API](https://developers.google.com/maps/documentation/places/web-service)
- [Python Google Maps Client](https://googlemaps.github.io/google-maps-services-python/)

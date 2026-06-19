from typing import List, Dict, Any
import json
import logging
from urllib.parse import urlencode
from urllib.request import urlopen

logger = logging.getLogger(__name__)


class MapsDataProvider:
    """Fetch data from Google Maps API for places, vendors, and reviews."""
    
    def __init__(self, api_key: str):
        """Initialize Google Maps client."""
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"

    def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        query_params = dict(params)
        query_params["key"] = self.api_key
        url = f"{self.base_url}/{endpoint}/json?{urlencode(query_params)}"
        with urlopen(url, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("status") not in ["OK", "ZERO_RESULTS"]:
            logger.warning("Google Maps API returned status %s for %s", payload.get("status"), endpoint)
        return payload
    
    def get_places_nearby(self, latitude: float, longitude: float, 
                         search_type: str = "tourist_attraction", 
                         radius: int = 5000) -> List[Dict[str, Any]]:
        """
        Fetch nearby places using Google Maps Places Nearby API.
        
        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            search_type: Type of place (e.g., 'tourist_attraction', 'museum', 'restaurant')
            radius: Search radius in meters
            
        Returns:
            List of place dictionaries with name, address, coordinates, rating, etc.
        """
        try:
            payload = self._request(
                "nearbysearch",
                {
                    "location": f"{latitude},{longitude}",
                    "radius": radius,
                    "type": search_type,
                },
            )

            results = []
            for place in payload.get("results", []):
                results.append(self._parse_place_data(place))

            logger.info(f"Fetched {len(results)} places nearby ({latitude}, {longitude})")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching nearby places: {str(e)}")
            return []
    
    def get_vendors_nearby(self, latitude: float, longitude: float,
                          radius: int = 5000) -> List[Dict[str, Any]]:
        """
        Fetch nearby businesses/vendors (restaurants, shops, hotels, etc.).
        
        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            radius: Search radius in meters
            
        Returns:
            List of vendor dictionaries
        """
        vendor_types = ['restaurant', 'cafe', 'hotel', 'shopping_mall', 'store']
        all_vendors = []
        
        for vendor_type in vendor_types:
            vendors = self.get_places_nearby(latitude, longitude, vendor_type, radius)
            for vendor in vendors:
                vendor['category'] = vendor_type
                all_vendors.append(vendor)
        
        logger.info(f"Fetched {len(all_vendors)} vendors")
        return all_vendors
    
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific place.
        
        Args:
            place_id: Google Maps place ID
            
        Returns:
            Dictionary with detailed place information
        """
        try:
            payload = self._request(
                "details",
                {
                    "place_id": place_id,
                    "fields": "place_id,name,formatted_address,geometry,rating,reviews,opening_hours,website,formatted_phone_number",
                },
            )
            result = payload.get('result', {})
            return self._parse_place_details(result)
                
        except Exception as e:
            logger.error(f"Error fetching place details: {str(e)}")
            return {}
    
    def get_place_reviews(self, place_id: str) -> List[Dict[str, Any]]:
        """
        Extract reviews from place details.
        
        Args:
            place_id: Google Maps place ID
            
        Returns:
            List of review dictionaries
        """
        try:
            details = self.get_place_details(place_id)
            reviews = details.get('reviews', []) if isinstance(details, dict) else []

            parsed_reviews = []
            for review in reviews:
                parsed_reviews.append({
                    'author': review.get('author_name', 'Anonymous'),
                    'rating': review.get('rating', 0),
                    'text': review.get('text', ''),
                    'time': review.get('time', None)
                })

            logger.info(f"Fetched {len(parsed_reviews)} reviews for place {place_id}")
            return parsed_reviews
                
        except Exception as e:
            logger.error(f"Error fetching place reviews: {str(e)}")
            return []
    
    def search_places_by_query(self, query: str, 
                              latitude: float = None, 
                              longitude: float = None) -> List[Dict[str, Any]]:
        """
        Search for places by text query.
        
        Args:
            query: Search query (e.g., "restaurants in Cairo")
            latitude: Optional center latitude for location bias
            longitude: Optional center longitude for location bias
            
        Returns:
            List of place dictionaries matching the query
        """
        try:
            search_params = {'query': query}

            if latitude and longitude:
                search_params['location'] = f"{latitude},{longitude}"
                search_params['radius'] = 5000
            
            results = self._request("textsearch", search_params)
            
            places = []
            for place in results.get('results', []):
                place_data = self._parse_place_data(place)
                places.append(place_data)
            
            logger.info(f"Found {len(places)} places for query: {query}")
            return places
            
        except Exception as e:
            logger.error(f"Error searching places: {str(e)}")
            return []
    
    def _parse_place_data(self, place: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Google Maps place data into our format.
        
        Args:
            place: Raw place data from Google Maps API
            
        Returns:
            Parsed place dictionary
        """
        location = place.get('geometry', {}).get('location', {})
        
        return {
            'place_id': place.get('place_id'),
            'name': place.get('name', ''),
            'address': place.get('vicinity', ''),
            'latitude': location.get('lat'),
            'longitude': location.get('lng'),
            'rating': place.get('rating'),
            'types': place.get('types', []),
            'opening_hours': place.get('opening_hours'),
            'photos': place.get('photos', []),
            'business_status': place.get('business_status')
        }
    
    def _parse_place_details(self, place_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse detailed place information from Google Maps API.
        
        Args:
            place_details: Raw place details from Google Maps API
            
        Returns:
            Parsed place details dictionary
        """
        location = place_details.get('geometry', {}).get('location', {})
        
        return {
            'place_id': place_details.get('place_id'),
            'name': place_details.get('name', ''),
            'address': place_details.get('formatted_address', ''),
            'latitude': location.get('lat'),
            'longitude': location.get('lng'),
            'phone': place_details.get('formatted_phone_number'),
            'website': place_details.get('website'),
            'url': place_details.get('url'),
            'rating': place_details.get('rating'),
            'review_count': place_details.get('user_ratings_total', 0),
            'opening_hours': place_details.get('opening_hours'),
            'types': place_details.get('types', []),
            'description': place_details.get('editorial_summary', {}).get('overview', '')
        }

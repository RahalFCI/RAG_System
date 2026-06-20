from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Any

from .places import Place
from .vendor import VendorProfile

def prepare_documents_for_chunking(db: Session, top_n_reviews: int = 3) -> List[Dict[str, Any]]:
    """
    Fetches places and vendors, combines their data with top-rated reviews,
    and returns a list of rich text documents ready for chunking.

    Each document is a dictionary containing the source entity's ID, type,
    and the combined text.

    Args:
        db: The SQLAlchemy session.
        top_n_reviews: The number of top reviews to include for each item.

    Returns:
        A list of dictionaries, where each dictionary represents a document.
    """
    documents = []

    # 1. Process Places
    places = db.query(Place).options(joinedload(Place.reviews)).all()
    for place in places:
        # Sort reviews by rating (highest first) and take the top N
        top_reviews = sorted(place.reviews or [], key=lambda r: r.rating or 0, reverse=True)[:top_n_reviews]

        # Format the reviews into a readable string
        review_texts = [f'- Review: "{r.content}" (Rating: {r.rating}/5)' for r in top_reviews]
        review_section = "\n".join(review_texts)

        # Combine all information into a single rich text document
        document_text = f"""Type: Historical Place
Name: {place.name}
Location: {place.area}, {place.government}
Description: {place.description}

Recent Reviews:
{review_section if review_section else "No reviews available."}"""

        documents.append({
            "source_id": str(place.place_uuid),
            "source_type": "place",
            "text": document_text
        })

    # 2. Process Vendors (similar logic)
    vendors = db.query(VendorProfile).options(joinedload(VendorProfile.reviews)).all()
    for vendor in vendors:
        top_reviews = sorted(vendor.reviews or [], key=lambda r: r.rating or 0, reverse=True)[:top_n_reviews]
        review_texts = [f'- Review: "{r.content}" (Rating: {r.rating}/5)' for r in top_reviews]
        review_section = "\n".join(review_texts)

        document_text = f"""Type: Vendor/Business
Name: {vendor.name}
Location: {vendor.area}, {vendor.government}
Description: {vendor.description}

Recent Reviews:
{review_section if review_section else "No reviews available."}"""

        documents.append({"source_id": str(vendor.id), "source_type": "vendor", "text": document_text})

    return documents

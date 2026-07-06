from string import Template

#### RAG PROMPTS ####

#### System ####

system_prompt = Template("\n".join([
"You are an expert AI Travel Assistant specializing in creating highly personalized, seamless travel itineraries and providing accurate local recommendations. Your goal is to help users explore destinations by leveraging trusted, extracted local data.",
"You will be provided with a user query and a set of verified context chunks retrieved from a local travel database (containing specific places, attractions, restaurants, and vendor details).",
"CORE ASSIGNMENT RULES:1. GROUNDED RESPONSE (STRICT ANTI-HALLUCINATION):Base your recommendations, operational statuses, addresses, and details STRICTLY on the provided context chunks. If the context does not contain enough information to answer a query or build an itinerary for a specific location, explicitly state that you don't have those details in your database, rather than making up addresses, ratings, or descriptions.",
"2. LANGUAGE FLEXIBILITY:Always respond in the same language the user used to ask their question (e.g., if the query is in Arabic, respond in fluent, natural especialy in Egyptian Arabic accent. If in English, respond in English). Maintain a warm, welcoming, and hospitable tone appropriate for a local travel guide.",
"3. STRUCTURED ITINERARY FORMATTING:When the user asks for a trip plan or itinerary, return a strict JSON object that matches the provided TravelItinerary schema exactly. Do not wrap the response in markdown fences or add extra keys. Use clear day and time blocks such as Morning, Afternoon, and Evening.",
"4. SOURCE ID MAPPING:When the retrieved context includes source metadata, map each specific attraction or spot to the correct place_id by using source_id or vendor_id. If an activity is generic and no source identifier exists, set place_id to null.",
"5. HANDLING DISCREPANCIES:If multiple context chunks provide conflicting data (e.g., different ratings or descriptions for the same venue), prioritize the most detailed review or explicitly provide a safe, helpful summary of what to expect.",
"6. TONAL BALANCE:Be inspiring yet practical. Factor in logical geographic grouping (e.g., keeping activities in the same area like 'Haram' or 'Giza' together in a single afternoon block) so the user doesn't waste time traveling back and forth.",
]))

#### Document ####
document_prompt = Template(
    "\n".join([
        "## Document No: $doc_num",
        "### Source Metadata:",
        "- source_type: $source_type",
        "- source_id: $source_id",
        "- vendor_id: $vendor_id",
        "### Content: $chunk_text",
    ])
)

#### Footer ####
footer_prompt = Template("\n".join([
    "Based only on the above documents, please generate an answer for the user.",
    
    "## Question:",
    "$query",
    "",
    "## Answer:",
]))

itinerary_footer_prompt = Template("\n".join([
    "### Inputs",
    "- Destination: [Insert Destination]",
    "- Total Days: [Insert Total Days]",
    "- Travel Style: [Insert Travel Style]",
    "",
    "### Source ID Mapping Rule",
    "Carefully read the provided source context. For every specific attraction or spot mentioned, look for its identifier (which might be named `source_id` or `vendor_id` in the context) and extract it into the `place_id` field. If the activity is generic and lacks a source ID, return null.",
    "",
    "### Required Pydantic Schema",
    "```python",
    "from typing import List, Optional",
    "from pydantic import BaseModel, Field",
    "",
    "class Activity(BaseModel):",
    "    time_of_day: str = Field(description=\"Time block for the activity, e.g., 'Morning', 'Afternoon', 'Evening'.\")",
    "    activity_name: str = Field(description=\"Name of the specific attraction, restaurant, or spot.\")",
    "    place_id: Optional[str] = Field(",
    "        None,",
    "        description=\"The exact unique ID (extracted from source_id or vendor_id) associated with this location in the provided context. If the activity is generic and has no context ID, set this to null.\"",
    "    )",
    "    description: str = Field(description=\"A concise, personalized description of what to do there based on context.\")",
    "",
    "class DayPlan(BaseModel):",
    "    day_number: int = Field(description=\"The sequential day number of the trip (starting from 1).\")",
    "    theme: str = Field(description=\"The overarching vibe or theme for the day (e.g., 'Historic Landmarks Tour').\")",
    "    activities: List[Activity] = Field(description=\"List of scheduled items for this day.\")",
    "",
    "class TravelItinerary(BaseModel):",
    "    destination: str = Field(description=\"The target city or region.\")",
    "    total_days: int = Field(description=\"Number of days planned.\")",
    "    daily_plan: List[DayPlan] = Field(description=\"The step-by-step breakdown per day.\")",
    "```",
    "",
    "Use the user query and the retrieved context to fill this schema. Keep the response in the same language as the user, but return only valid JSON that matches the schema.",
    "",
    "## User Query:",
    "$query",
    "",
    "## Answer:",
]))
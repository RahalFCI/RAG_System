# RAG_System
Project Overview
TravelGenie RAG is a sophisticated travel planning engine that combines the creative
power of Large Language Models (LLMs) with a curated knowledge base of
destinations, flight schedules, and local attractions. Unlike standard AI planners that

might hallucinate non-existent flights or closed attractions, this system retrieves real-
world data before generating recommendations.

## 🚀 Key Features

* **Fact-Based Itineraries:** Unlike standard LLMs, this system retrieves actual data from a vector database to prevent suggesting non-existent places or closed attractions.
* **Contextual Personalization:** Tailors trips based on specific user constraints like budget, dietary restrictions (e.g., "vegan-friendly"), and accessibility needs.
* **Semantic Search:** Uses vector embeddings to find destinations that match the *vibe* of your query (e.g., "hidden gems with a bohemian feel").
* **Source Transparency:** Provides references to the original travel blogs or official guides used to generate the plan.

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **backend** | FastAPI, docker, PostgreSQL, SQLAlchemy
| **LLM** | Local LLm using ollama 
| **Vector Database** | pgvector |
| **Embedding Model** | OpenAI `text-embedding-3-small` |


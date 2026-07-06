import json
import logging
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from RAG_System.Models.Asset import Asset
from RAG_System.Models.datachunk import DataChunk
from RAG_System.Models.places import Place
from RAG_System.Models.project import Project
from RAG_System.Models.vendor import VendorProfile
from RAG_System.Repos.AssetRepo import AssetRepo
from RAG_System.Repos.ChunckRepo import ChunkRepo
from RAG_System.Repos.ProjectRepo import projectRepo
from RAG_System.Services.LLM.LLMEnums import DocumentTypeEnum
from ..Controllers.BaseController import BaseController

logger = logging.getLogger(__name__)


class NLPController(BaseController):
    def __init__(self, vectordb_client, generation_client, embedding_client, template_parser, db_client=None):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser
        self.db_client = db_client

    def process_text(self, text):
        return str(text or "")[: self.app_settings.INPUT_DAFAULT_MAX_CHARACTERS or 1024].strip()

    def create_collection_name(self, project_id: int):
        return f"collection_{self.vectordb_client.default_vector_size}_{project_id}".strip()

    async def ensure_project(self, project_id: int):
        project_repo = await projectRepo.create_instance(self.db_client)
        return await project_repo.get_project_or_create_one(project_id=project_id)

    async def ensure_maps_asset(self, project: Project):
        asset_repo = await AssetRepo.create_instance(self.db_client)
        existing = await asset_repo.get_asset_record(
            asset_project_id=project.project_id,
            asset_name="maps_sync_data",
        )
        if existing:
            return existing

        asset = Asset(
            asset_project_id=project.project_id,
            asset_type="maps",
            asset_name="maps_sync_data",
            asset_size=0,
            asset_config={"source": "postgresql_maps_data"},
        )
        return await asset_repo.create_asset(asset)

    async def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)

    async def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = await self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(json.dumps(collection_info, default=lambda x: x.__dict__))

    def _format_reviews(self, reviews, review_text_key: str = "content"):
        review_lines = []
        for review in reviews or []:
            review_text = getattr(review, review_text_key, None) if not isinstance(review, dict) else review.get(review_text_key)
            review_rating = getattr(review, "rating", None) if not isinstance(review, dict) else review.get("rating")
            review_author = getattr(review, "author", None) if not isinstance(review, dict) else review.get("author")
            review_text = str(review_text or "").strip()
            if not review_text:
                continue
            review_lines.append(f"- {review_author or 'Anonymous'} ({review_rating or 'N/A'}/5): {review_text}")
        return review_lines

    def _limit_words(self, text: str, max_words: int) -> str:
        words = str(text or "").split()
        if len(words) <= max_words:
            return str(text or "").strip()
        return " ".join(words[:max_words]).strip()

    def _format_source_metadata(self, metadata: dict = None):
        metadata = metadata or {}
        source_type = str(metadata.get("source_type") or "unknown").strip()
        source_id = str(metadata.get("source_id") or "").strip()
        vendor_id = source_id if source_type.lower() == "vendor" else str(metadata.get("vendor_id") or "").strip()
        return source_type, source_id, vendor_id

    def _summarize_reviews_for_place(self, place: Place, max_words: int = 150) -> str:
        review_lines = self._format_reviews(place.reviews, review_text_key="comment")
        if not review_lines:
            return "No reviews available."

        reviews_text = "\n".join(review_lines)
        prompt = (
            "Summarize the following place reviews into one concise paragraph. "
            f"Keep the response grounded in the reviews, avoid adding new facts, and stay within {max_words} words.\n\n"
            f"Reviews:\n{reviews_text}"
        )

        summary = None
        if self.generation_client:
            try:
                summary = self.generation_client.generate_text(
                    prompt=prompt,
                    max_tokens=max_words + 40,
                    temperature=0.2,
                )
            except Exception:
                logger.exception("Failed to summarize place reviews with the generation client.")

        if not summary:
            summary = " ".join(review_lines)

        return self._limit_words(summary.strip(), max_words)

    def _summarize_reviews_for_vendor(self, vendor: VendorProfile, max_words: int = 150) -> str:
        review_lines = self._format_reviews(vendor.reviews, review_text_key="content")
        if not review_lines:
            return "No reviews available."

        reviews_text = "\n".join(review_lines)
        prompt = (
            "Summarize the following vendor reviews into one concise paragraph. "
            f"Keep the response grounded in the reviews, avoid adding new facts, and stay within {max_words} words.\n\n"
            f"Reviews:\n{reviews_text}"
        )

        summary = None
        if self.generation_client:
            try:
                summary = self.generation_client.generate_text(
                    prompt=prompt,
                    max_tokens=max_words + 40,
                    temperature=0.2,
                )
            except Exception:
                logger.exception("Failed to summarize vendor reviews with the generation client.")

        if not summary:
            summary = " ".join(review_lines)

        return self._limit_words(summary.strip(), max_words)

    def _split_text_with_overlap(self, text: str, chunk_size: int, overlap_size: int) -> List[str]:
        clean_text = str(text or "").strip()
        if not clean_text:
            return []

        words = clean_text.split()
        if len(words) <= chunk_size:
            return [clean_text]

        safe_overlap = max(0, min(overlap_size, chunk_size - 1))
        step = max(1, chunk_size - safe_overlap)

        chunks: List[str] = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            if chunk_words:
                chunks.append(" ".join(chunk_words))
            if end >= len(words):
                break
            start += step
        return chunks

    def _build_place_document(self, place: Place):
        review_summary = self._summarize_reviews_for_place(place, max_words=150)
        document_text = (
            f"Type: Place\n"
            f"Name: {place.name}\n"
            f"Government: {place.government}\n"
            f"Area: {place.area}\n"
            f"Address: {place.address}\n"
            f"Coordinates: {place.lattitude}, {place.longitude}\n"
            f"Description: {place.description}\n\n"
            f"Review Summary (max 150 words):\n"
            f"{review_summary}"
        )
        metadata = {
            "source_type": "place",
            "source_id": str(place.place_uuid),
            "name": place.name,
            "government": place.government,
            "area": place.area,
        }
        return document_text, metadata

    def _build_vendor_document(self, vendor: VendorProfile):
        review_summary = self._summarize_reviews_for_vendor(vendor, max_words=150)
        document_text = (
            f"Type: Vendor\n"
            f"Name: {vendor.name}\n"
            f"Government: {vendor.government}\n"
            f"Area: {vendor.area}\n"
            f"Address: {vendor.address}\n"
            f"Coordinates: {vendor.lattitude}, {vendor.longitude}\n"
            f"Description: {vendor.description}\n\n"
            f"Review Summary (max 150 words):\n"
            f"{review_summary}"
        )
        metadata = {
            "source_type": "vendor",
            "source_id": str(vendor.id),
            "name": vendor.name,
            "government": vendor.government,
            "area": vendor.area,
        }
        return document_text, metadata

    async def build_documents_from_maps_db(self, top_n_reviews: int = 3):
        documents = []
        async with self.db_client() as session:
            Plast_id = 20
            place_stmt = select(Place).options(joinedload(Place.reviews)).where(Place.id > Plast_id)
            place_result = await session.execute(place_stmt)
            places = place_result.scalars().unique().all()

            Vlast_id = 100

            vendor_stmt = select(VendorProfile).options(joinedload(VendorProfile.reviews)).where(VendorProfile.id > Vlast_id)

            vendor_result = await session.execute(vendor_stmt)
            vendors = vendor_result.scalars().unique().all() 

        for place in places:
            sorted_reviews = sorted(place.reviews or [], key=lambda review: review.rating or 0, reverse=True)[:top_n_reviews]
            place.reviews = sorted_reviews
            text, metadata = self._build_place_document(place)
            documents.append({"text": text, "metadata": metadata})

        for vendor in vendors:
            sorted_reviews = sorted(vendor.reviews or [], key=lambda review: review.rating or 0, reverse=True)[:top_n_reviews]
            vendor.reviews = sorted_reviews
            text, metadata = self._build_vendor_document(vendor)
            documents.append({"text": text, "metadata": metadata})

        return documents

    async def create_chunks_from_maps_db(
        self,
        project_id: int,
        chunk_size: int = 220,
        overlap_size: int = 30,
        top_n_reviews: int = 3,
        do_reset: bool = False,
    ) -> List[DataChunk]:
        project = await self.ensure_project(project_id=project_id)
        asset = await self.ensure_maps_asset(project=project)
        chunk_repo = await ChunkRepo.create_instance(self.db_client)

        if do_reset:
            await chunk_repo.delete_chunks_by_project_id(project_id=project.project_id)

        documents = await self.build_documents_from_maps_db(top_n_reviews=top_n_reviews)
        created_chunks: List[DataChunk] = []
        chunk_order = 0

        for document in documents:
            chunks = self._split_text_with_overlap(
                text=document["text"],
                chunk_size=chunk_size,
                overlap_size=overlap_size,
            )

            for chunk_index, chunk_text in enumerate(chunks):
                chunk = DataChunk(
                    chunk_text=chunk_text,
                    chunk_metadata={
                        **document["metadata"],
                        "chunk_index": chunk_index,
                        "chunk_count": len(chunks),
                    },
                    chunk_order=chunk_order,
                    chunk_project_id=project.project_id,
                    chunk_asset_id=asset.asset_id,
                )
                created_chunk = await chunk_repo.create_chunk(chunk)
                created_chunks.append(created_chunk)
                chunk_order += 1

        return created_chunks

    async def index_into_vector_db(self, project: Project, chunks: List[DataChunk], chunks_ids: List[int], do_reset: bool = False):
        collection_name = self.create_collection_name(project_id=project.project_id)
        texts = [chunk.chunk_text for chunk in chunks]
        metadatas = [chunk.chunk_metadata for chunk in chunks]
        vectors = await self.embedding_client.get_embeddings(texts=texts, document_type=DocumentTypeEnum.DOCUMENT.value)

        await self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        await self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadatas,
            vectors=vectors,
            record_ids=chunks_ids,
        )
        return True


    async def vectorize_project_data(self, project_id: int):
        project = await self.ensure_project(project_id=project_id)
        chunk_repo = await ChunkRepo.create_instance(self.db_client)
        chunks = await chunk_repo.get_poject_chunks(project_id=project.project_id,page_no=1,page_size=1000)
        if not chunks:
            return False

        collection_name = self.create_collection_name(project_id=project.project_id)
        texts = [chunk.chunk_text for chunk in chunks]
        metadatas = [chunk.chunk_metadata for chunk in chunks]
        vectors = await self.embedding_client.get_embeddings(texts=texts, document_type=DocumentTypeEnum.DOCUMENT.value)

        await self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=True,
        )

        await self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadatas,
            vectors=vectors,
            record_ids=[chunk.chunk_id for chunk in chunks],
        )
        return True

    async def build_and_index_maps_data(
        self,
        project_id: int,
        chunk_size: int = 520,
        overlap_size: int = 30,
        top_n_reviews: int = 3,
        do_reset: bool = False,
    ):
        project = await self.ensure_project(project_id=project_id)
        chunks = await self.create_chunks_from_maps_db(
            project_id=project_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
            top_n_reviews=top_n_reviews,
            do_reset=do_reset,
        )
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        return await self.index_into_vector_db(
            project=project,
            chunks=chunks,
            chunks_ids=chunk_ids,
            do_reset=do_reset,
        )

    async def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
        collection_name = self.create_collection_name(project_id=project.project_id)
        vectors = await self.embedding_client.get_embeddings(texts=[text], document_type=DocumentTypeEnum.QUERY.value)
        if not vectors:
            return False

        query_vector = vectors[0]
        if not query_vector:
            return False

        results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=query_vector,
            limit=limit,
        )
        if not results:
            return False
        return results

    async def answer_rag_question(self, project: Project, query: str, limit: int = 10):
        retrieved_documents = await self.search_vector_db_collection(project=project, text=query, limit=limit)
        if not retrieved_documents:
            return None, None, None

        system_prompt = self.template_parser.get("rag", "system_prompt")
        documents_prompts = []
        for idx, doc in enumerate(retrieved_documents):
            source_type, source_id, vendor_id = self._format_source_metadata(getattr(doc, "metadata", None))
            documents_prompts.append(
                self.template_parser.get(
                    "rag",
                    "document_prompt",
                    {
                        "doc_num": idx + 1,
                        "source_type": source_type,
                        "source_id": source_id,
                        "vendor_id": vendor_id,
                        "chunk_text": self.generation_client.process_text(doc.text),
                    },
                )
            )

        footer_prompt = self.template_parser.get("rag", "itinerary_footer_prompt", {"query": query})
        chat_history = [self.generation_client.construct_prompt(prompt=system_prompt, role="system")]
        full_prompt = "\n\n".join(["\n".join(documents_prompts), footer_prompt])
        answer = self.generation_client.generate_text(prompt=full_prompt, chat_history=chat_history)
        logger.info(f"FULL PROMPT SENT TO LLM: {full_prompt}")
        logger.info(f"RAG question answered for project_id={project.project_id}, query='{query}' -> answer='{answer}'")
        return answer, full_prompt, chat_history

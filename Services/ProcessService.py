from .BaseService import BaseService
from .ProjectService import ProjectService
import os
import json
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import JSONLoader
from fastapi import UploadFile
from typing import Any, Dict, List, Tuple



class ProcessService(BaseService):
    def __init__(self,project_id:str):
        super().__init__()
        self.project_id=project_id
        self.project_path=ProjectService().get_project_path(project_id)
    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]


    def get_file_loader(self, file_id: str):
        file_path = file_id if os.path.isabs(file_id) else os.path.join(self.project_path, file_id)
        file_extension = self.get_file_extension(file_id).lower()

        if file_extension == ".json":
            return JSONLoader(file_path=file_path, jq_schema=self._infer_json_jq_schema(file_path), text_content=False)
        if file_extension == ".pdf":
            return PyMuPDFLoader(file_path)
        if file_extension in [".txt", ".md", ".csv"]:
            return TextLoader(file_path, encoding="utf-8")

        return None


    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id)
        if loader:
            return loader.load()
             
        return None

    def process_file_content(self, file_content: list, file_id: str,
                                                         chunk_size: int=200, overlap_size: int=30):
            if not file_content:
                return [], []

            file_extension = self.get_file_extension(file_id).lower()

            if file_extension == ".json":
                return self._process_json_content(
                    file_content=file_content,
                    file_id=file_id,
                    chunk_size=chunk_size,
                    overlap_size=overlap_size,
                )

            texts: List[str] = []
            metadatas: List[dict] = []
            for doc_index, doc in enumerate(file_content):
                text = (getattr(doc, "page_content", "") or "").strip()
                if not text:
                    continue

                metadata = dict(getattr(doc, "metadata", {}) or {})
                metadata.update({
                    "source_file": file_id,
                    "source_type": "document",
                    "document_index": doc_index,
                })

                texts.append(text)
                metadatas.append(metadata)

            return self.process_simpler_splitter(
                texts=texts,
                metadatas=metadatas,
                chunk_size=chunk_size,
                overlap_size=overlap_size,
            )

    def process_simpler_splitter(
        self,
        texts: List[str],
        metadatas: List[dict],
        chunk_size: int,
        overlap_size: int = 30,
        splitter_tag: str = "\n",
    ) -> Tuple[List[str], List[dict]]:
        chunked_texts: List[str] = []
        chunked_metadatas: List[dict] = []

        for text_index, text in enumerate(texts):
            metadata = dict(metadatas[text_index] if text_index < len(metadatas) else {})
            text_chunks = self._split_text_with_overlap(
                text=text,
                chunk_size=chunk_size,
                overlap_size=overlap_size,
            )

            for chunk_index, chunk_text in enumerate(text_chunks):
                chunk_metadata = dict(metadata)
                chunk_metadata.update({
                    "chunk_index": chunk_index,
                    "chunk_count": len(text_chunks),
                    "splitter_tag": splitter_tag,
                })
                chunked_texts.append(chunk_text)
                chunked_metadatas.append(chunk_metadata)

        return chunked_texts, chunked_metadatas

    def _process_json_content(
        self,
        file_content: List[Any],
        file_id: str,
        chunk_size: int,
        overlap_size: int,
    ) -> Tuple[List[str], List[dict]]:
        texts: List[str] = []
        metadatas: List[dict] = []

        for doc_index, doc in enumerate(file_content):
            raw_payload = getattr(doc, "page_content", None)
            record = self._parse_json_payload(raw_payload)
            if not isinstance(record, dict):
                continue

            loader_metadata = dict(getattr(doc, "metadata", {}) or {})

            if self._is_place_record(record):
                place_id = str(record.get("id", f"place_{doc_index}"))
                place_name = str(record.get("name", "Unknown place"))
                place_text = (
                    f"Place: {place_name}. "
                    f"Place ID: {place_id}. "
                    f"Latitude: {record.get('lat')}. Longitude: {record.get('lng')}. "
                    f"Radius: {record.get('radius')} meters."
                )
                place_metadata = {
                    "source_file": file_id,
                    "source_type": "place",
                    "place_id": place_id,
                    "place_name": place_name,
                    "document_index": doc_index,
                    **loader_metadata,
                }
                texts.append(place_text)
                metadatas.append(place_metadata)
                continue

            if self._is_review_record(record):
                place_id = str(record.get("place_id", "unknown_place"))
                review_id = str(record.get("review_id") or record.get("id") or f"{place_id}_{doc_index}")
                review_text = str(record.get("content", "")).strip()
                if not review_text:
                    continue

                review_chunks = self._split_text_with_overlap(
                    text=review_text,
                    chunk_size=chunk_size,
                    overlap_size=overlap_size,
                )

                for review_chunk_index, review_chunk_text in enumerate(review_chunks):
                    review_metadata = {
                        "source_file": file_id,
                        "source_type": "review",
                        "place_id": place_id,
                        "review_id": review_id,
                        "review_chunk_index": review_chunk_index,
                        "review_chunk_count": len(review_chunks),
                        "author": record.get("author"),
                        "rating": record.get("rating"),
                        "document_index": doc_index,
                        **loader_metadata,
                    }
                    texts.append(review_chunk_text)
                    metadatas.append(review_metadata)
                continue

            generic_text = json.dumps(record, ensure_ascii=False)
            generic_chunks = self._split_text_with_overlap(
                text=generic_text,
                chunk_size=chunk_size,
                overlap_size=overlap_size,
            )
            for generic_chunk_index, generic_chunk_text in enumerate(generic_chunks):
                generic_metadata = {
                    "source_file": file_id,
                    "source_type": "json",
                    "document_index": doc_index,
                    "chunk_index": generic_chunk_index,
                    "chunk_count": len(generic_chunks),
                    **loader_metadata,
                }
                texts.append(generic_chunk_text)
                metadatas.append(generic_metadata)

        return texts, metadatas

    def _infer_json_jq_schema(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as json_file:
                payload = json.load(json_file)
        except Exception:
            return "."

        if isinstance(payload, dict):
            if isinstance(payload.get("places"), list):
                return ".places[]"
            if isinstance(payload.get("reviews"), list):
                return ".reviews[]"
        if isinstance(payload, list):
            return ".[]"

        return "."

    def _parse_json_payload(self, payload: Any) -> Any:
        if isinstance(payload, (dict, list)):
            return payload
        if not isinstance(payload, str):
            return None

        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return None

    def _is_place_record(self, record: Dict[str, Any]) -> bool:
        return "id" in record and "name" in record and "lat" in record and "lng" in record

    def _is_review_record(self, record: Dict[str, Any]) -> bool:
        return "content" in record and ("place_id" in record or "author" in record)

    def _split_text_with_overlap(self, text: str, chunk_size: int, overlap_size: int) -> List[str]:
        clean_text = text.strip()
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



        
from abc import ABC, abstractmethod
from typing import Any, List, Optional


class LLMInterface(ABC):
    def __init__(self, llm=None):
        self.llm = llm
        self.embedding_size = None

    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_size = embedding_size

    def set_emebedding_model(self, model_id: str, embedding_size: int):
        self.set_embedding_model(model_id=model_id, embedding_size=embedding_size)

    @abstractmethod
    def generate_text(self, prompt: str, chat_history: Optional[list] = None, max_output_tokens: int = 100, temperature: float = 0.7):
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str = None):
        pass

    async def get_embeddings(self, texts: List[str], document_type: str = None):
        if isinstance(texts, str):
            texts = [texts]

        vectors: List[Any] = []
        for text in texts:
            embedded = self.embed_text(text=text, document_type=document_type)
            if isinstance(embedded, list) and len(embedded) > 0:
                vectors.append(embedded[0])
            else:
                vectors.append(embedded)
        return vectors

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        pass

    def process_text(self, text: str):
        return text
    
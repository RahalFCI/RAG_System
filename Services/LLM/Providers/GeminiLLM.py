import logging
from typing import Any, List, Optional, Union

import httpx

from ..LLMEnums import OpenAIEnums
from ..LLMInterface import LLMInterface


class GeminiLLM(LLMInterface):
    def __init__(
        self,
        api_key: str,
        generation_model_id: str = "gemini-2.0-flash",
        embedding_model_id: str = "text-embedding-004",
        api_base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        default_input_max_characters: int = 1000,
        default_output_max_tokens: int = 1000,
        default_temperature: float = 0.1,
    ):
        super().__init__(llm=None)
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip("/")
        self.generation_model_id = generation_model_id
        self.embedding_model_id = embedding_model_id
        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature
        self.client = httpx.Client(timeout=60.0)
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        super().set_embedding_model(model_id=model_id, embedding_size=embedding_size)
        self.embedding_model_id = model_id

    def _auth_params(self):
        return {"key": self.api_key}

    def _chat_to_gemini_contents(self, chat_history: Optional[list], prompt: str):
        contents = []
        system_instruction = None

        for message in chat_history or []:
            role = message.get("role")
            content = message.get("content")
            if not content:
                continue
            if role == OpenAIEnums.SYSTEM.value:
                system_instruction = content
                continue
            contents.append({"role": role or OpenAIEnums.USER.value, "parts": [{"text": content}]})

        contents.append({"role": OpenAIEnums.USER.value, "parts": [{"text": prompt}]})
        return system_instruction, contents

    def generate_text(
        self,
        prompt: str,
        chat_history: Optional[list] = None,
        max_tokens: int = None,
        temperature: float = None,
    ):
        if not self.api_key:
            self.logger.error("Gemini API key is not configured.")
            return None

        max_tokens = max_tokens if max_tokens is not None else self.default_output_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature
        system_instruction, contents = self._chat_to_gemini_contents(chat_history, prompt)

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = f"{self.api_base_url}/models/{self.generation_model_id}:generateContent"
        try:
            response = self.client.post(url, params=self._auth_params(), json=payload)
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                self.logger.error("Gemini returned no candidates.")
                return None

            parts = candidates[0].get("content", {}).get("parts", [])
            text_parts = [part.get("text", "") for part in parts if isinstance(part, dict)]
            return "".join(text_parts).strip() if text_parts else None
        except Exception as exc:
            self.logger.error(f"Gemini text generation failed: {exc}")
            return None

    def embed_text(self, text: Union[str, List[str]], document_type: str = None):
        if not self.api_key:
            self.logger.error("Gemini API key is not configured.")
            return None

        if isinstance(text, str):
            texts = [text]
        else:
            texts = text

        vectors = []
        for item in texts:
            url = f"{self.api_base_url}/models/{self.embedding_model_id}:embedContent"
            payload = {"content": {"parts": [{"text": self.process_text(item)}]}}
            try:
                response = self.client.post(url, params=self._auth_params(), json=payload)
                response.raise_for_status()
                data = response.json()
                embedding = data.get("embedding", {}).get("values")
                if embedding is None:
                    self.logger.error("Gemini returned no embedding values.")
                    return None
                vectors.append(embedding)
            except Exception as exc:
                self.logger.error(f"Gemini embedding failed: {exc}")
                return None

        return vectors

    async def get_embeddings(self, texts: List[str], document_type: str = None):
        return self.embed_text(text=texts, document_type=document_type)

    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": prompt}

    def process_text(self, text: str):
        if text is None:
            return ""
        return str(text)[: self.default_input_max_characters].strip()
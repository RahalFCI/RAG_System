import logging
from typing import List,Union
from urllib import response

from openai import OpenAI
from ..LLMEnums import OpenAIEnums


from ..LLMInterfac import LLMInterface


class OpenAILLM(LLMInterface):
    def __init__(self, api_key, api_url, default_input_max_characters=1000, default_output_max_tokens=1000, default_temperature=0.1):
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None
        self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)
        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id:str):
        self.generation_model_id = model_id
    def set_embedding_model(self, model_id:str, embedding_size:int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def generate_text(self, prompt: str, chat_history: list=[], max_tokens: int = None, temperature: float = None) :
        if self.generation_model_id is None:
            self.logger.error("Generation model ID is not set. Please set it using set_generation_model() method.")
            return None
        if not self.client:
            self.logger.error("OpenAI client is not initialized.")
            return None
        max_tokens = max_tokens if max_tokens is not None else self.default_output_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature
        chat_history.append(self.construct_prompt(prompt,role=OpenAIEnums.USER.value)) 
        response = self.client.chat.completions.create(
            model = self.generation_model_id,
            messages = chat_history,
            max_tokens = max_tokens,
            temperature = temperature
        )
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("No response or choices received from OpenAI API.")
            return None
        return response.choices[0].message.content
    
    def embed_text(self, text:Union[str,List[str]] , document_type: str = None):
        if self.embedding_model_id is None:
            self.logger.error("Embedding model ID is not set. Please set it using set_embedding_model() method.")
            return None
        if not self.client:
            self.logger.error("OpenAI client is not initialized.")
            return None
        if isinstance(text, str):
            text = [text]
        response = self.client.embeddings.create(
            model = self.embedding_model_id,
            input = text,
        )
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("No response or data received from OpenAI API for embeddings.")
            return None
        return [rec.embedding for rec in response.data]
    








  
    def construct_prompt(self, prompt: str , role: str ):
            return {"role": role,
                   "content": prompt,
                        }


  
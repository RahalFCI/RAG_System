from abc import ABC, abstractmethod 

class LLMInterface(ABC):
    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    def set_generation_model(self, model_id:str):
        pass

    def set_emebedding_model(self, model_id:str,embedding_size:int):
        pass
    @abstractmethod
    def generate_text(self, prompt:str, chat_history:list=[], max_output_tokens:int=100, temperature:float=0.7):
        pass
    @abstractmethod
    def embed_text(self, text:str, document_type:str=None):
        pass
    @abstractmethod
    def construct_prompt(self, prompt:str, role:str):
        pass
    
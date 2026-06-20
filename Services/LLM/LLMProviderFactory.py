
from .LLMEnums import LLMEnums
from .Providers.OpenAILLM import OpenAILLM

class LLMProviderFactory:
    def __init__(self, config):
        self.config = config

    def create(self, provider: str):
        provider_upper = str(provider).upper() if provider else ""
        
        if provider_upper == LLMEnums.OPENAI.value:
            return OpenAILLM(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL or "https://api.openai.com/v1",
                default_input_max_characters=self.config.INPUT_DAFAULT_MAX_CHARACTERS or 1024,
                default_output_max_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS or 512,
                default_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE or 0.1
            )
        
        raise ValueError(f"Unsupported LLM provider: {provider}")

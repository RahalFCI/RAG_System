


class NLPController(BaseController):
    def __init__(self, ):
        super().__init__()
        self.nlp_service = nlp_service

    def process_text(self, text):
        # Process the text using the NLP service
        return self.nlp_service.analyze_text(text)
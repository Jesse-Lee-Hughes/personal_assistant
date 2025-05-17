from abc import ABC

import google.generativeai as genai

from .. import config


class BaseTool(ABC):
    def __init__(self, model_name: str = 'gemini-2.0-flash'):
        self.model_name = model_name
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(model_name=self.model_name)

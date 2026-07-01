from abc import ABC, abstractmethod
from typing import List, Optional
from models.config import TranslationSettings

class BaseTranslator(ABC):
    @abstractmethod
    async def translate_batch(self, texts: List[str], source_lang: str, target_lang: str, settings: TranslationSettings) -> List[str]:
        """Translates a batch of strings asynchronously."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Tests API key or connection."""
        pass

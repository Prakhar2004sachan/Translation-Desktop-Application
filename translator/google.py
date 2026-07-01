from typing import List
import asyncio
from deep_translator import GoogleTranslator
from translator.translator import BaseTranslator
from models.config import TranslationSettings

class GoogleTranslatorProvider(BaseTranslator):
    def __init__(self):
        pass
        
    async def translate_batch(self, texts: List[str], source_lang: str, target_lang: str, settings: TranslationSettings) -> List[str]:
        src = 'auto' if source_lang.lower() == 'auto detect' else source_lang.lower()
        
        lang_map = {
            'english': 'en', 'hindi': 'hi', 'japanese': 'ja', 'chinese': 'zh-CN',
            'korean': 'ko', 'russian': 'ru', 'spanish': 'es', 'german': 'de',
            'french': 'fr', 'italian': 'it', 'portuguese': 'pt'
        }
        dest = lang_map.get(target_lang.lower(), 'en')
        src_code = lang_map.get(src, 'auto') if src != 'auto' else 'auto'

        translator = GoogleTranslator(source=src_code, target=dest)

        results = []
        try:
            # We must run this in a thread since deep-translator is blocking
            loop = asyncio.get_event_loop()
            
            for text in texts:
                if not text.strip():
                    results.append(text)
                    continue
                
                temp_text = text
                if settings.translate_underscores:
                    temp_text = temp_text.replace('_', ' ')
                if settings.translate_hyphens:
                    temp_text = temp_text.replace('-', ' ')
                    
                # Run the blocking translation in an executor
                translated = await loop.run_in_executor(None, translator.translate, temp_text)
                
                if settings.keep_uppercase and text.isupper():
                    translated = translated.upper()
                
                results.append(translated)
        except Exception as e:
            print(f"Google translate error: {e}")
            while len(results) < len(texts):
                results.append(texts[len(results)])
                
        return results

    def test_connection(self) -> bool:
        try:
            res = GoogleTranslator(source='auto', target='es').translate("Hello")
            return True if res else False
        except Exception:
            return False

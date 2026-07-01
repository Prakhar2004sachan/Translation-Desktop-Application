import asyncio
import json
from typing import List
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

from translator.translator import BaseTranslator
from models.config import TranslationSettings

class GeminiTranslatorProvider(BaseTranslator):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def translate_batch(self, texts: List[str], source_lang: str, target_lang: str, settings: TranslationSettings) -> List[str]:
        if not self.api_key:
            print("Gemini API Key is missing! Returning original names.")
            return texts

        # Initialize the modern google-genai Client
        client = genai.Client(api_key=self.api_key)
        
        # Increase chunk size to 150 to minimize requests and prevent hitting quota limits (429)
        chunk_size = 150
        results = []
        loop = asyncio.get_event_loop()

        # Describe source language cleanly for Gemini
        src_desc = f"'{source_lang}'" if source_lang.lower() != "auto detect" else "their automatically detected languages"

        for i in range(0, len(texts), chunk_size):
            chunk = texts[i:i+chunk_size]
            
            # Prepare instructions
            prompt = (
                f"You are a professional filesystem localization utility. "
                f"Translate the following list of directory and file names from {src_desc} to '{target_lang}'.\n"
                f"Guidelines:\n"
                f"- Translate the base name accurately. For mixed CJK/English names (e.g. 'KK幼儿园'), translate the CJK parts to '{target_lang}' (e.g., 'KK Kindergarten').\n"
                f"- Do NOT translate or modify file extensions (e.g., keep '.srt', '.jpg', '.png' exactly as is at the end of the name).\n"
                f"- Keep numbers, dates, and special symbols intact.\n"
                f"- Return the output strictly as a JSON list of strings, in the exact same order as the input.\n\n"
                f"Input Names:\n{json.dumps(chunk, ensure_ascii=False)}"
            )

            max_retries = 5
            for attempt in range(max_retries):
                try:
                    def call_gemini():
                        # Call generate_content using the new google-genai client
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json"
                            )
                        )
                        return response.text

                    response_text = await loop.run_in_executor(None, call_gemini)
                    translated_chunk = json.loads(response_text)

                    if isinstance(translated_chunk, list) and len(translated_chunk) == len(chunk):
                        results.extend(translated_chunk)
                        break # Success, break retry loop!
                    else:
                        raise ValueError("Gemini returned an unexpected length or format.")
                except Exception as e:
                    # Check if it is a 429 rate limit error
                    is_rate_limit = False
                    if isinstance(e, ClientError) and e.code == 429:
                        is_rate_limit = True
                    
                    if is_rate_limit and attempt < max_retries - 1:
                        # Exponential backoff: 5s, 10s, 20s, 40s...
                        sleep_time = (2 ** attempt) * 5.0
                        print(f"Rate limit (429) hit. Retrying in {sleep_time} seconds... (Attempt {attempt+1}/{max_retries})")
                        await asyncio.sleep(sleep_time)
                    else:
                        # Raise if not a 429 or if we ran out of retries
                        error_msg = str(e)
                        if isinstance(e, APIError):
                            error_msg = f"{e.code} {e.message}"
                        raise RuntimeError(f"Gemini translation failed: {error_msg}") from e

        return results

    def test_connection(self) -> bool:
        if not self.api_key:
            return False
        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents="Say OK",
            )
            return "OK" in response.text or response.text is not None
        except Exception:
            return False

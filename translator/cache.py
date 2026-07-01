import sqlite3
from pathlib import Path

class TranslationCache:
    def __init__(self, db_path: str = "config/translation_cache.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                hash_key TEXT PRIMARY KEY,
                original TEXT,
                translated TEXT,
                source_lang TEXT,
                target_lang TEXT,
                provider TEXT
            )
        ''')
        self.conn.commit()

    def _generate_key(self, text: str, source_lang: str, target_lang: str, provider: str) -> str:
        import hashlib
        raw = f"{text}_{source_lang}_{target_lang}_{provider}"
        return hashlib.md5(raw.encode('utf-8')).hexdigest()

    def get(self, text: str, source_lang: str, target_lang: str, provider: str) -> str:
        key = self._generate_key(text, source_lang, target_lang, provider)
        cursor = self.conn.cursor()
        cursor.execute("SELECT translated FROM cache WHERE hash_key=?", (key,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None

    def set(self, text: str, translated: str, source_lang: str, target_lang: str, provider: str):
        key = self._generate_key(text, source_lang, target_lang, provider)
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO cache (hash_key, original, translated, source_lang, target_lang, provider)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (key, text, translated, source_lang, target_lang, provider))
        self.conn.commit()

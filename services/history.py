import sqlite3
from pathlib import Path
import json

class HistoryService:
    def __init__(self, db_path: str = "logs/history.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rename_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_items INTEGER,
                provider TEXT,
                source_lang TEXT,
                target_lang TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rename_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER,
                original_path TEXT,
                new_path TEXT,
                FOREIGN KEY(batch_id) REFERENCES rename_batches(id)
            )
        ''')
        self.conn.commit()

    def save_batch(self, provider: str, source_lang: str, target_lang: str, items: list):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO rename_batches (total_items, provider, source_lang, target_lang)
            VALUES (?, ?, ?, ?)
        ''', (len(items), provider, source_lang, target_lang))
        
        batch_id = cursor.lastrowid
        
        records = [
            (batch_id, str(item.original_path), str(item.new_path))
            for item in items if item.new_path
        ]
        
        cursor.executemany('''
            INSERT INTO rename_items (batch_id, original_path, new_path)
            VALUES (?, ?, ?)
        ''', records)
        
        self.conn.commit()

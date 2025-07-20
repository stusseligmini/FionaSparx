import sqlite3
import os
from datetime import datetime

class ContentDatabase:
    def __init__(self, db_path="data/content.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT,
                    image BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    published BOOLEAN DEFAULT 0
                )
            """)
            conn.commit()

    def save_content(self, text, image_bytes):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO content (text, image, published)
                VALUES (?, ?, 0)
            """, (text, image_bytes))
            conn.commit()

    def get_unpublis_

import sqlite3
import os
from typing import Optional, Dict

class CullingDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS culling_data (
                    photo_id TEXT PRIMARY KEY,
                    rating INTEGER,
                    is_picked INTEGER,
                    is_rejected INTEGER,
                    color_label TEXT
                );
            """)
            conn.commit()

    def save_culling_data(self, photo_id: str, rating: int, is_picked: bool, is_rejected: bool, color_label: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO culling_data 
                (photo_id, rating, is_picked, is_rejected, color_label)
                VALUES (?, ?, ?, ?, ?);
            """, (photo_id, rating, int(is_picked), int(is_rejected), color_label))
            conn.commit()

    def load_culling_data(self, photo_ids: list[str]) -> Dict[str, Dict]:
        culling_data = {}
        if not photo_ids:
            return culling_data

        placeholders = ', '.join('' for _ in photo_ids)
        query = f"SELECT photo_id, rating, is_picked, is_rejected, color_label FROM culling_data WHERE photo_id IN ({placeholders})"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, photo_ids)
            for row in cursor.fetchall():
                culling_data[row[0]] = {
                    "rating": row[1],
                    "is_picked": bool(row[2]),
                    "is_rejected": bool(row[3]),
                    "color_label": row[4]
                }
        return culling_data

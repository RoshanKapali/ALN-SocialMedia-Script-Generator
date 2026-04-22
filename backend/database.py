# database.py
# -----------
# Handles saving and fetching content generation history using SQLite.
# SQLite is a file-based database — no server needed, no setup required.
# The database file (history.db) is created automatically in the backend folder.

import sqlite3
import json
from datetime import datetime

# Path to the database file — will be created automatically if it doesn't exist
DB_PATH = "history.db"


def init_db():
    """
    Creates the history table if it does not already exist.
    Call this once when the FastAPI app starts.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            input_text TEXT NOT NULL,
            format_type TEXT NOT NULL,
            output_text TEXT NOT NULL,
            brand_score TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_to_history(input_text: str, format_type: str, output_text: str, brand_score: str = None):
    """
    Saves one generated output to the history table.

    Args:
        input_text: the original article or text the user submitted
        format_type: "newsletter", "linkedin", "twitter", or "tiktok"
        output_text: the AI-generated content
        brand_score: the brand check result string (optional)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO history (created_at, input_text, format_type, output_text, brand_score)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        input_text[:500],  # only save first 500 chars of input to save space
        format_type,
        output_text,
        brand_score
    ))

    conn.commit()
    conn.close()


def get_history(limit: int = 20) -> list[dict]:
    """
    Fetches the most recent generated outputs from history.
    Returns a list of dicts ordered by newest first.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # makes rows behave like dicts
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, created_at, format_type, input_text, output_text, brand_score
        FROM history
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def delete_history_item(item_id: int):
    """
    Deletes a single history item by its ID.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

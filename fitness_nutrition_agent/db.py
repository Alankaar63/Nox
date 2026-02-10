from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._init_tables()

    def _init_tables(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT,
                goal TEXT DEFAULT 'maintenance',
                daily_calorie_target INTEGER DEFAULT 2200
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                exercise TEXT NOT NULL,
                sets INTEGER,
                reps INTEGER,
                weight REAL,
                duration_min INTEGER,
                rpe REAL,
                notes TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                meal_name TEXT NOT NULL,
                description TEXT NOT NULL,
                estimated_calories REAL NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                strategy TEXT,
                reward REAL,
                feedback_notes TEXT
            )
            """
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO user_profile (id, name, goal, daily_calorie_target)
            VALUES (1, 'User', 'maintenance', 2200)
            """
        )
        self.conn.commit()

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self.conn.cursor()
            cur.execute(query, params)
            self.conn.commit()
            return cur

    def fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        with self._lock:
            cur = self.conn.cursor()
            cur.execute(query, params)
            return cur.fetchall()

    def fetchone(self, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
        with self._lock:
            cur = self.conn.cursor()
            cur.execute(query, params)
            return cur.fetchone()

    def close(self) -> None:
        with self._lock:
            self.conn.close()

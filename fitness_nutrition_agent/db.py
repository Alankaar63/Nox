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
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._lock = threading.Lock()
        self._init_tables()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------
    def _init_tables(self) -> None:
        cur = self.conn.cursor()

        # ---- User profile (expanded) ----
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT DEFAULT 'Athlete',
                goal TEXT DEFAULT 'maintenance',
                daily_calorie_target INTEGER DEFAULT 2200,
                height_cm REAL,
                weight_kg REAL,
                age INTEGER,
                gender TEXT DEFAULT 'male',
                activity_level TEXT DEFAULT 'moderate',
                dietary_preference TEXT DEFAULT 'non_vegetarian',
                training_level TEXT DEFAULT 'intermediate',
                active_split TEXT DEFAULT 'ppl',
                protein_target_g REAL,
                carbs_target_g REAL,
                fat_target_g REAL
            )
            """
        )

        # ---- Legacy workouts table (kept for migration) ----
        cur.execute(
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

        # ---- Workout sessions ----
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS workout_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                session_type TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                total_volume_kg REAL DEFAULT 0,
                total_sets INTEGER DEFAULT 0,
                notes TEXT,
                status TEXT DEFAULT 'active'
            )
            """
        )

        # ---- Individual exercise sets ----
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS exercise_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                set_number INTEGER NOT NULL,
                weight_kg REAL DEFAULT 0,
                reps INTEGER DEFAULT 0,
                rpe REAL,
                notes TEXT,
                timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES workout_sessions(id)
            )
            """
        )

        # ---- Lock-in schedule ----
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS lock_in_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scheduled_date TEXT NOT NULL,
                scheduled_time TEXT,
                session_type TEXT NOT NULL,
                duration_min INTEGER DEFAULT 60,
                recurring_pattern TEXT,
                status TEXT DEFAULT 'scheduled',
                skip_reason TEXT,
                notes TEXT,
                created_at TEXT
            )
            """
        )

        # ---- Food log (individual food entries with macros) ----
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS food_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                meal_label TEXT NOT NULL,
                food_name TEXT NOT NULL,
                quantity_g REAL NOT NULL,
                protein_g REAL DEFAULT 0,
                carbs_g REAL DEFAULT 0,
                fat_g REAL DEFAULT 0,
                calories REAL DEFAULT 0,
                logged_at TEXT
            )
            """
        )

        # ---- Legacy meals table (kept for migration) ----
        cur.execute(
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

        # ---- LLM interactions ----
        cur.execute(
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

        # ---- Default profile ----
        cur.execute(
            """
            INSERT OR IGNORE INTO user_profile (id, name, goal, daily_calorie_target)
            VALUES (1, 'Athlete', 'maintenance', 2200)
            """
        )

        # Ensure new columns exist on older databases
        self._add_column_if_missing(cur, "user_profile", "height_cm", "REAL")
        self._add_column_if_missing(cur, "user_profile", "weight_kg", "REAL")
        self._add_column_if_missing(cur, "user_profile", "age", "INTEGER")
        self._add_column_if_missing(cur, "user_profile", "gender", "TEXT DEFAULT 'male'")
        self._add_column_if_missing(cur, "user_profile", "activity_level", "TEXT DEFAULT 'moderate'")
        self._add_column_if_missing(cur, "user_profile", "dietary_preference", "TEXT DEFAULT 'non_vegetarian'")
        self._add_column_if_missing(cur, "user_profile", "training_level", "TEXT DEFAULT 'intermediate'")
        self._add_column_if_missing(cur, "user_profile", "active_split", "TEXT DEFAULT 'ppl'")
        self._add_column_if_missing(cur, "user_profile", "protein_target_g", "REAL")
        self._add_column_if_missing(cur, "user_profile", "carbs_target_g", "REAL")
        self._add_column_if_missing(cur, "user_profile", "fat_target_g", "REAL")

        self.conn.commit()

    @staticmethod
    def _add_column_if_missing(cur: sqlite3.Cursor, table: str, column: str, col_type: str) -> None:
        cols = {row[1] for row in cur.execute(f"PRAGMA table_info({table})").fetchall()}
        if column not in cols:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def execute(self, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self.conn.cursor()
            cur.execute(query, params)
            self.conn.commit()
            return cur

    def executemany(self, query: str, params_list: list[tuple[Any, ...]]) -> None:
        with self._lock:
            cur = self.conn.cursor()
            cur.executemany(query, params_list)
            self.conn.commit()

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

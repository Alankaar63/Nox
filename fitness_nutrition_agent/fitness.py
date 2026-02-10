from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from statistics import mean
from typing import Any

from .db import Database


class FitnessCoach:
    def __init__(self, db: Database) -> None:
        self.db = db

    def log_workout(
        self,
        workout_date: str,
        exercise: str,
        sets: int,
        reps: int,
        weight: float,
        duration_min: int,
        rpe: float,
        notes: str,
    ) -> None:
        self.db.execute(
            """
            INSERT INTO workouts (date, exercise, sets, reps, weight, duration_min, rpe, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (workout_date, exercise.lower().strip(), sets, reps, weight, duration_min, rpe, notes.strip()),
        )

    def recent_workouts(self, days: int = 14) -> list[dict[str, Any]]:
        since = (date.today() - timedelta(days=days)).isoformat()
        rows = self.db.fetchall(
            """
            SELECT date, exercise, sets, reps, weight, duration_min, rpe, notes
            FROM workouts
            WHERE date >= ?
            ORDER BY date DESC, id DESC
            """,
            (since,),
        )
        return [dict(r) for r in rows]

    def workout_streak(self) -> int:
        rows = self.db.fetchall("SELECT DISTINCT date FROM workouts ORDER BY date DESC")
        if not rows:
            return 0

        streak = 0
        current = date.today()
        logged_dates = {r["date"] for r in rows}

        if current.isoformat() not in logged_dates and (current - timedelta(days=1)).isoformat() in logged_dates:
            current = current - timedelta(days=1)

        while current.isoformat() in logged_dates:
            streak += 1
            current -= timedelta(days=1)
        return streak

    def _exercise_load_trends(self) -> dict[str, float]:
        rows = self.db.fetchall(
            """
            SELECT exercise, date, sets, reps, weight
            FROM workouts
            ORDER BY date DESC, id DESC
            """
        )
        per_exercise: dict[str, list[float]] = defaultdict(list)
        for r in rows:
            sets = r["sets"] or 0
            reps = r["reps"] or 0
            weight = r["weight"] or 0.0
            load = sets * reps * weight
            per_exercise[r["exercise"]].append(load)

        trend: dict[str, float] = {}
        for ex, loads in per_exercise.items():
            if len(loads) < 4:
                continue
            recent = mean(loads[:3])
            older = mean(loads[3:6]) if len(loads) >= 6 else mean(loads[3:])
            if older > 0:
                trend[ex] = ((recent - older) / older) * 100
        return trend

    def adaptive_routine(self) -> str:
        workouts = self.recent_workouts(days=14)
        if not workouts:
            return (
                "No workout history yet. Start with 3 full-body sessions/week: "
                "squat, push, pull, hinge, core (3 sets each, moderate effort)."
            )

        avg_rpe = mean([w["rpe"] for w in workouts if w["rpe"] is not None]) if workouts else 0
        trends = self._exercise_load_trends()
        positive = [ex for ex, t in trends.items() if t >= 3]
        flat_or_down = [ex for ex, t in trends.items() if t < 3]

        suggestions = []
        if avg_rpe >= 8.6:
            suggestions.append("Recovery signal is high. Run a deload for 5-7 days: reduce volume by ~20%.")
        elif positive:
            suggestions.append(
                "Progress is trending up. Add 2.5-5% load or 1 extra rep on: " + ", ".join(sorted(positive)[:4]) + "."
            )
        else:
            suggestions.append("Keep load steady and improve movement quality this week.")

        if flat_or_down:
            suggestions.append(
                "For plateaued lifts (" + ", ".join(sorted(flat_or_down)[:4]) + "), add one back-off set at lighter weight."
            )

        suggestions.append("Weekly split suggestion: 2 strength days, 1 hypertrophy day, 1 conditioning session.")
        return "\n".join(f"- {s}" for s in suggestions)

    def motivation_message(self) -> str:
        streak = self.workout_streak()
        trends = self._exercise_load_trends()
        improving = len([t for t in trends.values() if t > 0])

        if streak >= 10:
            return f"{streak}-day streak. Consistency is your superpower. Keep execution tight and recover hard."
        if streak >= 3:
            return f"{streak}-day streak active. You're building momentum; protect it with one solid session today."
        if improving >= 2:
            return "Your loads are trending upward on multiple exercises. Stay patient and let compounding work."
        return "Every rep logged is data and progress. Get one focused workout in today and reset momentum."

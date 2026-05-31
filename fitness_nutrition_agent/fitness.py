from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from statistics import mean
from typing import Any

from .db import Database
from .exercise_library import get_exercise_type, suggest_rest_seconds, suggest_weight_increment


class FitnessCoach:
    """Session-based workout tracking with progressive overload intelligence."""

    def __init__(self, db: Database) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------
    def start_session(self, session_type: str, notes: str = "") -> int:
        """Start a new workout session. Returns session_id."""
        now = datetime.now()
        cur = self.db.execute(
            """
            INSERT INTO workout_sessions (date, session_type, start_time, notes, status)
            VALUES (?, ?, ?, ?, 'active')
            """,
            (now.date().isoformat(), session_type.strip(), now.isoformat(), notes.strip()),
        )
        return int(cur.lastrowid)

    def log_set(
        self,
        session_id: int,
        exercise_name: str,
        set_number: int,
        weight_kg: float,
        reps: int,
        rpe: float | None = None,
        notes: str = "",
    ) -> dict[str, Any]:
        """Log a single set within a session. Returns comparison data."""
        now = datetime.now().isoformat()
        self.db.execute(
            """
            INSERT INTO exercise_sets (session_id, exercise_name, set_number, weight_kg, reps, rpe, notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, exercise_name.strip(), set_number, weight_kg, reps, rpe, notes.strip(), now),
        )

        # Update session totals
        volume = weight_kg * reps
        self.db.execute(
            "UPDATE workout_sessions SET total_volume_kg = total_volume_kg + ?, total_sets = total_sets + 1 WHERE id = ?",
            (volume, session_id),
        )

        # Compare to last session
        comparison = self._compare_to_last(exercise_name, set_number, weight_kg, reps)

        # Rest suggestion
        rest_secs, rest_reason = suggest_rest_seconds(exercise_name, reps)

        return {
            "logged": True,
            "exercise": exercise_name,
            "set": set_number,
            "weight_kg": weight_kg,
            "reps": reps,
            "volume": volume,
            "comparison": comparison,
            "rest_seconds": rest_secs,
            "rest_reason": rest_reason,
        }

    def end_session(self, session_id: int, notes: str = "") -> dict[str, Any]:
        """End a workout session and generate summary."""
        now = datetime.now()
        self.db.execute(
            "UPDATE workout_sessions SET end_time = ?, status = 'completed', notes = COALESCE(notes || ' ' || ?, notes) WHERE id = ?",
            (now.isoformat(), notes.strip(), session_id),
        )

        session = self.get_session_summary(session_id)
        prs = self._detect_prs(session_id)
        next_targets = self._next_session_targets(session_id)

        session["prs"] = prs
        session["next_targets"] = next_targets
        session["recovery_hours"] = 48

        return session

    def get_session_summary(self, session_id: int) -> dict[str, Any]:
        """Get structured summary for a session."""
        session_row = self.db.fetchone(
            "SELECT * FROM workout_sessions WHERE id = ?", (session_id,)
        )
        if not session_row:
            return {"error": "Session not found"}

        sets = self.db.fetchall(
            "SELECT * FROM exercise_sets WHERE session_id = ? ORDER BY exercise_name, set_number",
            (session_id,),
        )

        # Group sets by exercise
        exercises: dict[str, list[dict]] = defaultdict(list)
        for s in sets:
            exercises[s["exercise_name"]].append({
                "set": s["set_number"],
                "weight_kg": s["weight_kg"],
                "reps": s["reps"],
                "rpe": s["rpe"],
            })

        # Calculate duration
        duration_min = 0
        if session_row["start_time"] and session_row["end_time"]:
            try:
                start = datetime.fromisoformat(session_row["start_time"])
                end = datetime.fromisoformat(session_row["end_time"])
                duration_min = int((end - start).total_seconds() / 60)
            except (ValueError, TypeError):
                pass

        return {
            "session_id": session_id,
            "date": session_row["date"],
            "session_type": session_row["session_type"],
            "status": session_row["status"],
            "duration_min": duration_min,
            "total_volume_kg": session_row["total_volume_kg"] or 0,
            "total_sets": session_row["total_sets"] or 0,
            "exercises": dict(exercises),
            "notes": session_row["notes"] or "",
        }

    # ------------------------------------------------------------------
    # Progressive overload analysis
    # ------------------------------------------------------------------
    def _compare_to_last(self, exercise: str, set_number: int, weight: float, reps: int) -> dict[str, Any]:
        """Compare current set to the same set from the last session with this exercise."""
        row = self.db.fetchone(
            """
            SELECT es.weight_kg, es.reps
            FROM exercise_sets es
            JOIN workout_sessions ws ON es.session_id = ws.id
            WHERE es.exercise_name = ? AND es.set_number = ? AND ws.status = 'completed'
            ORDER BY ws.date DESC, es.id DESC
            LIMIT 1
            """,
            (exercise.strip(), set_number),
        )
        if not row:
            return {"has_previous": False, "message": "First time logging this exercise/set."}

        prev_weight = row["weight_kg"]
        prev_reps = row["reps"]
        weight_delta = weight - prev_weight
        rep_delta = reps - prev_reps

        # Check for significant drop
        prev_volume = prev_weight * prev_reps
        curr_volume = weight * reps
        volume_change_pct = ((curr_volume - prev_volume) / prev_volume * 100) if prev_volume > 0 else 0

        message = ""
        if volume_change_pct < -10:
            message = f"⚠️ Volume dropped {abs(volume_change_pct):.0f}% vs last session ({prev_weight}kg x {prev_reps}). Possible fatigue."
        elif weight_delta > 0:
            message = f"🔥 Weight up +{weight_delta:.1f}kg from last session!"
        elif rep_delta > 0:
            message = f"💪 Reps up +{rep_delta} from last session!"
        elif weight_delta == 0 and rep_delta == 0:
            message = f"Same as last session ({prev_weight}kg x {prev_reps}). Push for +1 rep or +2.5kg next time."
        else:
            message = f"Slight drop from last ({prev_weight}kg x {prev_reps}). Monitor recovery."

        return {
            "has_previous": True,
            "prev_weight_kg": prev_weight,
            "prev_reps": prev_reps,
            "weight_delta": weight_delta,
            "rep_delta": rep_delta,
            "volume_change_pct": round(volume_change_pct, 1),
            "message": message,
        }

    def _detect_prs(self, session_id: int) -> list[dict[str, Any]]:
        """Detect personal records hit in the current session."""
        sets = self.db.fetchall(
            "SELECT exercise_name, weight_kg, reps FROM exercise_sets WHERE session_id = ?",
            (session_id,),
        )
        prs = []
        for s in sets:
            # Check if this weight is the highest ever for this exercise
            best = self.db.fetchone(
                """
                SELECT MAX(weight_kg) as max_weight
                FROM exercise_sets es
                JOIN workout_sessions ws ON es.session_id = ws.id
                WHERE es.exercise_name = ? AND es.id NOT IN (
                    SELECT id FROM exercise_sets WHERE session_id = ?
                ) AND ws.status = 'completed'
                """,
                (s["exercise_name"], session_id),
            )
            if best and best["max_weight"] is not None:
                if s["weight_kg"] > best["max_weight"]:
                    prs.append({
                        "exercise": s["exercise_name"],
                        "weight_kg": s["weight_kg"],
                        "reps": s["reps"],
                        "prev_best_kg": best["max_weight"],
                        "improvement_kg": round(s["weight_kg"] - best["max_weight"], 1),
                    })
        # Deduplicate by exercise
        seen = set()
        unique_prs = []
        for pr in prs:
            if pr["exercise"] not in seen:
                seen.add(pr["exercise"])
                unique_prs.append(pr)
        return unique_prs

    def _next_session_targets(self, session_id: int) -> list[dict[str, Any]]:
        """Suggest weight targets for the next session based on this session's performance."""
        sets = self.db.fetchall(
            """
            SELECT exercise_name, set_number, weight_kg, reps, rpe
            FROM exercise_sets WHERE session_id = ?
            ORDER BY exercise_name, set_number
            """,
            (session_id,),
        )
        exercises: dict[str, list[dict]] = defaultdict(list)
        for s in sets:
            exercises[s["exercise_name"]].append(dict(s))

        targets = []
        for exercise, ex_sets in exercises.items():
            increment = suggest_weight_increment(exercise)
            # If all sets hit target reps (>= 8 for hypertrophy), suggest increase
            all_hit = all(s["reps"] >= 8 for s in ex_sets)
            avg_rpe = mean([s["rpe"] for s in ex_sets if s["rpe"]]) if any(s["rpe"] for s in ex_sets) else 7

            if all_hit and avg_rpe < 9:
                suggestion = f"Try {ex_sets[0]['weight_kg'] + increment:.1f}kg on sets 1-2"
                action = "increase"
            elif avg_rpe >= 9.5:
                suggestion = f"Keep {ex_sets[0]['weight_kg']:.1f}kg, focus on form and controlled reps"
                action = "maintain"
            else:
                suggestion = f"Keep {ex_sets[0]['weight_kg']:.1f}kg, aim for +1 rep per set"
                action = "maintain"

            targets.append({
                "exercise": exercise,
                "current_weight_kg": ex_sets[0]["weight_kg"],
                "suggestion": suggestion,
                "action": action,
            })

        return targets

    # ------------------------------------------------------------------
    # History & analytics
    # ------------------------------------------------------------------
    def session_history(self, days: int = 30, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent session summaries."""
        since = (date.today() - timedelta(days=days)).isoformat()
        rows = self.db.fetchall(
            """
            SELECT id, date, session_type, total_volume_kg, total_sets, status, start_time, end_time
            FROM workout_sessions
            WHERE date >= ? AND status = 'completed'
            ORDER BY date DESC, id DESC
            LIMIT ?
            """,
            (since, limit),
        )
        results = []
        for r in rows:
            duration = 0
            if r["start_time"] and r["end_time"]:
                try:
                    start = datetime.fromisoformat(r["start_time"])
                    end = datetime.fromisoformat(r["end_time"])
                    duration = int((end - start).total_seconds() / 60)
                except (ValueError, TypeError):
                    pass
            results.append({
                "session_id": r["id"],
                "date": r["date"],
                "session_type": r["session_type"],
                "total_volume_kg": r["total_volume_kg"] or 0,
                "total_sets": r["total_sets"] or 0,
                "duration_min": duration,
            })
        return results

    def volume_trend(self, exercise: str, weeks: int = 6) -> list[dict[str, Any]]:
        """Get weekly volume trend for an exercise."""
        since = (date.today() - timedelta(weeks=weeks)).isoformat()
        rows = self.db.fetchall(
            """
            SELECT ws.date, SUM(es.weight_kg * es.reps) as volume
            FROM exercise_sets es
            JOIN workout_sessions ws ON es.session_id = ws.id
            WHERE es.exercise_name = ? AND ws.date >= ? AND ws.status = 'completed'
            GROUP BY ws.date
            ORDER BY ws.date
            """,
            (exercise.strip(), since),
        )
        return [{"date": r["date"], "volume_kg": r["volume"] or 0} for r in rows]

    def exercise_history(self, exercise: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get historical performance for a specific exercise."""
        rows = self.db.fetchall(
            """
            SELECT ws.date, es.set_number, es.weight_kg, es.reps, es.rpe
            FROM exercise_sets es
            JOIN workout_sessions ws ON es.session_id = ws.id
            WHERE es.exercise_name = ? AND ws.status = 'completed'
            ORDER BY ws.date DESC, es.set_number
            LIMIT ?
            """,
            (exercise.strip(), limit * 5),
        )
        return [dict(r) for r in rows]

    def all_prs(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get all-time PRs for each exercise."""
        rows = self.db.fetchall(
            """
            SELECT exercise_name, MAX(weight_kg) as best_weight, reps
            FROM exercise_sets es
            JOIN workout_sessions ws ON es.session_id = ws.id
            WHERE ws.status = 'completed'
            GROUP BY exercise_name
            ORDER BY best_weight DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [{"exercise": r["exercise_name"], "weight_kg": r["best_weight"], "reps": r["reps"]} for r in rows]

    # ------------------------------------------------------------------
    # Legacy compatibility + streak
    # ------------------------------------------------------------------
    def workout_streak(self) -> int:
        """Calculate consecutive workout days."""
        rows = self.db.fetchall(
            """
            SELECT DISTINCT date FROM workout_sessions WHERE status = 'completed'
            UNION
            SELECT DISTINCT date FROM workouts
            ORDER BY date DESC
            """
        )
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

    def recent_workouts(self, days: int = 14) -> list[dict[str, Any]]:
        """Legacy: get recent workouts from old table."""
        since = (date.today() - timedelta(days=days)).isoformat()
        rows = self.db.fetchall(
            "SELECT date, exercise, sets, reps, weight, duration_min, rpe, notes FROM workouts WHERE date >= ? ORDER BY date DESC, id DESC",
            (since,),
        )
        return [dict(r) for r in rows]

    def log_workout(self, workout_date: str, exercise: str, sets: int, reps: int,
                    weight: float, duration_min: int, rpe: float, notes: str) -> None:
        """Legacy: log a workout to the old table."""
        self.db.execute(
            "INSERT INTO workouts (date, exercise, sets, reps, weight, duration_min, rpe, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (workout_date, exercise.lower().strip(), sets, reps, weight, duration_min, rpe, notes.strip()),
        )

    def motivation_message(self) -> str:
        streak = self.workout_streak()
        if streak >= 10:
            return f"🔥 {streak}-day streak. Consistency is your superpower. Keep execution tight and recover hard."
        if streak >= 3:
            return f"💪 {streak}-day streak active. You're building momentum — protect it with one solid session today."
        return "Every rep logged is data and progress. Get one focused workout in today and reset momentum."

    def adaptive_routine(self) -> str:
        """Generate adaptive training suggestions."""
        sessions = self.session_history(days=14)
        workouts = self.recent_workouts(days=14)

        if not sessions and not workouts:
            return "No workout history yet. Start with 3 full-body sessions/week: squat, push, pull, hinge, core (3 sets each, moderate effort)."

        suggestions = []
        if sessions:
            avg_volume = mean([s["total_volume_kg"] for s in sessions]) if sessions else 0
            suggestions.append(f"Average session volume: {avg_volume:,.0f} kg across {len(sessions)} sessions.")

        suggestions.append("Weekly split suggestion: Follow your active training split consistently for 4-6 weeks before evaluating changes.")
        return "\n".join(f"- {s}" for s in suggestions)

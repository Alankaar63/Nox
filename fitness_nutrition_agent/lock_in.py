from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta
from typing import Any

from .db import Database


class LockIn:
    """Great Lock In — focus-mode session scheduling with AI recommendations."""

    def __init__(self, db: Database) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def create(self, scheduled_date: str, scheduled_time: str, session_type: str,
               duration_min: int = 60, recurring_pattern: str | None = None,
               notes: str = "") -> int:
        """Create a new lock-in session. Returns lock_in_id."""
        cur = self.db.execute(
            """
            INSERT INTO lock_in_schedule
                (scheduled_date, scheduled_time, session_type, duration_min, recurring_pattern, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, 'scheduled', ?, ?)
            """,
            (scheduled_date, scheduled_time, session_type.strip(),
             duration_min, recurring_pattern, notes.strip(), datetime.now().isoformat()),
        )
        lock_in_id = int(cur.lastrowid)

        # Handle recurring pattern (e.g., "mon,wed,fri")
        if recurring_pattern:
            self._generate_recurring(lock_in_id, scheduled_time, session_type,
                                     duration_min, recurring_pattern, weeks=4)

        return lock_in_id

    def update(self, lock_in_id: int, **fields: Any) -> dict[str, Any]:
        """Update lock-in fields."""
        allowed = {"scheduled_date", "scheduled_time", "session_type", "duration_min", "notes", "status"}
        updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if not updates:
            return {"ok": False, "error": "No valid fields to update"}

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [lock_in_id]
        self.db.execute(
            f"UPDATE lock_in_schedule SET {set_clause} WHERE id = ?",
            tuple(values),
        )
        return {"ok": True, "updated": list(updates.keys())}

    def delete(self, lock_in_id: int, skip_reason: str = "") -> dict[str, Any]:
        """Delete/skip a lock-in with optional reason."""
        if skip_reason:
            self.db.execute(
                "UPDATE lock_in_schedule SET status = 'skipped', skip_reason = ? WHERE id = ?",
                (skip_reason.strip(), lock_in_id),
            )
        else:
            self.db.execute("DELETE FROM lock_in_schedule WHERE id = ?", (lock_in_id,))
        return {"ok": True}

    def complete(self, lock_in_id: int) -> dict[str, Any]:
        """Mark a lock-in as completed."""
        self.db.execute(
            "UPDATE lock_in_schedule SET status = 'completed' WHERE id = ?",
            (lock_in_id,),
        )
        return {"ok": True}

    # ------------------------------------------------------------------
    # Schedule queries
    # ------------------------------------------------------------------
    def get_schedule(self, week_offset: int = 0) -> list[dict[str, Any]]:
        """Get schedule for a specific week (0=this week, 1=next week, etc.)."""
        today = date.today()
        # Monday of target week
        monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        sunday = monday + timedelta(days=6)

        rows = self.db.fetchall(
            """
            SELECT * FROM lock_in_schedule
            WHERE scheduled_date BETWEEN ? AND ?
            ORDER BY scheduled_date, scheduled_time
            """,
            (monday.isoformat(), sunday.isoformat()),
        )
        return [dict(r) for r in rows]

    def get_today(self) -> list[dict[str, Any]]:
        """Get today's scheduled sessions."""
        today = date.today().isoformat()
        rows = self.db.fetchall(
            "SELECT * FROM lock_in_schedule WHERE scheduled_date = ? ORDER BY scheduled_time",
            (today,),
        )
        return [dict(r) for r in rows]

    def get_upcoming(self, days: int = 7) -> list[dict[str, Any]]:
        """Get upcoming scheduled sessions."""
        today = date.today()
        end = today + timedelta(days=days)
        rows = self.db.fetchall(
            """
            SELECT * FROM lock_in_schedule
            WHERE scheduled_date BETWEEN ? AND ? AND status = 'scheduled'
            ORDER BY scheduled_date, scheduled_time
            """,
            (today.isoformat(), end.isoformat()),
        )
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # AI Recommendations
    # ------------------------------------------------------------------
    def get_recommendations(self) -> list[dict[str, Any]]:
        """Generate AI-powered scheduling recommendations."""
        recommendations = []

        # 1. Best time-of-day analysis
        best_time = self._best_time_of_day()
        if best_time:
            recommendations.append(best_time)

        # 2. Recovery analysis
        recovery = self._recovery_analysis()
        if recovery:
            recommendations.append(recovery)

        # 3. Consistency analysis
        consistency = self._consistency_analysis()
        if consistency:
            recommendations.append(consistency)

        # If no data, give generic recommendation
        if not recommendations:
            recommendations.append({
                "type": "general",
                "confidence": 0.6,
                "suggestion": "Start with 3 sessions this week: Mon/Wed/Fri at a consistent time.",
                "reason": "No training history yet — building a consistent schedule is the first priority.",
            })

        return recommendations

    def _best_time_of_day(self) -> dict[str, Any] | None:
        """Analyze which time slots produce the best performance."""
        rows = self.db.fetchall(
            """
            SELECT start_time, total_volume_kg
            FROM workout_sessions
            WHERE status = 'completed' AND start_time IS NOT NULL
            ORDER BY date DESC
            LIMIT 30
            """
        )
        if len(rows) < 3:
            return None

        # Bucket by hour
        hour_volumes: dict[int, list[float]] = {}
        for r in rows:
            try:
                hour = datetime.fromisoformat(r["start_time"]).hour
                vol = r["total_volume_kg"] or 0
                hour_volumes.setdefault(hour, []).append(vol)
            except (ValueError, TypeError):
                continue

        if not hour_volumes:
            return None

        # Find best hour
        best_hour = max(hour_volumes, key=lambda h: sum(hour_volumes[h]) / len(hour_volumes[h]))
        avg_vol = sum(hour_volumes[best_hour]) / len(hour_volumes[best_hour])
        count = len(hour_volumes[best_hour])

        return {
            "type": "optimal_time",
            "confidence": min(0.95, 0.5 + count * 0.05),
            "suggestion": f"Your optimal training window is around {best_hour}:00-{best_hour+1}:00.",
            "reason": f"Based on {count} sessions, you average {avg_vol:,.0f}kg volume at this time — your highest.",
        }

    def _recovery_analysis(self) -> dict[str, Any] | None:
        """Analyze muscle group recovery based on last session."""
        last_session = self.db.fetchone(
            "SELECT id, date, session_type FROM workout_sessions WHERE status = 'completed' ORDER BY date DESC LIMIT 1"
        )
        if not last_session:
            return None

        last_date = date.fromisoformat(last_session["date"])
        days_since = (date.today() - last_date).days

        if days_since >= 2:
            return {
                "type": "recovery",
                "confidence": 0.85,
                "suggestion": f"You're {days_since} days since your last session ({last_session['session_type']}). Recovery is complete — lock in today.",
                "reason": f"48+ hours since last {last_session['session_type']} session. Muscles are recovered and ready.",
            }
        elif days_since == 1:
            return {
                "type": "recovery",
                "confidence": 0.7,
                "suggestion": f"Last session was yesterday ({last_session['session_type']}). Hit a different muscle group today.",
                "reason": "24-hour recovery window — avoid same muscle group to prevent overtraining.",
            }
        return None

    def _consistency_analysis(self) -> dict[str, Any] | None:
        """Analyze which days the user trains most consistently."""
        rows = self.db.fetchall(
            "SELECT date FROM workout_sessions WHERE status = 'completed' ORDER BY date DESC LIMIT 30"
        )
        if len(rows) < 5:
            return None

        # Count by day of week
        day_counts: Counter = Counter()
        for r in rows:
            try:
                d = date.fromisoformat(r["date"])
                day_counts[d.strftime("%A")] += 1
            except ValueError:
                continue

        if not day_counts:
            return None

        best_day, count = day_counts.most_common(1)[0]
        total = sum(day_counts.values())
        pct = round(count / total * 100)

        return {
            "type": "consistency",
            "confidence": min(0.9, 0.5 + count * 0.05),
            "suggestion": f"{best_day} is your most consistent training day ({pct}% of sessions).",
            "reason": f"You've completed {count} of your last {total} sessions on {best_day}s.",
        }

    # ------------------------------------------------------------------
    # Context for LLM
    # ------------------------------------------------------------------
    def get_lock_in_context(self) -> dict[str, Any]:
        """Get full lock-in context for LLM injection."""
        return {
            "this_week": self.get_schedule(0),
            "today": self.get_today(),
            "upcoming": self.get_upcoming(7),
            "recommendations": self.get_recommendations(),
        }

    # ------------------------------------------------------------------
    # Recurring generation
    # ------------------------------------------------------------------
    def _generate_recurring(self, parent_id: int, time: str, session_type: str,
                            duration: int, pattern: str, weeks: int = 4) -> None:
        """Generate recurring sessions from a pattern like 'mon,wed,fri'."""
        day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
        target_days = []
        for part in pattern.lower().split(","):
            part = part.strip()[:3]
            if part in day_map:
                target_days.append(day_map[part])

        if not target_days:
            return

        today = date.today()
        for week in range(weeks):
            for day_num in target_days:
                # Find next occurrence of this day
                days_ahead = day_num - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                target_date = today + timedelta(days=days_ahead + 7 * week)

                self.db.execute(
                    """
                    INSERT INTO lock_in_schedule
                        (scheduled_date, scheduled_time, session_type, duration_min, recurring_pattern, status, created_at)
                    VALUES (?, ?, ?, ?, ?, 'scheduled', ?)
                    """,
                    (target_date.isoformat(), time, session_type, duration, pattern, datetime.now().isoformat()),
                )

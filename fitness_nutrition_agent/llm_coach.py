from __future__ import annotations

import json
import math
import os
import random
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any

from .db import Database


class LLMCoach:
    """NOX AI Coach with rich context assembly and multi-provider support."""

    def __init__(self, db: Database) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Provider status
    # ------------------------------------------------------------------
    def status(self) -> dict[str, Any]:
        host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

        try:
            req = urllib.request.Request(f"{host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=4) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return {
                "enabled": False,
                "provider": "ollama",
                "model": model,
                "message": "Ollama not reachable. Start Ollama and run: ollama pull " + model,
            }

        installed = {m.get("name", "") for m in payload.get("models", []) if isinstance(m, dict)}
        if model not in installed:
            return {
                "enabled": False,
                "provider": "ollama",
                "model": model,
                "message": f"Model '{model}' not found. Run: ollama pull {model}",
            }

        return {"enabled": True, "provider": "ollama", "model": model, "message": "Configured"}

    # ------------------------------------------------------------------
    # NOX System Prompt
    # ------------------------------------------------------------------
    def _system_prompt(self, strategy: str) -> str:
        style_map = {
            "concise": "Keep responses compact and actionable. Short bullet points. Zero fluff.",
            "motivational": "Use an intense coaching tone. High conviction. Short, punchy sentences. Like a coach tapping you on the shoulder before you walk onto the field.",
            "analytical": "Use data-first explanation with reasoning from trends and specific metrics. Cite exact data points.",
        }
        return (
            "You are NOX — an elite AI fitness coach built for serious athletes. "
            "You combine the tactical intelligence of a data-driven strength coach, "
            "the nutritional precision of a sports dietitian, and the motivational energy of a world-class mentor.\n\n"
            "RULES:\n"
            "- Never fabricate data. If you don't have a data point, say so.\n"
            "- Every recommendation cites its source: 'Based on your last 4 sessions...' not 'You should probably...'\n"
            "- Always include a concrete, actionable next step.\n"
            "- Format for mobile: short paragraphs, bullet points, structured text.\n"
            "- When discussing training philosophy, reference specific coaches (Dorian Yates, Mike Mentzer, Arnold, etc.) and their principles.\n\n"
            f"Response style: {style_map.get(strategy, style_map['concise'])}"
        )

    # ------------------------------------------------------------------
    # Context Assembly
    # ------------------------------------------------------------------
    def _build_context(self) -> str:
        """Build rich context from all data sources for the LLM."""
        sections = []

        # 1. User Profile
        profile = self.db.fetchone("SELECT * FROM user_profile WHERE id = 1")
        if profile:
            sections.append(
                f"USER PROFILE:\n"
                f"  Name: {profile['name']}\n"
                f"  Goal: {profile['goal']}\n"
                f"  Training Level: {profile['training_level'] or 'intermediate'}\n"
                f"  Active Split: {profile['active_split'] or 'ppl'}\n"
                f"  Weight: {profile['weight_kg'] or 'not set'}kg\n"
                f"  Daily Calorie Target: {profile['daily_calorie_target']} kcal\n"
                f"  Macros: P:{profile['protein_target_g'] or '?'}g / C:{profile['carbs_target_g'] or '?'}g / F:{profile['fat_target_g'] or '?'}g"
            )

        # 2. Recent Sessions (last 5)
        sessions = self.db.fetchall(
            """
            SELECT date, session_type, total_volume_kg, total_sets
            FROM workout_sessions WHERE status = 'completed'
            ORDER BY date DESC LIMIT 5
            """
        )
        if sessions:
            lines = [f"  - {s['date']}: {s['session_type']} | {s['total_volume_kg']:,.0f}kg volume | {s['total_sets']} sets"
                     for s in sessions]
            sections.append("RECENT SESSIONS:\n" + "\n".join(lines))

        # 3. Today's Nutrition
        today = datetime.now().date().isoformat()
        nutrition = self.db.fetchone(
            """
            SELECT COALESCE(SUM(calories),0) AS cal, COALESCE(SUM(protein_g),0) AS p,
                   COALESCE(SUM(carbs_g),0) AS c, COALESCE(SUM(fat_g),0) AS f
            FROM food_log WHERE date = ?
            """,
            (today,),
        )
        if nutrition:
            target_cal = profile["daily_calorie_target"] if profile else 2200
            sections.append(
                f"TODAY'S NUTRITION ({today}):\n"
                f"  Logged: {nutrition['cal']:.0f} kcal | P:{nutrition['p']:.0f}g C:{nutrition['c']:.0f}g F:{nutrition['f']:.0f}g\n"
                f"  Target: {target_cal} kcal"
            )

        # 4. Upcoming Schedule
        schedule = self.db.fetchall(
            "SELECT scheduled_date, scheduled_time, session_type FROM lock_in_schedule WHERE status = 'scheduled' AND scheduled_date >= ? ORDER BY scheduled_date LIMIT 3",
            (today,),
        )
        if schedule:
            lines = [f"  - {s['scheduled_date']} {s['scheduled_time'] or ''}: {s['session_type']}" for s in schedule]
            sections.append("UPCOMING SCHEDULE:\n" + "\n".join(lines))

        # 5. Legacy workouts (fallback if no sessions)
        if not sessions:
            workouts = self.db.fetchall(
                "SELECT date, exercise, sets, reps, weight, rpe FROM workouts ORDER BY date DESC, id DESC LIMIT 6"
            )
            if workouts:
                lines = [f"  - {w['date']}: {w['exercise']} {w['sets']}x{w['reps']} @ {w['weight']}kg (RPE {w['rpe']})"
                         for w in workouts]
                sections.append("RECENT WORKOUTS:\n" + "\n".join(lines))

        # 6. Legacy meals (fallback)
        meals = self.db.fetchall(
            "SELECT date, meal_name, estimated_calories, description FROM meals ORDER BY date DESC, id DESC LIMIT 4"
        )
        if meals:
            lines = [f"  - {m['date']}: {m['meal_name']} {m['estimated_calories']:.0f} kcal ({m['description'][:60]})"
                     for m in meals]
            sections.append("RECENT MEALS:\n" + "\n".join(lines))

        return "\n\n".join(sections) if sections else "No user data available yet."

    # ------------------------------------------------------------------
    # Strategy selection (UCB1)
    # ------------------------------------------------------------------
    def _strategy_scores(self) -> dict[str, float]:
        strategies = ["concise", "motivational", "analytical"]
        rows = self.db.fetchall(
            """
            SELECT strategy, AVG(COALESCE(reward, 0)) AS avg_reward, COUNT(reward) AS reward_count
            FROM llm_interactions WHERE strategy IS NOT NULL GROUP BY strategy
            """
        )
        stats = {s: {"avg": 0.0, "n": 0} for s in strategies}
        total = 0
        for r in rows:
            s = r["strategy"]
            if s in stats:
                stats[s]["avg"] = float(r["avg_reward"] or 0.0)
                stats[s]["n"] = int(r["reward_count"] or 0)
                total += int(r["reward_count"] or 0)

        scores: dict[str, float] = {}
        for s in strategies:
            avg = stats[s]["avg"]
            n = stats[s]["n"]
            bonus = math.sqrt(2 * math.log(total + 1) / (n + 1))
            scores[s] = avg + bonus
        return scores

    def _select_strategy(self) -> str:
        if random.random() < 0.18:
            return random.choice(["concise", "motivational", "analytical"])
        scores = self._strategy_scores()
        return max(scores.items(), key=lambda x: x[1])[0]

    # ------------------------------------------------------------------
    # LLM Call
    # ------------------------------------------------------------------
    def _call_ollama(self, user_message: str, strategy: str) -> tuple[str, dict[str, Any]]:
        host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        context = self._build_context()
        system = self._system_prompt(strategy)

        prompt = f"Current user data context:\n{context}\n\nUser message:\n{user_message}"

        body = {
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "options": {"temperature": 0.7},
        }

        req = urllib.request.Request(
            f"{host}/api/chat",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else str(e)
            raise RuntimeError(f"Ollama API error: {detail[:400]}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Ollama connection error: {e}") from e

        msg = payload.get("message", {}) if isinstance(payload, dict) else {}
        text = msg.get("content", "") if isinstance(msg, dict) else ""
        text = text.strip() if isinstance(text, str) else ""
        if not text:
            raise RuntimeError("Ollama returned empty output.")

        return text, payload

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def chat(self, user_message: str) -> dict[str, Any]:
        strategy = self._select_strategy()
        response_text, raw = self._call_ollama(user_message, strategy)

        cur = self.db.execute(
            """
            INSERT INTO llm_interactions (created_at, user_message, assistant_response, strategy, reward, feedback_notes)
            VALUES (?, ?, ?, ?, NULL, NULL)
            """,
            (datetime.utcnow().isoformat(), user_message.strip(), response_text, strategy),
        )

        interaction_id = int(cur.lastrowid)
        return {
            "interaction_id": interaction_id,
            "response": response_text,
            "strategy": strategy,
            "provider": "ollama",
            "model": raw.get("model", os.getenv("OLLAMA_MODEL", "llama3.1:8b")),
        }

    def feedback(self, interaction_id: int, reward: float, notes: str = "") -> dict[str, Any]:
        clipped = max(-1.0, min(1.0, float(reward)))
        self.db.execute(
            "UPDATE llm_interactions SET reward = ?, feedback_notes = ? WHERE id = ?",
            (clipped, notes.strip(), interaction_id),
        )
        return {"ok": True, "reward": clipped}

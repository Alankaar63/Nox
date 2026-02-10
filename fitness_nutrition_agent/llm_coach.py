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
    def __init__(self, db: Database) -> None:
        self.db = db

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
                "message": "Ollama not reachable. Start Ollama and run: ollama pull llama3.1:8b",
            }

        installed = {m.get("name", "") for m in payload.get("models", []) if isinstance(m, dict)}
        if model not in installed:
            return {
                "enabled": False,
                "provider": "ollama",
                "model": model,
                "message": f"Model '{model}' not found. Run: ollama pull {model}",
            }

        return {
            "enabled": True,
            "provider": "ollama",
            "model": model,
            "message": "Configured",
        }

    def _recent_context(self) -> str:
        profile = self.db.fetchone("SELECT name, goal, daily_calorie_target FROM user_profile WHERE id = 1")
        workouts = self.db.fetchall(
            """
            SELECT date, exercise, sets, reps, weight, duration_min, rpe
            FROM workouts
            ORDER BY date DESC, id DESC
            LIMIT 6
            """
        )
        meals = self.db.fetchall(
            """
            SELECT date, meal_name, estimated_calories, description
            FROM meals
            ORDER BY date DESC, id DESC
            LIMIT 6
            """
        )
        today = datetime.now().date().isoformat()
        total_today = self.db.fetchone(
            "SELECT COALESCE(SUM(estimated_calories),0) AS total FROM meals WHERE date = ?",
            (today,),
        )

        workout_lines = [
            f"- {w['date']}: {w['exercise']} {w['sets']}x{w['reps']} @ {w['weight']} (rpe {w['rpe']})"
            for w in workouts
        ]
        meal_lines = [
            f"- {m['date']}: {m['meal_name']} {m['estimated_calories']:.0f} kcal ({m['description']})"
            for m in meals
        ]

        return (
            f"User: {profile['name']}\n"
            f"Goal: {profile['goal']}\n"
            f"Daily calorie target: {profile['daily_calorie_target']}\n"
            f"Calories today: {float(total_today['total']) if total_today else 0:.0f}\n"
            f"Recent workouts:\n" + ("\n".join(workout_lines) if workout_lines else "- none") + "\n"
            f"Recent meals:\n" + ("\n".join(meal_lines) if meal_lines else "- none")
        )

    def _strategy_scores(self) -> dict[str, float]:
        strategies = ["concise", "motivational", "analytical"]
        rows = self.db.fetchall(
            """
            SELECT strategy, AVG(COALESCE(reward, 0)) AS avg_reward, COUNT(reward) AS reward_count
            FROM llm_interactions
            WHERE strategy IS NOT NULL
            GROUP BY strategy
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

    def _system_prompt(self, strategy: str) -> str:
        style_map = {
            "concise": "Keep responses compact and actionable. Use short bullet points.",
            "motivational": "Use an energetic coaching tone with strong encouragement and clear next action.",
            "analytical": "Use data-first explanation with reasoning from trends and specific metrics.",
        }
        return (
            "You are NOX, a fitness coach and nutrition assistant. "
            "Give practical and safe guidance. Avoid medical diagnosis. "
            "Always include a short actionable plan for next 24 hours. "
            f"Response style: {style_map.get(strategy, style_map['concise'])}"
        )

    def _call_ollama(self, user_message: str, strategy: str) -> tuple[str, dict[str, Any]]:
        host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        context = self._recent_context()
        system = self._system_prompt(strategy)

        prompt = (
            "Current user data context:\n"
            f"{context}\n\n"
            "User message:\n"
            f"{user_message}"
        )

        body = {
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "options": {
                "temperature": 0.7,
            },
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

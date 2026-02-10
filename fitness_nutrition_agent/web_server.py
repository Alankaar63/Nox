from __future__ import annotations

import argparse
import json
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .agent import FitnessNutritionAgent


class AgentWebHandler(SimpleHTTPRequestHandler):
    server_version = "FitnessNutritionAgent/1.0"

    def __init__(self, *args, directory: str | None = None, agent: FitnessNutritionAgent | None = None, **kwargs):
        self.agent = agent
        super().__init__(*args, directory=directory, **kwargs)

    def _send_json(self, payload: dict | list, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/dashboard":
            profile = self.agent.get_profile()
            today = __import__("datetime").date.today().isoformat()
            calories_today = self.agent.nutrition.daily_calories(today)
            payload = {
                "date": today,
                "profile": profile,
                "calories_today": calories_today,
                "workout_streak": self.agent.fitness.workout_streak(),
                "motivation": self.agent.fitness.motivation_message(),
            }
            self._send_json(payload)
            return

        if path == "/api/profile":
            self._send_json(self.agent.get_profile())
            return

        if path == "/api/workouts":
            days = int(query.get("days", ["30"])[0])
            self._send_json({"workouts": self.agent.fitness.recent_workouts(days)})
            return

        if path == "/api/adaptive-plan":
            self._send_json({"plan": self.agent.fitness.adaptive_routine()})
            return

        if path == "/api/meals":
            self._send_json({"meals": self.agent.nutrition.meal_history(40)})
            return

        if path == "/api/calorie-summary":
            day = query.get("date", [None])[0]
            total = self.agent.nutrition.daily_calories(day)
            target = self.agent.get_profile()["daily_calorie_target"]
            delta = total - float(target)
            self._send_json(
                {
                    "date": day or __import__("datetime").date.today().isoformat(),
                    "total": total,
                    "target": target,
                    "delta": delta,
                }
            )
            return

        if path == "/api/recipes":
            profile_goal = str(self.agent.get_profile()["goal"])
            goal = query.get("goal", [profile_goal])[0]
            meal_type = query.get("meal_type", [None])[0]
            raw_max = query.get("max_calories", [None])[0]
            max_calories = int(raw_max) if raw_max else None
            recipes = self.agent.nutrition.recipe_suggestions(goal, max_calories, meal_type)
            self._send_json({"recipes": recipes[:8]})
            return

        if path == "/api/coach/status":
            self._send_json(self.agent.coach.status())
            return

        super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        try:
            data = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON body."}, status=HTTPStatus.BAD_REQUEST)
            return

        if path == "/api/profile":
            goal = str(data.get("goal", "maintenance"))
            daily_target = data.get("daily_calorie_target")
            if daily_target is not None:
                daily_target = int(daily_target)
            self.agent.set_profile_goal(goal, daily_target)
            self._send_json({"ok": True, "profile": self.agent.get_profile()})
            return

        if path == "/api/workouts":
            workout_date = str(data.get("date") or __import__("datetime").date.today().isoformat())
            self.agent.fitness.log_workout(
                workout_date=workout_date,
                exercise=str(data.get("exercise", "")),
                sets=int(data.get("sets", 0)),
                reps=int(data.get("reps", 0)),
                weight=float(data.get("weight", 0.0)),
                duration_min=int(data.get("duration_min", 0)),
                rpe=float(data.get("rpe", 7.0)),
                notes=str(data.get("notes", "")),
            )
            self._send_json(
                {
                    "ok": True,
                    "motivation": self.agent.fitness.motivation_message(),
                    "workouts": self.agent.fitness.recent_workouts(30),
                }
            )
            return

        if path == "/api/meals":
            meal_name = str(data.get("meal_name", "meal"))
            description = str(data.get("description", ""))
            meal_date = str(data.get("date") or __import__("datetime").date.today().isoformat())
            calories, details = self.agent.nutrition.log_meal(meal_name, description, meal_date)
            self._send_json(
                {
                    "ok": True,
                    "estimated_calories": calories,
                    "details": details,
                    "meals": self.agent.nutrition.meal_history(40),
                }
            )
            return

        if path == "/api/coach/chat":
            user_message = str(data.get("message", "")).strip()
            if not user_message:
                self._send_json({"error": "message is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.agent.coach.chat(user_message)
            except RuntimeError as e:
                self._send_json({"error": str(e)}, status=HTTPStatus.BAD_GATEWAY)
                return
            self._send_json({"ok": True, **result})
            return

        if path == "/api/coach/feedback":
            try:
                interaction_id = int(data.get("interaction_id"))
                reward = float(data.get("reward"))
            except (TypeError, ValueError):
                self._send_json({"error": "interaction_id (int) and reward (number) are required"}, status=HTTPStatus.BAD_REQUEST)
                return
            notes = str(data.get("notes", ""))
            result = self.agent.coach.feedback(interaction_id, reward, notes)
            self._send_json(result)
            return

        self._send_json({"error": "Endpoint not found."}, status=HTTPStatus.NOT_FOUND)


def run_web(host: str = "127.0.0.1", port: int = 8080) -> None:
    root = Path(__file__).resolve().parent
    web_dir = root / "web"
    agent = FitnessNutritionAgent(root)

    def handler(*args, **kwargs):
        return AgentWebHandler(*args, directory=str(web_dir), agent=agent, **kwargs)

    server = ThreadingHTTPServer((host, port), handler)
    print(f"Web app running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        agent.close()
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run local Fitness Nutrition web app.")
    parser.add_argument(
        "--host",
        default=os.getenv("HOST", "127.0.0.1"),
        help="Host interface to bind (default: HOST env or 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8080")),
        help="Port to bind (default: PORT env or 8080)",
    )
    args = parser.parse_args()
    run_web(host=args.host, port=args.port)

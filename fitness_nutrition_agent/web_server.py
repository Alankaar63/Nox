from __future__ import annotations

import argparse
import json
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .architecture import architecture_status

WEB_ROOT = Path(__file__).parent / "web"


class WebServer(BaseHTTPRequestHandler):
    agent: Any = None

    def _set_headers(self, status: int = 200, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        self._set_headers(200, "text/plain")

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def _send_json(self, data: Any, status: int = 200) -> None:
        self._set_headers(status)
        self.wfile.write(json.dumps(data).encode("utf-8"))

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------
    def do_GET(self) -> None:
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if not self.agent:
            self._send_json({"error": "Agent not initialized"}, 500)
            return

        try:
            # 1. Profile
            if path == "/api/architecture/status":
                self._send_json(architecture_status())

            elif path == "/api/dashboard":
                profile = self.agent.db.fetchone("SELECT * FROM user_profile WHERE id = 1")
                calories = self.agent.nutrition.daily_calories(date.today().isoformat())
                completed = self.agent.db.fetchall(
                    "SELECT DISTINCT date FROM workout_sessions WHERE status = 'completed' ORDER BY date DESC LIMIT 14"
                )
                self._send_json({
                    "date": date.today().isoformat(),
                    "profile": dict(profile) if profile else {},
                    "calories_today": calories,
                    "workout_streak": len(completed),
                    "motivation": "NOX is tracking lock-ins, training load, nutrition and knowledge retrieval.",
                })

            elif path == "/api/workouts":
                rows = self.agent.db.fetchall(
                    "SELECT * FROM workouts ORDER BY date DESC, id DESC LIMIT 30"
                )
                self._send_json({"workouts": [dict(r) for r in rows]})

            elif path == "/api/meals":
                rows = self.agent.db.fetchall(
                    "SELECT * FROM meals ORDER BY date DESC, id DESC LIMIT 30"
                )
                self._send_json({"meals": [dict(r) for r in rows]})

            elif path == "/api/adaptive-plan":
                recs = self.agent.lock_in.get_recommendations()
                plan = " | ".join(r["suggestion"] for r in recs[:3])
                self._send_json({"plan": plan})

            elif path == "/api/recipes":
                profile = self.agent.db.fetchone("SELECT * FROM user_profile WHERE id = 1")
                goal = query.get("goal", [profile["goal"] if profile else "maintenance"])[0]
                meal_type = query.get("meal_type", [None])[0] or None
                max_calories_raw = query.get("max_calories", [None])[0]
                max_calories = int(max_calories_raw) if max_calories_raw else None
                self._send_json({
                    "recipes": self.agent.nutrition.recipe_suggestions(goal, max_calories, meal_type)
                })

            elif path == "/api/profile":
                profile = self.agent.db.fetchone("SELECT * FROM user_profile WHERE id = 1")
                self._send_json(dict(profile) if profile else {})

            # 2. Nutrition
            elif path == "/api/nutrition/summary":
                day = query.get("date", [date.today().isoformat()])[0]
                self._send_json(self.agent.nutrition.daily_macro_summary(day))

            elif path == "/api/nutrition/log":
                day = query.get("date", [date.today().isoformat()])[0]
                self._send_json(self.agent.nutrition.food_log_today(day))

            elif path == "/api/nutrition/search":
                q = query.get("q", [""])[0]
                pref = query.get("preference", [None])[0]
                self._send_json(self.agent.nutrition.search_food(q, pref))

            elif path == "/api/nutrition/chart":
                goal = query.get("goal", ["maintenance"])[0]
                pref = query.get("preference", ["non_vegetarian"])[0]
                self._send_json(self.agent.nutrition.generate_diet_chart(goal=goal, preference=pref))

            elif path == "/api/nutrition/alert":
                day = query.get("date", [date.today().isoformat()])[0]
                self._send_json(self.agent.nutrition.protein_deficit_alert(day) or {"status": "ok"})

            # 3. Lock-In Schedule
            elif path == "/api/schedule":
                self._send_json(self.agent.lock_in.get_schedule())

            elif path == "/api/schedule/upcoming":
                self._send_json(self.agent.lock_in.get_upcoming(7))

            elif path == "/api/schedule/recommendations":
                self._send_json(self.agent.lock_in.get_recommendations())

            # 4. Fitness & Splits
            elif path == "/api/fitness/splits":
                from .splits import list_splits
                self._send_json(list_splits())

            elif path == "/api/fitness/split":
                key = query.get("key", [""])[0]
                from .splits import get_split
                split = get_split(key)
                if split:
                    self._send_json(split)
                else:
                    self._send_json({"error": "Split not found"}, 404)

            elif path == "/api/fitness/history":
                self._send_json(self.agent.fitness.session_history())

            elif path == "/api/fitness/prs":
                self._send_json(self.agent.fitness.all_prs())

            elif path == "/api/fitness/exercise":
                name = query.get("name", [""])[0]
                self._send_json(self.agent.fitness.exercise_history(name))

            # 5. Knowledge Vault
            elif path == "/api/knowledge":
                q = query.get("q", [""])[0]
                coach = query.get("coach", [None])[0]
                self._send_json(self.agent.knowledge.query(q, coach_filter=coach))

            # 6. Static files
            elif path == "/" or path == "/index.html":
                self._serve_file("index.html", "text/html")
            elif path == "/app.js":
                self._serve_file("app.js", "application/javascript")
            elif path == "/styles.css":
                self._serve_file("styles.css", "text/css")
            elif path.startswith("/assets/"):
                self._serve_file(path.lstrip("/"), self._content_type(path))
            elif path.startswith("/downloads/"):
                self._serve_file(path.lstrip("/"), "application/vnd.android.package-archive")
            else:
                self._send_json({"error": "Not Found"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def do_POST(self) -> None:
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if not self.agent:
            self._send_json({"error": "Agent not initialized"}, 500)
            return

        try:
            body = self._read_json()

            # 1. Chat
            if path == "/api/chat":
                msg = body.get("message", "")
                res = self.agent.chat(msg)
                self._send_json(res)

            elif path == "/api/chat/feedback":
                interaction_id = body.get("interaction_id")
                reward = body.get("reward")
                notes = body.get("notes", "")
                if interaction_id is None or reward is None:
                    self._send_json({"error": "Missing parameters"}, 400)
                    return
                self._send_json(self.agent.coach.feedback(interaction_id, float(reward), notes))

            # 2. Nutrition Logging
            elif path == "/api/nutrition/log":
                food = body.get("food")
                qty = body.get("quantity_g")
                label = body.get("meal_label", "meal")
                if not food or not qty:
                    self._send_json({"error": "Missing food or quantity"}, 400)
                    return
                res = self.agent.nutrition.log_food(food, float(qty), label)
                self._send_json(res)

            elif path == "/api/nutrition/log_text":
                text = body.get("text", "")
                name = body.get("name", "Meal")
                cals, details = self.agent.nutrition.log_meal_description(name, text)
                self._send_json({"logged_calories": cals, "details": details})

            # 3. Lock-In Schedule
            elif path == "/api/schedule":
                scheduled_date = body.get("scheduled_date")
                scheduled_time = body.get("scheduled_time")
                type_ = body.get("session_type")
                if not scheduled_date or not type_:
                    self._send_json({"error": "Missing date or type"}, 400)
                    return
                lock_id = self.agent.lock_in.create(
                    scheduled_date, scheduled_time, type_,
                    body.get("duration_min", 60),
                    body.get("recurring_pattern"),
                    body.get("notes", "")
                )
                self._send_json({"lock_in_id": lock_id})

            # 4. Fitness Sessions
            elif path == "/api/fitness/session/start":
                type_ = body.get("session_type")
                notes = body.get("notes", "")
                if not type_:
                    self._send_json({"error": "Missing session_type"}, 400)
                    return
                sid = self.agent.fitness.start_session(type_, notes)
                self._send_json({"session_id": sid})

            elif path == "/api/fitness/session/end":
                sid = body.get("session_id")
                notes = body.get("notes", "")
                if not sid:
                    self._send_json({"error": "Missing session_id"}, 400)
                    return
                res = self.agent.fitness.end_session(sid, notes)
                self._send_json(res)

            elif path == "/api/fitness/set":
                sid = body.get("session_id")
                ex = body.get("exercise_name")
                s_num = body.get("set_number")
                w = body.get("weight_kg")
                r = body.get("reps")
                if not all(v is not None for v in (sid, ex, s_num, w, r)):
                    self._send_json({"error": "Missing required fields"}, 400)
                    return
                res = self.agent.fitness.log_set(
                    sid, ex, s_num, float(w), int(r), body.get("rpe"), body.get("notes", "")
                )
                self._send_json(res)

            elif path == "/api/workouts":
                self.agent.db.execute(
                    """
                    INSERT INTO workouts
                        (date, exercise, sets, reps, weight, duration_min, rpe, notes, user_name, provider)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        body.get("date") or date.today().isoformat(),
                        body.get("exercise", "Training"),
                        int(body.get("sets", 0) or 0),
                        int(body.get("reps", 0) or 0),
                        float(body.get("weight", 0) or 0),
                        int(body.get("duration_min", 0) or 0),
                        float(body.get("rpe", 7) or 7),
                        body.get("notes", ""),
                        body.get("user_name") or "Athlete",
                        body.get("provider") or "guest",
                    ),
                )
                self._send_json({"ok": True})

            elif path == "/api/meals":
                cals, details = self.agent.nutrition.log_meal_description(
                    body.get("meal_name", "meal"),
                    body.get("description", ""),
                    body.get("date") or date.today().isoformat(),
                )
                self.agent.db.execute(
                    """
                    UPDATE meals
                    SET user_name = ?, provider = ?
                    WHERE id = (SELECT MAX(id) FROM meals)
                    """,
                    (body.get("user_name") or "Athlete", body.get("provider") or "guest"),
                )
                self._send_json({"ok": True, "estimated_calories": cals, "details": details})

            # 5. Profile Update
            elif path == "/api/profile":
                # Filter out None and keys that aren't allowed
                allowed = {"name", "goal", "daily_calorie_target", "height_cm", "weight_kg",
                           "age", "gender", "activity_level", "dietary_preference",
                           "training_level", "active_split", "protein_target_g",
                           "carbs_target_g", "fat_target_g"}
                updates = {k: v for k, v in body.items() if k in allowed and v is not None}
                if updates:
                    set_clause = ", ".join(f"{k} = ?" for k in updates)
                    values = list(updates.values())
                    self.agent.db.execute(f"UPDATE user_profile SET {set_clause} WHERE id = 1", tuple(values))
                self._send_json({"ok": True, "updated": list(updates.keys())})

            else:
                self._send_json({"error": "Not Found"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _serve_file(self, filepath: str, content_type: str) -> None:
        path = WEB_ROOT / filepath
        if not path.exists():
            self.send_response(404)
            self.end_headers()
            return

        self._set_headers(200, content_type)
        with path.open("rb") as f:
            self.wfile.write(f.read())

    @staticmethod
    def _content_type(path: str) -> str:
        if path.endswith(".jpg") or path.endswith(".jpeg"):
            return "image/jpeg"
        if path.endswith(".png"):
            return "image/png"
        if path.endswith(".svg"):
            return "image/svg+xml"
        if path.endswith(".css"):
            return "text/css"
        if path.endswith(".js"):
            return "application/javascript"
        return "application/octet-stream"


def run_server(agent: Any, host: str = "127.0.0.1", port: int = 8080) -> None:
    WebServer.agent = agent
    server = HTTPServer((host, port), WebServer)
    print(f"NOX Server running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="NOX web backend")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    from .agent import FitnessAgent

    base_dir = Path(__file__).parent.parent
    agent = FitnessAgent(
        db_path=base_dir / "agent_data.sqlite3",
        data_dir=base_dir / "fitness_nutrition_agent" / "data",
    )
    run_server(agent, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

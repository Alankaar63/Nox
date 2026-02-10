from __future__ import annotations

from datetime import date
from pathlib import Path

from .db import Database
from .fitness import FitnessCoach
from .llm_coach import LLMCoach
from .nutrition import NutritionAssistant


class FitnessNutritionAgent:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.db = Database(root / "agent_data.sqlite3")
        self.fitness = FitnessCoach(self.db)
        self.nutrition = NutritionAssistant(self.db, root / "data" / "recipes.json")
        self.coach = LLMCoach(self.db)

    def close(self) -> None:
        self.db.close()

    def get_profile(self) -> dict[str, str | int]:
        row = self.db.fetchone("SELECT name, goal, daily_calorie_target FROM user_profile WHERE id = 1")
        return {
            "name": row["name"],
            "goal": row["goal"],
            "daily_calorie_target": row["daily_calorie_target"],
        }

    def set_profile_goal(self, goal: str, daily_target: int | None = None) -> None:
        goal = goal.lower().strip()
        if goal not in {"fat_loss", "maintenance", "muscle_gain"}:
            goal = "maintenance"

        if daily_target is None:
            defaults = {"fat_loss": 1800, "maintenance": 2200, "muscle_gain": 2800}
            daily_target = defaults[goal]

        self.db.execute(
            "UPDATE user_profile SET goal = ?, daily_calorie_target = ? WHERE id = 1",
            (goal, daily_target),
        )

    def dashboard(self) -> str:
        profile = self.get_profile()
        today = date.today().isoformat()
        cals_today = self.nutrition.daily_calories(today)
        streak = self.fitness.workout_streak()
        motivation = self.fitness.motivation_message()

        return (
            f"Date: {today}\n"
            f"Goal: {profile['goal']}\n"
            f"Daily calorie target: {profile['daily_calorie_target']} kcal\n"
            f"Calories logged today: {cals_today:.0f} kcal\n"
            f"Workout streak: {streak} day(s)\n"
            f"Motivation: {motivation}"
        )

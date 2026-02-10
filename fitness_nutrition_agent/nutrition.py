from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from .db import Database
from .foods import FOOD_CALORIES_PER_100G, UNIT_TO_GRAMS


class NutritionAssistant:
    ITEM_RE = re.compile(
        r"^\s*(?:(?P<qty>\d+(?:\.\d+)?)\s*)?(?:(?P<unit>g|gram|grams|kg|ml|cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons|scoop|scoops|slice|slices|egg|eggs|banana|bananas|apple|apples)\s+)?(?P<food>[a-zA-Z ]+)\s*$"
    )

    def __init__(self, db: Database, recipe_path: Path) -> None:
        self.db = db
        self.recipes = self._load_recipes(recipe_path)

    def _load_recipes(self, recipe_path: Path) -> list[dict[str, Any]]:
        with recipe_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _normalize_food_name(food: str) -> str:
        food = food.lower().strip()
        aliases = {
            "rice": "rice cooked",
            "brown rice": "brown rice cooked",
            "lentils": "lentils cooked",
            "chickpeas": "chickpeas cooked",
            "yogurt": "greek yogurt",
            "chicken": "chicken breast",
            "eggs": "egg",
        }
        normalized = aliases.get(food, food)
        if normalized not in FOOD_CALORIES_PER_100G and normalized.endswith("s"):
            singular = normalized[:-1]
            if singular in FOOD_CALORIES_PER_100G:
                return singular
        return normalized

    def estimate_calories(self, description: str) -> tuple[float, list[str]]:
        total = 0.0
        details: list[str] = []

        for raw_item in [p.strip() for p in description.split(",") if p.strip()]:
            match = self.ITEM_RE.match(raw_item)
            if not match:
                details.append(f"Skipped '{raw_item}' (format not recognized)")
                continue

            qty = float(match.group("qty") or 1)
            raw_unit = match.group("unit")
            unit = raw_unit.lower() if raw_unit else ""
            food_name = self._normalize_food_name(match.group("food"))

            if food_name not in FOOD_CALORIES_PER_100G:
                details.append(f"Skipped '{raw_item}' (food not in local database)")
                continue

            if not unit:
                # If user enters "1 banana" or "2 eggs", infer typical unit weight.
                if food_name in UNIT_TO_GRAMS:
                    grams = qty * UNIT_TO_GRAMS[food_name]
                else:
                    grams = qty
            elif unit in {"gram", "grams", "g", "ml"}:
                grams = qty
            elif unit == "kg":
                grams = qty * 1000
            else:
                grams = qty * UNIT_TO_GRAMS.get(unit, 100)

            cals = (grams / 100.0) * FOOD_CALORIES_PER_100G[food_name]
            total += cals
            details.append(f"{raw_item} -> {cals:.0f} kcal")

        return round(total, 1), details

    def log_meal(self, meal_name: str, description: str, meal_date: str | None = None) -> tuple[float, list[str]]:
        target_date = meal_date or date.today().isoformat()
        calories, details = self.estimate_calories(description)
        self.db.execute(
            """
            INSERT INTO meals (date, meal_name, description, estimated_calories)
            VALUES (?, ?, ?, ?)
            """,
            (target_date, meal_name.strip(), description.strip(), calories),
        )
        return calories, details

    def daily_calories(self, day: str | None = None) -> float:
        target_day = day or date.today().isoformat()
        row = self.db.fetchone(
            "SELECT COALESCE(SUM(estimated_calories), 0) AS total FROM meals WHERE date = ?",
            (target_day,),
        )
        return float(row["total"]) if row else 0.0

    def meal_history(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.db.fetchall(
            """
            SELECT date, meal_name, description, estimated_calories
            FROM meals
            ORDER BY date DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(r) for r in rows]

    def recipe_suggestions(
        self,
        goal: str,
        max_calories: int | None = None,
        meal_type: str | None = None,
    ) -> list[dict[str, Any]]:
        goal = goal.lower().strip()
        valid_goal = goal if goal in {"fat_loss", "maintenance", "muscle_gain"} else "maintenance"

        matches = []
        for recipe in self.recipes:
            if valid_goal not in recipe.get("goal_tags", []):
                continue
            if meal_type and recipe.get("meal_type", "").lower() != meal_type.lower():
                continue
            if max_calories and recipe.get("calories", 0) > max_calories:
                continue
            matches.append(recipe)

        return sorted(matches, key=lambda x: x.get("protein_g", 0), reverse=True)

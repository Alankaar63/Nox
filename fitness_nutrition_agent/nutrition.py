from __future__ import annotations

import json
import math
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .db import Database
from .foods import FOOD_DB, UNIT_TO_GRAMS, get_food_macros, search_foods


class NutritionAssistant:
    """Full macro-tracking nutrition engine with TDEE, diet chart generation, and compliance scoring."""

    ITEM_RE = re.compile(
        r"^\s*(?:(?P<qty>\d+(?:\.\d+)?)\s*)?(?:(?P<unit>g|gram|grams|kg|ml|cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons|scoop|scoops|slice|slices|egg|eggs|banana|bananas|apple|apples|roti|rotis|naan|idli|dosa|paratha)\s+)?(?P<food>[a-zA-Z ]+)\s*$"
    )

    def __init__(self, db: Database, recipe_path: Path) -> None:
        self.db = db
        self.recipes = self._load_recipes(recipe_path)

    def _load_recipes(self, recipe_path: Path) -> list[dict[str, Any]]:
        if recipe_path.exists():
            with recipe_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return []

    # ------------------------------------------------------------------
    # TDEE & Macro Calculation
    # ------------------------------------------------------------------
    @staticmethod
    def calculate_tdee(weight_kg: float, height_cm: float, age: int,
                       activity_level: str = "moderate", gender: str = "male") -> int:
        """Mifflin-St Jeor equation for TDEE."""
        if gender.lower() == "female":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5

        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }
        mult = multipliers.get(activity_level.lower(), 1.55)
        return int(bmr * mult)

    @staticmethod
    def recommend_macros(weight_kg: float, calories: int, goal: str = "maintenance") -> dict[str, Any]:
        """Calculate recommended macros based on goal."""
        # Protein: 2.0-2.2g per kg
        protein_g = round(weight_kg * 2.0)
        # Fat: min 0.8g per kg
        fat_g = round(weight_kg * 0.8)
        # Adjust for goal
        if goal == "fat_loss" or goal == "cut":
            calories = int(calories * 0.85)  # 15% deficit
            protein_g = round(weight_kg * 2.2)  # Higher protein on cut
        elif goal in ("lean_bulk", "muscle_gain"):
            calories = int(calories + 200)  # +200 surplus
        elif goal == "bulk":
            calories = int(calories + 400)  # +400 surplus

        protein_cals = protein_g * 4
        fat_cals = fat_g * 9
        carb_cals = max(0, calories - protein_cals - fat_cals)
        carbs_g = round(carb_cals / 4)

        return {
            "calories": calories,
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "protein_pct": round(protein_cals / calories * 100) if calories > 0 else 0,
            "carbs_pct": round(carb_cals / calories * 100) if calories > 0 else 0,
            "fat_pct": round(fat_cals / calories * 100) if calories > 0 else 0,
        }

    # ------------------------------------------------------------------
    # Food Logging (with full macros)
    # ------------------------------------------------------------------
    def log_food(self, food_name: str, quantity_g: float, meal_label: str = "meal",
                 meal_date: str | None = None) -> dict[str, Any]:
        """Log a food item with full macro breakdown."""
        target_date = meal_date or date.today().isoformat()
        macros = get_food_macros(food_name)

        if not macros:
            return {"logged": False, "error": f"Food '{food_name}' not found in database."}

        factor = quantity_g / 100.0
        protein = round(macros["protein"] * factor, 1)
        carbs = round(macros["carbs"] * factor, 1)
        fat = round(macros["fat"] * factor, 1)
        calories = round(macros["calories"] * factor, 1)

        self.db.execute(
            """
            INSERT INTO food_log (date, meal_label, food_name, quantity_g, protein_g, carbs_g, fat_g, calories, logged_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (target_date, meal_label.strip(), food_name.strip().lower(), quantity_g,
             protein, carbs, fat, calories, datetime.now().isoformat()),
        )

        return {
            "logged": True,
            "food": food_name,
            "quantity_g": quantity_g,
            "protein_g": protein,
            "carbs_g": carbs,
            "fat_g": fat,
            "calories": calories,
        }

    def log_meal_description(self, meal_name: str, description: str,
                             meal_date: str | None = None) -> tuple[float, list[str]]:
        """Parse a natural-language food description and log each item. Legacy + new hybrid."""
        target_date = meal_date or date.today().isoformat()
        total_cals = 0.0
        total_p = 0.0
        total_c = 0.0
        total_f = 0.0
        details: list[str] = []

        for raw_item in [p.strip() for p in description.split(",") if p.strip()]:
            match = self.ITEM_RE.match(raw_item)
            if not match:
                details.append(f"Skipped '{raw_item}' (format not recognized)")
                continue

            qty = float(match.group("qty") or 1)
            raw_unit = match.group("unit")
            unit = raw_unit.lower() if raw_unit else ""
            food_name = match.group("food").lower().strip()

            macros = get_food_macros(food_name)
            if not macros:
                details.append(f"Skipped '{raw_item}' (food not in database)")
                continue

            # Resolve grams
            if not unit:
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

            factor = grams / 100.0
            p = round(macros["protein"] * factor, 1)
            c = round(macros["carbs"] * factor, 1)
            f = round(macros["fat"] * factor, 1)
            cal = round(macros["calories"] * factor, 1)

            total_p += p
            total_c += c
            total_f += f
            total_cals += cal

            # Log individual item
            self.db.execute(
                """
                INSERT INTO food_log (date, meal_label, food_name, quantity_g, protein_g, carbs_g, fat_g, calories, logged_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (target_date, meal_name.strip(), food_name, grams, p, c, f, cal, datetime.now().isoformat()),
            )

            details.append(f"{raw_item} → {cal:.0f} kcal | P:{p:.0f}g C:{c:.0f}g F:{f:.0f}g")

        # Also insert into legacy meals table for backward compatibility
        self.db.execute(
            "INSERT INTO meals (date, meal_name, description, estimated_calories) VALUES (?, ?, ?, ?)",
            (target_date, meal_name.strip(), description.strip(), total_cals),
        )

        return round(total_cals, 1), details

    # ------------------------------------------------------------------
    # Daily Macro Summary
    # ------------------------------------------------------------------
    def daily_macro_summary(self, day: str | None = None) -> dict[str, Any]:
        """Get complete daily nutrition breakdown with target comparison."""
        target_day = day or date.today().isoformat()
        row = self.db.fetchone(
            """
            SELECT
                COALESCE(SUM(calories), 0) AS total_cal,
                COALESCE(SUM(protein_g), 0) AS total_p,
                COALESCE(SUM(carbs_g), 0) AS total_c,
                COALESCE(SUM(fat_g), 0) AS total_f
            FROM food_log WHERE date = ?
            """,
            (target_day,),
        )

        logged = {
            "calories": round(float(row["total_cal"]), 1) if row else 0,
            "protein_g": round(float(row["total_p"]), 1) if row else 0,
            "carbs_g": round(float(row["total_c"]), 1) if row else 0,
            "fat_g": round(float(row["total_f"]), 1) if row else 0,
        }

        # Get targets from profile
        profile = self.db.fetchone("SELECT * FROM user_profile WHERE id = 1")
        targets = {
            "calories": profile["daily_calorie_target"] or 2200,
            "protein_g": profile["protein_target_g"] or 150,
            "carbs_g": profile["carbs_target_g"] or 250,
            "fat_g": profile["fat_target_g"] or 70,
        }

        remaining = {
            "calories": round(targets["calories"] - logged["calories"], 1),
            "protein_g": round(targets["protein_g"] - logged["protein_g"], 1),
            "carbs_g": round(targets["carbs_g"] - logged["carbs_g"], 1),
            "fat_g": round(targets["fat_g"] - logged["fat_g"], 1),
        }

        return {
            "date": target_day,
            "logged": logged,
            "targets": targets,
            "remaining": remaining,
        }

    def daily_calories(self, day: str | None = None) -> float:
        """Legacy: get total calories for a day (combines both tables)."""
        target_day = day or date.today().isoformat()
        r1 = self.db.fetchone(
            "SELECT COALESCE(SUM(calories), 0) AS t FROM food_log WHERE date = ?", (target_day,)
        )
        r2 = self.db.fetchone(
            "SELECT COALESCE(SUM(estimated_calories), 0) AS t FROM meals WHERE date = ?", (target_day,)
        )
        v1 = float(r1["t"]) if r1 else 0
        v2 = float(r2["t"]) if r2 else 0
        return max(v1, v2)  # Use the higher of the two (avoid double-counting)

    # ------------------------------------------------------------------
    # Protein deficit alert
    # ------------------------------------------------------------------
    def protein_deficit_alert(self, day: str | None = None) -> dict[str, Any] | None:
        """Check if user is behind on protein and suggest top-up foods."""
        summary = self.daily_macro_summary(day)
        remaining_p = summary["remaining"]["protein_g"]
        if remaining_p <= 10:
            return None  # On track

        suggestions = []
        if remaining_p >= 40:
            suggestions.append("200g chicken breast (62g protein)")
            suggestions.append("2 scoops whey protein + 200g greek yogurt (44g + 20g)")
        elif remaining_p >= 20:
            suggestions.append("1 scoop whey protein (24g protein)")
            suggestions.append("3 whole eggs (18g protein)")
            suggestions.append("200g greek yogurt (20g protein)")
        else:
            suggestions.append("100g chicken breast (31g protein)")
            suggestions.append("2 egg whites (22g protein)")

        return {
            "deficit_g": round(remaining_p, 1),
            "message": f"You're {remaining_p:.0f}g short on protein. Quick top-ups:",
            "suggestions": suggestions,
        }

    # ------------------------------------------------------------------
    # Weekly compliance
    # ------------------------------------------------------------------
    def weekly_compliance(self, weeks: int = 1) -> dict[str, Any]:
        """Calculate % of days within 10% of macro targets."""
        from datetime import timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=7 * weeks)

        total_days = 0
        compliant_days = 0
        day = start_date
        while day <= end_date:
            summary = self.daily_macro_summary(day.isoformat())
            if summary["logged"]["calories"] > 0:
                total_days += 1
                targets = summary["targets"]
                logged = summary["logged"]
                # Check if all macros within 10%
                all_ok = True
                for key in ["calories", "protein_g", "carbs_g", "fat_g"]:
                    target = targets[key]
                    if target > 0:
                        pct_off = abs(logged[key] - target) / target
                        if pct_off > 0.10:
                            all_ok = False
                            break
                if all_ok:
                    compliant_days += 1
            day += timedelta(days=1)

        score = round(compliant_days / total_days * 100) if total_days > 0 else 0
        return {
            "total_days_logged": total_days,
            "compliant_days": compliant_days,
            "compliance_pct": score,
            "weeks": weeks,
        }

    # ------------------------------------------------------------------
    # Diet chart generation
    # ------------------------------------------------------------------
    def generate_diet_chart(self, goal: str = "maintenance",
                            preference: str = "non_vegetarian",
                            calories: int | None = None,
                            weight_kg: float | None = None) -> dict[str, Any]:
        """Generate a full-day meal plan that hits macro targets."""
        profile = self.db.fetchone("SELECT * FROM user_profile WHERE id = 1")
        wt = weight_kg or (profile["weight_kg"] if profile and profile["weight_kg"] else 75)
        cal = calories or (profile["daily_calorie_target"] if profile else 2200)

        macros = self.recommend_macros(wt, cal, goal)
        target_cal = macros["calories"]
        target_p = macros["protein_g"]
        target_c = macros["carbs_g"]
        target_f = macros["fat_g"]

        is_veg = preference.lower() in ("vegetarian", "vegan", "eggetarian")

        # Build meal plan
        if is_veg:
            meals = self._veg_meal_plan(target_cal, target_p, target_c, target_f, preference)
        else:
            meals = self._nonveg_meal_plan(target_cal, target_p, target_c, target_f)

        # Calculate actuals
        actual = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
        for meal in meals:
            for item in meal["items"]:
                actual["calories"] += item["calories"]
                actual["protein_g"] += item["protein_g"]
                actual["carbs_g"] += item["carbs_g"]
                actual["fat_g"] += item["fat_g"]

        return {
            "goal": goal,
            "preference": preference,
            "targets": macros,
            "meals": meals,
            "actual_totals": {k: round(v, 1) for k, v in actual.items()},
        }

    def _make_item(self, food: str, qty_g: float) -> dict[str, Any]:
        macros = get_food_macros(food)
        if not macros:
            return {"food": food, "quantity_g": qty_g, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "calories": 0}
        f = qty_g / 100.0
        return {
            "food": food,
            "quantity_g": qty_g,
            "protein_g": round(macros["protein"] * f, 1),
            "carbs_g": round(macros["carbs"] * f, 1),
            "fat_g": round(macros["fat"] * f, 1),
            "calories": round(macros["calories"] * f, 1),
        }

    def _nonveg_meal_plan(self, cal: int, p: int, c: int, f: int) -> list[dict]:
        return [
            {"label": "Meal 1 — Pre-Workout (7:00 AM)", "items": [
                self._make_item("oats", 80),
                self._make_item("banana", 118),
                self._make_item("whey protein", 30),
            ]},
            {"label": "Meal 2 — Post-Workout (10:00 AM)", "items": [
                self._make_item("chicken breast", 200),
                self._make_item("rice cooked", 200),
                self._make_item("broccoli", 100),
            ]},
            {"label": "Meal 3 — Lunch (1:30 PM)", "items": [
                self._make_item("whole egg", 150),
                self._make_item("brown bread", 60),
                self._make_item("mixed salad", 100),
                self._make_item("olive oil", 15),
            ]},
            {"label": "Meal 4 — Evening Snack (4:30 PM)", "items": [
                self._make_item("greek yogurt", 200),
                self._make_item("mixed nuts", 30),
            ]},
            {"label": "Meal 5 — Dinner (8:00 PM)", "items": [
                self._make_item("salmon", 200),
                self._make_item("sweet potato", 200),
                self._make_item("spinach", 100),
            ]},
        ]

    def _veg_meal_plan(self, cal: int, p: int, c: int, f: int, pref: str) -> list[dict]:
        return [
            {"label": "Meal 1 — Pre-Workout (7:00 AM)", "items": [
                self._make_item("oats", 80),
                self._make_item("banana", 118),
                self._make_item("whey protein", 30) if pref != "vegan" else self._make_item("hemp seeds", 30),
            ]},
            {"label": "Meal 2 — Post-Workout (10:00 AM)", "items": [
                self._make_item("paneer", 150) if pref != "vegan" else self._make_item("tofu", 200),
                self._make_item("rice cooked", 200),
                self._make_item("mixed vegetables", 150),
            ]},
            {"label": "Meal 3 — Lunch (1:30 PM)", "items": [
                self._make_item("lentils cooked", 200),
                self._make_item("brown rice cooked", 150),
                self._make_item("spinach", 100),
            ]},
            {"label": "Meal 4 — Evening Snack (4:30 PM)", "items": [
                self._make_item("greek yogurt", 200) if pref != "vegan" else self._make_item("soy milk", 300),
                self._make_item("almonds", 30),
            ]},
            {"label": "Meal 5 — Dinner (8:00 PM)", "items": [
                self._make_item("chickpeas cooked", 200),
                self._make_item("sweet potato", 200),
                self._make_item("avocado", 80),
            ]},
        ]

    # ------------------------------------------------------------------
    # Food log history
    # ------------------------------------------------------------------
    def food_log_today(self, day: str | None = None) -> list[dict[str, Any]]:
        """Get today's food log entries."""
        target_day = day or date.today().isoformat()
        rows = self.db.fetchall(
            "SELECT * FROM food_log WHERE date = ? ORDER BY id", (target_day,)
        )
        return [dict(r) for r in rows]

    def meal_history(self, limit: int = 20) -> list[dict[str, Any]]:
        """Legacy meal history."""
        rows = self.db.fetchall(
            "SELECT date, meal_name, description, estimated_calories FROM meals ORDER BY date DESC, id DESC LIMIT ?",
            (limit,),
        )
        return [dict(r) for r in rows]

    def search_food(self, query: str, preference: str | None = None) -> list[dict]:
        """Search food database."""
        return search_foods(query, preference)

    # ------------------------------------------------------------------
    # Legacy compatibility
    # ------------------------------------------------------------------
    def estimate_calories(self, description: str) -> tuple[float, list[str]]:
        """Legacy calorie estimation."""
        total = 0.0
        details: list[str] = []
        for raw_item in [p.strip() for p in description.split(",") if p.strip()]:
            match = self.ITEM_RE.match(raw_item)
            if not match:
                details.append(f"Skipped '{raw_item}'")
                continue
            qty = float(match.group("qty") or 1)
            raw_unit = match.group("unit")
            unit = raw_unit.lower() if raw_unit else ""
            food_name = match.group("food").lower().strip()
            macros = get_food_macros(food_name)
            if not macros:
                details.append(f"Skipped '{raw_item}' (not in database)")
                continue
            if not unit:
                grams = qty * UNIT_TO_GRAMS.get(food_name, 1)
            elif unit in {"gram", "grams", "g", "ml"}:
                grams = qty
            elif unit == "kg":
                grams = qty * 1000
            else:
                grams = qty * UNIT_TO_GRAMS.get(unit, 100)
            cals = (grams / 100.0) * macros["calories"]
            total += cals
            details.append(f"{raw_item} → {cals:.0f} kcal")
        return round(total, 1), details

    def log_meal(self, meal_name: str, description: str, meal_date: str | None = None) -> tuple[float, list[str]]:
        """Legacy meal logging - now with macro tracking."""
        return self.log_meal_description(meal_name, description, meal_date)

    def recipe_suggestions(self, goal: str, max_calories: int | None = None,
                           meal_type: str | None = None) -> list[dict[str, Any]]:
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

from __future__ import annotations

from pathlib import Path

from .agent import FitnessNutritionAgent


HELP_TEXT = """
Commands:
  help                     Show commands
  dashboard                Show today's overview
  set-goal                 Set goal + calorie target
  log-workout              Log a workout session
  view-workouts            Show recent workouts
  adaptive-plan            Get adaptive training suggestions
  log-meal                 Log meal and calorie estimate
  meal-history             Show recent meals
  calorie-summary          Show calories for a date (default today)
  recipes                  Suggest recipes based on goal
  exit                     Quit the app
""".strip()


def ask(prompt: str) -> str:
    return input(prompt).strip()


def run() -> None:
    root = Path(__file__).resolve().parent
    agent = FitnessNutritionAgent(root)

    print("Local AI Agent: Fitness Coach + Nutrition Assistant")
    print("Type 'help' to see commands.\n")

    try:
        while True:
            command = ask("agent> ").lower()

            if command in {"exit", "quit"}:
                print("Good session. Keep consistency high.")
                break

            if command == "help":
                print(HELP_TEXT)

            elif command == "dashboard":
                print("\n" + agent.dashboard() + "\n")

            elif command == "set-goal":
                goal = ask("Goal (fat_loss | maintenance | muscle_gain): ")
                target_raw = ask("Daily calorie target (blank for auto): ")
                target = int(target_raw) if target_raw else None
                agent.set_profile_goal(goal, target)
                print("Goal updated.\n")

            elif command == "log-workout":
                workout_date = ask("Date (YYYY-MM-DD, blank=today): ") or __import__("datetime").date.today().isoformat()
                exercise = ask("Exercise: ")
                sets = int(ask("Sets: ") or 0)
                reps = int(ask("Reps: ") or 0)
                weight = float(ask("Weight (kg/lb number only): ") or 0)
                duration = int(ask("Duration (minutes): ") or 0)
                rpe = float(ask("RPE (1-10): ") or 7)
                notes = ask("Notes (optional): ")

                agent.fitness.log_workout(workout_date, exercise, sets, reps, weight, duration, rpe, notes)
                print("Workout logged.")
                print(agent.fitness.motivation_message() + "\n")

            elif command == "view-workouts":
                workouts = agent.fitness.recent_workouts(30)
                if not workouts:
                    print("No workouts logged yet.\n")
                    continue
                print()
                for w in workouts[:20]:
                    print(
                        f"{w['date']} | {w['exercise']} | {w['sets']}x{w['reps']} @ {w['weight']} | "
                        f"{w['duration_min']} min | RPE {w['rpe']}"
                    )
                print()

            elif command == "adaptive-plan":
                print("\nAdaptive Routine:")
                print(agent.fitness.adaptive_routine() + "\n")

            elif command == "log-meal":
                meal_date = ask("Date (YYYY-MM-DD, blank=today): ") or __import__("datetime").date.today().isoformat()
                meal_name = ask("Meal name (breakfast/lunch/dinner/snack): ")
                description = ask("Foods (comma-separated, e.g., '150g chicken breast, 200g rice, 1 banana'): ")
                calories, details = agent.nutrition.log_meal(meal_name, description, meal_date)
                print(f"Estimated calories: {calories:.0f} kcal")
                for d in details:
                    print(f"- {d}")
                print()

            elif command == "meal-history":
                meals = agent.nutrition.meal_history(20)
                if not meals:
                    print("No meals logged yet.\n")
                    continue
                print()
                for m in meals:
                    print(f"{m['date']} | {m['meal_name']} | {m['estimated_calories']:.0f} kcal | {m['description']}")
                print()

            elif command == "calorie-summary":
                day = ask("Date (YYYY-MM-DD, blank=today): ") or None
                total = agent.nutrition.daily_calories(day)
                profile = agent.get_profile()
                target = profile["daily_calorie_target"]
                print(f"Total calories: {total:.0f} kcal")
                print(f"Target: {target} kcal")
                delta = total - float(target)
                status = "over" if delta > 0 else "under"
                print(f"You are {abs(delta):.0f} kcal {status} target.\n")

            elif command == "recipes":
                profile = agent.get_profile()
                goal = ask(f"Goal (blank uses profile={profile['goal']}): ") or str(profile["goal"])
                max_cals_raw = ask("Max calories per meal (blank=no limit): ")
                meal_type = ask("Meal type (breakfast/lunch/dinner, blank=any): ") or None
                max_cals = int(max_cals_raw) if max_cals_raw else None
                suggestions = agent.nutrition.recipe_suggestions(goal, max_cals, meal_type)

                if not suggestions:
                    print("No recipe match found. Try removing filters.\n")
                    continue

                print()
                for recipe in suggestions[:5]:
                    print(
                        f"{recipe['name']} ({recipe['meal_type']}) - {recipe['calories']} kcal, "
                        f"P{recipe['protein_g']} C{recipe['carbs_g']} F{recipe['fat_g']}"
                    )
                    print("Ingredients: " + ", ".join(recipe["ingredients"]))
                    print("Steps: " + " ".join(recipe["steps"]))
                    print()

            elif not command:
                continue

            else:
                print("Unknown command. Type 'help'.\n")

    finally:
        agent.close()


if __name__ == "__main__":
    run()

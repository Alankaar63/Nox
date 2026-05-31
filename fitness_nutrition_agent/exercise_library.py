from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------
# Master Exercise Library — ~80 exercises covering all 6 splits
# ---------------------------------------------------------------

EXERCISES: list[dict[str, Any]] = [
    # ===== CHEST =====
    {"name": "Bench Press", "primary": "chest", "secondary": ["triceps", "front delts"], "type": "compound", "equipment": "barbell", "pattern": "push"},
    {"name": "Incline Bench Press", "primary": "chest", "secondary": ["triceps", "front delts"], "type": "compound", "equipment": "barbell", "pattern": "push"},
    {"name": "Decline Bench Press", "primary": "chest", "secondary": ["triceps"], "type": "compound", "equipment": "barbell", "pattern": "push"},
    {"name": "Incline DB Press", "primary": "chest", "secondary": ["triceps", "front delts"], "type": "compound", "equipment": "dumbbell", "pattern": "push"},
    {"name": "Flat DB Press", "primary": "chest", "secondary": ["triceps"], "type": "compound", "equipment": "dumbbell", "pattern": "push"},
    {"name": "Incline Smith Press", "primary": "chest", "secondary": ["triceps", "front delts"], "type": "compound", "equipment": "smith machine", "pattern": "push"},
    {"name": "Cable Fly", "primary": "chest", "secondary": [], "type": "isolation", "equipment": "cable", "pattern": "push"},
    {"name": "Cable Crossover", "primary": "chest", "secondary": [], "type": "isolation", "equipment": "cable", "pattern": "push"},
    {"name": "Dips", "primary": "chest", "secondary": ["triceps", "front delts"], "type": "compound", "equipment": "bodyweight", "pattern": "push"},
    {"name": "Pec Deck", "primary": "chest", "secondary": [], "type": "isolation", "equipment": "machine", "pattern": "push"},

    # ===== BACK =====
    {"name": "Deadlift", "primary": "back", "secondary": ["hamstrings", "glutes", "traps"], "type": "compound", "equipment": "barbell", "pattern": "pull"},
    {"name": "Rack Pulls", "primary": "back", "secondary": ["traps", "glutes"], "type": "compound", "equipment": "barbell", "pattern": "pull"},
    {"name": "Bent-Over Row", "primary": "back", "secondary": ["biceps", "rear delts"], "type": "compound", "equipment": "barbell", "pattern": "pull"},
    {"name": "T-Bar Row", "primary": "back", "secondary": ["biceps", "rear delts"], "type": "compound", "equipment": "barbell", "pattern": "pull"},
    {"name": "Pulldown", "primary": "back", "secondary": ["biceps"], "type": "compound", "equipment": "cable", "pattern": "pull"},
    {"name": "Lat Pulldown", "primary": "back", "secondary": ["biceps"], "type": "compound", "equipment": "cable", "pattern": "pull"},
    {"name": "Seated Cable Row", "primary": "back", "secondary": ["biceps", "rear delts"], "type": "compound", "equipment": "cable", "pattern": "pull"},
    {"name": "Cable Row", "primary": "back", "secondary": ["biceps", "rear delts"], "type": "compound", "equipment": "cable", "pattern": "pull"},
    {"name": "Pull-ups", "primary": "back", "secondary": ["biceps"], "type": "compound", "equipment": "bodyweight", "pattern": "pull"},
    {"name": "Hammer Strength Row", "primary": "back", "secondary": ["biceps"], "type": "compound", "equipment": "machine", "pattern": "pull"},
    {"name": "Pullover Machine", "primary": "back", "secondary": ["chest"], "type": "isolation", "equipment": "machine", "pattern": "pull"},
    {"name": "DB Row", "primary": "back", "secondary": ["biceps"], "type": "compound", "equipment": "dumbbell", "pattern": "pull"},

    # ===== SHOULDERS =====
    {"name": "Overhead Press", "primary": "shoulders", "secondary": ["triceps"], "type": "compound", "equipment": "barbell", "pattern": "push"},
    {"name": "OHP", "primary": "shoulders", "secondary": ["triceps"], "type": "compound", "equipment": "barbell", "pattern": "push"},
    {"name": "Smith Machine OHP", "primary": "shoulders", "secondary": ["triceps"], "type": "compound", "equipment": "smith machine", "pattern": "push"},
    {"name": "Arnold Press", "primary": "shoulders", "secondary": ["triceps"], "type": "compound", "equipment": "dumbbell", "pattern": "push"},
    {"name": "Lateral Raise", "primary": "shoulders", "secondary": [], "type": "isolation", "equipment": "dumbbell", "pattern": "push"},
    {"name": "Cable Lateral Raise", "primary": "shoulders", "secondary": [], "type": "isolation", "equipment": "cable", "pattern": "push"},
    {"name": "Front Raise", "primary": "shoulders", "secondary": [], "type": "isolation", "equipment": "dumbbell", "pattern": "push"},
    {"name": "Face Pull", "primary": "rear delts", "secondary": ["traps"], "type": "isolation", "equipment": "cable", "pattern": "pull"},
    {"name": "Rear Delt Fly", "primary": "rear delts", "secondary": [], "type": "isolation", "equipment": "dumbbell", "pattern": "pull"},
    {"name": "Shrugs", "primary": "traps", "secondary": [], "type": "isolation", "equipment": "barbell", "pattern": "pull"},

    # ===== BICEPS =====
    {"name": "Barbell Curl", "primary": "biceps", "secondary": ["forearms"], "type": "isolation", "equipment": "barbell", "pattern": "pull"},
    {"name": "Hammer Curl", "primary": "biceps", "secondary": ["forearms", "brachialis"], "type": "isolation", "equipment": "dumbbell", "pattern": "pull"},
    {"name": "Preacher Curl", "primary": "biceps", "secondary": [], "type": "isolation", "equipment": "barbell", "pattern": "pull"},
    {"name": "Incline DB Curl", "primary": "biceps", "secondary": [], "type": "isolation", "equipment": "dumbbell", "pattern": "pull"},
    {"name": "Cable Curl", "primary": "biceps", "secondary": [], "type": "isolation", "equipment": "cable", "pattern": "pull"},
    {"name": "Concentration Curl", "primary": "biceps", "secondary": [], "type": "isolation", "equipment": "dumbbell", "pattern": "pull"},

    # ===== TRICEPS =====
    {"name": "Tricep Pushdown", "primary": "triceps", "secondary": [], "type": "isolation", "equipment": "cable", "pattern": "push"},
    {"name": "Overhead Extension", "primary": "triceps", "secondary": [], "type": "isolation", "equipment": "cable", "pattern": "push"},
    {"name": "Skull Crushers", "primary": "triceps", "secondary": [], "type": "isolation", "equipment": "barbell", "pattern": "push"},
    {"name": "Tricep Dips", "primary": "triceps", "secondary": ["chest"], "type": "compound", "equipment": "bodyweight", "pattern": "push"},
    {"name": "Close Grip Bench", "primary": "triceps", "secondary": ["chest"], "type": "compound", "equipment": "barbell", "pattern": "push"},

    # ===== QUADRICEPS / LEGS (PUSH) =====
    {"name": "Squat", "primary": "quadriceps", "secondary": ["glutes", "hamstrings"], "type": "compound", "equipment": "barbell", "pattern": "legs"},
    {"name": "Front Squat", "primary": "quadriceps", "secondary": ["core", "glutes"], "type": "compound", "equipment": "barbell", "pattern": "legs"},
    {"name": "Hack Squat", "primary": "quadriceps", "secondary": ["glutes"], "type": "compound", "equipment": "machine", "pattern": "legs"},
    {"name": "Leg Press", "primary": "quadriceps", "secondary": ["glutes", "hamstrings"], "type": "compound", "equipment": "machine", "pattern": "legs"},
    {"name": "Leg Extension", "primary": "quadriceps", "secondary": [], "type": "isolation", "equipment": "machine", "pattern": "legs"},
    {"name": "Bulgarian Split Squat", "primary": "quadriceps", "secondary": ["glutes"], "type": "compound", "equipment": "dumbbell", "pattern": "legs"},
    {"name": "Walking Lunge", "primary": "quadriceps", "secondary": ["glutes", "hamstrings"], "type": "compound", "equipment": "dumbbell", "pattern": "legs"},

    # ===== HAMSTRINGS / LEGS (PULL) =====
    {"name": "Romanian Deadlift", "primary": "hamstrings", "secondary": ["glutes", "lower back"], "type": "compound", "equipment": "barbell", "pattern": "legs"},
    {"name": "Stiff-Leg Deadlift", "primary": "hamstrings", "secondary": ["glutes", "lower back"], "type": "compound", "equipment": "barbell", "pattern": "legs"},
    {"name": "Lying Leg Curl", "primary": "hamstrings", "secondary": [], "type": "isolation", "equipment": "machine", "pattern": "legs"},
    {"name": "Seated Leg Curl", "primary": "hamstrings", "secondary": [], "type": "isolation", "equipment": "machine", "pattern": "legs"},
    {"name": "Leg Curl", "primary": "hamstrings", "secondary": [], "type": "isolation", "equipment": "machine", "pattern": "legs"},
    {"name": "Good Morning", "primary": "hamstrings", "secondary": ["lower back", "glutes"], "type": "compound", "equipment": "barbell", "pattern": "legs"},

    # ===== GLUTES =====
    {"name": "Hip Thrust", "primary": "glutes", "secondary": ["hamstrings"], "type": "compound", "equipment": "barbell", "pattern": "legs"},
    {"name": "Glute Bridge", "primary": "glutes", "secondary": ["hamstrings"], "type": "compound", "equipment": "bodyweight", "pattern": "legs"},
    {"name": "Cable Kickback", "primary": "glutes", "secondary": [], "type": "isolation", "equipment": "cable", "pattern": "legs"},

    # ===== CALVES =====
    {"name": "Standing Calf Raise", "primary": "calves", "secondary": [], "type": "isolation", "equipment": "machine", "pattern": "legs"},
    {"name": "Seated Calf Raise", "primary": "calves", "secondary": [], "type": "isolation", "equipment": "machine", "pattern": "legs"},
    {"name": "Calf Raise", "primary": "calves", "secondary": [], "type": "isolation", "equipment": "machine", "pattern": "legs"},

    # ===== CORE =====
    {"name": "Crunches", "primary": "abs", "secondary": [], "type": "isolation", "equipment": "bodyweight", "pattern": "core"},
    {"name": "Hanging Leg Raise", "primary": "abs", "secondary": ["hip flexors"], "type": "isolation", "equipment": "bodyweight", "pattern": "core"},
    {"name": "Cable Crunch", "primary": "abs", "secondary": [], "type": "isolation", "equipment": "cable", "pattern": "core"},
    {"name": "Plank", "primary": "abs", "secondary": ["core"], "type": "isolation", "equipment": "bodyweight", "pattern": "core"},
    {"name": "Ab Wheel Rollout", "primary": "abs", "secondary": ["core"], "type": "compound", "equipment": "ab wheel", "pattern": "core"},
    {"name": "Russian Twist", "primary": "obliques", "secondary": ["abs"], "type": "isolation", "equipment": "bodyweight", "pattern": "core"},

    # ===== FOREARMS =====
    {"name": "Wrist Curl", "primary": "forearms", "secondary": [], "type": "isolation", "equipment": "barbell", "pattern": "pull"},
    {"name": "Reverse Curl", "primary": "forearms", "secondary": ["biceps"], "type": "isolation", "equipment": "barbell", "pattern": "pull"},
    {"name": "Farmer's Walk", "primary": "forearms", "secondary": ["traps", "core"], "type": "compound", "equipment": "dumbbell", "pattern": "pull"},

    # ===== CARDIO / CONDITIONING =====
    {"name": "Running", "primary": "cardio", "secondary": ["legs"], "type": "cardio", "equipment": "none", "pattern": "cardio"},
    {"name": "Cycling", "primary": "cardio", "secondary": ["quadriceps"], "type": "cardio", "equipment": "bike", "pattern": "cardio"},
    {"name": "Jump Rope", "primary": "cardio", "secondary": ["calves"], "type": "cardio", "equipment": "rope", "pattern": "cardio"},
    {"name": "Battle Ropes", "primary": "cardio", "secondary": ["shoulders", "core"], "type": "cardio", "equipment": "battle ropes", "pattern": "cardio"},
    {"name": "Rowing Machine", "primary": "cardio", "secondary": ["back", "legs"], "type": "cardio", "equipment": "machine", "pattern": "cardio"},
]

# Build lookup index
_EXERCISE_INDEX: dict[str, dict[str, Any]] = {}
for _ex in EXERCISES:
    _EXERCISE_INDEX[_ex["name"].lower()] = _ex


def get_exercise(name: str) -> dict[str, Any] | None:
    """Lookup exercise by name (case-insensitive, fuzzy)."""
    key = name.lower().strip()
    if key in _EXERCISE_INDEX:
        return _EXERCISE_INDEX[key]
    # Fuzzy: check if query is a substring
    for ex_key, ex in _EXERCISE_INDEX.items():
        if key in ex_key or ex_key in key:
            return ex
    return None


def get_exercises_by_muscle(muscle: str) -> list[dict[str, Any]]:
    """Get all exercises targeting a muscle group."""
    m = muscle.lower().strip()
    return [
        ex for ex in EXERCISES
        if ex["primary"] == m or m in ex.get("secondary", [])
    ]


def get_exercises_by_pattern(pattern: str) -> list[dict[str, Any]]:
    """Get exercises by movement pattern (push/pull/legs/core/cardio)."""
    p = pattern.lower().strip()
    return [ex for ex in EXERCISES if ex["pattern"] == p]


def get_exercise_type(name: str) -> str:
    """Returns 'compound', 'isolation', or 'cardio' for rest duration logic."""
    ex = get_exercise(name)
    return ex["type"] if ex else "compound"


def suggest_rest_seconds(exercise_name: str, rep_range: int) -> tuple[int, str]:
    """Suggest rest duration based on exercise type and rep range.

    Returns (seconds, explanation).
    """
    ex_type = get_exercise_type(exercise_name)

    if ex_type == "cardio":
        return (60, "Cardio — 60s active rest between intervals")

    if ex_type == "compound" and rep_range <= 6:
        return (210, "Heavy compound — 3-4 min rest for CNS recovery")
    elif ex_type == "compound" and rep_range <= 12:
        return (150, "Compound hypertrophy — 2-3 min rest")
    elif ex_type == "compound":
        return (120, "Compound endurance — 2 min rest")
    elif ex_type == "isolation" and rep_range <= 10:
        return (90, "Isolation — 60-90s rest for hypertrophy")
    else:
        return (60, "Isolation / accessory — 45-60s rest")


def suggest_weight_increment(exercise_name: str) -> float:
    """Suggest weight increment for progressive overload.

    Returns kg increment.
    """
    ex_type = get_exercise_type(exercise_name)
    if ex_type == "compound":
        return 5.0  # +5 kg for compounds
    return 2.5  # +2.5 kg for isolations

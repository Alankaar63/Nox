from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------
# Training Split Templates — All 6 splits from the APEX spec
# Each split has: name, key, philosophy, days, and per-level prescriptions
# ---------------------------------------------------------------

SPLITS: dict[str, dict[str, Any]] = {
    # ----- 1. Dorian Yates HIT (4-day) -----
    "yates_hit": {
        "name": "Dorian Yates HIT Split",
        "key": "yates_hit",
        "days_per_week": 4,
        "philosophy": "One all-out set taken to failure. That's all you need. High Intensity Training — one working set per exercise, taken beyond failure. Low volume, maximum intensity. Built for intermediate-advanced lifters who can handle brutal effort.",
        "quote": "One all-out set taken to failure. That's all you need.",
        "coach": "Dorian Yates",
        "days": [
            {"day": 1, "label": "Chest & Triceps", "exercises": [
                "Incline Smith Press", "Flat DB Press", "Cable Crossover", "Tricep Pushdown", "Overhead Extension"
            ]},
            {"day": 2, "label": "Back & Rear Delts", "exercises": [
                "Rack Pulls", "Hammer Strength Row", "Seated Cable Row", "Pullover Machine", "Face Pull"
            ]},
            {"day": 3, "label": "Rest", "exercises": []},
            {"day": 4, "label": "Shoulders & Triceps", "exercises": [
                "Smith Machine OHP", "Lateral Raise", "Cable Lateral Raise", "Tricep Dips"
            ]},
            {"day": 5, "label": "Legs", "exercises": [
                "Leg Press", "Hack Squat", "Lying Leg Curl", "Stiff-Leg Deadlift", "Standing Calf Raise"
            ]},
            {"day": 6, "label": "Rest", "exercises": []},
            {"day": 7, "label": "Rest", "exercises": []},
        ],
        "prescription": {
            "beginner":     {"sets": 3, "reps": "10-12", "rpe": "6-7", "note": "Focus on form. 2-3 warm-up sets, 1 working set."},
            "intermediate": {"sets": 3, "reps": "8-10",  "rpe": "8-9", "note": "2 progressive warm-up sets, 1 all-out working set."},
            "advanced":     {"sets": 3, "reps": "6-8",   "rpe": "10",  "note": "2 warm-ups, 1 working set beyond failure. Forced reps, negatives."},
        },
        "key_principle": "One working set per exercise, preceded by 2-3 progressive warm-up sets. If you can do 8 reps, add weight next session.",
    },

    # ----- 2. Mike Mentzer Heavy Duty (2-day rotation) -----
    "mentzer_hd": {
        "name": "Mike Mentzer Heavy Duty Split",
        "key": "mentzer_hd",
        "days_per_week": 2,
        "philosophy": "Less is more. Intensity, not volume, is the key to growth. Ultra-low frequency, ultra-high intensity. Train once every 4-7 days per muscle group. Built around compound movements with forced reps and negatives.",
        "quote": "Less is more. Intensity, not volume, is the key to growth.",
        "coach": "Mike Mentzer",
        "days": [
            {"day": 1, "label": "Workout A — Chest/Back/Abs", "exercises": [
                "Incline Bench Press", "Dips", "Lat Pulldown", "Bent-Over Row", "Crunches"
            ]},
            {"day": 2, "label": "Rest (2-3 days)", "exercises": []},
            {"day": 3, "label": "Workout B — Shoulders/Arms/Legs", "exercises": [
                "Overhead Press", "Lateral Raise", "Barbell Curl", "Skull Crushers", "Squat", "Leg Curl"
            ]},
            {"day": 4, "label": "Rest (3-4 days)", "exercises": []},
        ],
        "prescription": {
            "beginner":     {"sets": 2, "reps": "8-10", "rpe": "7-8", "note": "Learn the movements. 1 warm-up, 1 working set."},
            "intermediate": {"sets": 2, "reps": "6-8",  "rpe": "9-10", "note": "1 warm-up, 1 all-out set with slow negatives."},
            "advanced":     {"sets": 2, "reps": "4-6",  "rpe": "10+",  "note": "Rest-pause, forced reps, negative-only on last rep. Absolute failure."},
        },
        "key_principle": "The workout ends when intensity is truly maxed out, not when a volume target is met.",
    },

    # ----- 3. Arnold Classic (6-day) -----
    "arnold": {
        "name": "Arnold / Classic Bro Split",
        "key": "arnold",
        "days_per_week": 6,
        "philosophy": "The last three or four reps is what makes the muscle grow. High volume, high frequency per muscle group (2x per week). The original bodybuilding blueprint.",
        "quote": "The last three or four reps is what makes the muscle grow.",
        "coach": "Arnold Schwarzenegger",
        "days": [
            {"day": 1, "label": "Chest & Back", "exercises": [
                "Bench Press", "Incline Bench Press", "Cable Fly", "Bent-Over Row", "Pulldown", "T-Bar Row"
            ]},
            {"day": 2, "label": "Shoulders & Arms", "exercises": [
                "Overhead Press", "Lateral Raise", "Arnold Press", "Barbell Curl", "Hammer Curl", "Skull Crushers", "Dips"
            ]},
            {"day": 3, "label": "Legs", "exercises": [
                "Squat", "Leg Press", "Leg Curl", "Leg Extension", "Standing Calf Raise", "Seated Calf Raise"
            ]},
            {"day": 4, "label": "Chest & Back (repeat)", "exercises": [
                "Bench Press", "Incline Bench Press", "Cable Fly", "Bent-Over Row", "Pulldown", "T-Bar Row"
            ]},
            {"day": 5, "label": "Shoulders & Arms (repeat)", "exercises": [
                "Overhead Press", "Lateral Raise", "Arnold Press", "Barbell Curl", "Hammer Curl", "Skull Crushers", "Dips"
            ]},
            {"day": 6, "label": "Legs (repeat)", "exercises": [
                "Squat", "Leg Press", "Leg Curl", "Leg Extension", "Standing Calf Raise", "Seated Calf Raise"
            ]},
            {"day": 7, "label": "Rest", "exercises": []},
        ],
        "prescription": {
            "beginner":     {"sets": 3, "reps": "10-12", "rpe": "6-7", "note": "3 sets per exercise, moderate load, perfect form."},
            "intermediate": {"sets": 4, "reps": "8-12",  "rpe": "8",   "note": "4 sets, chase the pump, mind-muscle connection."},
            "advanced":     {"sets": 5, "reps": "6-12",  "rpe": "9",   "note": "5 sets, supersets on opposing muscles, drop sets on last set."},
        },
        "key_principle": "Volume is king. 2x frequency per muscle group per week. Chase the pump.",
    },

    # ----- 4. Push / Pull / Legs (PPL) -----
    "ppl": {
        "name": "Push / Pull / Legs (PPL)",
        "key": "ppl",
        "days_per_week": 6,
        "philosophy": "The most versatile, evidence-based split for natural lifters. Group muscles by movement pattern. High weekly volume per group with 2x frequency at 6 days/week.",
        "quote": "Train by movement pattern, not body part.",
        "coach": "Evidence-Based",
        "days": [
            {"day": 1, "label": "Push A", "exercises": [
                "Bench Press", "Overhead Press", "Incline DB Press", "Lateral Raise", "Tricep Pushdown", "Overhead Extension"
            ]},
            {"day": 2, "label": "Pull A", "exercises": [
                "Deadlift", "Bent-Over Row", "Pulldown", "Cable Row", "Face Pull", "Barbell Curl", "Hammer Curl"
            ]},
            {"day": 3, "label": "Legs A", "exercises": [
                "Squat", "Romanian Deadlift", "Leg Press", "Leg Curl", "Calf Raise"
            ]},
            {"day": 4, "label": "Push B", "exercises": [
                "Incline Bench Press", "Arnold Press", "Cable Fly", "Lateral Raise", "Skull Crushers", "Tricep Pushdown"
            ]},
            {"day": 5, "label": "Pull B", "exercises": [
                "Bent-Over Row", "Pull-ups", "Seated Cable Row", "Face Pull", "Hammer Curl", "Preacher Curl"
            ]},
            {"day": 6, "label": "Legs B", "exercises": [
                "Front Squat", "Stiff-Leg Deadlift", "Leg Extension", "Seated Leg Curl", "Standing Calf Raise"
            ]},
            {"day": 7, "label": "Rest", "exercises": []},
        ],
        "prescription": {
            "beginner":     {"sets": 3, "reps": "10-12", "rpe": "6-7", "note": "Focus on form, not load. Add reps before adding weight."},
            "intermediate": {"sets": 4, "reps": "8-10",  "rpe": "8-9", "note": "Progressive overload priority. Paused reps, slow eccentrics."},
            "advanced":     {"sets": 4, "reps": "6-10",  "rpe": "9",   "note": "Wave loading, drop sets, rest-pause. Track MEV/MAV/MRV."},
        },
        "key_principle": "Group muscles by movement pattern. High weekly volume per group with 2x frequency.",
    },

    # ----- 5. Upper / Lower (4-day) -----
    "upper_lower": {
        "name": "Upper / Lower Split",
        "key": "upper_lower",
        "days_per_week": 4,
        "philosophy": "Ideal for intermediate lifters. High frequency, manageable volume. Alternates strength and hypertrophy focus.",
        "quote": "Frequency and balance — the intermediate sweet spot.",
        "coach": "Evidence-Based",
        "days": [
            {"day": 1, "label": "Upper (Strength)", "exercises": [
                "Bench Press", "Bent-Over Row", "Overhead Press", "Pulldown", "Barbell Curl", "Overhead Extension"
            ]},
            {"day": 2, "label": "Lower (Strength)", "exercises": [
                "Squat", "Romanian Deadlift", "Leg Press", "Leg Curl"
            ]},
            {"day": 3, "label": "Rest", "exercises": []},
            {"day": 4, "label": "Upper (Hypertrophy)", "exercises": [
                "Incline DB Press", "Cable Row", "Lateral Raise", "Face Pull", "Hammer Curl", "Tricep Pushdown"
            ]},
            {"day": 5, "label": "Lower (Hypertrophy)", "exercises": [
                "Front Squat", "Leg Extension", "Seated Leg Curl", "Calf Raise"
            ]},
            {"day": 6, "label": "Rest", "exercises": []},
            {"day": 7, "label": "Rest", "exercises": []},
        ],
        "prescription": {
            "beginner":     {"sets": 3, "reps": "10-12", "rpe": "6-7", "note": "3 sets, moderate load, learn the compound lifts."},
            "intermediate": {"sets": 4, "reps": "6-10",  "rpe": "8",   "note": "Strength days: 4x5-6. Hypertrophy days: 4x8-12."},
            "advanced":     {"sets": 5, "reps": "4-10",  "rpe": "9",   "note": "Periodise strength vs hypertrophy blocks. Deload every 4-6 weeks."},
        },
        "key_principle": "Strength focus early in the week, hypertrophy focus later. 2x frequency per muscle group.",
    },

    # ----- 6. Classic Bro Split (5-day) -----
    "bro_split": {
        "name": "Classic Bro Split",
        "key": "bro_split",
        "days_per_week": 5,
        "philosophy": "One muscle group per day. High isolation volume. Cult favourite for aesthetics. Maximum pump per session.",
        "quote": "Destroy one muscle group per day. Maximum pump.",
        "coach": "Classic Bodybuilding",
        "days": [
            {"day": 1, "label": "Chest", "exercises": [
                "Bench Press", "Incline Bench Press", "Decline Bench Press", "Cable Fly", "Dips"
            ]},
            {"day": 2, "label": "Back", "exercises": [
                "Deadlift", "Pulldown", "Cable Row", "T-Bar Row", "Pullover Machine"
            ]},
            {"day": 3, "label": "Shoulders", "exercises": [
                "Overhead Press", "Lateral Raise", "Front Raise", "Rear Delt Fly", "Shrugs"
            ]},
            {"day": 4, "label": "Arms", "exercises": [
                "Barbell Curl", "Hammer Curl", "Preacher Curl", "Skull Crushers", "Tricep Dips", "Tricep Pushdown"
            ]},
            {"day": 5, "label": "Legs", "exercises": [
                "Squat", "Leg Press", "Leg Curl", "Leg Extension", "Calf Raise"
            ]},
            {"day": 6, "label": "Rest", "exercises": []},
            {"day": 7, "label": "Rest", "exercises": []},
        ],
        "prescription": {
            "beginner":     {"sets": 3, "reps": "10-12", "rpe": "6-7", "note": "3 sets per exercise, focus on feeling the target muscle."},
            "intermediate": {"sets": 4, "reps": "8-12",  "rpe": "8",   "note": "4 sets, last set to failure. Mind-muscle connection."},
            "advanced":     {"sets": 5, "reps": "6-15",  "rpe": "9",   "note": "5 sets, drop sets on final exercise, giant sets optional."},
        },
        "key_principle": "One muscle group per day. Maximum isolation volume. Full recovery before next hit.",
    },
}


# ---------------------------------------------------------------
# API functions
# ---------------------------------------------------------------

def list_splits() -> list[dict[str, Any]]:
    """Return summary of all available splits."""
    return [
        {
            "key": s["key"],
            "name": s["name"],
            "days_per_week": s["days_per_week"],
            "coach": s["coach"],
            "quote": s["quote"],
        }
        for s in SPLITS.values()
    ]


def get_split(key: str, level: str = "intermediate") -> dict[str, Any] | None:
    """Get full split details with level-appropriate prescription."""
    split = SPLITS.get(key)
    if not split:
        # Try fuzzy match
        for k, v in SPLITS.items():
            if key.lower() in k or key.lower() in v["name"].lower():
                split = v
                break
    if not split:
        return None

    level = level.lower().strip()
    if level not in ("beginner", "intermediate", "advanced"):
        level = "intermediate"

    return {
        **split,
        "active_prescription": split["prescription"].get(level, split["prescription"]["intermediate"]),
        "level": level,
    }


def get_session_type_for_day(split_key: str, day_of_week: int) -> str:
    """Given a split and day (1-7, Mon=1), return the session type label."""
    split = SPLITS.get(split_key)
    if not split:
        return "Training"
    days = split["days"]
    idx = (day_of_week - 1) % len(days)
    return days[idx]["label"]


def get_exercises_for_day(split_key: str, day_of_week: int) -> list[str]:
    """Get exercise list for a specific day of a split."""
    split = SPLITS.get(split_key)
    if not split:
        return []
    days = split["days"]
    idx = (day_of_week - 1) % len(days)
    return days[idx].get("exercises", [])

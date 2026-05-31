from __future__ import annotations

# ---------------------------------------------------------------
# Full macro database: protein_g, carbs_g, fat_g, calories per 100g
# ---------------------------------------------------------------

FOOD_DB: dict[str, dict[str, float]] = {
    # ===== NON-VEGETARIAN =====
    "chicken breast":       {"protein": 31.0, "carbs": 0.0,  "fat": 3.6,  "calories": 165},
    "whole egg":            {"protein": 12.0, "carbs": 1.1,  "fat": 10.0, "calories": 140},
    "egg white":            {"protein": 11.0, "carbs": 0.7,  "fat": 0.2,  "calories": 52},
    "salmon":               {"protein": 25.0, "carbs": 0.0,  "fat": 13.0, "calories": 208},
    "tuna":                 {"protein": 26.0, "carbs": 0.0,  "fat": 1.0,  "calories": 116},
    "turkey breast":        {"protein": 29.0, "carbs": 0.0,  "fat": 1.0,  "calories": 135},
    "lean beef mince":      {"protein": 26.0, "carbs": 0.0,  "fat": 5.0,  "calories": 152},
    "prawns":               {"protein": 24.0, "carbs": 0.0,  "fat": 1.7,  "calories": 119},
    "shrimp":               {"protein": 24.0, "carbs": 0.0,  "fat": 1.7,  "calories": 119},
    "sardines":             {"protein": 25.0, "carbs": 0.0,  "fat": 11.0, "calories": 208},
    "cottage cheese":       {"protein": 11.0, "carbs": 3.4,  "fat": 5.0,  "calories": 98},
    "whey protein":         {"protein": 80.0, "carbs": 10.0, "fat": 5.0,  "calories": 400},
    "lamb":                 {"protein": 25.0, "carbs": 0.0,  "fat": 14.0, "calories": 230},
    "beef steak":           {"protein": 26.0, "carbs": 0.0,  "fat": 15.0, "calories": 242},
    "cod":                  {"protein": 18.0, "carbs": 0.0,  "fat": 0.7,  "calories": 82},
    "tilapia":              {"protein": 26.0, "carbs": 0.0,  "fat": 2.0,  "calories": 128},
    "mackerel":             {"protein": 19.0, "carbs": 0.0,  "fat": 14.0, "calories": 205},
    "chicken thigh":        {"protein": 26.0, "carbs": 0.0,  "fat": 10.0, "calories": 200},

    # ===== DAIRY =====
    "greek yogurt":         {"protein": 10.0, "carbs": 3.6,  "fat": 5.0,  "calories": 97},
    "greek yogurt low fat": {"protein": 10.0, "carbs": 3.6,  "fat": 0.7,  "calories": 59},
    "milk":                 {"protein": 3.5,  "carbs": 4.8,  "fat": 1.5,  "calories": 42},
    "skimmed milk":         {"protein": 3.5,  "carbs": 4.8,  "fat": 0.2,  "calories": 35},
    "paneer":               {"protein": 18.0, "carbs": 3.4,  "fat": 20.0, "calories": 265},
    "cheddar cheese":       {"protein": 25.0, "carbs": 1.3,  "fat": 33.0, "calories": 403},
    "mozzarella":           {"protein": 22.0, "carbs": 2.2,  "fat": 22.0, "calories": 300},

    # ===== VEGETARIAN / VEGAN PROTEIN =====
    "tofu":                 {"protein": 8.0,  "carbs": 2.0,  "fat": 4.8,  "calories": 83},
    "tempeh":               {"protein": 19.0, "carbs": 9.0,  "fat": 11.0, "calories": 193},
    "seitan":               {"protein": 25.0, "carbs": 14.0, "fat": 1.9,  "calories": 185},
    "edamame":              {"protein": 11.0, "carbs": 10.0, "fat": 5.0,  "calories": 122},
    "soy milk":             {"protein": 3.2,  "carbs": 1.6,  "fat": 1.8,  "calories": 35},

    # ===== LEGUMES =====
    "lentils cooked":       {"protein": 9.0,  "carbs": 20.0, "fat": 0.4,  "calories": 116},
    "chickpeas cooked":     {"protein": 8.9,  "carbs": 27.0, "fat": 2.6,  "calories": 164},
    "black beans cooked":   {"protein": 8.9,  "carbs": 23.0, "fat": 0.5,  "calories": 132},
    "kidney beans cooked":  {"protein": 8.7,  "carbs": 22.0, "fat": 0.5,  "calories": 127},
    "rajma cooked":         {"protein": 8.7,  "carbs": 22.0, "fat": 0.5,  "calories": 127},
    "dal cooked":           {"protein": 9.0,  "carbs": 20.0, "fat": 0.4,  "calories": 116},

    # ===== GRAINS & CARBS =====
    "rice cooked":          {"protein": 2.7,  "carbs": 28.0, "fat": 0.3,  "calories": 130},
    "brown rice cooked":    {"protein": 2.6,  "carbs": 23.0, "fat": 0.9,  "calories": 123},
    "oats":                 {"protein": 13.0, "carbs": 67.0, "fat": 6.0,  "calories": 389},
    "quinoa cooked":        {"protein": 4.4,  "carbs": 21.0, "fat": 1.9,  "calories": 120},
    "bread":                {"protein": 9.0,  "carbs": 49.0, "fat": 3.2,  "calories": 265},
    "brown bread":          {"protein": 10.0, "carbs": 43.0, "fat": 3.5,  "calories": 252},
    "white bread":          {"protein": 9.0,  "carbs": 49.0, "fat": 3.2,  "calories": 265},
    "sweet potato":         {"protein": 1.6,  "carbs": 20.0, "fat": 0.1,  "calories": 86},
    "potato":               {"protein": 2.0,  "carbs": 17.0, "fat": 0.1,  "calories": 77},
    "pasta cooked":         {"protein": 5.0,  "carbs": 25.0, "fat": 0.9,  "calories": 131},
    "roti":                 {"protein": 8.0,  "carbs": 48.0, "fat": 3.0,  "calories": 260},
    "naan":                 {"protein": 9.0,  "carbs": 50.0, "fat": 3.5,  "calories": 275},
    "corn":                 {"protein": 3.2,  "carbs": 19.0, "fat": 1.2,  "calories": 86},
    "poha":                 {"protein": 1.7,  "carbs": 23.0, "fat": 0.5,  "calories": 110},
    "upma":                 {"protein": 3.0,  "carbs": 18.0, "fat": 4.0,  "calories": 120},

    # ===== FRUITS =====
    "banana":               {"protein": 1.3,  "carbs": 27.0, "fat": 0.3,  "calories": 89},
    "apple":                {"protein": 0.3,  "carbs": 14.0, "fat": 0.2,  "calories": 52},
    "mango":                {"protein": 0.8,  "carbs": 15.0, "fat": 0.4,  "calories": 60},
    "orange":               {"protein": 0.9,  "carbs": 12.0, "fat": 0.1,  "calories": 47},
    "watermelon":           {"protein": 0.6,  "carbs": 8.0,  "fat": 0.2,  "calories": 30},
    "grapes":               {"protein": 0.7,  "carbs": 18.0, "fat": 0.2,  "calories": 69},
    "blueberries":          {"protein": 0.7,  "carbs": 14.0, "fat": 0.3,  "calories": 57},
    "strawberries":         {"protein": 0.7,  "carbs": 8.0,  "fat": 0.3,  "calories": 32},
    "papaya":               {"protein": 0.5,  "carbs": 11.0, "fat": 0.3,  "calories": 43},

    # ===== VEGETABLES =====
    "broccoli":             {"protein": 2.8,  "carbs": 7.0,  "fat": 0.4,  "calories": 35},
    "spinach":              {"protein": 2.9,  "carbs": 3.6,  "fat": 0.4,  "calories": 23},
    "mixed vegetables":     {"protein": 2.5,  "carbs": 10.0, "fat": 0.3,  "calories": 50},
    "tomato":               {"protein": 0.9,  "carbs": 3.9,  "fat": 0.2,  "calories": 18},
    "cucumber":             {"protein": 0.7,  "carbs": 3.6,  "fat": 0.1,  "calories": 16},
    "capsicum":             {"protein": 0.9,  "carbs": 6.0,  "fat": 0.3,  "calories": 26},
    "carrot":               {"protein": 0.9,  "carbs": 10.0, "fat": 0.2,  "calories": 41},
    "cauliflower":          {"protein": 1.9,  "carbs": 5.0,  "fat": 0.3,  "calories": 25},
    "cabbage":              {"protein": 1.3,  "carbs": 6.0,  "fat": 0.1,  "calories": 25},
    "onion":                {"protein": 1.1,  "carbs": 9.0,  "fat": 0.1,  "calories": 40},
    "mushroom":             {"protein": 3.1,  "carbs": 3.3,  "fat": 0.3,  "calories": 22},
    "lettuce":              {"protein": 1.4,  "carbs": 2.9,  "fat": 0.2,  "calories": 15},
    "kale":                 {"protein": 4.3,  "carbs": 9.0,  "fat": 0.9,  "calories": 49},
    "peas":                 {"protein": 5.4,  "carbs": 14.0, "fat": 0.4,  "calories": 81},
    "mixed salad":          {"protein": 1.0,  "carbs": 3.0,  "fat": 0.2,  "calories": 15},

    # ===== NUTS & SEEDS =====
    "almonds":              {"protein": 21.0, "carbs": 22.0, "fat": 49.0, "calories": 579},
    "peanut butter":        {"protein": 25.0, "carbs": 20.0, "fat": 50.0, "calories": 588},
    "peanuts":              {"protein": 26.0, "carbs": 16.0, "fat": 49.0, "calories": 567},
    "walnuts":              {"protein": 15.0, "carbs": 14.0, "fat": 65.0, "calories": 654},
    "cashews":              {"protein": 18.0, "carbs": 30.0, "fat": 44.0, "calories": 553},
    "mixed nuts":           {"protein": 20.0, "carbs": 21.0, "fat": 51.0, "calories": 607},
    "hemp seeds":           {"protein": 33.0, "carbs": 8.7,  "fat": 47.0, "calories": 567},
    "chia seeds":           {"protein": 17.0, "carbs": 42.0, "fat": 31.0, "calories": 486},
    "flax seeds":           {"protein": 18.0, "carbs": 29.0, "fat": 42.0, "calories": 534},
    "sunflower seeds":      {"protein": 21.0, "carbs": 20.0, "fat": 51.0, "calories": 584},
    "pumpkin seeds":        {"protein": 30.0, "carbs": 5.0,  "fat": 49.0, "calories": 559},

    # ===== FATS & OILS =====
    "olive oil":            {"protein": 0.0,  "carbs": 0.0,  "fat": 100.0,"calories": 884},
    "coconut oil":          {"protein": 0.0,  "carbs": 0.0,  "fat": 99.0, "calories": 862},
    "butter":               {"protein": 0.9,  "carbs": 0.1,  "fat": 81.0, "calories": 717},
    "ghee":                 {"protein": 0.0,  "carbs": 0.0,  "fat": 99.5, "calories": 900},
    "avocado":              {"protein": 2.0,  "carbs": 9.0,  "fat": 15.0, "calories": 160},

    # ===== SUPPLEMENTS =====
    "casein protein":       {"protein": 75.0, "carbs": 8.0,  "fat": 3.0,  "calories": 370},
    "mass gainer":          {"protein": 15.0, "carbs": 75.0, "fat": 5.0,  "calories": 400},
    "creatine":             {"protein": 0.0,  "carbs": 0.0,  "fat": 0.0,  "calories": 0},
    "bcaa":                 {"protein": 0.0,  "carbs": 0.0,  "fat": 0.0,  "calories": 0},

    # ===== MISC / INDIAN STAPLES =====
    "honey":                {"protein": 0.3,  "carbs": 82.0, "fat": 0.0,  "calories": 304},
    "sugar":                {"protein": 0.0,  "carbs": 100.0,"fat": 0.0,  "calories": 387},
    "dark chocolate":       {"protein": 5.0,  "carbs": 46.0, "fat": 31.0, "calories": 546},
    "idli":                 {"protein": 2.0,  "carbs": 13.0, "fat": 0.4,  "calories": 58},
    "dosa":                 {"protein": 2.5,  "carbs": 18.0, "fat": 3.0,  "calories": 110},
    "paratha":              {"protein": 5.0,  "carbs": 32.0, "fat": 9.0,  "calories": 230},
}

# Legacy alias for backward compatibility
FOOD_CALORIES_PER_100G: dict[str, float] = {name: data["calories"] for name, data in FOOD_DB.items()}
# Add old aliases
FOOD_CALORIES_PER_100G["egg"] = 140
FOOD_DB["egg"] = FOOD_DB["whole egg"]

# ---------------------------------------------------------------
# Unit-to-grams mapping for natural language parsing
# ---------------------------------------------------------------
UNIT_TO_GRAMS: dict[str, float] = {
    "egg": 50,
    "eggs": 50,
    "banana": 118,
    "bananas": 118,
    "apple": 182,
    "apples": 182,
    "orange": 131,
    "oranges": 131,
    "tbsp": 15,
    "tablespoon": 15,
    "tablespoons": 15,
    "tsp": 5,
    "teaspoon": 5,
    "teaspoons": 5,
    "cup": 240,
    "cups": 240,
    "scoop": 30,
    "scoops": 30,
    "slice": 30,
    "slices": 30,
    "roti": 40,
    "rotis": 40,
    "naan": 90,
    "idli": 40,
    "dosa": 60,
    "paratha": 60,
}

# ---------------------------------------------------------------
# Dietary preference tags
# ---------------------------------------------------------------
VEGETARIAN_FOODS = {
    "tofu", "tempeh", "seitan", "edamame", "soy milk",
    "lentils cooked", "chickpeas cooked", "black beans cooked", "kidney beans cooked",
    "rajma cooked", "dal cooked", "paneer", "greek yogurt", "greek yogurt low fat",
    "milk", "skimmed milk", "cottage cheese", "cheddar cheese", "mozzarella",
    "oats", "quinoa cooked", "rice cooked", "brown rice cooked", "bread",
    "brown bread", "white bread", "sweet potato", "potato", "pasta cooked",
    "roti", "naan", "corn", "poha", "upma",
    "banana", "apple", "mango", "orange", "watermelon", "grapes",
    "blueberries", "strawberries", "papaya",
    "broccoli", "spinach", "mixed vegetables", "tomato", "cucumber",
    "capsicum", "carrot", "cauliflower", "cabbage", "onion", "mushroom",
    "lettuce", "kale", "peas", "mixed salad",
    "almonds", "peanut butter", "peanuts", "walnuts", "cashews", "mixed nuts",
    "hemp seeds", "chia seeds", "flax seeds", "sunflower seeds", "pumpkin seeds",
    "olive oil", "coconut oil", "butter", "ghee", "avocado",
    "whey protein", "casein protein", "mass gainer", "creatine", "bcaa",
    "honey", "sugar", "dark chocolate", "idli", "dosa", "paratha",
    "whole egg", "egg", "egg white",
}

VEGAN_FOODS = VEGETARIAN_FOODS - {
    "paneer", "greek yogurt", "greek yogurt low fat", "milk", "skimmed milk",
    "cottage cheese", "cheddar cheese", "mozzarella", "butter", "ghee",
    "whey protein", "casein protein", "mass gainer",
    "whole egg", "egg", "egg white", "honey",
}

NON_VEG_ONLY = set(FOOD_DB.keys()) - VEGETARIAN_FOODS


def get_food_macros(food_name: str) -> dict[str, float] | None:
    """Return macros for a food, or None if not found."""
    name = food_name.lower().strip()
    if name in FOOD_DB:
        return FOOD_DB[name]

    # Try common aliases
    aliases = {
        "rice": "rice cooked",
        "brown rice": "brown rice cooked",
        "lentils": "lentils cooked",
        "chickpeas": "chickpeas cooked",
        "yogurt": "greek yogurt",
        "chicken": "chicken breast",
        "eggs": "whole egg",
        "egg": "whole egg",
        "tuna can": "tuna",
        "peanut": "peanuts",
        "almond": "almonds",
        "steak": "beef steak",
        "beef": "lean beef mince",
        "shrimps": "shrimp",
        "dal": "dal cooked",
        "rajma": "rajma cooked",
    }
    resolved = aliases.get(name, name)
    if resolved in FOOD_DB:
        return FOOD_DB[resolved]

    # Strip trailing 's'
    if name.endswith("s") and name[:-1] in FOOD_DB:
        return FOOD_DB[name[:-1]]

    return None


def search_foods(query: str, preference: str | None = None) -> list[dict]:
    """Fuzzy search food database with optional dietary filter."""
    q = query.lower().strip()
    results = []
    for name, macros in FOOD_DB.items():
        if q in name:
            if preference == "vegetarian" and name not in VEGETARIAN_FOODS:
                continue
            if preference == "vegan" and name not in VEGAN_FOODS:
                continue
            results.append({"name": name, **macros})
    return sorted(results, key=lambda x: x["protein"], reverse=True)

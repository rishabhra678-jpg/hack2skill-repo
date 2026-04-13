"""
NutriMind – AI Engine
Food recognition (mock CNN), context-aware recommendations,
behavior analysis, and meal plan generation.
"""

import random
from datetime import datetime

# ─────────────────────────────────────────────
# Food Recognition Database (simulating a CNN)
# ─────────────────────────────────────────────

FOOD_DATABASE = {
    "pizza": {
        "calories": 285, "protein": 12, "carbs": 36, "fats": 11,
        "health_score": 35, "category": "junk",
        "alternatives": ["whole wheat flatbread with veggies", "cauliflower crust pizza", "grilled paneer wrap"]
    },
    "burger": {
        "calories": 354, "protein": 17, "carbs": 29, "fats": 19,
        "health_score": 30, "category": "junk",
        "alternatives": ["grilled chicken lettuce wrap", "black bean burger", "turkey burger on whole grain"]
    },
    "salad": {
        "calories": 120, "protein": 4, "carbs": 14, "fats": 6,
        "health_score": 90, "category": "healthy",
        "alternatives": ["quinoa salad", "mediterranean bowl", "thai peanut salad"]
    },
    "rice": {
        "calories": 206, "protein": 4, "carbs": 45, "fats": 0.4,
        "health_score": 60, "category": "staple",
        "alternatives": ["brown rice", "quinoa", "cauliflower rice"]
    },
    "chicken breast": {
        "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6,
        "health_score": 85, "category": "protein",
        "alternatives": ["grilled salmon", "tofu stir-fry", "turkey breast"]
    },
    "french fries": {
        "calories": 312, "protein": 3, "carbs": 41, "fats": 15,
        "health_score": 20, "category": "junk",
        "alternatives": ["sweet potato fries (baked)", "roasted vegetables", "air-fried zucchini sticks"]
    },
    "pasta": {
        "calories": 220, "protein": 8, "carbs": 43, "fats": 1.3,
        "health_score": 45, "category": "carb_heavy",
        "alternatives": ["zucchini noodles", "whole wheat pasta", "lentil pasta"]
    },
    "ice cream": {
        "calories": 207, "protein": 3.5, "carbs": 24, "fats": 11,
        "health_score": 25, "category": "dessert",
        "alternatives": ["frozen yogurt", "banana nice cream", "dark chocolate squares"]
    },
    "smoothie": {
        "calories": 150, "protein": 5, "carbs": 30, "fats": 2,
        "health_score": 75, "category": "healthy",
        "alternatives": ["green smoothie", "protein shake", "chia pudding"]
    },
    "sandwich": {
        "calories": 250, "protein": 12, "carbs": 32, "fats": 8,
        "health_score": 55, "category": "moderate",
        "alternatives": ["whole grain wrap", "lettuce wrap", "open-face sandwich on rye"]
    },
    "biryani": {
        "calories": 350, "protein": 15, "carbs": 42, "fats": 14,
        "health_score": 45, "category": "carb_heavy",
        "alternatives": ["brown rice pulao", "quinoa biryani", "millet khichdi"]
    },
    "dosa": {
        "calories": 168, "protein": 4, "carbs": 28, "fats": 4,
        "health_score": 60, "category": "moderate",
        "alternatives": ["ragi dosa", "oats dosa", "moong dal chilla"]
    },
    "samosa": {
        "calories": 262, "protein": 4, "carbs": 25, "fats": 16,
        "health_score": 25, "category": "junk",
        "alternatives": ["baked samosa", "sprout chaat", "roasted makhana"]
    },
    "dal": {
        "calories": 180, "protein": 12, "carbs": 28, "fats": 3,
        "health_score": 82, "category": "healthy",
        "alternatives": ["moong dal soup", "masoor dal", "chana dal"]
    },
    "paneer tikka": {
        "calories": 260, "protein": 18, "carbs": 8, "fats": 18,
        "health_score": 65, "category": "protein",
        "alternatives": ["grilled tofu tikka", "soya chaap", "mushroom tikka"]
    },
    "oatmeal": {
        "calories": 154, "protein": 5, "carbs": 27, "fats": 3,
        "health_score": 88, "category": "healthy",
        "alternatives": ["overnight oats", "muesli bowl", "chia seed pudding"]
    },
    "egg": {
        "calories": 155, "protein": 13, "carbs": 1.1, "fats": 11,
        "health_score": 80, "category": "protein",
        "alternatives": ["boiled eggs", "egg white omelette", "scrambled tofu"]
    },
    "noodles": {
        "calories": 220, "protein": 5, "carbs": 40, "fats": 3.5,
        "health_score": 40, "category": "carb_heavy",
        "alternatives": ["soba noodles", "shirataki noodles", "veggie stir-fry"]
    },
    "cake": {
        "calories": 350, "protein": 4, "carbs": 50, "fats": 15,
        "health_score": 15, "category": "dessert",
        "alternatives": ["oat flour banana bread", "date energy balls", "fruit salad with honey"]
    },
    "apple": {
        "calories": 95, "protein": 0.5, "carbs": 25, "fats": 0.3,
        "health_score": 92, "category": "fruit",
        "alternatives": ["berries mix", "pear", "guava"]
    },
    "banana": {
        "calories": 105, "protein": 1.3, "carbs": 27, "fats": 0.4,
        "health_score": 85, "category": "fruit",
        "alternatives": ["apple", "papaya", "kiwi"]
    },
}


def scan_food(food_name: str) -> dict:
    """
    Simulate AI food recognition from an image.
    In production, this would pass an image through a CNN model.
    Returns nutritional data and healthier alternatives.
    """
    food_key = food_name.lower().strip()

    # Try exact match
    if food_key in FOOD_DATABASE:
        data = FOOD_DATABASE[food_key]
    else:
        # Fuzzy matching: find partial match
        matched = None
        for key in FOOD_DATABASE:
            if key in food_key or food_key in key:
                matched = FOOD_DATABASE[key]
                food_key = key
                break

        if matched:
            data = matched
        else:
            # Unknown food — generate plausible random data
            data = {
                "calories": random.randint(100, 400),
                "protein": round(random.uniform(2, 25), 1),
                "carbs": round(random.uniform(10, 50), 1),
                "fats": round(random.uniform(2, 20), 1),
                "health_score": random.randint(30, 70),
                "category": "unknown",
                "alternatives": ["grilled chicken salad", "fruit bowl", "vegetable soup"]
            }

    return {
        "food_name": food_name.title(),
        "calories": data["calories"],
        "protein": data["protein"],
        "carbs": data["carbs"],
        "fats": data["fats"],
        "health_score": data["health_score"],
        "category": data.get("category", "unknown"),
        "alternatives": data["alternatives"],
        "ai_confidence": round(random.uniform(0.82, 0.98), 2)
    }


# ─────────────────────────────────────────────
# Context-Aware Recommendation Engine
# ─────────────────────────────────────────────

CONTEXTUAL_SUGGESTIONS = {
    "early_morning": {  # 5-8 AM
        "message": "Rise and shine! ☀️ Start with something energizing.",
        "suggestions": [
            {"name": "Oatmeal with berries", "calories": 180, "protein": 6, "carbs": 32, "fats": 4, "score": 90},
            {"name": "Banana smoothie", "calories": 160, "protein": 8, "carbs": 28, "fats": 3, "score": 85},
            {"name": "Boiled eggs + toast", "calories": 220, "protein": 16, "carbs": 18, "fats": 10, "score": 82},
        ]
    },
    "morning": {  # 8-11 AM
        "message": "Good morning! 🌅 Fuel up with a balanced breakfast.",
        "suggestions": [
            {"name": "Moong dal chilla", "calories": 190, "protein": 12, "carbs": 24, "fats": 5, "score": 88},
            {"name": "Greek yogurt parfait", "calories": 200, "protein": 15, "carbs": 22, "fats": 6, "score": 86},
            {"name": "Veggie omelette", "calories": 210, "protein": 18, "carbs": 5, "fats": 14, "score": 83},
        ]
    },
    "afternoon": {  # 11 AM - 2 PM
        "message": "Lunch time! 🍽️ Go for something balanced and filling.",
        "suggestions": [
            {"name": "Brown rice + dal + veggies", "calories": 380, "protein": 16, "carbs": 55, "fats": 8, "score": 85},
            {"name": "Grilled chicken salad", "calories": 320, "protein": 30, "carbs": 15, "fats": 14, "score": 88},
            {"name": "Quinoa bowl with chickpeas", "calories": 350, "protein": 18, "carbs": 48, "fats": 10, "score": 90},
        ]
    },
    "evening": {  # 2-6 PM
        "message": "Snack time! 🥜 Choose something light but nourishing.",
        "suggestions": [
            {"name": "Mixed nuts & seeds", "calories": 170, "protein": 6, "carbs": 8, "fats": 14, "score": 82},
            {"name": "Apple with peanut butter", "calories": 200, "protein": 5, "carbs": 28, "fats": 10, "score": 80},
            {"name": "Roasted makhana", "calories": 110, "protein": 4, "carbs": 18, "fats": 2, "score": 88},
        ]
    },
    "dinner": {  # 6-9 PM
        "message": "Dinner goals! 🌙 Keep it light and protein-rich.",
        "suggestions": [
            {"name": "Grilled paneer + roti", "calories": 340, "protein": 22, "carbs": 30, "fats": 14, "score": 78},
            {"name": "Vegetable soup + multigrain bread", "calories": 250, "protein": 10, "carbs": 35, "fats": 6, "score": 86},
            {"name": "Steamed fish with salad", "calories": 280, "protein": 32, "carbs": 8, "fats": 12, "score": 90},
        ]
    },
    "late_night": {  # 9 PM - 5 AM
        "message": "Late night cravings? 🌜 Go light on your stomach.",
        "suggestions": [
            {"name": "Warm turmeric milk", "calories": 80, "protein": 4, "carbs": 10, "fats": 3, "score": 85},
            {"name": "Handful of almonds", "calories": 90, "protein": 3, "carbs": 3, "fats": 8, "score": 80},
            {"name": "Chamomile tea + 2 crackers", "calories": 60, "protein": 1, "carbs": 12, "fats": 1, "score": 78},
        ]
    },
}


def get_time_context(hour: int = None) -> str:
    """Determine the time-of-day context."""
    if hour is None:
        hour = datetime.now().hour
    if 5 <= hour < 8:
        return "early_morning"
    elif 8 <= hour < 11:
        return "morning"
    elif 11 <= hour < 14:
        return "afternoon"
    elif 14 <= hour < 18:
        return "evening"
    elif 18 <= hour < 21:
        return "dinner"
    else:
        return "late_night"


def get_contextual_recommendations(hour: int = None, goal: str = None, diet: str = None) -> dict:
    """
    Get food recommendations based on time of day, user goal, and dietary preference.
    """
    context = get_time_context(hour)
    data = CONTEXTUAL_SUGGESTIONS[context]

    suggestions = data["suggestions"][:]

    # Filter by diet preference
    if diet == "vegan":
        # Remove obviously non-vegan items
        non_vegan_keywords = ["chicken", "fish", "egg", "yogurt", "paneer", "milk"]
        suggestions = [s for s in suggestions if not any(kw in s["name"].lower() for kw in non_vegan_keywords)]
    elif diet == "veg":
        non_veg_keywords = ["chicken", "fish", "turkey"]
        suggestions = [s for s in suggestions if not any(kw in s["name"].lower() for kw in non_veg_keywords)]

    # Adjust message by goal
    goal_tip = ""
    if goal == "weight_loss":
        goal_tip = " Keep portions moderate and prioritize protein! 💪"
    elif goal == "muscle_gain":
        goal_tip = " Load up on protein and complex carbs! 🏋️"
    elif goal == "maintenance":
        goal_tip = " Stay balanced and consistent! ⚖️"

    # Ensure at least one suggestion
    if not suggestions:
        suggestions = [{"name": "Fresh fruit bowl", "calories": 120, "protein": 2, "carbs": 28, "fats": 1, "score": 88}]

    return {
        "time_context": context,
        "message": data["message"] + goal_tip,
        "suggestions": suggestions
    }


# ─────────────────────────────────────────────
# Behavior Analysis Engine
# ─────────────────────────────────────────────

def analyze_behavior(food_logs: list) -> dict:
    """
    Analyze a user's food log history to detect eating patterns.
    Returns insights and nudges.
    """
    if not food_logs:
        return {
            "patterns": [],
            "nudges": ["Start logging your meals to get personalized insights! 📝"],
            "avg_health_score": 0,
            "total_logs": 0
        }

    total = len(food_logs)
    avg_calories = sum(log.calories for log in food_logs) / total
    avg_health_score = sum(log.health_score for log in food_logs) / total

    junk_count = sum(1 for log in food_logs if log.health_score < 40)
    healthy_count = sum(1 for log in food_logs if log.health_score >= 70)

    patterns = []
    nudges = []

    # Junk food pattern
    junk_ratio = junk_count / total if total > 0 else 0
    if junk_ratio > 0.4:
        patterns.append("frequent_junk")
        nudges.append("🍔 You've been eating a lot of junk food lately. Try swapping one junk meal with a salad or fruit bowl!")
    elif junk_ratio > 0.2:
        patterns.append("moderate_junk")
        nudges.append("⚠️ Some junk food detected in your logs. Balance it out with healthy snacks!")

    # Healthy eating pattern
    healthy_ratio = healthy_count / total if total > 0 else 0
    if healthy_ratio > 0.6:
        patterns.append("healthy_eater")
        nudges.append("🌟 Amazing! You're making great food choices. Keep the streak going!")

    # Calorie analysis
    if avg_calories > 500:
        patterns.append("high_calorie")
        nudges.append("📊 Your average meal is calorie-heavy. Consider portion control.")
    elif avg_calories < 150:
        patterns.append("under_eating")
        nudges.append("🍽️ You might be under-eating. Make sure you're getting enough nutrition!")

    # Late night eating detection
    late_night_logs = [log for log in food_logs if log.logged_at and log.logged_at.hour >= 22]
    if len(late_night_logs) > 2:
        patterns.append("late_night_eating")
        nudges.append("🌙 You frequently eat late at night. Try having dinner before 9 PM for better digestion.")

    if not nudges:
        nudges.append("✅ Your eating habits look good! Stay consistent.")

    return {
        "patterns": patterns,
        "nudges": nudges,
        "avg_health_score": round(avg_health_score, 1),
        "avg_calories": round(avg_calories, 1),
        "total_logs": total,
        "junk_ratio": round(junk_ratio * 100, 1),
        "healthy_ratio": round(healthy_ratio * 100, 1),
    }


# ─────────────────────────────────────────────
# Meal Plan Generator
# ─────────────────────────────────────────────

MEAL_PLAN_DATABASE = {
    "veg": {
        "breakfast": [
            {"name": "Oats porridge with fruits", "cal": 180, "p": 6, "c": 32, "f": 4},
            {"name": "Poha with peanuts", "cal": 200, "p": 5, "c": 35, "f": 6},
            {"name": "Idli with sambar", "cal": 210, "p": 7, "c": 38, "f": 3},
            {"name": "Moong dal chilla", "cal": 190, "p": 12, "c": 24, "f": 5},
            {"name": "Sprouts salad + toast", "cal": 220, "p": 10, "c": 30, "f": 6},
            {"name": "Ragi dosa + chutney", "cal": 185, "p": 5, "c": 30, "f": 5},
            {"name": "Besan chilla with veggies", "cal": 195, "p": 10, "c": 22, "f": 7},
        ],
        "lunch": [
            {"name": "Rajma chawal", "cal": 380, "p": 14, "c": 55, "f": 8},
            {"name": "Chole roti + raita", "cal": 400, "p": 15, "c": 50, "f": 12},
            {"name": "Dal + brown rice + sabzi", "cal": 360, "p": 14, "c": 52, "f": 7},
            {"name": "Vegetable pulao + curd", "cal": 340, "p": 10, "c": 50, "f": 9},
            {"name": "Paneer bhurji + roti", "cal": 380, "p": 20, "c": 35, "f": 16},
            {"name": "Sambar rice + papad", "cal": 350, "p": 12, "c": 55, "f": 6},
            {"name": "Kadhi chawal + salad", "cal": 370, "p": 10, "c": 55, "f": 10},
        ],
        "dinner": [
            {"name": "Vegetable soup + multigrain bread", "cal": 250, "p": 8, "c": 35, "f": 6},
            {"name": "Palak paneer + 1 roti", "cal": 300, "p": 16, "c": 25, "f": 14},
            {"name": "Khichdi with veggies", "cal": 280, "p": 10, "c": 42, "f": 5},
            {"name": "Grilled paneer salad", "cal": 270, "p": 18, "c": 15, "f": 15},
            {"name": "Methi thepla + curd", "cal": 260, "p": 8, "c": 35, "f": 9},
            {"name": "Mixed dal + roti + sabzi", "cal": 320, "p": 14, "c": 40, "f": 8},
            {"name": "Mushroom stir-fry + brown rice", "cal": 290, "p": 10, "c": 40, "f": 8},
        ],
        "snack": [
            {"name": "Fruit chaat", "cal": 100, "p": 1, "c": 24, "f": 0.5},
            {"name": "Roasted makhana", "cal": 110, "p": 4, "c": 18, "f": 2},
            {"name": "Green smoothie", "cal": 130, "p": 3, "c": 22, "f": 3},
            {"name": "Mixed nuts (small handful)", "cal": 160, "p": 5, "c": 6, "f": 14},
            {"name": "Yogurt + seeds", "cal": 140, "p": 8, "c": 14, "f": 5},
            {"name": "Cucumber + hummus", "cal": 100, "p": 4, "c": 12, "f": 4},
            {"name": "Peanut butter banana toast", "cal": 200, "p": 6, "c": 26, "f": 9},
        ],
    },
    "non_veg": {
        "breakfast": [
            {"name": "Egg bhurji + toast", "cal": 240, "p": 16, "c": 20, "f": 12},
            {"name": "Boiled eggs + fruit", "cal": 200, "p": 14, "c": 15, "f": 10},
            {"name": "Chicken sausage wrap", "cal": 280, "p": 18, "c": 25, "f": 12},
            {"name": "Omelette + multigrain bread", "cal": 250, "p": 16, "c": 22, "f": 11},
            {"name": "Oats porridge with fruits", "cal": 180, "p": 6, "c": 32, "f": 4},
            {"name": "Eggs + avocado toast", "cal": 300, "p": 14, "c": 24, "f": 16},
            {"name": "Moong dal chilla", "cal": 190, "p": 12, "c": 24, "f": 5},
        ],
        "lunch": [
            {"name": "Chicken curry + rice", "cal": 420, "p": 28, "c": 45, "f": 14},
            {"name": "Grilled chicken salad", "cal": 320, "p": 30, "c": 15, "f": 14},
            {"name": "Fish curry + roti", "cal": 380, "p": 26, "c": 35, "f": 12},
            {"name": "Egg fried rice + raita", "cal": 400, "p": 16, "c": 50, "f": 14},
            {"name": "Chicken wrap + veggies", "cal": 370, "p": 24, "c": 32, "f": 14},
            {"name": "Dal + rice + chicken tikka", "cal": 440, "p": 30, "c": 48, "f": 12},
            {"name": "Tuna sandwich + soup", "cal": 350, "p": 22, "c": 35, "f": 10},
        ],
        "dinner": [
            {"name": "Grilled fish + salad", "cal": 280, "p": 32, "c": 8, "f": 12},
            {"name": "Chicken soup + bread", "cal": 260, "p": 20, "c": 25, "f": 8},
            {"name": "Egg curry + 1 roti", "cal": 300, "p": 16, "c": 28, "f": 12},
            {"name": "Tandoori chicken + mint chutney", "cal": 280, "p": 30, "c": 5, "f": 14},
            {"name": "Steamed fish + brown rice", "cal": 310, "p": 28, "c": 32, "f": 8},
            {"name": "Chicken stir-fry + quinoa", "cal": 340, "p": 28, "c": 30, "f": 12},
            {"name": "Mixed dal + roti + egg", "cal": 350, "p": 18, "c": 40, "f": 10},
        ],
        "snack": [
            {"name": "Boiled egg", "cal": 78, "p": 6, "c": 0.5, "f": 5},
            {"name": "Chicken tikka (3 pcs)", "cal": 150, "p": 18, "c": 3, "f": 7},
            {"name": "Mixed nuts", "cal": 160, "p": 5, "c": 6, "f": 14},
            {"name": "Fruit + yogurt", "cal": 140, "p": 6, "c": 20, "f": 4},
            {"name": "Protein shake", "cal": 180, "p": 25, "c": 10, "f": 3},
            {"name": "Peanut butter toast", "cal": 200, "p": 7, "c": 22, "f": 10},
            {"name": "Sprout chaat", "cal": 120, "p": 8, "c": 16, "f": 2},
        ],
    },
    "vegan": {
        "breakfast": [
            {"name": "Smoothie bowl (banana, berries)", "cal": 200, "p": 5, "c": 38, "f": 4},
            {"name": "Oats with almond milk", "cal": 180, "p": 5, "c": 30, "f": 5},
            {"name": "Tofu scramble + toast", "cal": 230, "p": 14, "c": 22, "f": 10},
            {"name": "Chia seed pudding", "cal": 190, "p": 6, "c": 24, "f": 8},
            {"name": "Poha with vegetables", "cal": 200, "p": 4, "c": 36, "f": 5},
            {"name": "Ragi porridge with jaggery", "cal": 170, "p": 4, "c": 32, "f": 3},
            {"name": "Sprouts salad + fruit", "cal": 180, "p": 10, "c": 26, "f": 3},
        ],
        "lunch": [
            {"name": "Quinoa bowl + chickpeas", "cal": 350, "p": 16, "c": 50, "f": 8},
            {"name": "Rajma chawal", "cal": 380, "p": 14, "c": 55, "f": 8},
            {"name": "Tofu stir-fry + rice", "cal": 360, "p": 18, "c": 42, "f": 12},
            {"name": "Vegetable biryani (no cream)", "cal": 340, "p": 8, "c": 52, "f": 9},
            {"name": "Chole + roti + salad", "cal": 390, "p": 14, "c": 50, "f": 12},
            {"name": "Mixed bean salad bowl", "cal": 320, "p": 16, "c": 42, "f": 8},
            {"name": "Sambar rice + papad", "cal": 350, "p": 12, "c": 55, "f": 6},
        ],
        "dinner": [
            {"name": "Vegetable soup + bread", "cal": 220, "p": 6, "c": 32, "f": 5},
            {"name": "Tofu curry + roti", "cal": 300, "p": 16, "c": 30, "f": 12},
            {"name": "Mushroom stir-fry + quinoa", "cal": 290, "p": 12, "c": 38, "f": 9},
            {"name": "Khichdi with veggies", "cal": 280, "p": 10, "c": 42, "f": 5},
            {"name": "Lentil soup + multigrain roti", "cal": 270, "p": 14, "c": 35, "f": 6},
            {"name": "Stuffed bell peppers", "cal": 250, "p": 8, "c": 30, "f": 10},
            {"name": "Mixed dal + brown rice", "cal": 320, "p": 14, "c": 48, "f": 5},
        ],
        "snack": [
            {"name": "Roasted chickpeas", "cal": 130, "p": 6, "c": 20, "f": 3},
            {"name": "Fruit bowl", "cal": 100, "p": 1, "c": 24, "f": 0.5},
            {"name": "Trail mix", "cal": 170, "p": 5, "c": 14, "f": 12},
            {"name": "Hummus + veggie sticks", "cal": 120, "p": 5, "c": 14, "f": 5},
            {"name": "Date + almond energy balls", "cal": 140, "p": 4, "c": 20, "f": 6},
            {"name": "Peanut butter banana", "cal": 190, "p": 6, "c": 26, "f": 8},
            {"name": "Roasted makhana", "cal": 110, "p": 4, "c": 18, "f": 2},
        ],
    },
}

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def generate_meal_plan(goal: str = "maintenance", diet: str = "veg", budget_friendly: bool = True) -> list:
    """
    Generate a weekly meal plan based on user preferences.
    Returns a list of daily meal plans.
    """
    diet_key = diet if diet in MEAL_PLAN_DATABASE else "veg"
    meals = MEAL_PLAN_DATABASE[diet_key]
    plan = []

    for i, day in enumerate(DAYS_OF_WEEK):
        day_plan = {"day": day, "meals": []}
        for meal_type in ["breakfast", "lunch", "snack", "dinner"]:
            options = meals[meal_type]
            choice = options[i % len(options)]

            # Adjust calories by goal
            cal_factor = 1.0
            if goal == "weight_loss":
                cal_factor = 0.85
            elif goal == "muscle_gain":
                cal_factor = 1.15

            day_plan["meals"].append({
                "meal_type": meal_type,
                "food_name": choice["name"],
                "calories": round(choice["cal"] * cal_factor),
                "protein": round(choice["p"] * cal_factor, 1),
                "carbs": round(choice["c"] * cal_factor, 1),
                "fats": round(choice["f"] * cal_factor, 1),
                "budget_friendly": budget_friendly,
            })
        plan.append(day_plan)

    return plan


# ─────────────────────────────────────────────
# Badge / Achievement System
# ─────────────────────────────────────────────

BADGES = [
    {"id": "first_scan", "name": "First Scan", "icon": "📸", "desc": "Scanned your first food item!", "requirement": lambda logs, streak: len(logs) >= 1},
    {"id": "five_logs", "name": "Logging Pro", "icon": "📝", "desc": "Logged 5 meals!", "requirement": lambda logs, streak: len(logs) >= 5},
    {"id": "ten_logs", "name": "Dedicated Logger", "icon": "🏆", "desc": "Logged 10 meals!", "requirement": lambda logs, streak: len(logs) >= 10},
    {"id": "healthy_streak3", "name": "Healthy Start", "icon": "🌱", "desc": "3-day healthy eating streak!", "requirement": lambda logs, streak: streak >= 3},
    {"id": "healthy_streak7", "name": "Week Warrior", "icon": "⚡", "desc": "7-day streak! Unstoppable!", "requirement": lambda logs, streak: streak >= 7},
    {"id": "health_master", "name": "Health Master", "icon": "👑", "desc": "Average health score above 75!", "requirement": lambda logs, streak: len(logs) > 0 and (sum(l.health_score for l in logs) / len(logs)) > 75},
    {"id": "calorie_watch", "name": "Calorie Watcher", "icon": "🔥", "desc": "Kept average calories under 350!", "requirement": lambda logs, streak: len(logs) > 3 and (sum(l.calories for l in logs) / len(logs)) < 350},
]


def check_new_badges(food_logs: list, streak: int, existing_badge_ids: list) -> list:
    """
    Check if the user has earned any new badges.
    Returns a list of newly earned badge dicts.
    """
    new_badges = []
    for badge in BADGES:
        if badge["id"] not in existing_badge_ids:
            try:
                if badge["requirement"](food_logs, streak):
                    new_badges.append({
                        "badge_id": badge["id"],
                        "badge_name": badge["name"],
                        "badge_icon": badge["icon"],
                        "description": badge["desc"],
                    })
            except Exception:
                pass
    return new_badges

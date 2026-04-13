"""
NutriMind – AI Food Decision Coach
Main FastAPI Application

Run with: uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import os

from .database import get_db, init_db, engine, Base
from .models import User, FoodLog, Achievement, MealPlan, WaterLog, WeightLog
from .auth import hash_password, verify_password, create_access_token, decode_token, oauth2_scheme
from .ai_engine import (
    scan_food,
    get_contextual_recommendations,
    analyze_behavior,
    generate_meal_plan,
    check_new_badges,
    FOOD_DATABASE,
)

# ─────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────

app = FastAPI(
    title="NutriMind – AI Food Decision Coach",
    description="AI-powered food decision coaching API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.on_event("startup")
def on_startup():
    """Initialize the database on startup."""
    Base.metadata.create_all(bind=engine)


# ─────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ProfileUpdate(BaseModel):
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    gender: Optional[str] = None
    goal: Optional[str] = None
    diet_preference: Optional[str] = None
    health_conditions: Optional[str] = None
    activity_level: Optional[str] = None
    daily_calorie_target: Optional[int] = None

class FoodScanRequest(BaseModel):
    food_name: str

class FoodLogRequest(BaseModel):
    food_name: str
    calories: float
    protein: float
    carbs: float
    fats: float
    health_score: int
    meal_type: Optional[str] = "snack"

class WaterLogRequest(BaseModel):
    amount_ml: int = 250

class WeightLogRequest(BaseModel):
    weight: float
    unit: str = "kg"


# ─────────────────────────────────────────────
# Helper: Get current user from token
# ─────────────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ─────────────────────────────────────────────
# ROUTES: Frontend Serving
# ─────────────────────────────────────────────

@app.get("/")
async def serve_frontend():
    """Serve the main frontend HTML."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "NutriMind API is running. Frontend not found."}


# ─────────────────────────────────────────────
# ROUTES: Authentication
# ─────────────────────────────────────────────

@app.post("/api/auth/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        name=req.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"user_id": user.id, "email": user.email})
    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "profile_complete": False,
        }
    }


@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": user.id, "email": user.email})
    profile_complete = all([user.age, user.weight, user.height, user.goal])
    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "profile_complete": profile_complete,
        }
    }


# ─────────────────────────────────────────────
# ROUTES: User Profile
# ─────────────────────────────────────────────

@app.get("/api/profile")
def get_profile(user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "weight": user.weight,
        "height": user.height,
        "gender": user.gender,
        "goal": user.goal,
        "diet_preference": user.diet_preference,
        "health_conditions": user.health_conditions,
        "activity_level": user.activity_level,
        "daily_calorie_target": user.daily_calorie_target,
        "points": user.points,
        "streak_days": user.streak_days,
    }


@app.put("/api/profile")
def update_profile(update: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update the user's profile and health details."""
    for field, value in update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(user, field, value)

    # Auto-calculate calorie target based on goal if not set
    if update.goal and update.weight and update.height and update.age:
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age
        if user.gender == "male":
            bmr += 5
        else:
            bmr -= 161

        activity_multiplier = {"sedentary": 1.2, "moderate": 1.55, "active": 1.75}
        tdee = bmr * activity_multiplier.get(user.activity_level, 1.55)

        if user.goal == "weight_loss":
            user.daily_calorie_target = int(tdee - 400)
        elif user.goal == "muscle_gain":
            user.daily_calorie_target = int(tdee + 300)
        else:
            user.daily_calorie_target = int(tdee)

    db.commit()
    db.refresh(user)
    return {"message": "Profile updated", "daily_calorie_target": user.daily_calorie_target}


# ─────────────────────────────────────────────
# ROUTES: AI Food Scanner
# ─────────────────────────────────────────────

@app.post("/api/scan-food")
def scan_food_item(req: FoodScanRequest, user: User = Depends(get_current_user)):
    """
    AI Food Scanner: detect food and return nutritional info.
    In production, this would accept an image and run it through a CNN.
    """
    result = scan_food(req.food_name)

    # Adjust health score based on user conditions
    if user.health_conditions:
        conditions = user.health_conditions.lower()
        if "diabetes" in conditions and result["carbs"] > 40:
            result["health_score"] = max(result["health_score"] - 15, 5)
            result["warning"] = "⚠️ High carbs detected. Be cautious with diabetes."
        if "bp" in conditions or "blood pressure" in conditions:
            if result["category"] in ["junk", "carb_heavy"]:
                result["health_score"] = max(result["health_score"] - 10, 5)
                result["warning"] = result.get("warning", "") + " ⚠️ Consider low-sodium options for BP management."

    return result


@app.get("/api/food-database")
def get_food_list(user: User = Depends(get_current_user)):
    """Get the list of recognized foods for autocomplete."""
    return {"foods": sorted(FOOD_DATABASE.keys())}


# ─────────────────────────────────────────────
# ROUTES: Food Logging
# ─────────────────────────────────────────────

@app.post("/api/food-log")
def log_food(req: FoodLogRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Log a food item to the user's history."""
    log = FoodLog(
        user_id=user.id,
        food_name=req.food_name,
        calories=req.calories,
        protein=req.protein,
        carbs=req.carbs,
        fats=req.fats,
        health_score=req.health_score,
        meal_type=req.meal_type,
    )
    db.add(log)

    # Update streak
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if user.last_log_date != today:
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        if user.last_log_date == yesterday:
            user.streak_days += 1
        else:
            user.streak_days = 1
        user.last_log_date = today

    # Award points based on health score
    points_earned = max(req.health_score // 10, 1)
    user.points += points_earned

    # Check for new badges
    all_logs = db.query(FoodLog).filter(FoodLog.user_id == user.id).all()
    existing_badges = [a.badge_id for a in db.query(Achievement).filter(Achievement.user_id == user.id).all()]
    new_badges = check_new_badges(all_logs + [log], user.streak_days, existing_badges)

    for badge in new_badges:
        achievement = Achievement(
            user_id=user.id,
            badge_id=badge["badge_id"],
            badge_name=badge["badge_name"],
            badge_icon=badge["badge_icon"],
            description=badge["description"],
        )
        db.add(achievement)
        user.points += 50  # Bonus points for badges

    db.commit()

    return {
        "message": "Food logged successfully! 🎉",
        "points_earned": points_earned,
        "total_points": user.points,
        "streak": user.streak_days,
        "new_badges": new_badges,
    }

@app.delete("/api/food-log/{log_id}")
def delete_food_log(log_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a specific food log."""
    log = db.query(FoodLog).filter(FoodLog.id == log_id, FoodLog.user_id == user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    db.delete(log)
    db.commit()
    return {"message": "Log deleted successfully"}


@app.get("/api/food-logs")
def get_food_logs(days: int = 7, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the user's food logs for the specified number of days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    logs = db.query(FoodLog).filter(
        FoodLog.user_id == user.id,
        FoodLog.logged_at >= cutoff
    ).order_by(FoodLog.logged_at.desc()).all()

    return {
        "logs": [
            {
                "id": log.id,
                "food_name": log.food_name,
                "calories": log.calories,
                "protein": log.protein,
                "carbs": log.carbs,
                "fats": log.fats,
                "health_score": log.health_score,
                "meal_type": log.meal_type,
                "logged_at": log.logged_at.isoformat() if log.logged_at else None,
            }
            for log in logs
        ]
    }


# ─────────────────────────────────────────────
# ROUTES: Dashboard & Analytics
# ─────────────────────────────────────────────

@app.get("/api/dashboard")
def get_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the user's daily dashboard summary."""
    today = datetime.now(timezone.utc).date()
    today_start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)

    # Today's logs
    today_logs = db.query(FoodLog).filter(
        FoodLog.user_id == user.id,
        FoodLog.logged_at >= today_start
    ).all()

    total_calories = sum(log.calories for log in today_logs)
    total_protein = sum(log.protein for log in today_logs)
    total_carbs = sum(log.carbs for log in today_logs)
    total_fats = sum(log.fats for log in today_logs)
    avg_health = round(sum(log.health_score for log in today_logs) / max(len(today_logs), 1), 1)

    # All time logs for behavior
    all_logs = db.query(FoodLog).filter(FoodLog.user_id == user.id).order_by(FoodLog.logged_at.desc()).limit(50).all()
    behavior = analyze_behavior(all_logs)

    # Achievements
    achievements = db.query(Achievement).filter(Achievement.user_id == user.id).all()

    return {
        "user": {
            "name": user.name,
            "points": user.points,
            "streak_days": user.streak_days,
            "daily_calorie_target": user.daily_calorie_target,
            "goal": user.goal,
        },
        "today": {
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "carbs": round(total_carbs, 1),
            "fats": round(total_fats, 1),
            "avg_health_score": avg_health,
            "meals_logged": len(today_logs),
            "calorie_target": user.daily_calorie_target,
            "calorie_remaining": max(user.daily_calorie_target - total_calories, 0),
        },
        "behavior": behavior,
        "achievements": [
            {
                "badge_id": a.badge_id,
                "badge_name": a.badge_name,
                "badge_icon": a.badge_icon,
                "description": a.description,
                "earned_at": a.earned_at.isoformat() if a.earned_at else None,
            }
            for a in achievements
        ],
    }


# ─────────────────────────────────────────────
# ROUTES: Context-Aware Recommendations
# ─────────────────────────────────────────────

@app.get("/api/recommendations")
def get_recommendations(user: User = Depends(get_current_user)):
    """Get context-aware food recommendations based on time and user profile."""
    hour = datetime.now().hour
    result = get_contextual_recommendations(
        hour=hour,
        goal=user.goal,
        diet=user.diet_preference,
    )
    return result


# ─────────────────────────────────────────────
# ROUTES: Meal Planner
# ─────────────────────────────────────────────

@app.get("/api/meal-plan")
def get_meal_plan(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate or retrieve a personalized weekly meal plan."""
    # Check if user already has a plan (less than 7 days old)
    existing_plan = db.query(MealPlan).filter(MealPlan.user_id == user.id).all()
    
    if existing_plan:
        # Format existing plan
        plan = []
        days = sorted(list(set(p.day_of_week for p in existing_plan)))
        # Restore order
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        sorted_days = [d for d in day_order if d in days]
        
        for day in sorted_days:
            day_meals = [p for p in existing_plan if p.day_of_week == day]
            plan.append({
                "day": day,
                "meals": [
                    {
                        "meal_type": m.meal_type,
                        "food_name": m.food_name,
                        "calories": m.calories,
                        "protein": m.protein,
                        "carbs": m.carbs,
                        "fats": m.fats,
                        "budget_friendly": m.budget_friendly,
                    }
                    for m in day_meals
                ]
            })
        return {"meal_plan": plan}

    # Generate new plan if none exists
    generated = generate_meal_plan(
        goal=user.goal or "maintenance",
        diet=user.diet_preference or "veg",
        budget_friendly=True,
    )
    
    # Save to database
    for day in generated:
        for meal in day["meals"]:
            db_meal = MealPlan(
                user_id=user.id,
                day_of_week=day["day"],
                meal_type=meal["meal_type"],
                food_name=meal["food_name"],
                calories=meal["calories"],
                protein=meal["protein"],
                carbs=meal["carbs"],
                fats=meal["fats"],
                budget_friendly=meal["budget_friendly"]
            )
            db.add(db_meal)
    
    db.commit()
    return {"meal_plan": generated}


@app.post("/api/meal-plan/reset")
def reset_meal_plan(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Clear the existing meal plan so a new one can be generated."""
    db.query(MealPlan).filter(MealPlan.user_id == user.id).delete()
    db.commit()
    return {"message": "Meal plan reset successfully"}


# ─────────────────────────────────────────────
# ROUTES: Achievements
# ─────────────────────────────────────────────

@app.get("/api/achievements")
def get_achievements(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all user achievements/badges."""
    achievements = db.query(Achievement).filter(Achievement.user_id == user.id).all()
    return {
        "achievements": [
            {
                "badge_id": a.badge_id,
                "badge_name": a.badge_name,
                "badge_icon": a.badge_icon,
                "description": a.description,
                "earned_at": a.earned_at.isoformat() if a.earned_at else None,
            }
            for a in achievements
        ],
        "total_points": user.points,
        "streak": user.streak_days,
    }


# ─────────────────────────────────────────────
# ROUTES: Water / Hydration Tracking
# ─────────────────────────────────────────────

@app.post("/api/water-log")
def log_water(req: WaterLogRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Log water intake in ml."""
    log = WaterLog(user_id=user.id, amount_ml=req.amount_ml)
    db.add(log)
    db.commit()

    # Get today's total
    today = datetime.now(timezone.utc).date()
    today_start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    today_logs = db.query(WaterLog).filter(
        WaterLog.user_id == user.id,
        WaterLog.logged_at >= today_start
    ).all()
    total_ml = sum(w.amount_ml for w in today_logs)

    return {
        "message": f"Logged {req.amount_ml}ml 💧",
        "today_total_ml": total_ml,
        "today_glasses": round(total_ml / 250, 1),
        "goal_ml": 2500,
    }


@app.get("/api/water-log")
def get_water_log(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get today's water intake summary."""
    today = datetime.now(timezone.utc).date()
    today_start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    today_logs = db.query(WaterLog).filter(
        WaterLog.user_id == user.id,
        WaterLog.logged_at >= today_start
    ).all()
    total_ml = sum(w.amount_ml for w in today_logs)

    return {
        "today_total_ml": total_ml,
        "today_glasses": round(total_ml / 250, 1),
        "goal_ml": 2500,
        "logs": [
            {"amount_ml": w.amount_ml, "logged_at": w.logged_at.isoformat()}
            for w in today_logs
        ]
    }


# ─────────────────────────────────────────────
# ROUTES: Calorie History (for charts)
# ─────────────────────────────────────────────

@app.get("/api/calorie-history")
def get_calorie_history(days: int = 7, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get daily calorie totals for the last N days (for bar chart)."""
    history = []
    for i in range(days - 1, -1, -1):
        day = datetime.now(timezone.utc).date() - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        day_logs = db.query(FoodLog).filter(
            FoodLog.user_id == user.id,
            FoodLog.logged_at >= day_start,
            FoodLog.logged_at < day_end
        ).all()
        total_cal = sum(log.calories for log in day_logs)
        history.append({
            "date": day.isoformat(),
            "day_label": day.strftime("%a"),
            "calories": round(total_cal, 1),
            "meals": len(day_logs),
        })

    return {
        "history": history,
        "calorie_target": user.daily_calorie_target,
    }
# ─────────────────────────────────────────────
# ROUTES: Weight Tracking
# ─────────────────────────────────────────────

@app.post("/api/weight-log")
def log_weight(req: WeightLogRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Log user's current weight."""
    log = WeightLog(user_id=user.id, weight=req.weight)
    db.add(log)
    
    # Update user's current weight in profile too
    user.weight = req.weight
    
    db.commit()
    return {"message": f"Weight logged: {req.weight}kg ⚖️", "weight": req.weight}

@app.delete("/api/weight-log/{log_id}")
def delete_weight_log(log_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a weight log entry."""
    log = db.query(WeightLog).filter(WeightLog.id == log_id, WeightLog.user_id == user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
    return {"message": "Weight log deleted"}

@app.get("/api/weight-history")
def get_weight_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get weight history for charts."""
    logs = db.query(WeightLog).filter(WeightLog.user_id == user.id).order_by(WeightLog.logged_at.asc()).all()
    return {
        "history": [
            {"weight": log.weight, "date": log.logged_at.isoformat()}
            for log in logs
        ]
    }

# ─────────────────────────────────────────────
# ROUTES: Grocery List
# ─────────────────────────────────────────────

@app.get("/api/grocery-list")
def get_grocery_list(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate a grocery list from the current meal plan."""
    plan = db.query(MealPlan).filter(MealPlan.user_id == user.id).all()
    if not plan:
        return {"grocery_list": [], "message": "No meal plan found. Generate one first!"}
    
    # Mock aggregation of ingredients
    # In a real app, you'd map food_name to a list of ingredients
    unique_items = sorted(list(set(m.food_name for m in plan)))
    
    grocery_list = []
    category_map = {
        "Produce": ["Salad", "Veggie", "Apple", "Banana", "Cucumber", "Spinach", "Bell peppers", "Mushroom"],
        "Protein": ["Chicken", "Fish", "Paneer", "Tofu", "Egg", "Tuna", "Dal", "Chickpeas"],
        "Pantry": ["Rice", "Oats", "Quinoa", "Pasta", "Flour", "Oil", "Nuts", "Seeds"],
        "Dairy": ["Curd", "Milk", "Cheese", "Yogurt", "Paneer"],
    }
    
    for item in unique_items:
        found_cat = "Other"
        for cat, keywords in category_map.items():
            if any(kw.lower() in item.lower() for kw in keywords):
                found_cat = cat
                break
        grocery_list.append({"item": item, "category": found_cat, "quantity": "1 unit"})
        
    return {"grocery_list": grocery_list}

# ─────────────────────────────────────────────
# ROUTES: Recipes
# ─────────────────────────────────────────────

@app.get("/api/recipe/{food_name}")
def get_recipe(food_name: str, user: User = Depends(get_current_user)):
    """Get a mock recipe for a food item."""
    # This would ideally call a recipe API or use a local DB
    # We'll just generate a nice looking mock response
    return {
        "food_name": food_name,
        "prep_time": "15-20 min",
        "servings": 1,
        "difficulty": "Easy",
        "ingredients": [
            f"Fresh {food_name}",
            "Olive oil",
            "Salt & Black pepper",
            "Seasonal herbs",
            "Garlic and Ginger"
        ],
        "instructions": [
            f"Thoroughly clean and prep the {food_name}.",
            "Heat a pan with olive oil over medium-high heat.",
            "Season according to your taste preferences.",
            f"Cook until {food_name} is tender and aromatic.",
            "Garnish with herbs and serve hot!"
        ],
        "pro_tip": "Add a dash of lemon juice for enhanced flavor balance."
    }

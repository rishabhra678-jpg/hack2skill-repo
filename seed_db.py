"""
NutriMind – Database Seed Script
Populate the database with sample data for demonstration.
"""

import random
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models import User, FoodLog, Achievement, WaterLog
from backend.auth import hash_password
from datetime import datetime, timedelta, timezone

def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Create a demo user
    demo_user = User(
        email="demo@nutrimind.ai",
        hashed_password=hash_password("password123"),
        name="Alex Smith",
        age=28,
        weight=75.5,
        height=180.0,
        gender="male",
        goal="muscle_gain",
        diet_preference="non_veg",
        activity_level="active",
        daily_calorie_target=2800,
        points=450,
        streak_days=5,
        last_log_date=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    
    # 2. Add some food logs for the past few days
    foods = [
        {"name": "Oatmeal", "cal": 250, "p": 10, "c": 40, "f": 5, "score": 90, "type": "breakfast"},
        {"name": "Chicken Breast", "cal": 400, "p": 45, "c": 0, "f": 10, "score": 85, "type": "lunch"},
        {"name": "Salmon", "cal": 350, "p": 35, "c": 0, "f": 15, "score": 92, "type": "dinner"},
        {"name": "Greek Yogurt", "cal": 150, "p": 15, "c": 10, "f": 2, "score": 88, "type": "snack"},
        {"name": "Pizza", "cal": 800, "p": 25, "c": 100, "f": 35, "score": 30, "type": "dinner"},
    ]
    
    now = datetime.now(timezone.utc)
    for i in range(7):
        day = now - timedelta(days=i)
        for f in foods[:random.randint(2, 4)]:
            log = FoodLog(
                user_id=demo_user.id,
                food_name=f["name"],
                calories=f["cal"],
                protein=f["p"],
                carbs=f["c"],
                fats=f["f"],
                health_score=f["score"],
                meal_type=f["type"],
                logged_at=day
            )
            db.add(log)
            
    # 3. Add some water logs
    for i in range(5):
        w = WaterLog(
            user_id=demo_user.id,
            amount_ml=250,
            logged_at=now - timedelta(hours=i)
        )
        db.add(w)
        
    # 4. Add achievements
    achievements = [
        {"id": "first_scan", "name": "First Scan", "icon": "📸", "desc": "Scanned your first food item!"},
        {"id": "five_logs", "name": "Logging Pro", "icon": "📝", "desc": "Logged 5 meals!"},
    ]
    for a in achievements:
        ach = Achievement(
            user_id=demo_user.id,
            badge_id=a["id"],
            badge_name=a["name"],
            badge_icon=a["icon"],
            description=a["desc"]
        )
        db.add(ach)
        
    db.commit()
    db.close()
    print("Database seeded successfully with demo user 'demo@nutrimind.ai'!")

if __name__ == "__main__":
    seed()
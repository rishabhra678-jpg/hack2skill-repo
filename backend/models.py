"""
NutriMind – Database Models
All SQLAlchemy ORM models for user profiles, food logs, meal plans, and achievements.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)           # kg
    height = Column(Float, nullable=True)           # cm
    gender = Column(String(20), nullable=True)      # male, female, other
    goal = Column(String(50), nullable=True)        # weight_loss, muscle_gain, maintenance
    diet_preference = Column(String(30), nullable=True)  # veg, non_veg, vegan
    health_conditions = Column(Text, nullable=True)      # comma-separated: diabetes,bp
    activity_level = Column(String(30), default="moderate")  # sedentary, moderate, active
    daily_calorie_target = Column(Integer, default=2000)
    points = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    last_log_date = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    food_logs = relationship("FoodLog", back_populates="user")
    achievements = relationship("Achievement", back_populates="user")
    weight_logs = relationship("WeightLog", back_populates="user")


class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_name = Column(String(200), nullable=False)
    calories = Column(Float, default=0)
    protein = Column(Float, default=0)      # grams
    carbs = Column(Float, default=0)        # grams
    fats = Column(Float, default=0)         # grams
    health_score = Column(Integer, default=50)  # 0-100
    meal_type = Column(String(30), nullable=True)  # breakfast, lunch, dinner, snack
    image_path = Column(String(500), nullable=True)
    logged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="food_logs")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(String(50), nullable=False)
    badge_name = Column(String(100), nullable=False)
    badge_icon = Column(String(10), nullable=True)
    description = Column(String(255), nullable=True)
    earned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="achievements")


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_ml = Column(Integer, default=250)  # milliliters
    logged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_of_week = Column(String(15), nullable=False)  # monday, tuesday...
    meal_type = Column(String(30), nullable=False)     # breakfast, lunch, dinner, snack
    food_name = Column(String(200), nullable=False)
    calories = Column(Float, default=0)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fats = Column(Float, default=0)
    budget_friendly = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weight = Column(Float, nullable=False)
    logged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="weight_logs")

# NutriMind – AI Food Decision Coach 🧠🥗

NutriMind is a premium, AI-powered health and nutrition coaching application designed to help users make smarter food choices in real-time. It features a stunning glassmorphism UI, a robust FastAPI backend, and an intelligent recommendation engine.

![NutriMind Dashboard](https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=1000&q=80)

## ✨ Core Features

- **📸 AI Food Scanner**: Identify food items from photos (simulated) or text search and get instant nutritional data.
- **🎯 Context-Aware Recommendations**: Get personalized meal suggestions based on the time of day, your goals, and dietary preferences.
- **📊 Interactive Dashboard**: Track your daily calories, macros, and hydration with beautiful animated visualizations.
- **🏆 Gamified Achievements**: Earn points and unlock badges for healthy streaks and consistent logging.
- **📅 Weekly Meal Planner**: AI-generated weekly plans tailored to your specific health goals (Weight Loss, Muscle Gain, or Maintenance).
- **🧠 Behavioral Insights**: AI-driven analysis of your eating patterns with actionable "nudges" for improvement.

## 🛠️ Tech Stack

- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), JavaScript (ES6+).
- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic.
- **Database**: SQLite (local storage).
- **Auth**: JWT (JSON Web Tokens) with Secure Password Hashing (Bcrypt).

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/nutri-minds.git
   cd nutri-minds
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```
   The app will be available at `http://localhost:8000`.

## 📂 Project Structure

```text
nutri-minds/
├── backend/            # FastAPI Backend
│   ├── ai_engine.py    # AI logic & mock database
│   ├── auth.py         # JWT & Security
│   ├── database.py     # SQLite/SQLAlchemy setup
│   ├── main.py         # API endpoints
│   └── models.py       # Database schemas
├── frontend/           # Vanilla JS Frontend
│   ├── index.html      # Main UI structure
│   ├── style.css       # Premium Glassmorphism styles
│   └── app.js          # App logic & API integration
├── requirements.txt    # Python dependencies
└── run.py              # Application entry point
```

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---
Built with ❤️ by NutriMind Team

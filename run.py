import uvicorn
import os
import sys

# Ensure the current directory is in the path so we can import 'backend'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("NutriMind API is starting...")
    print("Link Local: http://localhost:8000")
    print("Info: To access the frontend, open the URL above.")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "backend.main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False  # Disable reload in production
    )

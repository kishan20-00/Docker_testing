# main.py
from fastapi import FastAPI, HTTPException
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression # Example using a simple sklearn model
# import matplotlib.pyplot as plt # Matplotlib is typically for plotting, not direct API returns

# --- 1. Define Settings Class for Environment Variables ---
# BaseSettings from pydantic-settings helps manage settings,
# validating data and reading from environment variables by default.
class Settings(BaseSettings):
    """
    Settings class to load environment variables.
    pydantic-settings automatically looks for environment variables
    matching the field names (case-insensitive by default).
    """
    app_name: str = "MyCoolFastAPIApp" # Default value if APP_NAME is not set
    api_key: str # This variable is required. If not set, pydantic will raise an error.
    database_url: str = "sqlite:///./sql_app.db" # Another example with a default

    # Configuration for how settings are loaded.
    # '.env' file support is automatically enabled if python-dotenv is installed.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False # Environment variables can be APP_NAME or app_name
    )

# --- 2. Initialize FastAPI Application ---
app = FastAPI(
    title="Environment Variable and Data Science Example API",
    description="A FastAPI app demonstrating environment variables and basic data science library usage.",
    version="1.0.1" # Updated version to reflect changes
)

# --- 3. Load Settings ---
# Create an instance of the Settings class.
# This will automatically load variables from .env file (if exists)
# and then from actual environment variables, with env vars taking precedence.
try:
    settings = Settings()
except Exception as e:
    # Handle cases where required environment variables are missing
    print(f"Error loading settings: {e}")
    settings = None # Indicate that settings failed to load


# --- 4. Define Endpoints ---

@app.get("/")
async def read_root():
    """
    Root endpoint that returns a welcome message using the app name.
    """
    if settings:
        return {"message": f"Welcome to {settings.app_name}!"}
    else:
        raise HTTPException(status_code=500, detail="Application settings not loaded.")

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """
    Example endpoint.
    """
    return {"item_id": item_id, "message": "This is a sample item."}

@app.get("/secure-data")
async def get_secure_data(user_api_key: str):
    """
    A simple example of a protected endpoint using the API_KEY from settings.
    In a real app, use proper authentication (e.g., OAuth2 with bearer tokens).
    """
    if not settings or user_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")
    return {"message": "Access granted to secure data!", "database_info": settings.database_url}

@app.get("/analyze-data")
async def analyze_data():
    """
    Endpoint demonstrating the use of NumPy, Pandas, and Sci-kit Learn.
    It creates a sample dataset, performs a simple calculation,
    and pretends to train a simple model.
    """
    # Using NumPy
    data = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    mean_value = np.mean(data)
    std_dev = np.std(data)

    # Using Pandas to create a DataFrame
    df = pd.DataFrame({
        'feature1': np.random.rand(10) * 100,
        'feature2': np.random.rand(10) * 50,
        'target': np.random.rand(10) * 200
    })
    df_description = df.describe().to_dict() # Get descriptive statistics

    # Using Sci-kit Learn (a very basic example: dummy model or import check)
    # In a real scenario, you'd train a model with actual features and targets.
    try:
        model = LinearRegression()
        # For demonstration, let's just show it's imported and could be used
        # If we had actual features X and target y, we'd do model.fit(X, y)
        sklearn_info = "sklearn.linear_model.LinearRegression imported successfully."
    except Exception as e:
        sklearn_info = f"Failed to load sklearn model: {e}"

    return {
        "message": "Data analysis performed using NumPy, Pandas, and Sci-kit Learn.",
        "numpy_results": {
            "mean": float(mean_value), # Convert numpy types to native Python types for JSON serialization
            "standard_deviation": float(std_dev)
        },
        "pandas_dataframe_description": df_description,
        "sklearn_status": sklearn_info
    }

# --- 5. How to Run This Application ---
# To run this application, you will need Uvicorn.
# 1. Save the code above as `main.py`.
# 2. Ensure necessary libraries are installed (from your requirements.txt):
#    pip install -r requirements.txt
# 3. Create a `.env` file in the same directory as `main.py` (optional, but recommended):
#    APP_NAME="My Production API"
#    API_KEY="supersecretapikey123"
#    DATABASE_URL="postgresql://user:password@host:port/dbname"
# 4. Run the application from your terminal:
#    uvicorn main:app --reload

# After running, open your browser to:
# - http://127.0.0.1:8000/
# - http://127.0.0.1:8000/docs (for interactive API documentation)
# - Try http://127.0.0.1:8000/secure-data?user_api_key=your_api_key_from_env
# - Try the new data analysis endpoint: http://127.0.0.1:8000/analyze-data

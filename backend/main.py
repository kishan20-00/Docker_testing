# main.py
from fastapi import FastAPI, HTTPException
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

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
    title="Environment Variable Example API",
    description="A simple FastAPI app demonstrating environment variable usage.",
    version="1.0.0"
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
    # In a real-world scenario, you might want to log this and exit
    # sys.exit(1) or raise the exception. For this example, we'll let
    # FastAPI start but endpoint calls related to missing vars will fail.
    # For demonstration, we'll just print and let it potentially crash later.
    settings = None # Indicate that settings failed to load


# --- 4. Define an Endpoint that Uses Environment Variables ---

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

# --- 5. How to Run This Application ---
# To run this application, you will need Uvicorn.
# 1. Save the code above as `main.py`.
# 2. Install necessary libraries:
#    pip install fastapi uvicorn "pydantic-settings[dotenv]"
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
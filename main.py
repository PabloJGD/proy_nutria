import uvicorn
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv(dotenv_path="configs/.env")

from src.api.app import app

if __name__ == "__main__":
    # check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not found in configs/.env")
    
    print("Starting AI Chef Agent API...")
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=True)

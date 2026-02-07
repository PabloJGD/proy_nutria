from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import ValidationError
import shutil
import os
import json
from src.models.schemas import AgentInput, UserProfile
from src.agents.chef_agent import process_request

app = FastAPI(title="AI Chef Agent", description="Generates recipes based on ingredients and profile.")

@app.post("/recommend")
async def recommend_recipe(
    text_description: str = Form(None),
    image: UploadFile = File(None),
    user_profile: str = Form(..., description="JSON string of UserProfile")
):
    """
    Endpoint to get recipe recommendations.
    Accepts text description, an image file, and a JSON user profile.
    """
    
    # Check inputs
    if not text_description and not image:
        raise HTTPException(status_code=400, detail="Provide at least text description or an image.")
    
    # Parse Profile
    try:
        profile_dict = json.loads(user_profile)
        profile = UserProfile(**profile_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user_profile JSON: {str(e)}")
    
    image_path = None
    if image:
        # Save temp file
        os.makedirs("temp", exist_ok=True)
        image_path = f"temp/{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
    # Construct Input
    agent_input = AgentInput(
        image_data=image_path if image_path else None,
        text_description=text_description,
        user_profile=profile
    )
    
    # Run Agent
    try:
        result = process_request(agent_input)
        
        # Cleanup
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            
        return {"recommendation": result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def home():
    return {"message": "AI Chef API is running."}

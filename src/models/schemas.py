from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class Ingredient(BaseModel):
    name: str = Field(description="Name of the ingredient")
    quantity: Optional[str] = Field(None, description="Estimated quantity if visible/known")

class NutritionalInfo(BaseModel):
    calories: float = Field(description="Total calories")
    protein: float = Field(description="Protein in grams")
    carbohydrates: float = Field(description="Carbohydrates in grams")
    fat: float = Field(description="Fat in grams")
    additional_info: Optional[Dict[str, float]] = Field(default_factory=dict, description="Other nutrients like vitamins currently")

class Recipe(BaseModel):
    title: str = Field(description="Title of the dish")
    description: str = Field(description="Short description of the dish")
    ingredients: List[Ingredient] = Field(description="List of ingredients used")
    instructions: List[str] = Field(description="Step by step cooking instructions")
    nutritional_info: Optional[NutritionalInfo] = Field(None, description="Nutritional breakdown")
    prep_time: Optional[str] = Field(None, description="Preparation time")
    cook_time: Optional[str] = Field(None, description="Cooking time")

class UserProfile(BaseModel):
    name: Optional[str] = Field("User", description="User's name")
    age: Optional[int] = Field(None, description="User's age")
    dietary_restrictions: List[str] = Field(default_factory=list, description="e.g. ['Vegan', 'Gluten-Free', 'Low-Carb']")
    allergies: List[str] = Field(default_factory=list, description="List of allergies")
    health_goals: Optional[str] = Field(None, description="e.g. 'Lose weight', 'Build muscle'")
    
class AgentInput(BaseModel):
    image_data: Optional[str] = Field(None, description="Base64 encoded image or URL")
    text_description: Optional[str] = Field(None, description="Text description of ingredients")
    user_profile: UserProfile = Field(description="User profile information")

class AgentOutput(BaseModel):
    recipes: List[Recipe] = Field(description="List of recommended recipes")
    advice: Optional[str] = Field(None, description="General nutritional advice based on the request")

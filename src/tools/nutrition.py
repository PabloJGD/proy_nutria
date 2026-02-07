import os
import requests
from langchain_core.tools import tool
from typing import List, Optional

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")

@tool
def find_recipes_by_ingredients(ingredients: str, number: int = 3) -> str:
    """
    Search for recipes using a comma-separated list of ingredients.
    Returns a JSON string with recipe titles and IDs.
    """
    if not SPOONACULAR_API_KEY:
        return "Error: Spoonacular API Key not set."
    
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "ingredients": ingredients,
        "number": number,
        "ranking": 1 # maximize used ingredients
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Simplify output
        results = []
        for item in data:
            results.append(f"ID: {item['id']} - Title: {item['title']} - Used Ingredients: {item['usedIngredientCount']}")
        
        return "\n".join(results)
    except Exception as e:
        return f"Error fetching recipes: {str(e)}"

@tool
def get_recipe_details(recipe_id: int) -> str:
    """
    Get detailed information about a recipe by its ID, including nutrition.
    """
    if not SPOONACULAR_API_KEY:
        return "Error: Spoonacular API Key not set."

    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "includeNutrition": True
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant info
        title = data.get('title')
        ready_in = data.get('readyInMinutes')
        servings = data.get('servings')
        nutrition = data.get('nutrition', {}).get('nutrients', [])
        
        # Format nutrition nicely
        nut_str = ", ".join([f"{n['name']}: {n['amount']}{n['unit']}" for n in nutrition if n['name'] in ['Calories', 'Protein', 'Carbohydrates', 'Fat']])
        
        instructions = data.get('instructions', 'No instructions provided.')
        
        return f"Title: {title}\nTime: {ready_in} mins\nServings: {servings}\nNutrition: {nut_str}\nInstructions: {instructions}"
    except Exception as e:
        return f"Error fetching details: {str(e)}"

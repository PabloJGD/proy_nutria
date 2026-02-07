"""
===============================================================================
NUTRITION.PY - Herramientas de Búsqueda de Recetas y Nutrición
===============================================================================

Este módulo contiene las herramientas que el agente usa para:
1. Buscar recetas basándose en ingredientes disponibles
2. Obtener información nutricional detallada de cada receta

Usa la API de Spoonacular (https://spoonacular.com/food-api):
- 150 requests/día en el plan gratuito
- Amplia base de datos de recetas con información nutricional
- Búsqueda por ingredientes con ranking de relevancia

IMPORTANTE: La API key debe estar configurada en configs/.env como:
    SPOONACULAR_API_KEY=tu_api_key_aqui
"""

import os
import requests
from langchain_core.tools import tool
from typing import List, Optional

# Cargar la API key de Spoonacular desde las variables de entorno
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")


@tool
def find_recipes_by_ingredients(ingredients: str, number: int = 3) -> str:
    """
    Busca recetas que se pueden preparar con los ingredientes proporcionados.
    
    Esta herramienta consulta la API de Spoonacular para encontrar recetas
    que maximicen el uso de los ingredientes disponibles.
    
    Args:
        ingredients (str): Lista de ingredientes separados por comas.
                          Ejemplo: "pollo, arroz, brócoli, ajo"
        number (int): Número máximo de recetas a retornar. Default: 3
    
    Returns:
        str: Lista formateada de recetas con ID, título e ingredientes usados.
             Formato: "ID: 123 - Title: Nombre - Used Ingredients: 4"
    
    Ejemplo de uso:
        >>> find_recipes_by_ingredients("chicken, rice, broccoli")
        "ID: 654959 - Title: Pasta With Chicken - Used Ingredients: 2
         ID: 633547 - Title: Baked Chicken - Used Ingredients: 2"
    
    Notas:
        - ranking=1: Prioriza recetas que usen MÁS ingredientes disponibles
        - Los IDs retornados se usan luego con get_recipe_details()
    """
    # Validar que la API key esté configurada
    if not SPOONACULAR_API_KEY:
        return "Error: La API Key de Spoonacular no está configurada en .env"
    
    # Endpoint de Spoonacular para buscar por ingredientes
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    
    # Parámetros de la petición
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "ingredients": ingredients,  # Lista CSV de ingredientes
        "number": number,            # Límite de resultados
        "ranking": 1                 # 1 = maximizar ingredientes usados, 2 = minimizar faltantes
    }
    
    try:
        # Hacer petición GET a la API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lanza excepción si hay error HTTP
        data = response.json()
        
        # Formatear resultados para que sean legibles por el agente
        results = []
        for item in data:
            results.append(
                f"ID: {item['id']} - "
                f"Title: {item['title']} - "
                f"Used Ingredients: {item['usedIngredientCount']}"
            )
        
        return "\n".join(results) if results else "No se encontraron recetas con esos ingredientes."
        
    except requests.exceptions.RequestException as e:
        return f"Error de conexión con Spoonacular: {str(e)}"
    except Exception as e:
        return f"Error al buscar recetas: {str(e)}"


@tool
def get_recipe_details(recipe_id: int) -> str:
    """
    Obtiene información detallada de una receta específica, incluyendo nutrición.
    
    Esta herramienta se usa DESPUÉS de find_recipes_by_ingredients para
    obtener los detalles completos de una receta seleccionada.
    
    Args:
        recipe_id (int): ID único de la receta obtenido de find_recipes_by_ingredients.
                        Ejemplo: 654959
    
    Returns:
        str: Información formateada con:
             - Título del plato
             - Tiempo de preparación
             - Número de porciones
             - Información nutricional (Calorías, Proteína, Carbohidratos, Grasa)
             - Instrucciones de preparación
    
    Ejemplo de uso:
        >>> get_recipe_details(654959)
        "Title: Pasta With Chicken
         Time: 45 mins
         Servings: 4
         Nutrition: Calories: 580kcal, Protein: 32g, Carbohydrates: 65g, Fat: 18g
         Instructions: Hervir la pasta..."
    
    Flujo típico:
        1. Usuario proporciona ingredientes
        2. find_recipes_by_ingredients() retorna IDs de recetas
        3. El agente llama get_recipe_details() con el ID más relevante
        4. Se presenta la receta completa al usuario
    """
    # Validar que la API key esté configurada
    if not SPOONACULAR_API_KEY:
        return "Error: La API Key de Spoonacular no está configurada en .env"

    # Endpoint para obtener detalles de una receta específica
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "includeNutrition": True  # Importante: incluir datos nutricionales
    }
    
    try:
        # Hacer petición GET a la API
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extraer información relevante
        title = data.get('title', 'Sin título')
        ready_in = data.get('readyInMinutes', '?')
        servings = data.get('servings', '?')
        
        # Extraer nutrientes de la respuesta
        nutrition = data.get('nutrition', {}).get('nutrients', [])
        
        # Filtrar solo los macronutrientes principales
        macros_importantes = ['Calories', 'Protein', 'Carbohydrates', 'Fat']
        nut_str = ", ".join([
            f"{n['name']}: {n['amount']}{n['unit']}" 
            for n in nutrition 
            if n['name'] in macros_importantes
        ])
        
        # Obtener instrucciones (pueden venir con HTML)
        instructions = data.get('instructions', 'No hay instrucciones disponibles.')
        
        # Formatear respuesta final
        return (
            f"Title: {title}\n"
            f"Time: {ready_in} mins\n"
            f"Servings: {servings}\n"
            f"Nutrition: {nut_str}\n"
            f"Instructions: {instructions}"
        )
        
    except requests.exceptions.RequestException as e:
        return f"Error de conexión con Spoonacular: {str(e)}"
    except Exception as e:
        return f"Error al obtener detalles: {str(e)}"

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    """
    Representa un ingrediente individual.
    
    Se usa para:
    - Listar ingredientes detectados en una imagen
    - Especificar ingredientes de una receta
    
    Ejemplo:
        >>> ing = Ingredient(name="Tomate", quantity="2 unidades")
    """
    name: str = Field(description="Nombre del ingrediente")
    quantity: Optional[str] = Field(None, description="Cantidad estimada si es visible/conocida")


class NutritionalInfo(BaseModel):
    """
    Información nutricional de una receta.
    
    Contiene los macronutrientes principales que el agente obtiene
    de la API de Spoonacular para cada receta recomendada.
    
    Campos:
        - calories: Calorías totales del plato
        - protein: Proteínas en gramos
        - carbohydrates: Carbohidratos en gramos  
        - fat: Grasas en gramos
        - additional_info: Otros nutrientes (vitaminas, fibra, etc.)
    
    Ejemplo:
        >>> info = NutritionalInfo(calories=450, protein=25, carbohydrates=30, fat=15)
    """
    calories: float = Field(description="Calorías totales")
    protein: float = Field(description="Proteínas en gramos")
    carbohydrates: float = Field(description="Carbohidratos en gramos")
    fat: float = Field(description="Grasas en gramos")
    additional_info: Optional[Dict[str, float]] = Field(
        default_factory=dict, 
        description="Otros nutrientes como vitaminas, fibra, sodio, etc."
    )


class Recipe(BaseModel):
    """
    Representa una receta completa recomendada por el agente.
    
    Esta es la estructura principal de salida. Contiene toda la información
    que el usuario final verá sobre un plato recomendado.
    
    Campos:
        - title: Nombre del plato (ej: "Ensalada César")
        - description: Breve descripción del plato
        - ingredients: Lista de ingredientes necesarios
        - instructions: Pasos de preparación
        - nutritional_info: Información nutricional (opcional)
        - prep_time: Tiempo de preparación (ej: "15 minutos")
        - cook_time: Tiempo de cocción (ej: "30 minutos")
    
    Ejemplo:
        >>> receta = Recipe(
        ...     title="Pasta con Vegetales",
        ...     description="Un plato saludable y rápido",
        ...     ingredients=[Ingredient(name="Pasta"), Ingredient(name="Tomate")],
        ...     instructions=["Hervir pasta", "Saltear vegetales", "Mezclar"]
        ... )
    """
    title: str = Field(description="Título del plato")
    description: str = Field(description="Descripción corta del plato")
    ingredients: List[Ingredient] = Field(description="Lista de ingredientes usados")
    instructions: List[str] = Field(description="Instrucciones paso a paso")
    nutritional_info: Optional[NutritionalInfo] = Field(None, description="Desglose nutricional")
    prep_time: Optional[str] = Field(None, description="Tiempo de preparación")
    cook_time: Optional[str] = Field(None, description="Tiempo de cocción")


class UserProfile(BaseModel):
    """
    Perfil del usuario con sus preferencias y restricciones.
    
    El agente usa este perfil para:
    1. Filtrar recetas incompatibles (ej: no sugerir carne a veganos)
    2. Priorizar recetas según objetivos (ej: alta proteína para músculo)
    3. Evitar alérgenos peligrosos
    
    Campos:
        - name: Nombre del usuario (para personalizar respuestas)
        - age: Edad (útil para requerimientos calóricos)
        - dietary_restrictions: Lista de dietas (Vegano, Keto, Sin Gluten, etc.)
        - allergies: Lista de alergias (Maní, Mariscos, Lácteos, etc.)
        - health_goals: Objetivo de salud (Perder peso, Ganar músculo, etc.)
    
    Ejemplo:
        >>> perfil = UserProfile(
        ...     name="Pablo",
        ...     age=30,
        ...     dietary_restrictions=["Vegetariano", "Sin Gluten"],
        ...     allergies=["Maní"],
        ...     health_goals="Ganar músculo"
        ... )
    """
    name: Optional[str] = Field("User", description="Nombre del usuario")
    age: Optional[float] = Field(None, description="Edad del usuario (soporta decimales para bebés)")
    dietary_restrictions: List[str] = Field(
        default_factory=list, 
        description="Restricciones dietéticas. Ej: ['Vegano', 'Sin Gluten', 'Keto']"
    )
    allergies: List[str] = Field(
        default_factory=list, 
        description="Lista de alergias alimentarias"
    )
    health_goals: Optional[str] = Field(
        None, 
        description="Objetivo de salud. Ej: 'Perder peso', 'Ganar músculo'"
    )


class AgentInput(BaseModel):
    """
    Estructura de entrada para el agente.
    
    Este modelo representa TODO lo que el usuario envía al sistema:
    - Una imagen de ingredientes (opcional)
    - Una descripción textual de ingredientes (opcional)
    - Su perfil con restricciones (obligatorio)
    
    Al menos uno de image_data o text_description debe estar presente.
    
    Campos:
        - image_data: Imagen codificada en Base64 o URL de imagen
        - text_description: Lista de ingredientes en texto plano
        - user_profile: Perfil completo del usuario
    
    Uso en la API:
        POST /recommend recibe este modelo como cuerpo de la petición.
    
    Ejemplo:
        >>> entrada = AgentInput(
        ...     text_description="Tengo pollo, arroz y brócoli",
        ...     user_profile=UserProfile(dietary_restrictions=["Sin Gluten"])
        ... )
    """
    image_data: Optional[str] = Field(None, description="Imagen en Base64 o URL")
    text_description: Optional[str] = Field(None, description="Descripción textual de ingredientes")
    user_profile: UserProfile = Field(description="Información del perfil del usuario")


class AgentOutput(BaseModel):
    """
    Estructura de salida del agente.
    
    Después de que el agente procesa la entrada (analiza imagen, busca recetas,
    obtiene nutrición), devuelve este modelo con:
    
    Campos:
        - recipes: Lista de recetas recomendadas (ordenadas por relevancia)
        - advice: Consejo nutricional general basado en el perfil
    
    Ejemplo de respuesta:
        >>> salida = AgentOutput(
        ...     recipes=[Recipe(title="Pollo al Horno", ...)],
        ...     advice="Dado tu objetivo de ganar músculo, estas recetas 
        ...             tienen alto contenido proteico."
        ... )
    """
    recipes: List[Recipe] = Field(description="Lista de recetas recomendadas")
    advice: Optional[str] = Field(None, description="Consejo nutricional general")

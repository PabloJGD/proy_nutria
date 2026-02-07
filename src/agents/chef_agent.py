"""
===============================================================================
CHEF_AGENT.PY - El Cerebro del Sistema
===============================================================================

Este es el módulo principal que orquesta todo el agente NutrIA.

Componentes:
    - LLM: GPT-4o de OpenAI (el "cerebro" que piensa)
    - Tools: Las 3 herramientas que el agente puede usar
    - Prompt: Las instrucciones de cómo comportarse
    - Executor: El motor que ejecuta el ciclo de razonamiento

Flujo del Agente:
    1. Recibe petición del usuario (ingredientes + perfil)
    2. Decide qué herramienta usar
    3. Ejecuta la herramienta
    4. Analiza el resultado
    5. Decide si necesita otra herramienta o puede responder
    6. Retorna la recomendación final
"""

import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src.tools.vision import analyze_image_for_ingredients
from src.tools.nutrition import find_recipes_by_ingredients, get_recipe_details
from src.prompts.chef_prompt import get_chat_prompt
from src.models.schemas import AgentInput

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DEL AGENTE
# ═══════════════════════════════════════════════════════════════════════════════

# Lista de herramientas disponibles para el agente
# El agente puede "decidir" cuál usar en cada momento
tools = [
    analyze_image_for_ingredients,  # 👁️ Ver ingredientes en fotos
    find_recipes_by_ingredients,     # 🔍 Buscar recetas
    get_recipe_details               # 📊 Obtener nutrición
]

# Inicializar el modelo de lenguaje (LLM)
# temperature=0.7: Balance entre creatividad y precisión
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Obtener el prompt del sistema (instrucciones para el chef)
prompt = get_chat_prompt()

# Crear el agente con capacidad de llamar herramientas
# create_tool_calling_agent: Versión moderna que usa function calling de OpenAI
agent = create_tool_calling_agent(llm, tools, prompt)

# Crear el ejecutor que maneja el ciclo de razonamiento
# verbose=True: Muestra en consola el proceso de pensamiento del agente
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def process_request(request: AgentInput) -> str:
    """
    Punto de entrada principal para procesar peticiones al agente.
    
    Esta función es el "mesero" entre el frontend y el agente chef.
    Toma los datos estructurados del usuario (AgentInput) y los traduce
    a un formato que el modelo de lenguaje pueda entender (texto plano).
    
    Args:
        request (AgentInput): Objeto Pydantic que contiene:
            - image_data (str, opcional): Ruta o URL de imagen con ingredientes
            - text_description (str, opcional): Lista de ingredientes en texto
            - user_profile (UserProfile): Perfil completo del usuario
                - age: Edad
                - health_goals: Objetivos (perder peso, ganar músculo)
                - dietary_restrictions: Restricciones (Vegano, Keto, etc.)
                - allergies: Alergias alimentarias
    
    Returns:
        str: Respuesta del agente con las recetas recomendadas y consejos.
    
    Ejemplo de uso:
        >>> from src.models.schemas import AgentInput, UserProfile
        >>> 
        >>> perfil = UserProfile(
        ...     age=30,
        ...     health_goals="Ganar músculo",
        ...     dietary_restrictions=["Sin Gluten"],
        ...     allergies=["Maní"]
        ... )
        >>> 
        >>> peticion = AgentInput(
        ...     text_description="pollo, arroz, brócoli",
        ...     user_profile=perfil
        ... )
        >>> 
        >>> respuesta = process_request(peticion)
        >>> print(respuesta)
        "Te recomiendo Pollo al Horno con Arroz porque tiene alto contenido
         de proteína (45g) ideal para tu objetivo de ganar músculo..."
    
    ¿Qué pasa internamente?
        1. Se extraen las restricciones y perfil como texto
        2. Se construye el mensaje del usuario
        3. Se invoca al agente con estos datos
        4. El agente puede usar herramientas múltiples veces
        5. Retorna la respuesta final
    """
    
    # ── Paso 1: Convertir el perfil del usuario a texto ──
    # El LLM necesita texto, no objetos Python
    profile_str = f"Edad: {request.user_profile.age}, Objetivos: {request.user_profile.health_goals}"
    
    # Combinar restricciones dietéticas y alergias en una lista
    restrictions_str = ", ".join(
        request.user_profile.dietary_restrictions + 
        request.user_profile.allergies
    )
    
    # ── Paso 2: Construir el mensaje del usuario ──
    user_input = ""
    
    # Si hay ingredientes en texto, añadirlos
    if request.text_description:
        user_input += f"Ingredientes disponibles: {request.text_description}.\n"
    
    # Si hay una imagen, indicar al agente que debe analizarla
    if request.image_data:
        user_input += f"Tengo una imagen de ingredientes en: {request.image_data}. Por favor analízala."
    
    # ── Paso 3: Invocar al agente ──
    # El agent_executor maneja todo el ciclo de razonamiento:
    # - Decide qué herramienta usar
    # - Ejecuta la herramienta
    # - Analiza el resultado
    # - Repite si es necesario
    # - Genera la respuesta final
    result = agent_executor.invoke({
        "input": user_input,           # Lo que el usuario quiere
        "user_profile": profile_str,   # Quién es el usuario
        "restrictions": restrictions_str  # Qué restricciones tiene
    })
    
    # ── Paso 4: Retornar la respuesta ──
    return result["output"]

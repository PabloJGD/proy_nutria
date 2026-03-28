"""
===============================================================================
CHEF_AGENT.PY - El Cerebro del Sistema (LangGraph)
===============================================================================

Usa create_react_agent (LangGraph prebuilt) con checkpointing nativo via
PostgresSaver (GCP) o MemorySaver (fallback local).

El historial de conversación por sesión es gestionado automáticamente por
el checkpointer a través del thread_id.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent

from src.tools.vision import analyze_image_for_ingredients
from src.tools.nutrition import find_recipes_by_ingredients, get_recipe_details
from src.tools.translator import translate_es_to_en
from src.rag.recipe_tool import search_peruvian_recipes
from src.prompts.chef_prompt import SYSTEM_TEMPLATE
from src.models.schemas import AgentInput
from src.db.checkpointer import get_checkpointer

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DEL AGENTE
# ═══════════════════════════════════════════════════════════════════════════════

tools = [
    analyze_image_for_ingredients,
    translate_es_to_en,
    search_peruvian_recipes,
    find_recipes_by_ingredients,
    get_recipe_details,
]

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)


def profile_modifier(state, config: RunnableConfig):
    """
    Inyecta el perfil del usuario y sus restricciones como SystemMessage
    al inicio de cada turno conversacional.
    Los valores se leen de config["configurable"] para evitar contaminar
    el historial persistido en el checkpointer.
    """
    profile_str = config["configurable"].get("user_profile", "")
    restrictions_str = config["configurable"].get("restrictions", "")
    user_name = config["configurable"].get("user_name", "Usuario")
    system_msg = SystemMessage(
        content=SYSTEM_TEMPLATE.format(
            user_profile=profile_str,
            restrictions=restrictions_str,
            user_name=user_name,
        )
    )
    return [system_msg] + state["messages"]


checkpointer = get_checkpointer()

agent = create_react_agent(
    llm,
    tools,
    state_modifier=profile_modifier,
    checkpointer=checkpointer,
)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def process_request(session_id: str, request: AgentInput, user_name: str = "Usuario") -> str:
    """
    Punto de entrada principal para procesar peticiones al agente.

    Args:
        session_id: Identificador de sesión (= thread_id del checkpointer).
        request:    AgentInput con ingredientes y perfil del usuario.

    Returns:
        Respuesta del agente en español.
    """
    # Construir strings del perfil
    profile_str = f"Edad: {request.user_profile.age}, Objetivos: {request.user_profile.health_goals}"
    restrictions_str = ", ".join(
        request.user_profile.dietary_restrictions + request.user_profile.allergies
    )

    # Construir mensaje del usuario
    user_input = ""
    if request.text_description:
        user_input += f"Ingredientes disponibles: {request.text_description}.\n"
    if request.image_data:
        user_input += f"Tengo una imagen de ingredientes en: {request.image_data}. Por favor analízala."

    result = agent.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config={
            "configurable": {
                "thread_id": session_id,
                "user_profile": profile_str,
                "restrictions": restrictions_str,
                "user_name": user_name,
            }
        },
    )
    return result["messages"][-1].content

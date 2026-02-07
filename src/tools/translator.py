"""
===============================================================================
TRANSLATOR.PY - Herramienta de Traducción para el Agente Chef
===============================================================================

Esta herramienta permite al agente traducir ingredientes y términos dietéticos
del español al inglés. Esto es crucial porque la API de Spoonacular 
funciona mejor (o exclusivamente en algunos endpoints) con términos en inglés.

Usa el LLM para asegurar que las traducciones sean contextualmente correctas
para alimentos e ingredientes.
"""

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os

@tool
def translate_es_to_en(text: str) -> str:
    """
    Traduce una lista de ingredientes o términos gastronómicos del español al inglés.
    Úsala cuando el usuario proporcione ingredientes en español antes de buscar recetas.
    
    Args:
        text (str): Texto en español a traducir (ej: "pollo, cebolla, ajo").
    
    Returns:
        str: Traducción al inglés (ej: "chicken, onion, garlic").
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    system_msg = SystemMessage(content=(
        "Eres un traductor experto especializado en gastronomía y nutrición. "
        "Traduce la lista de ingredientes del español al inglés. "
        "Devuelve únicamente la traducción separada por comas, sin explicaciones."
    ))
    
    human_msg = HumanMessage(content=text)
    
    try:
        response = llm.invoke([system_msg, human_msg])
        return response.content.strip()
    except Exception as e:
        return f"Error en la traducción: {str(e)}"

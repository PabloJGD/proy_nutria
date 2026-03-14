"""
recipe_tool.py - Tool @tool search_peruvian_recipes para el agente LangGraph.

El docstring es crítico: el LLM usa ese texto para decidir cuándo invocar
esta tool vs find_recipes_by_ingredients (Spoonacular).
"""

import logging
from typing import Optional

from langchain_core.tools import tool

from src.rag.filters import build_es_filters
from src.rag.store import get_vector_store

logger = logging.getLogger(__name__)


@tool
def search_peruvian_recipes(
    query: str,
    region: Optional[str] = None,
    meal_type: Optional[str] = None,
    dietary_restrictions: Optional[str] = None,
    allergies: Optional[str] = None,
    max_calories: Optional[int] = None,
    max_prep_time: Optional[int] = None,
) -> str:
    """
    Busca recetas de cocina peruana en la base de conocimiento local usando
    búsqueda híbrida (semántica + full-text).

    Úsala cuando:
    - El usuario pregunte por recetas peruanas, gastronomía del Perú o platos típicos.
    - El usuario mencione platos específicos: ceviche, lomo saltado, ají de gallina,
      causa, anticuchos, juane, rocoto relleno, u otros platos peruanos.
    - Se pidan recetas de una región peruana: costa, sierra o selva.
    - Se necesite filtrar estrictamente por dieta (vegetariano, vegano, sin gluten)
      o por alergias (mariscos, gluten, lácteos).

    NO la uses para recetas genéricas internacionales: usa find_recipes_by_ingredients.

    Args:
        query: Descripción en español de lo que busca. Ej: "plato frío con pescado",
               "algo dulce típico limeño", "proteína alta para después del gym".
        region: Región del Perú — "costa", "sierra" o "selva". Opcional.
        meal_type: Tipo de comida — "desayuno", "almuerzo", "cena",
                   "entrada", "postre" o "bebida". Opcional.
        dietary_restrictions: Restricciones separadas por coma.
                              Ej: "vegetariano,sin gluten". Opcional.
        allergies: Alergias separadas por coma. Ej: "mariscos,lácteos". Opcional.
        max_calories: Calorías máximas por porción. Opcional.
        max_prep_time: Tiempo máximo de preparación en minutos. Opcional.

    Returns:
        Descripción de las recetas encontradas con nombre, región, datos
        nutricionales e ingredientes principales. Si no hay resultados,
        indica qué filtros aplicar para ampliar la búsqueda.
    """
    store = get_vector_store()
    if store is None:
        return (
            "La base de recetas peruanas no está disponible en este momento "
            "(Elasticsearch no configurado). Puedo ayudarte con recetas generales "
            "usando find_recipes_by_ingredients."
        )

    # Parsear listas de strings
    diet_list = [r.strip() for r in dietary_restrictions.split(",")] if dietary_restrictions else []
    allergy_list = [a.strip() for a in allergies.split(",")] if allergies else []

    filters = build_es_filters(
        region=region,
        meal_type=meal_type,
        dietary_restrictions=diet_list,
        allergies=allergy_list,
        max_calories=max_calories,
        max_prep_time=max_prep_time,
    )

    try:
        docs = store.similarity_search(
            query=query,
            k=3,
            filter=filters if filters else None,
        )
    except Exception as e:
        logger.error(f"Error en búsqueda Elasticsearch: {e}")
        return f"Error al buscar recetas peruanas: {str(e)}"

    if not docs:
        filter_summary = []
        if region:
            filter_summary.append(f"región={region}")
        if meal_type:
            filter_summary.append(f"tipo={meal_type}")
        if diet_list:
            filter_summary.append(f"dieta={','.join(diet_list)}")
        if allergy_list:
            filter_summary.append(f"sin={','.join(allergy_list)}")
        applied = ", ".join(filter_summary) if filter_summary else "ninguno"
        return (
            f"No encontré recetas peruanas con los filtros aplicados ({applied}). "
            "Intenta ampliar la búsqueda eliminando algún filtro."
        )

    results = []
    for doc in docs:
        m = doc.metadata
        vegetariano = "✓ Vegetariano" if m.get("es_vegetariano") else ""
        vegano = "✓ Vegano" if m.get("es_vegano") else ""
        sin_gluten = "✓ Sin gluten" if m.get("es_sin_gluten") else ""
        badges = " | ".join(filter(None, [vegetariano, vegano, sin_gluten]))

        result = (
            f"🍽️ **{m.get('title', 'Sin nombre')}**\n"
            f"   Región: {m.get('region', '?').capitalize()} "
            f"({m.get('city', '')}) | Estilo: {m.get('cuisine_style', '?')}\n"
            f"   Tipo: {m.get('meal_type', '?')} | "
            f"Dificultad: {m.get('difficulty', '?')} | "
            f"Prep: {m.get('prep_time_min', '?')} min\n"
            f"   Calorías: {m.get('calories_per_serving', '?')} kcal | "
            f"Proteína: {m.get('protein_g', '?')}g\n"
            f"   Proteína principal: {m.get('main_protein', '?')}"
        )
        if badges:
            result += f"\n   {badges}"
        result += f"\n\n   {doc.page_content[:350]}..."
        results.append(result)

    header = f"Encontré {len(docs)} recetas peruanas:\n\n"
    return header + "\n\n---\n\n".join(results)

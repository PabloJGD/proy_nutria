"""
filters.py - Construcción de filtros ES Query DSL desde restricciones del usuario.
"""

from typing import Optional


def build_es_filters(
    region: Optional[str] = None,
    meal_type: Optional[str] = None,
    dietary_restrictions: Optional[list] = None,
    allergies: Optional[list] = None,
    max_calories: Optional[int] = None,
    max_prep_time: Optional[int] = None,
) -> list:
    """
    Convierte los parámetros del UserProfile a filtros de Elasticsearch Query DSL.

    Returns:
        Lista de dicts en formato ES Query DSL para pasar a
        ElasticsearchStore.similarity_search(filter=...).
    """
    filters = []

    if region:
        filters.append({"term": {"metadata.region": region.lower().strip()}})

    if meal_type:
        filters.append({"term": {"metadata.meal_type": meal_type.lower().strip()}})

    if max_calories:
        filters.append({"range": {"metadata.calories_per_serving": {"lte": max_calories}}})

    if max_prep_time:
        filters.append({"range": {"metadata.prep_time_min": {"lte": max_prep_time}}})

    # Restricciones dietéticas → campos booleanos
    DIET_MAP = {
        "vegetariano":  {"term": {"metadata.es_vegetariano": True}},
        "vegano":       {"term": {"metadata.es_vegano": True}},
        "sin gluten":   {"term": {"metadata.es_sin_gluten": True}},
        "sin_gluten":   {"term": {"metadata.es_sin_gluten": True}},
        "celíaco":      {"term": {"metadata.es_sin_gluten": True}},
        "celiaco":      {"term": {"metadata.es_sin_gluten": True}},
        "sin lactosa":  {"term": {"metadata.tiene_lacteos": False}},
        "sin_lactosa":  {"term": {"metadata.tiene_lacteos": False}},
    }
    for restriction in (dietary_restrictions or []):
        key = restriction.lower().strip()
        if key in DIET_MAP:
            filters.append(DIET_MAP[key])

    # Alergias → excluir recetas que contienen el alérgeno
    ALLERGY_MAP = {
        "mariscos":  {"term": {"metadata.tiene_mariscos": False}},
        "marisco":   {"term": {"metadata.tiene_mariscos": False}},
        "gluten":    {"term": {"metadata.tiene_gluten": False}},
        "lacteos":   {"term": {"metadata.tiene_lacteos": False}},
        "lácteos":   {"term": {"metadata.tiene_lacteos": False}},
        "lacteo":    {"term": {"metadata.tiene_lacteos": False}},
        "leche":     {"term": {"metadata.tiene_lacteos": False}},
    }
    for allergy in (allergies or []):
        key = allergy.lower().strip()
        if key in ALLERGY_MAP:
            filters.append(ALLERGY_MAP[key])

    return filters

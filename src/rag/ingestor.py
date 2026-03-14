"""
ingestor.py - Carga y preparación de documentos desde múltiples fuentes.

Pasos cubiertos:
  LOAD  → una función por fuente usando el loader LangChain apropiado
  SPLIT → una receta = un Document (sin text splitting)
          PDFs usan RecursiveCharacterTextSplitter

Loaders utilizados:
  - JSONLoader              → corpus JSON curado + Spoonacular descargado
  - HuggingFaceDatasetLoader→ dataset somosnlp/gastronomia-peruana
  - WebBaseLoader           → páginas individuales (Peru.info)
  - RecursiveUrlLoader      → crawl de sección completa (RecetasGratis.net)
  - PyPDFLoader             → PDFs del MINCUL / APEGA
"""

import json
import logging
from pathlib import Path
from typing import Optional

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _metadata_func(record: dict, metadata: dict) -> dict:
    """
    Función auxiliar para JSONLoader.
    Extrae todos los campos del schema al metadata del Document.
    También almacena ingredients e instructions para reconstruir page_content.
    """
    metadata["title"] = record.get("title", "")
    metadata["region"] = record.get("region", "")
    metadata["city"] = record.get("city", "")
    metadata["meal_type"] = record.get("meal_type", "")
    metadata["cuisine_style"] = record.get("cuisine_style", "")
    metadata["es_vegetariano"] = bool(record.get("es_vegetariano", False))
    metadata["es_vegano"] = bool(record.get("es_vegano", False))
    metadata["es_sin_gluten"] = bool(record.get("es_sin_gluten", False))
    metadata["tiene_mariscos"] = bool(record.get("tiene_mariscos", False))
    metadata["tiene_gluten"] = bool(record.get("tiene_gluten", False))
    metadata["tiene_lacteos"] = bool(record.get("tiene_lacteos", False))
    metadata["main_protein"] = record.get("main_protein", "")
    metadata["calories_per_serving"] = int(record.get("calories_per_serving", 0))
    metadata["protein_g"] = float(record.get("protein_g", 0.0))
    metadata["prep_time_min"] = int(record.get("prep_time_min", 0))
    metadata["difficulty"] = record.get("difficulty", "")
    metadata["is_typical"] = bool(record.get("is_typical", False))
    metadata["source_url"] = record.get("source_url", "")
    # Temporales para reconstruir page_content (se eliminan después)
    metadata["_ingredients"] = record.get("ingredients", [])
    metadata["_instructions"] = record.get("instructions", "")
    return metadata


def _enrich_page_content(doc: Document) -> Document:
    """
    Reconstruye el page_content con formato enriquecido para mejor
    semántica en el embedding y mejor recall en BM25.
    Elimina los campos temporales _ingredients e _instructions del metadata.
    """
    ingredients = doc.metadata.pop("_ingredients", [])
    instructions = doc.metadata.pop("_instructions", "")

    if isinstance(ingredients, list):
        ingredients_str = ", ".join(ingredients)
    else:
        ingredients_str = str(ingredients)

    if isinstance(instructions, list):
        instructions_str = " ".join(instructions)
    else:
        instructions_str = str(instructions)

    doc.page_content = (
        f"[Nombre] {doc.metadata.get('title', '')}\n"
        f"[Descripción] {doc.page_content}\n"
        f"[Ingredientes] {ingredients_str}\n"
        f"[Instrucciones] {instructions_str[:800]}"
    )
    return doc


# ─── LOAD: una función por fuente ─────────────────────────────────────────────

def load_from_json(file_path: str) -> list[Document]:
    """
    LOAD desde corpus JSON curado (scripts/data/recetas_peruanas.json).
    Loader: JSONLoader con jq_schema=".[]" para iterar el array de recetas.
    """
    from langchain_community.document_loaders import JSONLoader

    logger.info(f"Cargando corpus JSON desde {file_path}")
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=".[]",
        content_key="description",
        metadata_func=_metadata_func,
        text_content=True,
    )
    docs = loader.load()
    docs = [_enrich_page_content(doc) for doc in docs]
    logger.info(f"JSONLoader: {len(docs)} documentos cargados.")
    return docs


def load_from_spoonacular_json(file_path: str) -> list[Document]:
    """
    LOAD desde respuesta descargada de Spoonacular API (cuisine=peruvian).
    Loader: JSONLoader con jq_schema=".results[]".

    Uso previo:
        import requests, json
        r = requests.get("https://api.spoonacular.com/recipes/complexSearch",
                         params={"cuisine":"peruvian","number":50,
                                 "addRecipeNutrition":True,"apiKey":KEY})
        json.dump(r.json(), open("scripts/data/spoonacular_peruvian.json","w"))
    """
    from langchain_community.document_loaders import JSONLoader

    def spoonacular_metadata(record: dict, metadata: dict) -> dict:
        nutrients = {n["name"]: n["amount"]
                     for n in record.get("nutrition", {}).get("nutrients", [])}
        metadata["title"] = record.get("title", "")
        metadata["region"] = "costa"
        metadata["city"] = ""
        metadata["meal_type"] = "almuerzo"
        metadata["cuisine_style"] = "criollo"
        metadata["es_vegetariano"] = record.get("vegetarian", False)
        metadata["es_vegano"] = record.get("vegan", False)
        metadata["es_sin_gluten"] = record.get("glutenFree", False)
        metadata["tiene_mariscos"] = False
        metadata["tiene_gluten"] = not record.get("glutenFree", True)
        metadata["tiene_lacteos"] = record.get("dairyFree", True) is False
        metadata["main_protein"] = ""
        metadata["calories_per_serving"] = int(nutrients.get("Calories", 0))
        metadata["protein_g"] = float(nutrients.get("Protein", 0.0))
        metadata["prep_time_min"] = int(record.get("readyInMinutes", 0))
        metadata["difficulty"] = "media"
        metadata["is_typical"] = True
        metadata["source_url"] = record.get("sourceUrl", "")
        metadata["_ingredients"] = [
            i.get("original", "") for i in record.get("extendedIngredients", [])
        ]
        metadata["_instructions"] = record.get("instructions", "") or ""
        return metadata

    logger.info(f"Cargando Spoonacular JSON desde {file_path}")
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=".results[]",
        content_key="title",
        metadata_func=spoonacular_metadata,
        text_content=True,
    )
    docs = loader.load()
    docs = [_enrich_page_content(doc) for doc in docs]
    logger.info(f"Spoonacular JSONLoader: {len(docs)} documentos cargados.")
    return docs


def load_from_web(urls: list[str]) -> list[Document]:
    """
    LOAD desde páginas web individuales (ej: Peru.info).
    Loader: WebBaseLoader con filtrado BeautifulSoup para extraer solo
    el contenido relevante de la receta.
    Los documentos cargados tienen metadata mínima; requieren enriquecimiento manual.
    """
    from langchain_community.document_loaders import WebBaseLoader
    from bs4 import SoupStrainer

    logger.info(f"Cargando {len(urls)} URLs con WebBaseLoader")
    loader = WebBaseLoader(
        web_paths=urls,
        bs_kwargs={
            "parse_only": SoupStrainer(
                class_=["recipe-content", "article-body", "post-content", "entry-content"]
            )
        },
    )
    docs = loader.load()
    logger.info(f"WebBaseLoader: {len(docs)} documentos cargados.")
    return docs


def load_from_recursive_url(base_url: str, max_depth: int = 2) -> list[Document]:
    """
    LOAD mediante crawl de una sección completa (ej: RecetasGratis.net/peruanas).
    Loader: RecursiveUrlLoader para descubrir y cargar múltiples páginas.
    """
    from langchain_community.document_loaders import RecursiveUrlLoader
    from bs4 import BeautifulSoup

    def bs_extractor(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["nav", "footer", "aside", "script", "style"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)

    logger.info(f"Crawleando {base_url} (max_depth={max_depth})")
    loader = RecursiveUrlLoader(
        url=base_url,
        max_depth=max_depth,
        extractor=bs_extractor,
    )
    docs = loader.load()
    logger.info(f"RecursiveUrlLoader: {len(docs)} documentos cargados.")
    return docs


def load_from_pdf(file_path: str) -> list[Document]:
    """
    LOAD desde PDFs del MINCUL / APEGA.
    Loader: PyPDFLoader — retorna un Document por página.
    A diferencia de las recetas, los PDFs SÍ se splitean con
    RecursiveCharacterTextSplitter porque pueden contener múltiples recetas por página.
    """
    from langchain_community.document_loaders import PyPDFLoader

    logger.info(f"Cargando PDF desde {file_path}")
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    logger.info(f"PyPDFLoader: {len(pages)} páginas cargadas.")
    return pages


def load_from_huggingface(dataset_name: str, page_content_column: str = "receta") -> list[Document]:
    """
    LOAD desde dataset de HuggingFace Hub.
    Loader: HuggingFaceDatasetLoader
    Dataset sugerido: 'somosnlp-hackathon-2022/gastronomia-peruana'
    """
    from langchain_community.document_loaders import HuggingFaceDatasetLoader

    logger.info(f"Cargando dataset HuggingFace: {dataset_name}")
    loader = HuggingFaceDatasetLoader(
        path=dataset_name,
        page_content_column=page_content_column,
    )
    docs = loader.load()
    logger.info(f"HuggingFaceDatasetLoader: {len(docs)} documentos cargados.")
    return docs


# ─── SPLIT ────────────────────────────────────────────────────────────────────

def split_documents(docs: list[Document], from_pdf: bool = False) -> list[Document]:
    """
    SPLIT de documentos.

    - Recetas (from_pdf=False): una receta = un Document. Sin splitting.
    - PDFs (from_pdf=True): usa RecursiveCharacterTextSplitter porque un PDF
      puede contener múltiples recetas o guías de nutrición en varias páginas.
    """
    if not from_pdf:
        return docs

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "],
    )
    split = splitter.split_documents(docs)
    logger.info(f"PDF split: {len(docs)} páginas → {len(split)} chunks.")
    return split

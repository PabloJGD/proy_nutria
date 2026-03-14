"""
ingest_recipes.py - CLI para ingestar recetas peruanas en Elasticsearch.

Ejecutar:
    uv run python scripts/ingest_recipes.py                    # ingesta completa
    uv run python scripts/ingest_recipes.py --dry-run          # solo carga y muestra stats
    uv run python scripts/ingest_recipes.py --source json      # solo corpus JSON
    uv run python scripts/ingest_recipes.py --clear            # borra el índice y reinicia

Fuentes disponibles (--source):
    json         → scripts/data/recetas_peruanas.json (corpus curado)
    spoonacular  → scripts/data/spoonacular_peruvian.json (descarga previa de la API)
    pdf          → scripts/data/*.pdf (PDFs del MINCUL / APEGA)
    web          → páginas individuales (Peru.info)
    recursive    → crawl de sección completa
    huggingface  → dataset somosnlp-hackathon-2022/gastronomia-peruana
    all          → todas las fuentes disponibles (default)
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Asegurar que el root del proyecto está en sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / "configs" / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ingest")


def load_documents(source: str) -> list:
    """Carga documentos según la fuente seleccionada."""
    from src.rag.ingestor import (
        load_from_json,
        load_from_spoonacular_json,
        load_from_pdf,
        load_from_web,
        load_from_recursive_url,
        load_from_huggingface,
        split_documents,
    )

    data_dir = ROOT / "scripts" / "data"
    all_docs = []

    # ── JSON curado ──────────────────────────────────────────────────────────
    if source in ("json", "all"):
        json_path = data_dir / "recetas_peruanas.json"
        if json_path.exists():
            docs = load_from_json(str(json_path))
            all_docs.extend(docs)
        else:
            logger.warning(f"No encontrado: {json_path}")

    # ── Spoonacular JSON ─────────────────────────────────────────────────────
    if source in ("spoonacular", "all"):
        sp_path = data_dir / "spoonacular_peruvian.json"
        if sp_path.exists():
            docs = load_from_spoonacular_json(str(sp_path))
            all_docs.extend(docs)
        else:
            logger.warning(f"No encontrado: {sp_path} — omitiendo fuente Spoonacular.")

    # ── PDFs ─────────────────────────────────────────────────────────────────
    if source in ("pdf", "all"):
        pdf_files = list(data_dir.glob("*.pdf"))
        if pdf_files:
            for pdf_path in pdf_files:
                pages = load_from_pdf(str(pdf_path))
                chunks = split_documents(pages, from_pdf=True)
                all_docs.extend(chunks)
        else:
            logger.warning(f"No se encontraron PDFs en {data_dir} — omitiendo fuente PDF.")

    # ── Web (páginas individuales) ───────────────────────────────────────────
    if source in ("web", "all"):
        urls = []  # Añadir URLs de Peru.info aquí cuando estén disponibles
        if urls:
            docs = load_from_web(urls)
            all_docs.extend(docs)
        else:
            logger.info("No hay URLs web configuradas — omitiendo fuente web.")

    # ── Crawl recursivo ──────────────────────────────────────────────────────
    if source in ("recursive", "all"):
        # Configurar base_url cuando esté disponible
        base_url = ""
        if base_url:
            docs = load_from_recursive_url(base_url, max_depth=2)
            all_docs.extend(docs)
        else:
            logger.info("No hay URL recursiva configurada — omitiendo fuente recursiva.")

    # ── HuggingFace ──────────────────────────────────────────────────────────
    if source in ("huggingface", "all"):
        try:
            docs = load_from_huggingface("somosnlp-hackathon-2022/gastronomia-peruana")
            all_docs.extend(docs)
        except Exception as e:
            logger.warning(f"No se pudo cargar dataset HuggingFace ({e}) — omitiendo.")

    return all_docs


def ingest(source: str = "all", dry_run: bool = False, clear: bool = False) -> None:
    """Orquesta el pipeline completo: Load → Split → Embed → Store."""

    # ── 1. LOAD ──────────────────────────────────────────────────────────────
    logger.info(f"=== PASO 1: LOAD (fuente={source}) ===")
    docs = load_documents(source)

    if not docs:
        logger.error("No se cargaron documentos. Verifica las fuentes.")
        sys.exit(1)

    logger.info(f"Total documentos cargados: {len(docs)}")

    # Dry-run: mostrar stats y salir
    if dry_run:
        logger.info("=== DRY-RUN: mostrando primeros 3 documentos ===")
        for i, doc in enumerate(docs[:3]):
            logger.info(f"\n[Doc {i+1}]")
            logger.info(f"  Título: {doc.metadata.get('title', 'N/A')}")
            logger.info(f"  Región: {doc.metadata.get('region', 'N/A')}")
            logger.info(f"  Tipo:   {doc.metadata.get('meal_type', 'N/A')}")
            logger.info(f"  Content preview: {doc.page_content[:120]}...")
        logger.info(f"\nTotal: {len(docs)} documentos listos para ingestar.")
        return

    # ── Verificar conexión a Elasticsearch ───────────────────────────────────
    es_url = os.getenv("ELASTICSEARCH_URL")
    if not es_url:
        logger.error(
            "ELASTICSEARCH_URL no está configurada en configs/.env. "
            "Configura la URL antes de ingestar."
        )
        sys.exit(1)

    # ── 2. EMBED + STORE ─────────────────────────────────────────────────────
    logger.info("=== PASO 2-3: EMBED + STORE (Elasticsearch) ===")

    from src.rag.store import get_vector_store, reset_store

    if clear:
        logger.info("--clear: limpiando singleton y recreando índice...")
        reset_store()

    store = get_vector_store()
    if store is None:
        logger.error("No se pudo conectar a Elasticsearch. Verifica ELASTICSEARCH_URL y ELASTICSEARCH_API_KEY.")
        sys.exit(1)

    logger.info(f"Indexando {len(docs)} documentos en Elasticsearch...")
    try:
        store.add_documents(docs)
        logger.info(f"✓ {len(docs)} documentos indexados correctamente.")
    except Exception as e:
        logger.error(f"Error al indexar documentos: {e}")
        sys.exit(1)

    # ── 4. VERIFICACIÓN RETRIEVAL ─────────────────────────────────────────────
    logger.info("=== PASO 4: VERIFICACIÓN RETRIEVAL ===")
    try:
        results = store.similarity_search("plato típico con pescado", k=2)
        logger.info(f"Búsqueda de prueba: {len(results)} resultado(s) encontrado(s).")
        for r in results:
            logger.info(f"  → {r.metadata.get('title', 'N/A')} ({r.metadata.get('region', '?')})")
    except Exception as e:
        logger.warning(f"Búsqueda de prueba falló: {e}")

    logger.info("=== INGESTA COMPLETADA ===")


def main():
    parser = argparse.ArgumentParser(description="Ingestar recetas peruanas en Elasticsearch.")
    parser.add_argument(
        "--source",
        choices=["json", "spoonacular", "pdf", "web", "recursive", "huggingface", "all"],
        default="all",
        help="Fuente de datos a ingestar (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo carga documentos y muestra stats, sin indexar.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Limpia el singleton del store antes de ingestar (fuerza reconexión).",
    )
    args = parser.parse_args()

    ingest(source=args.source, dry_run=args.dry_run, clear=args.clear)


if __name__ == "__main__":
    main()

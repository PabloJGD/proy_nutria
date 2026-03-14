"""
store.py - Inicialización de ElasticsearchStore con patrón singleton + fallback.

Sigue el mismo patrón de get_checkpointer() en src/db/checkpointer.py:
- Si ELASTICSEARCH_URL está disponible → conecta a Elasticsearch GCP
- Si no → retorna None (la tool muestra mensaje amigable)
"""

import os
import logging

logger = logging.getLogger(__name__)

_store_instance = None


def get_vector_store():
    """
    Retorna una instancia singleton de ElasticsearchStore.
    Retorna None si ELASTICSEARCH_URL no está configurada o falla la conexión.
    """
    global _store_instance

    if _store_instance is not None:
        return _store_instance

    es_url = os.getenv("ELASTICSEARCH_URL")
    es_api_key = os.getenv("ELASTICSEARCH_API_KEY")
    index_name = os.getenv("ES_INDEX_NAME", "nutria-recetas-peruanas")

    if not es_url:
        logger.info("ELASTICSEARCH_URL no configurada — RAG de recetas peruanas deshabilitado.")
        return None

    try:
        from langchain_elasticsearch import ElasticsearchStore
        from langchain_openai import OpenAIEmbeddings

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        store = ElasticsearchStore(
            index_name=index_name,
            embedding=embeddings,
            es_url=es_url,
            es_api_key=es_api_key,
            strategy=ElasticsearchStore.ApproxRetrievalStrategy(
                hybrid=True,
                rrf=True,
            ),
        )

        logger.info(f"ElasticsearchStore conectado — índice: '{index_name}'.")
        _store_instance = store
        return _store_instance

    except Exception as e:
        logger.warning(f"No se pudo conectar a Elasticsearch ({e}). RAG deshabilitado.")
        return None


def reset_store():
    """Limpia el singleton (útil en tests)."""
    global _store_instance
    _store_instance = None

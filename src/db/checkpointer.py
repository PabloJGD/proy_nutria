"""
checkpointer.py - Gestión del checkpointer de LangGraph

Retorna PostgresSaver si DATABASE_URL está disponible,
sino MemorySaver como fallback local.
"""

import os
from langgraph.checkpoint.memory import MemorySaver


def get_checkpointer():
    """Retorna PostgresSaver si DATABASE_URL está disponible, sino MemorySaver."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            from psycopg_pool import ConnectionPool
            from langgraph.checkpoint.postgres import PostgresSaver

            pool = ConnectionPool(conninfo=db_url, max_size=10, open=False, kwargs={"autocommit": True, "prepare_threshold": 0})
            pool.open(wait=True, timeout=5)
            checkpointer = PostgresSaver(pool)
            checkpointer.setup()  # crea tablas necesarias (idempotente)
            print("INFO: Checkpointer PostgresSaver conectado correctamente.")
            return checkpointer
        except Exception as e:
            print(f"WARNING: No se pudo conectar a PostgreSQL ({e}). Usando MemorySaver.")
    else:
        print("INFO: DATABASE_URL no configurada. Usando MemorySaver (memoria solo en proceso).")
    return MemorySaver()

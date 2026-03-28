"""
session_store.py - CRUD para la tabla nutria_sessions

Gestiona perfiles de usuario asociados a cada sesión conversacional.
Usa psycopg v3 directamente.
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

_db_available: Optional[bool] = None  # None = no chequeado, True/False = resultado cacheado


def _get_conn():
    """Retorna una conexión psycopg3 o None. Cachea el estado de disponibilidad."""
    global _db_available
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return None
    if _db_available is False:
        return None  # ya sabemos que no está disponible, no reintentar
    try:
        import psycopg
        conn = psycopg.connect(db_url, connect_timeout=3)
        _db_available = True
        return conn
    except Exception as e:
        _db_available = False
        print(f"WARNING: No se pudo conectar a PostgreSQL ({e}).")
        return None


def init_db():
    """Crea la tabla nutria_sessions si no existe."""
    conn = _get_conn()
    if conn is None:
        print("INFO: Sin DATABASE_URL — se omite init_db (usando MemorySaver).")
        return
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS nutria_sessions (
                        session_id   TEXT PRIMARY KEY,
                        user_profile JSONB NOT NULL,
                        created_at   TIMESTAMPTZ DEFAULT NOW(),
                        updated_at   TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
        print("INFO: Tabla nutria_sessions lista.")
    except Exception as e:
        print(f"WARNING: No se pudo inicializar la base de datos ({e}). Continuando sin persistencia.")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def create_session(session_id: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Inserta una nueva sesión y retorna su info."""
    conn = _get_conn()
    if conn is None:
        # Fallback sin DB: solo devolver los datos recibidos
        return {
            "session_id": session_id,
            "user_profile": user_profile,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO nutria_sessions (session_id, user_profile)
                    VALUES (%s, %s)
                    RETURNING session_id, created_at
                    """,
                    (session_id, json.dumps(user_profile)),
                )
                row = cur.fetchone()
                return {
                    "session_id": row[0],
                    "user_profile": user_profile,
                    "created_at": row[1].isoformat(),
                }
    finally:
        conn.close()


def get_session_profile(session_id: str) -> Optional[Dict[str, Any]]:
    """Retorna el perfil de usuario para la sesión, o None si no existe."""
    conn = _get_conn()
    if conn is None:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_profile FROM nutria_sessions WHERE session_id = %s",
                (session_id,),
            )
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        conn.close()


def list_sessions() -> List[Dict[str, Any]]:
    """Retorna todas las sesiones ordenadas por updated_at desc."""
    conn = _get_conn()
    if conn is None:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT session_id, user_profile, created_at, updated_at "
                "FROM nutria_sessions ORDER BY updated_at DESC"
            )
            rows = cur.fetchall()
            return [
                {
                    "session_id": r[0],
                    "user_profile": r[1],
                    "created_at": r[2].isoformat(),
                    "updated_at": r[3].isoformat(),
                }
                for r in rows
            ]
    finally:
        conn.close()

import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno (incluye LangSmith y DATABASE_URL)
load_dotenv(dotenv_path="configs/.env")

from src.api.app import app  # noqa: F401 — importar para registrar rutas

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY no encontrada en configs/.env")

    langsmith_key = os.getenv("LANGCHAIN_API_KEY")
    if langsmith_key:
        print("INFO: LangSmith tracing habilitado (proyecto: nutria).")
    else:
        print("INFO: LANGCHAIN_API_KEY no configurada — tracing de LangSmith deshabilitado.")

    print("Iniciando NutrIA API...")
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=True)

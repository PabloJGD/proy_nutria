"""
===============================================================================
VISION.PY - Herramienta de Análisis de Imágenes con IA
===============================================================================

Este módulo contiene la herramienta de visión artificial que permite al agente
"ver" imágenes y detectar ingredientes alimenticios.

Usa Google Gemini 1.5 Flash por su:
- Velocidad de respuesta (optimizado para baja latencia)
- Capacidades de visión multimodal (texto + imagen)
- Costo cero en el plan gratuito de Google AI Studio

Flujo de la herramienta:
    1. Recibe una imagen (URL o archivo local)
    2. Codifica la imagen en Base64
    3. Envía la imagen a Gemini con el prompt de análisis
    4. Retorna lista de ingredientes detectados

IMPORTANTE: La API key debe estar configurada en configs/.env como:
    GOOGLE_STUDIO_AI_API_KEY=tu_api_key_aqui
"""

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.utils.helpers import encode_image, download_and_encode_image
import os


@tool
def analyze_image_for_ingredients(image_source: str) -> str:
    """
    Analiza una imagen para identificar ingredientes alimenticios usando Google Gemini.
    
    Esta herramienta es el "ojo" del agente. Permite que los usuarios tomen una foto
    de su nevera, despensa o ingredientes y el sistema los identifique automáticamente.
    
    Args:
        image_source (str): Puede ser:
                           - Ruta local a un archivo de imagen (ej: "/ruta/a/foto.jpg")
                           - URL de una imagen en internet (ej: "https://ejemplo.com/foto.png")
    
    Returns:
        str: Lista de ingredientes separados por comas.
             Ejemplo: "tomates, cebollas, pimiento rojo, ajo, aceite de oliva"
    
    Ejemplo de uso:
        >>> analyze_image_for_ingredients("/fotos/nevera.jpg")
        "leche, huevos, mantequilla, queso, zanahorias, apio"
        
        >>> analyze_image_for_ingredients("https://ejemplo.com/despensa.png")
        "arroz, pasta, lentejas, aceite, sal, especias"
    
    Procesamiento interno:
        1. Detecta si es URL (empieza con "http") o archivo local
        2. Descarga/lee la imagen y la convierte a Base64
        3. Envía a Gemini con prompt específico para detección de alimentos
        4. Gemini analiza la imagen y retorna los ingredientes detectados
    
    Notas:
        - Solo detecta ingredientes VISIBLES en la imagen
        - Retorna nombres genéricos (no marcas específicas)
        - Funciona mejor con imágenes bien iluminadas y claras
    """
    
    # Determinar si la fuente es una URL o un archivo local
    if image_source.startswith("http"):
        # Es una URL - descargar y codificar
        base64_image = download_and_encode_image(image_source)
    else:
        # Es un archivo local - verificar que existe
        if not os.path.exists(image_source):
            return "Error: El archivo de imagen no fue encontrado en la ruta especificada."
        # Leer y codificar el archivo
        base64_image = encode_image(image_source)

    # Inicializar el modelo Gemini 1.5 Flash (optimizado para velocidad)
    # Usamos la API key de Google AI Studio almacenada en .env
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=os.getenv("GOOGLE_STUDIO_AI_API_KEY")
    )
    
    # Construir el mensaje multimodal (texto + imagen)
    # El prompt está diseñado para obtener SOLO nombres de ingredientes
    message = HumanMessage(
        content=[
            {
                "type": "text", 
                "text": (
                    "Analiza esta imagen y lista SOLO los ingredientes alimenticios visibles. "
                    "Retorna únicamente los nombres de los ingredientes separados por comas. "
                    "No incluyas descripciones, cantidades ni explicaciones adicionales. "
                    "Ejemplo de formato esperado: tomate, cebolla, ajo, pollo"
                )
            },
            {
                "type": "image_url", 
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            },
        ]
    )
    
    try:
        # Invocar el modelo con el mensaje multimodal
        response = llm.invoke([message])
        
        # Retornar el contenido de la respuesta (lista de ingredientes)
        return response.content
        
    except Exception as e:
        # Manejar errores de la API de forma amigable
        return f"Error al analizar la imagen con Gemini: {str(e)}"

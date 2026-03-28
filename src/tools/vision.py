"""
vision.py - Análisis de imágenes con GPT-4o Vision
"""

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.utils.helpers import encode_image, download_and_encode_image
import os


@tool
def analyze_image_for_ingredients(image_source: str) -> str:
    """
    Analiza una imagen para identificar ingredientes alimenticios usando GPT-4o Vision.

    Args:
        image_source (str): Ruta local a un archivo de imagen o URL de una imagen.

    Returns:
        str: Lista de ingredientes separados por comas.
             Ejemplo: "tomates, cebollas, pimiento rojo, ajo, aceite de oliva"
    """

    if image_source.startswith("http"):
        base64_image = download_and_encode_image(image_source)
    else:
        if not os.path.exists(image_source):
            return "Error: El archivo de imagen no fue encontrado en la ruta especificada."
        base64_image = encode_image(image_source)

    llm = ChatOpenAI(
        model="gpt-4o",
        max_tokens=300,
    )

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "Analiza esta imagen y lista SOLO los ingredientes alimenticios visibles. "
                    "Retorna únicamente los nombres de los ingredientes separados por comas. "
                    "No incluyas descripciones, cantidades ni explicaciones adicionales. "
                    "Ejemplo de formato esperado: tomate, cebolla, ajo, pollo"
                ),
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "low",
                },
            },
        ]
    )

    try:
        response = llm.invoke([message])
        return response.content
    except Exception as e:
        return f"Error al analizar la imagen: {str(e)}"

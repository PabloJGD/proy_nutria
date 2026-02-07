from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.utils.helpers import encode_image, download_and_encode_image
import os

@tool
def analyze_image_for_ingredients(image_source: str) -> str:
    """
    Analyzes an image to identify food ingredients using Google Gemini.
    Accepts a local file path or a URL as image_source.
    Returns a comma-separated list of identified ingredients.
    """
    
    # Simple check if it's a URL or path
    if image_source.startswith("http"):
        base64_image = download_and_encode_image(image_source)
    else:
        if not os.path.exists(image_source):
            return "Error: Image file not found."
        base64_image = encode_image(image_source)

    # Use Gemini 1.5 Flash for speed and vision capabilities
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GOOGLE_STUDIO_AI_API_KEY"))
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": "Look at this image and list only the visible food ingredients nicely formatted. Return just the ingredient names separated by commas."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
        ]
    )
    
    try:
        response = llm.invoke([message])
        return response.content
    except Exception as e:
        return f"Error analyzing image with Gemini: {str(e)}"

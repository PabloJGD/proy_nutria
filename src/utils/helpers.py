import base64
import requests
from io import BytesIO

def encode_image(image_path: str) -> str:
    """Encodes a local image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def download_and_encode_image(image_url: str) -> str:
    """Downloads an image from URL and encodes to base64."""
    response = requests.get(image_url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode('utf-8')

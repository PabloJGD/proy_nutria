
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

load_dotenv()  # carga .env del directorio raíz

import uuid
from src.models.schemas import AgentInput, UserProfile
from src.agents.chef_agent import process_request

def test_translation():
    profile = UserProfile(
        name="TestUser",
        age=25,
        dietary_restrictions=["Ninguna"],
        allergies=["Ninguna"],
        health_goals="Comida saludable"
    )

    # Input en español
    request = AgentInput(
        text_description="pollo y brócoli",
        user_profile=profile
    )

    print("Iniciando procesamiento con ingredientes en español...")
    result = process_request(str(uuid.uuid4()), request)
    print("\nResultado del Agente:")
    print("="*50)
    print(result)
    print("="*50)

if __name__ == "__main__":
    test_translation()

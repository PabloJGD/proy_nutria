import os
import sys

# Add project root to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(dotenv_path="configs/.env")

from src.models.schemas import AgentInput, UserProfile
from src.agents.chef_agent import process_request

def main():
    print("\n🥗 Bienvenido a NutrIA - AI Chef 🥗")
    print("============================================\n")

    # 1. Collect User Profile
    print("--- Paso 1: Perfil del Usuario ---")
    name = input("Nombre [Usuario]: ").strip() or "Usuario"
    
    try:
        age_in = input("Edad: ").strip()
        age = int(age_in) if age_in else 30
    except ValueError:
        age = 30
        print("Edad inválida, usando 30.")

    print("\nIngrese restricciones dietéticas (separadas por comas, ej. Vegano, Sin Gluten)")
    restrictions_in = input("> ").strip()
    restrictions = [r.strip() for r in restrictions_in.split(",")] if restrictions_in else []

    print("\nIngrese alergias (separadas por comas, ej. Maní, Mariscos)")
    allergies_in = input("> ").strip()
    allergies = [a.strip() for a in allergies_in.split(",")] if allergies_in else []

    print("\nIngrese objetivos de salud (ej. Perder peso, Ganar músculo)")
    goals = input("> ").strip() or "Comer saludable"

    profile = UserProfile(
        name=name,
        age=age,
        dietary_restrictions=restrictions,
        allergies=allergies,
        health_goals=goals
    )

    # 2. Collect Ingredients
    print("\n--- Paso 2: Ingredientes ---")
    print("Proporcione ingredientes a través de texto o ruta de imagen.")
    
    ingredients_text = input("Lista de ingredientes (separados por comas): ").strip()
    
    image_path = input("Ruta de imagen (opcional, archivo local o URL): ").strip()
    
    if not ingredients_text and not image_path:
        print("\n❌ Error: Debes proporcionar ingredientes en texto o una ruta de imagen.")
        return

    # 3. Create Request
    request = AgentInput(
        text_description=ingredients_text if ingredients_text else None,
        image_data=image_path if image_path else None,
        user_profile=profile
    )

    # 4. Process
    print("\n👨‍🍳 NutrIA Chef está pensando... (esto puede tomar un momento)")
    try:
        result = process_request(request)
        print("\n" + "="*50)
        print("🍽️  RECOMENDACIÓN  🍽️")
        print("="*50 + "\n")
        print(result)
        print("\n" + "="*50)
    except Exception as e:
        print(f"\n❌ Error al procesar la solicitud: {e}")

if __name__ == "__main__":
    main()

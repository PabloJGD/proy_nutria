import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(dotenv_path="configs/.env")

from src.models.schemas import AgentInput, UserProfile
from src.agents.chef_agent import process_request


def collect_profile() -> UserProfile:
    print("\n--- Paso 1: Perfil del Usuario ---")
    name = input("Nombre [Usuario]: ").strip() or "Usuario"

    try:
        age_in = input("Edad (ej. 25 o 0.5 para 6 meses): ").strip()
        age = float(age_in) if age_in else None
    except ValueError:
        age = None
        print("Edad no especificada o formato inválido.")

    print("\nIngrese restricciones dietéticas (separadas por comas, ej. Vegano, Sin Gluten)")
    restrictions_in = input("> ").strip()
    restrictions = [r.strip() for r in restrictions_in.split(",")] if restrictions_in else []

    print("\nIngrese alergias (separadas por comas, ej. Maní, Mariscos)")
    allergies_in = input("> ").strip()
    allergies = [a.strip() for a in allergies_in.split(",")] if allergies_in else []

    print("\nIngrese objetivos de salud (ej. Perder peso, Ganar músculo)")
    goals = input("> ").strip() or "Comer saludable"

    return UserProfile(
        name=name,
        age=age,
        dietary_restrictions=restrictions,
        allergies=allergies,
        health_goals=goals,
    )


def main():
    print("\n🥗 Bienvenido a NutrIA - AI Chef 🥗")
    print("============================================\n")

    profile = collect_profile()
    session_id = str(uuid.uuid4())
    print(f"\n✅ Sesión iniciada: {session_id[:8]}…")
    print("\nEscribe 'salir' para terminar la conversación.\n")

    while True:
        print("\n--- Nuevo turno ---")
        ingredients_text = input("Ingredientes o pregunta de seguimiento: ").strip()

        if ingredients_text.lower() in ("salir", "exit", "quit"):
            print("\n👋 ¡Hasta pronto!")
            break

        image_path = input("Ruta de imagen (opcional, Enter para omitir): ").strip() or None

        if not ingredients_text and not image_path:
            print("❌ Debes proporcionar texto o una imagen.")
            continue

        request = AgentInput(
            text_description=ingredients_text if ingredients_text else None,
            image_data=image_path,
            user_profile=profile,
        )

        print("\n👨‍🍳 NutrIA está pensando…")
        try:
            result = process_request(session_id, request)
            print("\n" + "=" * 50)
            print("🍽️  RECOMENDACIÓN")
            print("=" * 50 + "\n")
            print(result)
            print("\n" + "=" * 50)
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

import streamlit as st
import requests
import json

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="NutrIA", page_icon="🥗", layout="wide")
st.title("🥗 NutrIA — Tu Nutricionista y Chef con IA")

# ─── Sidebar: perfil + gestión de sesión ─────────────────────────────────────
with st.sidebar:
    st.header("👤 Tu Perfil")
    name = st.text_input("Nombre", "Usuario")
    age = st.number_input("Edad", min_value=0.0, max_value=120.0, value=30.0, step=0.1)
    goals = st.text_area("Objetivos de salud", "Comer saludable")
    diet_options = ["Vegetariano", "Vegano", "Sin Gluten", "Sin Lácteos", "Low-Carb", "Keto", "Paleo"]
    selected_diets = st.multiselect("Restricciones dietéticas", diet_options)
    allergies_in = st.text_input("Alergias (separadas por comas)", "")

    user_profile = {
        "name": name,
        "age": age,
        "health_goals": goals,
        "dietary_restrictions": selected_diets,
        "allergies": [a.strip() for a in allergies_in.split(",") if a.strip()],
    }

    st.divider()

    col_new, col_resume = st.columns(2)

    with col_new:
        if st.button("➕ Nueva Sesión", use_container_width=True):
            try:
                resp = requests.post(
                    f"{API_BASE}/sessions",
                    json={"user_profile": user_profile},
                )
                resp.raise_for_status()
                data = resp.json()
                st.session_state["session_id"] = data["session_id"]
                st.session_state["messages"] = []
                st.success(f"Sesión creada")
                st.rerun()
            except Exception as e:
                st.error(f"Error al crear sesión: {e}")

    with col_resume:
        if st.button("🔄 Reanudar", use_container_width=True):
            session_id_input = st.session_state.get("resume_id", "")
            if session_id_input:
                try:
                    resp = requests.get(f"{API_BASE}/sessions/{session_id_input}/history")
                    resp.raise_for_status()
                    data = resp.json()
                    st.session_state["session_id"] = session_id_input
                    st.session_state["messages"] = data.get("messages", [])
                    st.success("Sesión reanudada")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al reanudar: {e}")

    resume_id = st.text_input("ID de sesión a reanudar", key="resume_id")

    if "session_id" in st.session_state:
        st.caption(f"Sesión activa: `{st.session_state['session_id'][:8]}…`")
    else:
        st.info("Crea una sesión para comenzar.")

# ─── Área principal de chat ───────────────────────────────────────────────────

for msg in st.session_state.get("messages", []):
    role_display = "user" if msg["role"] == "human" else "assistant"
    with st.chat_message(role_display):
        st.markdown(msg["content"])

uploaded_image = st.file_uploader("Adjuntar imagen de ingredientes (opcional)", type=["jpg", "jpeg", "png"])

if prompt := st.chat_input("¿Qué ingredientes tienes hoy?"):
    if "session_id" not in st.session_state:
        st.warning("Primero crea una sesión en el panel lateral.")
        st.stop()

    # Mostrar mensaje del usuario de inmediato
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state["messages"].append({"role": "human", "content": prompt})

    session_id = st.session_state["session_id"]

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                files = {}
                if uploaded_image:
                    uploaded_image.seek(0)
                    files = {"image": (uploaded_image.name, uploaded_image, "image/jpeg")}

                resp = requests.post(
                    f"{API_BASE}/sessions/{session_id}/chat",
                    data={"message": prompt},
                    files=files if files else None,
                )
                resp.raise_for_status()
                answer = resp.json()["response"]
                st.markdown(answer)
                st.session_state["messages"].append({"role": "ai", "content": answer})
            except requests.exceptions.ConnectionError:
                st.error("No se pudo conectar al backend. ¿Está corriendo `uvicorn main:app`?")
            except Exception as e:
                st.error(f"Error: {e}")

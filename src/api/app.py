import os
import json
import uuid
import shutil
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import ValidationError

from src.models.schemas import (
    AgentInput,
    UserProfile,
    ChatResponse,
    SessionInfo,
    SessionCreateRequest,
)
from src.agents.chef_agent import process_request, checkpointer as _checkpointer
from src.db.session_store import init_db, create_session, get_session_profile, list_sessions

app = FastAPI(title="NutrIA API", description="Agente conversacional de nutrición con IA.")


@app.on_event("startup")
async def startup():
    init_db()


# ─── Endpoints de sesión ──────────────────────────────────────────────────────

@app.post("/sessions", response_model=SessionInfo)
async def create_session_endpoint(body: SessionCreateRequest):
    """Crea una nueva sesión con el perfil del usuario."""
    session_id = str(uuid.uuid4())
    profile_dict = body.user_profile.model_dump()
    info = create_session(session_id, profile_dict)
    return SessionInfo(**info)


@app.get("/sessions", response_model=List[SessionInfo])
async def list_sessions_endpoint():
    """Lista todas las sesiones disponibles."""
    sessions = list_sessions()
    return [SessionInfo(**s) for s in sessions]


@app.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session_endpoint(session_id: str):
    """Retorna el perfil de una sesión."""
    profile = get_session_profile(session_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")
    return SessionInfo(session_id=session_id, user_profile=profile, created_at="")


@app.get("/sessions/{session_id}/history")
async def get_history(session_id: str):
    """Retorna el historial de mensajes de una sesión (desde el checkpointer)."""
    try:
        config = {"configurable": {"thread_id": session_id}}
        state = _checkpointer.get(config)
        if state is None:
            return {"messages": []}
        messages = []
        for msg in state.get("channel_values", {}).get("messages", []):
            role = "human" if msg.__class__.__name__ == "HumanMessage" else "ai"
            messages.append({"role": role, "content": msg.content})
        return {"messages": messages}
    except Exception as e:
        return {"messages": [], "error": str(e)}


# ─── Endpoint de chat conversacional ─────────────────────────────────────────

@app.post("/sessions/{session_id}/chat", response_model=ChatResponse)
async def chat(
    session_id: str,
    message: str = Form(...),
    image: UploadFile = File(None),
):
    """Envía un mensaje a la sesión y retorna la respuesta del agente."""
    profile_dict = get_session_profile(session_id)
    if profile_dict is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    try:
        profile = UserProfile(**profile_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Perfil de sesión inválido: {e}")

    image_path = None
    if image:
        os.makedirs("temp", exist_ok=True)
        image_path = f"temp/{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    agent_input = AgentInput(
        text_description=message,
        image_data=image_path,
        user_profile=profile,
    )

    try:
        result = process_request(session_id, agent_input)
        return ChatResponse(response=result, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


# ─── Endpoint legacy (compatibilidad) ────────────────────────────────────────

@app.post("/recommend")
async def recommend_recipe(
    text_description: str = Form(None),
    image: UploadFile = File(None),
    user_profile: str = Form(..., description="JSON string of UserProfile"),
):
    """Endpoint legacy — crea una sesión temporal y responde."""
    if not text_description and not image:
        raise HTTPException(status_code=400, detail="Proporciona texto o imagen.")

    try:
        profile_dict = json.loads(user_profile)
        profile = UserProfile(**profile_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"user_profile JSON inválido: {e}")

    image_path = None
    if image:
        os.makedirs("temp", exist_ok=True)
        image_path = f"temp/{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    session_id = str(uuid.uuid4())
    agent_input = AgentInput(
        image_data=image_path,
        text_description=text_description,
        user_profile=profile,
    )

    try:
        result = process_request(session_id, agent_input)
        return {"recommendation": result}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


def _get_or_create_profile(idagente: str) -> UserProfile:
    """Obtiene el perfil de sesión o crea uno genérico."""
    profile_dict = get_session_profile(idagente)
    if profile_dict is None:
        default_profile = UserProfile()
        create_session(idagente, default_profile.model_dump())
        return default_profile
    return UserProfile(**profile_dict)


@app.get("/agent")
async def agent_endpoint_get(idagente: str, msg: str, nombre: str = "Usuario"):
    """Endpoint GET — solo texto, compatible con el frontend Next.js."""
    from fastapi.responses import PlainTextResponse
    profile = _get_or_create_profile(idagente)
    agent_input = AgentInput(text_description=msg, user_profile=profile)
    try:
        result = process_request(idagente, agent_input, user_name=nombre)
        return PlainTextResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent")
async def agent_endpoint_post(
    idagente: str = Form(...),
    msg: str = Form(...),
    nombre: str = Form("Usuario"),
    image: UploadFile = File(None),
):
    """Endpoint POST — texto + imagen opcional, compatible con el frontend Next.js."""
    from fastapi.responses import PlainTextResponse
    profile = _get_or_create_profile(idagente)

    image_path = None
    if image:
        os.makedirs("temp", exist_ok=True)
        image_path = f"temp/{uuid.uuid4()}_{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    agent_input = AgentInput(
        text_description=msg,
        image_data=image_path,
        user_profile=profile,
    )

    try:
        result = process_request(idagente, agent_input, user_name=nombre)
        return PlainTextResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


@app.get("/")
def home():
    return {"message": "NutrIA API is running."}

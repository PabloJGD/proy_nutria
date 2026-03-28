# 🥗 NutrIA: Agente de Nutrición Inteligente con IA

> Asistente conversacional de nutrición impulsado por IA Agéntica + RAG, deployado en producción sobre Google Cloud Run y Vercel.

**Demo en vivo:** [https://nutria-frontend.vercel.app](https://nutria-frontend.vercel.app)
**API Backend:** [https://nutria-backend-722466450755.us-central1.run.app](https://nutria-backend-722466450755.us-central1.run.app)

---

## 📌 Descripción del Proyecto

**NutrIA** es un asistente conversacional de nutrición que:
- Acepta **texto o imagen** de ingredientes y recomienda recetas personalizadas
- Tiene **memoria conversacional** por sesión (LangGraph + PostgreSQL)
- Busca **recetas peruanas** en una base de conocimiento vectorial (RAG con Elasticsearch)
- Analiza **fotos de ingredientes** con visión artificial (Google Gemini)
- Responde siempre en **español** con información nutricional completa
- Tiene **frontend web responsive** con login Google, modo oscuro y soporte de imágenes

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                          │
│         Next.js 16 + TailwindCSS                    │
│              Vercel (CDN global)                     │
└──────────────────────┬──────────────────────────────┘
                       │ GET/POST /agent
┌──────────────────────▼──────────────────────────────┐
│                    BACKEND                           │
│              FastAPI + LangGraph                     │
│           Google Cloud Run (us-central1)             │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │         LangGraph ReAct Agent               │    │
│  │              (GPT-4o)                       │    │
│  │                                             │    │
│  │  Tools:                                     │    │
│  │  ├── 👁️  Vision (Gemini 2.0 Flash Lite)    │    │
│  │  ├── 🔤  Translator ES→EN (GPT-4o-mini)    │    │
│  │  ├── 🗂️  RAG Recetas Peruanas (ES)         │    │
│  │  ├── 🍎  Recipe Search (Spoonacular)        │    │
│  │  └── 📊  Nutrition Info (Spoonacular)       │    │
│  └──────────────────┬──────────────────────────┘    │
│                     │                                │
│  ┌──────────────────▼──────────────────────────┐    │
│  │           Checkpointer LangGraph            │    │
│  │   PostgresSaver (GCP) / MemorySaver (local) │    │
│  └─────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐         ┌──────────▼────────┐
│  PostgreSQL    │         │  Elasticsearch    │
│  GCP VM        │         │  GCP VM           │
│  (sesiones +   │         │  (24 recetas      │
│   historial)   │         │   peruanas RAG)   │
└────────────────┘         └───────────────────┘
                                     │
                           ┌─────────▼─────────┐
                           │   LangSmith        │
                           │   Observabilidad   │
                           └───────────────────┘
```

> 📐 Diagrama interactivo completo: [`docs/agent_architecture.drawio`](docs/agent_architecture.drawio) — abrir en [diagrams.net](https://app.diagrams.net) → pestaña **"NutrIA v4"**

### Flujo de una conversación
1. Usuario se autentica con Google (NextAuth)
2. Frontend envía mensaje (texto y/o imagen) a `GET|POST /agent`
3. Cloud Run recibe la request, carga perfil del usuario
4. LangGraph recupera historial de la sesión (PostgreSQL o MemorySaver)
5. Agente decide qué herramientas usar según el mensaje
6. Respuesta en español → guardada en checkpointer → retornada al frontend

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Frontend** | Next.js 16, TypeScript, TailwindCSS, NextAuth |
| **Backend** | FastAPI, Python 3.12 |
| **Agente** | LangGraph (`create_react_agent`), LangChain |
| **LLM Principal** | OpenAI GPT-4o |
| **Visión** | Google Gemini 2.0 Flash Lite |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Vector Store** | Elasticsearch 8.x (GCP VM) |
| **Memoria** | PostgresSaver (GCP) / MemorySaver (fallback) |
| **Observabilidad** | LangSmith |
| **Deploy Backend** | Google Cloud Run |
| **Deploy Frontend** | Vercel |
| **Package Manager** | uv (Python) / npm (Node) |

---

## 📂 Estructura del Proyecto

```
proy_nutria/
├── Dockerfile                   # Backend → Cloud Run (puerto 8080)
├── main.py                      # Entry point FastAPI
├── pyproject.toml               # Dependencias Python (uv)
├── requirements.txt             # Dependencias para Docker
│
├── configs/
│   └── .env                     # API keys (no commitear)
│
├── frontend/                    # Frontend Next.js → Vercel
│   ├── Dockerfile
│   ├── next.config.ts
│   ├── package.json
│   └── src/app/
│       ├── layout.tsx           # Shell + sidebar responsive
│       ├── page.tsx             # Chat UI + dark mode + imagen
│       ├── globals.css
│       ├── AuthProvider.tsx
│       └── api/
│           ├── agent/route.ts   # Proxy GET/POST → Cloud Run
│           └── auth/[...nextauth]/route.ts
│
├── src/
│   ├── agents/
│   │   └── chef_agent.py        # LangGraph ReAct agent + checkpointer
│   ├── api/
│   │   └── app.py               # FastAPI: /sessions + /agent + /recommend
│   ├── db/
│   │   ├── checkpointer.py      # PostgresSaver o MemorySaver
│   │   └── session_store.py     # CRUD tabla nutria_sessions
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── prompts/
│   │   └── chef_prompt.py       # System prompt template
│   ├── rag/
│   │   ├── filters.py           # build_es_filters() → ES Query DSL
│   │   ├── ingestor.py          # Loaders (JSON, PDF, Web, HuggingFace)
│   │   ├── recipe_tool.py       # @tool search_peruvian_recipes
│   │   └── store.py             # get_vector_store() singleton
│   └── tools/
│       ├── vision.py            # analyze_image_for_ingredients (Gemini)
│       ├── nutrition.py         # find_recipes + get_recipe_details (Spoonacular)
│       └── translator.py        # translate_es_to_en (GPT-4o-mini)
│
├── scripts/
│   ├── nutria_cli.py            # CLI multi-turno local
│   ├── ingest_recipes.py        # Ingesta → Elasticsearch
│   └── data/
│       └── recetas_peruanas.json  # 24 recetas peruanas (corpus curado)
│
└── tests/
    └── unit/
        └── test_models.py
```

---

## ⚙️ Configuración Local

### 1. Requisitos
- Python 3.12
- Node.js 20+
- [uv](https://github.com/astral-sh/uv) para gestión de paquetes Python

### 2. Clonar e instalar
```bash
git clone https://github.com/PabloJGD/proy_nutria.git
cd proy_nutria
uv sync
```

### 3. Variables de entorno
Crear `configs/.env`:
```env
# LLMs
OPENAI_API_KEY=...
GOOGLE_STUDIO_AI_API_KEY=...       # Google AI Studio

# Recetas
SPOONACULAR_API_KEY=...

# PostgreSQL — GCP (opcional; sin esto usa MemorySaver)
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME

# Elasticsearch — GCP (opcional; sin esto RAG deshabilitado)
ELASTICSEARCH_URL=http://HOST:9200
ELASTICSEARCH_API_KEY=...
ES_INDEX_NAME=nutria

# LangSmith — Observabilidad (opcional)
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=nutria
```

### 4. Correr localmente
```bash
# Backend (FastAPI)
uv run uvicorn main:app --reload --port 8000

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

### 5. Ingestar recetas peruanas (requiere Elasticsearch activo)
```bash
uv run python scripts/ingest_recipes.py --source json
```

---

## 🚀 Deploy en Producción

### Backend → Google Cloud Run

```bash
# 1. Autenticarse
gcloud auth login
gcloud config set project TU_PROJECT_ID

# 2. Build y push imagen
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/nutria-backend:latest .

# 3. Deploy
gcloud run deploy nutria-backend \
  --image gcr.io/TU_PROJECT_ID/nutria-backend:latest \
  --platform managed \
  --region us-central1 \
  --port 8080 \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_API_KEY=...,GOOGLE_STUDIO_AI_API_KEY=...,SPOONACULAR_API_KEY=...,DATABASE_URL=...,ELASTICSEARCH_URL=...,ELASTICSEARCH_API_KEY=...,ES_INDEX_NAME=nutria,LANGCHAIN_API_KEY=...,LANGCHAIN_TRACING_V2=true,LANGCHAIN_PROJECT=nutria"
```

### Frontend → Vercel

```bash
cd frontend
npm install -g vercel
vercel deploy --prod
```

Variables de entorno en Vercel:
```
BACKEND_URL=https://TU_CLOUD_RUN_URL
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
NEXTAUTH_SECRET=...
NEXTAUTH_URL=https://TU_APP.vercel.app
```

---

## 🧪 Cómo Testear el Agente

### Test 1 — Texto con ingredientes
```
"Tengo pollo, arroz y brócoli, ¿qué puedo preparar?"
→ El agente traduce a inglés y consulta Spoonacular
```

### Test 2 — Receta peruana (RAG)
```
"Quiero una receta de ceviche peruano"
→ El agente usa search_peruvian_recipes con Elasticsearch
```

### Test 3 — Filtros de dieta
```
"Receta peruana vegetariana de la sierra"
→ RAG con filtros: es_vegetariano=true, region=sierra
```

### Test 4 — Imagen de ingredientes
```
[Subir foto de ingredientes]
→ Gemini analiza la imagen → lista ingredientes → agente recomienda receta
```

### Test 5 — Memoria conversacional
```
Turno 1: "Soy intolerante a la lactosa"
Turno 2: "Dame una receta con pollo"
→ El agente recuerda la restricción del turno anterior
```

### Via API directamente
```bash
# Endpoint compatible con frontend
curl "https://nutria-backend-722466450755.us-central1.run.app/agent?idagente=test@gmail.com&msg=Quiero%20una%20receta%20peruana"

# Health check
curl "https://nutria-backend-722466450755.us-central1.run.app/"
```

---

## 🔌 API REST

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/agent` | Chat texto (compatible frontend) |
| `POST` | `/agent` | Chat texto + imagen (compatible frontend) |
| `POST` | `/sessions` | Crear sesión con perfil |
| `GET` | `/sessions` | Listar sesiones |
| `GET` | `/sessions/{id}` | Perfil de sesión |
| `GET` | `/sessions/{id}/history` | Historial de mensajes |
| `POST` | `/sessions/{id}/chat` | Chat por sesión |
| `GET` | `/docs` | Swagger UI interactivo |

---

## 🧠 Memoria Conversacional

| Modo | Cuándo | Persistencia |
|------|--------|-------------|
| `PostgresSaver` | `DATABASE_URL` configurada | Permanente entre reinicios |
| `MemorySaver` | Sin `DATABASE_URL` | Solo durante el proceso activo |

---

## 🗂️ RAG — Recetas Peruanas

Pipeline de 4 pasos:
```
Load (JSONLoader) → Split (1 receta = 1 Document) → Embed (text-embedding-3-small) → Store (Elasticsearch)
```

Filtros disponibles: `region` (costa/sierra/selva), `meal_type`, `dietary_restrictions`, `allergies`, `max_calories`, `max_prep_time`.

---

## 💰 Costos Estimados

| Servicio | Plan | Costo |
|---------|------|-------|
| Cloud Run | Free tier (2M req/mes) | $0 para demo |
| Vercel | Hobby (gratuito) | $0 |
| GPT-4o | Pay-per-use | ~$0.02-0.05 por conversación |
| Gemini 2.0 Flash Lite | Free tier (30 RPM) | $0 |
| Spoonacular | Free tier (150 req/día) | $0 |
| PostgreSQL GCP VM | e2-micro | ~$7/mes encendida |
| Elasticsearch GCP VM | e2-small | ~$15/mes encendida |

> Las VMs pueden apagarse cuando no se usen — el sistema funciona con fallbacks.

---

## ✅ Roadmap

- [x] LangGraph ReAct Agent con GPT-4o
- [x] Memoria conversacional (PostgresSaver + MemorySaver)
- [x] RAG Recetas Peruanas (Elasticsearch + text-embedding-3-small)
- [x] Visión artificial con Google Gemini
- [x] API REST conversacional con FastAPI
- [x] Frontend responsive Next.js (dark mode, imagen, cámara)
- [x] Deploy Cloud Run + Vercel
- [x] Observabilidad con LangSmith
- [ ] Más fuentes RAG (PDFs MINCUL, HuggingFace, crawl web)
- [ ] Sistema de autenticación propio

---

## 👥 Autor

**Pablo Guizado** — Proyecto Final de Especialización en IA Generativa

---

<p align="center">
  <b>🥗 NutrIA — Tu Chef y Nutricionista Personal con Inteligencia Artificial</b>
</p>

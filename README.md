# 🥗 NutrIA: Agente de Nutrición Inteligente

## 📝 Resumen Ejecutivo

**NutrIA** es un asistente conversacional de nutrición impulsado por **IA Agéntica**. Desarrollado con **LangGraph**, mantiene memoria por sesión (PostgresSaver / MemorySaver), identifica ingredientes mediante visión artificial (Google Gemini), busca recetas peruanas en una base de conocimiento vectorial (Elasticsearch) y conecta con APIs externas para generar recetas personalizadas con información nutricional completa. Las conversaciones son multi-turno: el agente recuerda el contexto de cada sesión.

---

## 🏗️ Arquitectura del Sistema

```mermaid
graph TD
    User([👤 Usuario]) -- "Mensaje + imagen opcional" --> API[🔌 FastAPI]
    API -- "session_id + AgentInput" --> Agent[🤖 LangGraph ReAct Agent]

    subgraph Checkpointer
        PG[(PostgresSaver\nGCP)]
        MEM[(MemorySaver\nfallback local)]
    end

    Agent <--> PG
    Agent <--> MEM

    subgraph Tools [Herramientas]
        Translator[🔤 Translator ES→EN]
        Vision[👁️ Vision Gemini 1.5]
        RAG[🗂️ RAG Recetas Peruanas]
        Nutrition[🍎 Spoonacular API]
    end

    Agent --> Translator
    Agent --> Vision
    Agent --> RAG
    Agent --> Nutrition

    subgraph RAG_Pipeline [RAG Pipeline]
        ES[(Elasticsearch\nGCP Elastic Cloud)]
        Corpus[📄 Corpus JSON\n24 recetas peruanas]
    end

    RAG <--> ES
    Corpus -- "ingest_recipes.py" --> ES

    Nutrition -- "Recetas + Nutrición" --> Agent
    Agent -- "Respuesta (ES)" --> API
    API -- "response" --> User

    subgraph Observability
        LS[📊 LangSmith]
    end
    Agent -.-> LS
```

### Flujo de trabajo
1. **Sesión**: El usuario crea una sesión (`POST /sessions`) con su perfil una sola vez.
2. **Chat multi-turno**: Cada mensaje se envía a `POST /sessions/{id}/chat`; el agente recuerda el contexto.
3. **Checkpointing**: LangGraph persiste el historial en PostgreSQL (GCP) o en memoria si no hay DB.
4. **RAG Peruano**: Si el usuario pregunta por recetas peruanas, el agente consulta el índice Elasticsearch (híbrido: KNN semántico + BM25 + RRF) con filtros de región, dieta y alergias.
5. **Herramientas generales**: el agente traduce ingredientes, analiza imágenes con Gemini y consulta Spoonacular para recetas internacionales.
6. **Trazabilidad**: cada invocación se registra en LangSmith automáticamente.

---

## 📂 Estructura del Proyecto

```
proy_nutria/
├── main.py                      # Entry point — FastAPI + carga de .env
├── pyproject.toml               # Dependencias (uv)
│
├── configs/
│   └── .env                     # API keys (no commitear)
│
├── src/
│   ├── agents/
│   │   └── chef_agent.py        # 🤖 LangGraph ReAct agent + checkpointer
│   │
│   ├── api/
│   │   └── app.py               # 🔌 FastAPI: /sessions + /chat + /recommend
│   │
│   ├── db/
│   │   ├── checkpointer.py      # PostgresSaver o MemorySaver (fallback)
│   │   └── session_store.py     # CRUD tabla nutria_sessions
│   │
│   ├── frontend/
│   │   └── app.py               # 📱 Streamlit — chat conversacional
│   │
│   ├── models/
│   │   └── schemas.py           # 📦 Pydantic models (UserProfile, ChatResponse…)
│   │
│   ├── prompts/
│   │   └── chef_prompt.py       # 📝 SYSTEM_TEMPLATE (string)
│   │
│   ├── rag/
│   │   ├── filters.py           # 🔍 build_es_filters() — ES Query DSL
│   │   ├── ingestor.py          # 📥 Loaders por fuente (JSON, PDF, Web, HF)
│   │   ├── recipe_tool.py       # 🗂️ @tool search_peruvian_recipes
│   │   └── store.py             # 🏪 get_vector_store() — singleton Elasticsearch
│   │
│   └── tools/
│       ├── vision.py            # 👁️ analyze_image_for_ingredients (Gemini)
│       ├── nutrition.py         # 🍎 find_recipes + get_recipe_details (Spoonacular)
│       └── translator.py        # 🔤 translate_es_to_en (GPT-4o-mini)
│
├── scripts/
│   ├── nutria_cli.py            # 💻 CLI multi-turno
│   ├── ingest_recipes.py        # 📥 CLI ingesta → Elasticsearch
│   └── data/
│       └── recetas_peruanas.json # 24 recetas peruanas (corpus curado)
│
└── tests/
    └── unit/
        └── test_models.py
```

---

## 🔧 Herramientas del Agente

| Tool | Archivo | Función | Backend |
|------|---------|---------|---------|
| **Vision** | `src/tools/vision.py` | `analyze_image_for_ingredients()` | Google Gemini 1.5 Flash |
| **Translator** | `src/tools/translator.py` | `translate_es_to_en()` | OpenAI GPT-4o Mini |
| **RAG Peruano** | `src/rag/recipe_tool.py` | `search_peruvian_recipes()` | Elasticsearch (GCP) |
| **Recipe Search** | `src/tools/nutrition.py` | `find_recipes_by_ingredients()` | Spoonacular |
| **Nutrition Info** | `src/tools/nutrition.py` | `get_recipe_details()` | Spoonacular |

---

## ⚙️ Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/PabloJGD/proy_nutria.git
cd proy_nutria
```

### 2. Instalar dependencias con uv
```bash
uv sync
```

### 3. Variables de entorno
Crea/edita `configs/.env`:

```env
# LLMs
OPENAI_API_KEY=...
GOOGLE_STUDIO_AI_API_KEY=...

# Recetas
SPOONACULAR_API_KEY=...

# PostgreSQL — GCP (opcional; sin esto se usa MemorySaver)
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME

# Elasticsearch — GCP Elastic Cloud (opcional; sin esto RAG deshabilitado)
ELASTICSEARCH_URL=https://<deployment>.es.us-central1.gcp.cloud.es.io
ELASTICSEARCH_API_KEY=...
ES_INDEX_NAME=nutria-recetas-peruanas

# LangSmith — Observabilidad (opcional)
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=nutria
```

> Sin `DATABASE_URL` el sistema funciona con `MemorySaver` (memoria solo en proceso).
> Sin `ELASTICSEARCH_URL` el RAG de recetas peruanas está deshabilitado; el agente usa Spoonacular como fallback.

---

## 🗂️ RAG — Base de Conocimiento de Recetas Peruanas

### Ingesta de datos
```bash
# Ver qué se cargará sin indexar
uv run python scripts/ingest_recipes.py --dry-run

# Ingestar solo el corpus JSON curado (24 recetas)
uv run python scripts/ingest_recipes.py --source json

# Ingestar todas las fuentes disponibles
uv run python scripts/ingest_recipes.py
```

### Fuentes de datos
| Fuente | Archivo | Contenido |
|--------|---------|-----------|
| **JSON curado** | `scripts/data/recetas_peruanas.json` | 24 recetas peruanas (costa, sierra, selva) con metadata completa |
| **Spoonacular JSON** | `scripts/data/spoonacular_peruvian.json` | Descarga previa de la API Spoonacular (cuisine=peruvian) |
| **PDFs** | `scripts/data/*.pdf` | Documentos del MINCUL / APEGA |
| **HuggingFace** | `somosnlp-hackathon-2022/gastronomia-peruana` | Dataset público |

### Pipeline RAG (4 pasos)
```
Load (JSONLoader / PyPDFLoader / WebBaseLoader / HuggingFaceDatasetLoader)
  → Split (1 receta = 1 Document; PDFs con RecursiveCharacterTextSplitter)
    → Embed (text-embedding-3-small, 1536 dims)
      → Store (ElasticsearchStore — índice híbrido KNN + BM25 + RRF)
        → Retrieval (similarity_search con filtros ES Query DSL)
```

### Filtros disponibles
El agente puede filtrar por: `region` (costa/sierra/selva), `meal_type`, `dietary_restrictions` (vegetariano, vegano, sin gluten), `allergies` (mariscos, gluten, lácteos), `max_calories`, `max_prep_time`.

---

## 🚀 Ejecución

### Opción A — CLI multi-turno
```bash
uv run python scripts/nutria_cli.py
```

### Opción B — Web (Streamlit + FastAPI)
```bash
# Terminal 1: API
uv run uvicorn main:app --reload

# Terminal 2: Frontend
uv run streamlit run src/frontend/app.py
```

---

## 🔌 API REST

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/sessions` | Crear sesión con perfil de usuario |
| `GET` | `/sessions` | Listar todas las sesiones |
| `GET` | `/sessions/{id}` | Obtener perfil de una sesión |
| `GET` | `/sessions/{id}/history` | Historial de mensajes de la sesión |
| `POST` | `/sessions/{id}/chat` | Enviar mensaje (texto + imagen opcional) |
| `POST` | `/recommend` | Endpoint legacy (compatibilidad) |

### Ejemplo rápido
```bash
# 1. Crear sesión
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_profile": {"name": "Pablo", "age": 30, "dietary_restrictions": [], "allergies": [], "health_goals": "perder peso"}}'

# 2. Preguntar por recetas peruanas (usará RAG)
curl -X POST http://localhost:8000/sessions/{session_id}/chat \
  -F "message=¿qué recetas peruanas de la sierra me recomiendas?"

# 3. Preguntar con ingredientes (usará Spoonacular)
curl -X POST http://localhost:8000/sessions/{session_id}/chat \
  -F "message=tengo pollo y brócoli, ¿qué preparo?"
```

---

## 🧪 Tests

```bash
# Tests unitarios
uv run pytest tests/unit/

# Todos los tests
uv run pytest
```

---

## 🧠 Memoria Persistente

NutrIA usa el sistema de checkpointing nativo de LangGraph:

| Modo | Cuándo se usa | Persistencia |
|------|---------------|--------------|
| `PostgresSaver` | `DATABASE_URL` configurada | Permanente entre reinicios |
| `MemorySaver` | Sin `DATABASE_URL` | Solo durante la sesión del proceso |

Las tablas de LangGraph se crean automáticamente con `checkpointer.setup()`. La tabla de perfiles `nutria_sessions` se crea en startup.

---

## 📊 Observabilidad con LangSmith

Con `LANGCHAIN_API_KEY` y `LANGCHAIN_TRACING_V2=true` configurados, cada invocación del agente aparece automáticamente en el proyecto `nutria` de LangSmith: trazas, herramientas usadas, tokens y latencia.

---

## 💰 Costos estimados

| Componente | Servicio | Costo |
|------------|----------|-------|
| LLM principal | OpenAI GPT-4o | Pay-per-use |
| LLM visión | Google Gemini 1.5 Flash | Free Tier |
| Recetas generales | Spoonacular | Free Tier (150 req/día) |
| Traducción | GPT-4o Mini | Ultra Low Cost |
| Embeddings | text-embedding-3-small | Pay-per-use (muy bajo) |
| Vector Store | Elasticsearch GCP | Elastic Cloud pricing |

---

## 🚀 Roadmap

- [x] Soporte multilingüe (español → inglés automático)
- [x] CLI Interface
- [x] **LangGraph Integration** — flujo ReAct con checkpointing
- [x] **Memoria conversacional** — PostgresSaver + MemorySaver fallback
- [x] **LangSmith tracing** — observabilidad automática
- [x] **API conversacional** — endpoints REST por sesión
- [x] **RAG Recetas Peruanas** — Elasticsearch híbrido (KNN + BM25 + RRF) con filtros de metadata
- [ ] Auth — sistema de usuarios
- [ ] Más fuentes RAG (PDFs MINCUL, HuggingFace, crawl web)

---

## 🐳 Docker

```bash
docker build -t nutria-agent .
docker run -p 8000:8000 --env-file configs/.env nutria-agent
```

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

---

## 👥 Contribuidores

- **Pablo Guizado** - Desarrollador Principal

---

<p align="center">
  <b>🥗 NutrIA - Tu Chef y Nutricionista Personal con Inteligencia Artificial</b>
</p>

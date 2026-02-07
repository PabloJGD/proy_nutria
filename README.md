# 🥗 NutrIA: Agente de Nutrición Inteligente

## 📝 Resumen Ejecutivo

**NutrIA** es un asistente de nutrición avanzada impulsado por **IA Agéntica**. Desarrollado con **LangChain**, este sistema ejecuta acciones autónomas como identificar ingredientes mediante visión artificial (Google Gemini), validar restricciones dietéticas según perfiles clínicos y conectar con APIs externas para generar recetas personalizadas con información nutricional completa.

---

## 🏗️ Arquitectura del Sistema

```mermaid
graph TD
    User([👤 Usuario]) -- "Ingredientes (ES/Imagen)" --> Agent[🤖 NutrIA Agent]
    
    subgraph Tools [Herramientas LangChain]
        Translator[🔤 Translator ES-EN]
        Vision[👁️ Vision Gemini 1.5]
        Nutrition[🍎 Spoonacular API]
    end
    
    Agent --> Translator
    Agent --> Vision
    Agent --> Nutrition
    
    Nutrition -- "Recetas + Nutrición" --> Agent
    Agent -- "Respuesta Amigable (ES)" --> User
```

---
### Flujo de Trabajo:
1.  **Entrada**: El usuario proporciona ingredientes (Texto/Imagen) y su perfil.
2.  **Traducción**: El agente utiliza `translate_es_to_en` para normalizar los términos a inglés (optimización para Spoonacular).
3.  **Identificación**: Gemini 1.5 Flash analiza imágenes para detectar ingredientes adicionales.
4.  **Búsqueda**: El agente consulta Spoonacular para encontrar recetas que coincidan con ingredientes y restricciones.
5.  **Validación**: Se obtiene la ficha nutricional completa para asegurar el cumplimiento de objetivos.
6.  **Entrega**: Respuesta final amigable en español.

---

## 📂 Estructura del Proyecto

```
proy_nutria/
├── main.py                    # Entry point - FastAPI server
├── requirements.txt           # Dependencies (pinned versions)
├── Dockerfile                 # Container config
│
├── configs/
│   └── .env                   # API Keys (OPENAI, GEMINI, SPOONACULAR)
│
├── src/
│   ├── agents/
│   │   └── chef_agent.py      # 🤖 Main LangChain Agent
│   │
│   ├── api/
│   │   └── app.py             # 🔌 FastAPI endpoints
│   │
│   ├── frontend/
│   │   └── app.py             # 📱 Streamlit Web UI
│   │
│   ├── models/
│   │   └── schemas.py         # 📦 Pydantic models
│   │
│   ├── prompts/
│   │   └── chef_prompt.py     # 📝 System prompts
│   │
│   ├── tools/
│   │   ├── vision.py          # 👁️ Image analysis (Gemini)
│   │   ├── nutrition.py       # 🍎 Recipe & nutrition (Spoonacular)
│   │   └── translator.py      # 🔤 Translation tool (ES to EN)
│   │
│   └── utils/
│       └── helpers.py         # 🔧 Utility functions
│
├── scripts/
│   └── nutria_cli.py          # 💻 Command Line Interface
│
└── tests/
```

---

## 🔧 Tools (Herramientas del Agente)

| Tool | Archivo | Función | API Externa |
|------|---------|---------|-------------|
| **Vision Tool** | `src/tools/vision.py` | `analyze_image_for_ingredients()` | Google Gemini 1.5 Flash |
| **Translation** | `src/tools/translator.py` | `translate_es_to_en()` | OpenAI GPT-4o Mini |
| **Recipe Search** | `src/tools/nutrition.py` | `find_recipes_by_ingredients()` | Spoonacular |
| **Nutrition Info** | `src/tools/nutrition.py` | `get_recipe_details()` | Spoonacular |

---

## ⚙️ Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/PabloJGD/proy_nutria.git
cd proy_nutria
```

### 2. Crear entorno virtual (Recomendado)
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Edita `configs/.env` con tus API keys:

```env
# LLM APIs
OPENAI_API_KEY=sk-proj-...
GOOGLE_STUDIO_AI_API_KEY=AIzaSy...

# Nutrition API
SPOONACULAR_API_KEY=eef177...

# Optional
TAVILY_API_KEY=tvly-dev-...
LANGGRAPH_API_KEY=lsv2_pt_...
```

---

## 🚀 Ejecución

### Opción A: Interfaz de Consola (CLI)
Ideal para pruebas rápidas y desarrolladores.
```bash
python scripts/nutria_cli.py
```

### Opción B: Interfaz Web (Streamlit)
```bash
# Terminal 1: API
uvicorn main:app --reload

# Terminal 2: Frontend
streamlit run src/frontend/app.py
```

---

## 📱 Uso

1. **Configura tu perfil**: Metas de salud, alergias y restricciones (Vegano, Keto, etc.).
2. **Añade ingredientes**:
   - 📷 **Cámara**: Foto en vivo de tu nevera.
   - 🖼️ **Upload**: Sube una imagen.
   - ✏️ **Texto**: Escribe "pollo, espinacas, ajo".
3. **Analiza y Cocina**: El agente traducirá tus términos, buscará recetas y te dará el paso a paso nutricional.

---

## 🧪 Tests

```bash
# Ejecutar tests unitarios
pytest tests/unit/

# Ejecutar todos los tests
pytest
```

---

## 🐳 Docker

```bash
# Construir imagen
docker build -t nutria-agent .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file configs/.env nutria-agent
```

---

## 💰 Costos (Estrategia $0)

| Componente | Servicio | Costo |
|------------|----------|-------|
| LLM Vision | Google Gemini 1.5 Flash | Free Tier |
| LLM Agent | OpenAI GPT-4o | Pay-per-use (Céntimos) |
| Recetas | Spoonacular | Free Tier |
| Traducción | GPT-4o Mini | Ultra Low Cost |

---

## 🚀 Roadmap

- [x] **Multi-idioma**: Soporte para español mediante traducción inteligente.
- [x] **CLI Interface**: Ejecución directa en terminal.
- [ ] **LangGraph Integration**: Migración a flujos de estados cíclicos.
- [ ] **RAG Integration**: Base de datos vectorial con guías OMS.
- [ ] **Auth**: Sistema de usuarios y persistencia.

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

---

## 👥 Contribuidores

- **Pablo Guizado** - Desarrollador Principal

---

<p align="center">
  <b>🍳 NutrIA - Tu Chef Personal con Inteligencia Artificial</b>
</p>
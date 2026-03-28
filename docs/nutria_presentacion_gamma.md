# NutrIA: Tu Chef y Nutricionista Personal con IA

Asistente conversacional de nutrición con IA Agéntica + RAG
Proyecto Final · Especialización en IA Generativa
Pablo Guizado
Demo en vivo: nutria-frontend.vercel.app

---

# El Problema

Comer bien es difícil cuando no sabes qué cocinar con lo que tienes

- El usuario tiene ingredientes pero no sabe qué preparar con ellos
- Las apps de nutrición son genéricas y no consideran preferencias culturales
- No hay un asistente que combine visión, recetas locales y memoria del usuario
- La IA generativa puede resolver esto en tiempo real

---

# La Solución

NutrIA: un agente que ve, recuerda y recomienda

- Acepta texto o foto de ingredientes y recomienda recetas personalizadas
- Busca recetas peruanas auténticas desde una base de conocimiento propia (RAG)
- Recuerda restricciones del usuario entre conversaciones
- Responde siempre en español con información nutricional completa
- Disponible 24/7 en la web, desde cualquier dispositivo

---

# Demo: ¿Qué puede hacer NutrIA?

- Texto: "Tengo pollo, arroz y brócoli ¿qué preparo?" → receta con macros
- Imagen: foto de la nevera → Gemini detecta ingredientes → agente recomienda
- RAG: "Dame una receta peruana vegetariana de la sierra" → ceviche de hongos
- Memoria: "Soy intolerante a la lactosa" → el agente lo recuerda en todos los turnos
- Login con Google → historial de conversaciones persistente

---

# Arquitectura del Sistema

Stack production-ready desplegado en la nube

- Frontend: Next.js 16 + TailwindCSS → Vercel (CDN global)
- Backend: FastAPI + LangGraph → Google Cloud Run (serverless, escala a cero)
- Agente: LangGraph create_react_agent con GPT-4o en loop ReAct
- Memoria: PostgresSaver en GCP · fallback automático a MemorySaver
- Observabilidad: LangSmith — trazas, latencia, tokens por conversación

---

# RAG: Recetas Peruanas

Base de conocimiento vectorial propia sobre gastronomía peruana

- Corpus curado: 24 recetas peruanas auténticas (costa, sierra, selva)
- Pipeline: JSON → Split → Embed (text-embedding-3-small) → Elasticsearch GCP
- Búsqueda vectorial por similitud semántica, no por palabras clave
- Filtros: región, tipo de comida, restricciones dietarias, calorías, tiempo
- El agente consulta el RAG automáticamente cuando detecta intención peruana

---

# Agente Conversacional (LangGraph)

Razonamiento multi-paso con herramientas especializadas

- Loop ReAct: Razona → Elige herramienta → Observa resultado → Repite
- 4 herramientas: Visión (Gemini), Traductor (GPT-4o-mini), RAG, Spoonacular
- Checkpointer: cada turno se guarda en PostgreSQL, la memoria persiste
- GPT-4o decide qué herramienta usar sin lógica adicional (fully agentic)
- Respuesta final siempre en español con contexto nutricional

---

# Stack Técnico y Deploy

Arquitectura cloud moderna con costos mínimos

- Python 3.12 · FastAPI · LangGraph · LangChain · Pydantic v2
- OpenAI GPT-4o · Gemini 2.0 Flash Lite · text-embedding-3-small
- Elasticsearch 8.x (GCP VM) · PostgreSQL (GCP VM)
- Deploy backend: gcloud builds submit → Cloud Run (1 comando)
- Deploy frontend: vercel deploy --prod (1 comando)
- Costo total en producción: ~$0/mes en free tiers

---

# Resultados

Sistema completo en producción

- Agente conversacional multi-turno con 5 herramientas integradas
- RAG vectorial con 24 recetas peruanas indexadas en Elasticsearch
- Visión artificial: análisis de fotos de ingredientes con Gemini
- Frontend responsive con login Google, modo oscuro y carga de imágenes
- Deploy en producción: Cloud Run + Vercel, accesible globalmente
- Observabilidad completa con LangSmith

---

# Próximos Pasos

Roadmap de mejoras

- Ampliar corpus RAG: PDFs de MINCUL, recetarios HuggingFace, crawl web
- Añadir perfil nutricional del usuario (edad, peso, objetivo calórico)
- Soporte multimodal en respuestas (imágenes de platos terminados)
- Sistema de autenticación propio sin depender de Google OAuth
- Cache de embeddings para reducir llamadas a OpenAI

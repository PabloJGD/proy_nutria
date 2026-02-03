# 🥗 NutrIA: Agente de Nutrición Inteligente

## 📝 1. Resumen Ejecutivo
**NutrIA** es un asistente de nutrición avanzada y gestión de desperdicio alimentario impulsado por **IA Agéntica**. Desarrollado con el framework **LangChain**, este sistema no se limita a responder preguntas; ejecuta acciones autónomas como identificar ingredientes mediante visión artificial, validar la seguridad alimentaria según perfiles clínicos (bebés, diabéticos, atletas) y conectar con APIs externas para generar planes de cocina reales y listas de compras.

---

## 🧠 2. Objetivo del Proyecto
Diseñar y construir un agente inteligente modular que resuelva dos problemas críticos: el desperdicio de alimentos en el hogar y la falta de personalización nutricional segura. El agente transforma un inventario doméstico aleatorio en una solución alimenticia técnica, eficiente y alineada con la salud del usuario.

---

## 🛠️ 3. Requisitos del Proyecto (Módulo II)

### A. Agente Inteligente Modular
Construido íntegramente con **LangChain**, el agente utiliza un motor de razonamiento que gestiona el contexto y toma decisiones dinámicas basadas en las entradas del usuario (texto o imagen).

### B. Herramientas Personalizadas (Custom Tools)
Se han desarrollado 3 herramientas fundamentales para cumplir con el estándar exigido:
1.  **`InventoryVisionTool` (Ingesta Multimodal):** Utiliza modelos de visión para analizar fotos de neveras o despensas y extraer una lista estructurada de ingredientes.
2.  **`ClinicalSafeGuardTool` (Filtro de Seguridad):** Actúa como un guardián lógico. Valida ingredientes y preparaciones según el perfil (ej. si detecta un bebé de 6 meses, bloquea automáticamente el uso de sal, miel o frutos secos enteros).
3.  **`SmartSourcingTool` (Ejecución de Terceros):** Conecta con la **API de Spoonacular** y **Tavily Search** para obtener recetas verificadas, ajustar porciones según comensales y generar la lista de compras de ingredientes faltantes.

### C. Lógica, Autonomía y Memoria
* **Memoria de Corto Plazo:** Implementación de `ConversationBufferMemory` para recordar restricciones y preferencias durante la sesión.
* **Autonomía:** El agente decide de forma independiente si debe sugerir un sustituto de ingrediente o si es estrictamente necesario añadir un ítem a la lista de compras.

---

## 💎 4. Implicancias y Diferenciadores
¿Por qué usar **NutrIA** en lugar de ChatGPT o Gemini estándar?
* **Agencia Real:** No solo genera texto; "hace" tareas (extrae datos de fotos, consulta bases de datos externas).
* **Validación de Seguridad:** Posee filtros lógicos programados para evitar alucinaciones en temas críticos de salud.
* **Personalización Persistente:** Considera el contexto biológico (etapa de crecimiento, patologías) como prioridad antes que el sabor.

---

## 💰 5. Análisis de Costos (Estrategia $0)
El proyecto es técnica y comercialmente viable sin inversión inicial en infraestructura:
* **LLM:** Google Gemini 1.5 Flash (Free Tier vía Google AI Studio).
* **Orquestación:** LangChain (Librería Open Source).
* **APIs de Datos:** Spoonacular y Tavily (Planes Gratuitos).
* **Hosting:** Streamlit Cloud / Vercel (Capa gratuita para desarrolladores).
* **Base de Datos:** SQLite o Supabase (Free Tier).

---

## 🚀 6. Roadmap y Escalabilidad (Mejoras Futuras)
Para elevar NutrIA a un nivel industrial/SaaS:
1.  **RAG (Retrieval Augmented Generation):** Integración de bases de datos vectoriales con guías oficiales de la OMS y pediatría para dar respaldo científico a cada sugerencia.
2.  **MCP (Model Context Protocol):** Conexión con dispositivos IoT (neveras inteligentes) y sincronización con Apple Health/Google Fit para monitoreo metabólico en tiempo real.

---

## 📦 7. Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/NutrIA.git](https://github.com/tu-usuario/NutrIA.git)
   cd NutrIA
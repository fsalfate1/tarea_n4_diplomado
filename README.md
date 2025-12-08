# Tarea N°4 – Demo HITL con LangChain

Implementación de un flujo **Human-in-the-Loop (HITL)** construido con LangChain, LangGraph y la API de OpenAI. El agente recibe una instrucción (`USER_PROMPT`) para crear archivos en disco mediante una herramienta sensible (`escribir_archivo`). Antes de ejecutar acciones de escritura se solicita confirmación humana, permitiendo aprobar, editar o rechazar la operación.

## Requisitos previos

- macOS / Linux / WSL con **Python 3.11+** y `pip`.
- Acceso a internet para instalar dependencias (pip) y llamar a los modelos de OpenAI.
- Claves válidas para los servicios usados (`OPENAI_API_KEY`, opcionalmente otras integraciones como Tavily, Langfuse o Redis si se habilitan).

## Configuración rápida

```bash
git clone https://github.com/fsalfate1/tarea_n4_diplomado.git
cd tarea_n4_diplomado
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # o crea tu propio archivo con las llaves necesarias
```

> **Nota:** Evita subir `.env` al repositorio; contiene credenciales. Añade el archivo a `.gitignore` si aún no lo está.

### Variables de entorno requeridas

Crea un archivo `.env` en la raíz del proyecto e incluye al menos:

```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...          # opcional: solo si usas búsquedas externas
LANGFUSE_SECRET_KEY=sk-lf-...    # opcional
LANGFUSE_PUBLIC_KEY=pk-lf-...    # opcional
LANGFUSE_BASE_URL=https://...    # opcional
REDIS_URL=redis://...            # opcional
```

Organiza el archivo según los servicios que realmente utilizarás.

## Ejecución

```bash
source .venv/bin/activate        # activa el entorno virtual
python tarea_4.py                # ejecuta el flujo HITL
```

Durante la ejecución verás:

1. **Solicitud al agente** con el `USER_PROMPT`.
2. Si la acción implica escritura, el middleware HITL interrumpe y muestra los argumentos propuestos.
3. El usuario responde con `approve`, `edit`, `reject` o `salir`.
4. El agente reanuda y actúa según la decisión entregada.

El prompt por defecto crea el archivo `memo_rag_v3.txt` con lineamientos básicos de RAG, pero puedes modificar `USER_PROMPT` (línea cercana al final de `tarea_4.py`) para definir otros escenarios.

## Archivos principales

- `tarea_4.py`: script que arma el agente, registra la herramienta `escribir_archivo` y orquesta el flujo HITL.
- `requirements.txt`: lista de dependencias (LangChain, LangGraph, Rich, python-dotenv, openai, langchain-openai, etc.).
- `.venv/`: entorno virtual local (no se versiona).
- `.env`: credenciales y llaves (no versionar).
- `memo_rag_v3.txt`: archivo de ejemplo generado por el agente.

## Problemas comunes

- **`zsh: command not found: python`**: activa el venv (`source .venv/bin/activate`) o usa `python3`.
- **`ModuleNotFoundError: No module named 'dotenv'`**: recuerda instalar dependencias con `pip install -r requirements.txt` dentro del venv.
- **`Unable to import langchain_openai`**: asegúrate de que la red permita bajar paquetes y ejecuta `pip install langchain-openai`.
- **Errores de red al instalar**: si estás tras un proxy o con red restringida, configura acceso o instala manualmente los wheels necesarios.

## Personalización

- Cambia `USER_PROMPT` y `THREAD_ID` para simular distintos casos de uso.
- Ajusta `escribir_archivo` o añade más herramientas con el decorador `@tool` de LangChain.
- Integra otros proveedores (`openai:gpt-4o-mini` se puede reemplazar por modelos compatibles con LangChain).

Esta documentación cubre el flujo estándar; adapta los pasos según tus necesidades académicas o experimentos adicionales.

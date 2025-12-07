"""Demo HITL interactivo para la Tarea 4, siguiendo la estructura del módulo."""

from textwrap import dedent
from uuid import uuid4

from dotenv import load_dotenv
from rich import print as rprint
from rich.pretty import Pretty

from langchain.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command


#python tarea_grupal_4_v3.py


load_dotenv()


# ---------------------------------------------------------------------------
# Herramienta sensible que requiere aprobación
# ---------------------------------------------------------------------------
@tool
def escribir_archivo(nombre: str, contenido: str) -> str:
    """Escribe un archivo de texto en disco. ACCIÓN SENSIBLE."""
    with open(nombre, "w", encoding="utf-8") as handler:
        handler.write(contenido)
    return f"✓ Archivo '{nombre}' creado exitosamente."


sys_prompt = dedent(
    """
    Ayuda al usuario creando archivos cuando lo solicite.
    Si ya has creado un archivo con escribir_archivo como respuesta a una solicitud,
    no vuelvas a llamar a escribir_archivo para la misma solicitud.
    En su lugar, informa al usuario que el archivo ya ha sido creado.
    """
).strip()

rprint("Sys prompt:")
rprint(sys_prompt)

# ---------------------------------------------------------------------------
# Crear agente con middleware HITL
# ---------------------------------------------------------------------------
agent_demo_hitl_interactivo = create_agent(
    model=init_chat_model("openai:gpt-4o-mini", temperature=0),
    tools=[escribir_archivo],
    system_prompt=sys_prompt,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "escribir_archivo": {
                    "allowed_decisions": ["approve", "edit", "reject"]
                }
            }
        )
    ],
    checkpointer=InMemorySaver(),
)

# ============================================================
# CONFIGURA TU ESCENARIO AQUÍ
# ============================================================
USER_PROMPT = "Genera un archivo 'memo_rag_v3.txt' con los lineamientos básicos de RAG."
THREAD_ID = "tarea4-hitl-v3"


def nueva_configuracion() -> dict:
    """Devuelve una configuración con un thread_id único."""
    return {"configurable": {"thread_id": f"{THREAD_ID}-{uuid4().hex}"}}


config = nueva_configuracion()

# ============================================================
# Paso 1: Invocar al agente
# ============================================================
print("\n[1] Enviando solicitud al agente...")
resultado = agent_demo_hitl_interactivo.invoke(
    {"messages": [{"role": "user", "content": USER_PROMPT}]},
    config=config,
)

print("El resultado de la primera llamada al agente:")
rprint(Pretty(resultado))

# ============================================================
# Paso 2: Verificar si hay interrupción
# ============================================================
if "__interrupt__" in resultado:
    while True:
        print("\n⚠️  ACCIÓN SENSIBLE DETECTADA\n")
        action_request = resultado["__interrupt__"][0].value["action_requests"][0]
        print("Vista previa de la acción pendiente:")
        rprint(Pretty(action_request))

        decision = input("Responde 'approve', 'edit', 'reject' o 'salir': ").strip().lower()
        if decision not in {"approve", "edit", "reject", "salir"}:
            print("Entrada inválida. Intenta nuevamente.")
            continue

        if decision == "salir":
            print("\n🚪 Salida solicitada. No se ejecutará la acción.")
            break

        if decision == "approve":
            print("\n✅ Decisión: APPROVE - Ejecutando acción.")
            payload = {"type": "approve"}
        elif decision == "edit":
            print("\n📝 Decisión: EDIT")
            nuevo_nombre = input("Nuevo nombre del archivo (Enter para mantener): ").strip() or action_request["args"]["nombre"]
            print("Ingresa el nuevo contenido (línea vacía para terminar, Enter directo para conservar):")
            lineas: list[str] = []
            while True:
                linea = input()
                if linea == "":
                    break
                lineas.append(linea)
            nuevo_contenido = "\n".join(lineas) if lineas else action_request["args"]["contenido"]
            payload = {
                "type": "edit",
                "edited_action": {
                    "name": "escribir_archivo",
                    "args": {"nombre": nuevo_nombre, "contenido": nuevo_contenido},
                },
            }
        else:  # reject
            motivo = input("Motivo del rechazo: ").strip() or "No autorizado para crear archivos en este momento"
            print("\n❌ Decisión: REJECT")
            payload = {"type": "reject", "message": motivo}

        resultado_final = agent_demo_hitl_interactivo.invoke(
            Command(resume={"decisions": [payload]}),
            config=config,
        )

        print("\n✓ Resultado final:")
        rprint(Pretty(resultado_final))
        if decision == "reject":
            print("\nMensaje final del agente (rechazo comunicado):")
            print("Acción rechazada manualmente; no se ejecutó la herramienta.")
        else:
            print("\nMensaje final del agente:")
            print(resultado_final["messages"][-1].content)
        if decision == "reject":
            print("✔ Acción rechazada. No se creó ningún archivo.")

        if decision == "reject":
            repetir = input("\n¿Quieres volver a intentar? (s/n): ").strip().lower()
            if repetir == "s":
                print("\n[Reintentando] Enviando nuevamente la solicitud...\n")
                config = nueva_configuracion()
                resultado = agent_demo_hitl_interactivo.invoke(
                    {"messages": [{"role": "user", "content": USER_PROMPT}]},
                    config=config,
                )
                if "__interrupt__" not in resultado:
                    print("\n✓ No se detectaron acciones sensibles en el reintento.")
                    print("Resultado:", resultado["messages"][-1].content)
                    break
                continue
            print("\nProceso finalizado tras el rechazo.")
        break
else:
    print("\n✓ No se detectaron acciones sensibles.")
    print("Resultado:", resultado["messages"][-1].content)

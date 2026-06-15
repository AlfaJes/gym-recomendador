"""
Gym Recomendador - AI Backend Server
Servidor FastAPI que usa DeepSeek vía OpenCode Zen para recomendaciones inteligentes de ejercicios.
"""
import os
import json
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# ─── Config ───────────────────────────────────────────────────────────
OPENCODE_ZEN_API_KEY = os.environ.get("OPENCODE_ZEN_API_KEY", "")
BASE_URL = "https://opencode.ai/zen/v1"
MODEL = "deepseek-v4-flash-free"

# Si no está en env, intentar obtener desde Hermes internamente
if not OPENCODE_ZEN_API_KEY:
    try:
        import sys
        sys.path.insert(0, "/opt/hermes")
        os.environ.setdefault("HERMES_HOME", "/opt/data")
        from hermes_cli.config import load_config
        import hermes_cli.runtime_provider as rp
        cfg = load_config()
        info = rp.resolve_runtime_provider()
        OPENCODE_ZEN_API_KEY = info.get("api_key", "")
        print(f"✓ API key obtenida de Hermes (longitud: {len(OPENCODE_ZEN_API_KEY)})", flush=True)
    except Exception as e:
        print(f"⚠ No se pudo obtener API key de Hermes: {e}", flush=True)

client = OpenAI(api_key=OPENCODE_ZEN_API_KEY, base_url=BASE_URL)

# ─── Base de datos de ejercicios (misma que la PWA) ──────────────────
EJERCICIOS = {
    "Pecho": [
        {"nombre": "Press banca con barra", "sets": "4", "reps": "8-12", "desc": "Acuéstate en el banco, baja la barra al pecho y empuja hacia arriba.", "emoji": "🏋️", "dificultad": "intermedio", "equipo": "barra, banco"},
        {"nombre": "Press inclinado con mancuernas", "sets": "4", "reps": "8-12", "desc": "Banco a 45°, baja las mancuernas al pecho y sube.", "emoji": "🏋️", "dificultad": "intermedio", "equipo": "mancuernas, banco"},
        {"nombre": "Aperturas con mancuernas", "sets": "3", "reps": "12-15", "desc": "Acuéstate en banco plano, brazos abiertos y junta las mancuernas.", "emoji": "🤲", "dificultad": "principiante", "equipo": "mancuernas, banco"},
        {"nombre": "Fondos en paralelas", "sets": "3", "reps": "8-15", "desc": "Sujétate en las paralelas, baja flexionando brazos y sube.", "emoji": "💪", "dificultad": "avanzado", "equipo": "paralelas"},
        {"nombre": "Press declinado con barra", "sets": "4", "reps": "8-12", "desc": "Banco declinado, enfoca el esfuerzo en el pecho inferior.", "emoji": "🏋️", "dificultad": "intermedio", "equipo": "barra, banco declinado"},
    ],
    "Espalda": [
        {"nombre": "Dominadas (Pull-ups)", "sets": "4", "reps": "6-12", "desc": "Agarre prono, sube hasta que la barbilla pase la barra.", "emoji": "🤸", "dificultad": "intermedio", "equipo": "barra de dominadas"},
        {"nombre": "Remo con barra", "sets": "4", "reps": "8-12", "desc": "Inclínate hacia adelante, lleva la barra al abdomen.", "emoji": "🏋️", "dificultad": "intermedio", "equipo": "barra"},
        {"nombre": "Jalón al pecho (Lat pulldown)", "sets": "4", "reps": "10-12", "desc": "En polea alta, lleva la barra al pecho con agarre ancho.", "emoji": "⬇️", "dificultad": "principiante", "equipo": "polea"},
        {"nombre": "Remo con mancuerna", "sets": "3", "reps": "10-12", "desc": "Apoya rodilla y mano en banco, rema con la mancuerna.", "emoji": "🦾", "dificultad": "principiante", "equipo": "mancuerna, banco"},
        {"nombre": "Peso muerto", "sets": "4", "reps": "6-8", "desc": "Barra en el suelo, espalda recta, levántala extendiendo caderas.", "emoji": "🏋️", "dificultad": "avanzado", "equipo": "barra, discos"},
    ],
    "Piernas": [
        {"nombre": "Sentadilla (Squat)", "sets": "4", "reps": "8-12", "desc": "Barra en trapecios, baja hasta paralela y sube.", "emoji": "🦵", "dificultad": "intermedio", "equipo": "barra, rack"},
        {"nombre": "Prensa de piernas", "sets": "4", "reps": "10-15", "desc": "Empuja la plataforma sin bloquear rodillas.", "emoji": "🦿", "dificultad": "principiante", "equipo": "máquina prensa"},
        {"nombre": "Peso muerto rumano", "sets": "4", "reps": "8-12", "desc": "Cadera atrás, baja la barra deslizándola por las piernas.", "emoji": "🏋️", "dificultad": "intermedio", "equipo": "barra"},
        {"nombre": "Extensiones de pierna", "sets": "3", "reps": "12-15", "desc": "Máquina de cuádriceps, extiende las piernas completamente.", "emoji": "🦵", "dificultad": "principiante", "equipo": "máquina extensiones"},
        {"nombre": "Curl femoral", "sets": "3", "reps": "12-15", "desc": "Máquina de isquiotibiales, flexiona piernas hacia el glúteo.", "emoji": "🦵", "dificultad": "principiante", "equipo": "máquina curl femoral"},
    ],
    "Hombros": [
        {"nombre": "Press militar con barra", "sets": "4", "reps": "8-12", "desc": "Barra al frente del mentón, empuja hacia arriba.", "emoji": "🏋️", "dificultad": "intermedio", "equipo": "barra"},
        {"nombre": "Elevaciones laterales", "sets": "3", "reps": "12-15", "desc": "Mancuernas a los lados, sube a la altura de los hombros.", "emoji": "🤷", "dificultad": "principiante", "equipo": "mancuernas"},
        {"nombre": "Elevaciones frontales", "sets": "3", "reps": "12-15", "desc": "Mancuernas al frente, sube a la altura de los hombros.", "emoji": "🙋", "dificultad": "principiante", "equipo": "mancuernas"},
        {"nombre": "Pájaros (Reverse fly)", "sets": "3", "reps": "12-15", "desc": "Inclinado, abre los brazos como alas.", "emoji": "🦅", "dificultad": "principiante", "equipo": "mancuernas"},
        {"nombre": "Press Arnold", "sets": "4", "reps": "8-12", "desc": "Mancuernas al frente, gira mientras subes sobre la cabeza.", "emoji": "🔄", "dificultad": "intermedio", "equipo": "mancuernas"},
    ],
    "Bíceps": [
        {"nombre": "Curl con barra", "sets": "4", "reps": "8-12", "desc": "Barra al frente, flexiona codos llevándola al pecho.", "emoji": "💪", "dificultad": "principiante", "equipo": "barra"},
        {"nombre": "Curl con mancuernas", "sets": "3", "reps": "10-12", "desc": "Alterna brazos flexionando hacia el hombro.", "emoji": "💪", "dificultad": "principiante", "equipo": "mancuernas"},
        {"nombre": "Curl martillo", "sets": "3", "reps": "10-12", "desc": "Mancuernas en agarre neutro, flexiona hacia el hombro.", "emoji": "🔨", "dificultad": "principiante", "equipo": "mancuernas"},
        {"nombre": "Curl predicador", "sets": "3", "reps": "10-12", "desc": "En banco predicador, curl con barra EZ.", "emoji": "💪", "dificultad": "intermedio", "equipo": "banco predicador, barra EZ"},
        {"nombre": "Curl concentrado", "sets": "3", "reps": "12-15", "desc": "Sentado, codo en el muslo, curl hacia el pecho.", "emoji": "🎯", "dificultad": "principiante", "equipo": "mancuerna"},
    ],
    "Tríceps": [
        {"nombre": "Press francés", "sets": "4", "reps": "8-12", "desc": "Acostado, barra EZ desde la frente extendiendo codos.", "emoji": "🏋️", "dificultad": "intermedio", "equipo": "barra EZ, banco"},
        {"nombre": "Extensiones en polea", "sets": "4", "reps": "12-15", "desc": "Polea alta, empuja hacia abajo extendiendo codos.", "emoji": "⬇️", "dificultad": "principiante", "equipo": "polea"},
        {"nombre": "Fondos en banco", "sets": "3", "reps": "10-15", "desc": "Manos en un banco, baja y sube con los brazos.", "emoji": "🪑", "dificultad": "principiante", "equipo": "banco"},
        {"nombre": "Patada de tríceps", "sets": "3", "reps": "12-15", "desc": "Inclinado, lleva mancuernas atrás extendiendo codos.", "emoji": "🦵", "dificultad": "principiante", "equipo": "mancuernas"},
        {"nombre": "Press banca agarre cerrado", "sets": "4", "reps": "8-12", "desc": "Agarre estrecho, press de banca enfocando tríceps.", "emoji": "🏋️", "dificultad": "intermedio", "equipo": "barra, banco"},
    ],
    "Abdominales": [
        {"nombre": "Plancha (Plank)", "sets": "3", "reps": "30-60s", "desc": "Antebrazos y puntas, cuerpo recto como una tabla.", "emoji": "📏", "dificultad": "principiante", "equipo": "ninguno"},
        {"nombre": "Crunch", "sets": "3", "reps": "15-20", "desc": "Acostado boca arriba, eleva el torso contrayendo el abdomen.", "emoji": "🧍", "dificultad": "principiante", "equipo": "ninguno"},
        {"nombre": "Elevación de piernas", "sets": "3", "reps": "12-15", "desc": "Colgado o acostado, eleva piernas rectas.", "emoji": "🦵", "dificultad": "intermedio", "equipo": "barra o esterilla"},
        {"nombre": "Russian twist", "sets": "3", "reps": "12-15", "desc": "Sentado inclinado, gira torso con peso a cada lado.", "emoji": "🔄", "dificultad": "intermedio", "equipo": "disco o mancuerna"},
        {"nombre": "Bicicleta", "sets": "3", "reps": "15-20", "desc": "Acostado, lleva codo a rodilla contraria alternando.", "emoji": "🚴", "dificultad": "principiante", "equipo": "ninguno"},
    ],
}

RUTINAS_PREDEFINIDAS = [
    {"nombre": "🔥 Push (Empuje)", "dias": "Lunes / Jueves", "desc": "Pecho, hombros y tríceps", "musculos": ["Pecho", "Hombros", "Tríceps"]},
    {"nombre": "💪 Pull (Tracción)", "dias": "Martes / Viernes", "desc": "Espalda, bíceps y abdominales", "musculos": ["Espalda", "Bíceps", "Abdominales"]},
    {"nombre": "🦵 Piernas + Core", "dias": "Miércoles / Sábado", "desc": "Piernas, glúteos y core", "musculos": ["Piernas", "Abdominales"]},
    {"nombre": "🎯 Full Body", "dias": "L/M/V", "desc": "Cuerpo completo para principiantes", "musculos": ["Pecho", "Espalda", "Piernas", "Hombros", "Bíceps", "Tríceps"]},
]

# ─── System Prompt para el asistente de gym ──────────────────────────
SYSTEM_PROMPT = """Eres un entrenador personal experto con más de 15 años de experiencia en 
fitness, musculación y entrenamiento funcional. Tu objetivo es ayudar a personas a 
mejorar su condición física con recomendaciones personalizadas, seguras y efectivas.

CONOCIMIENTOS:
- Anatomía y biomecánica del ejercicio
- Programación de entrenamientos (Push/Pull/Legs, Full Body, Upper/Lower, etc.)
- Técnica correcta de ejecución y prevención de lesiones
- Progresión de cargas y periodización
- Adaptaciones para principiantes, intermedios y avanzados
- Ejercicios con y sin equipo (barra, mancuernas, poleas, peso corporal)

BASES DE DATOS DISPONIBLES:
Ejercicios por grupo muscular y rutinas predefinidas están disponibles en el contexto.

REGLAS:
1. Siempre prioriza la seguridad y técnica sobre el peso
2. Adapta las recomendaciones al nivel del usuario
3. Sé motivador pero realista
4. Si el usuario menciona una lesión, recomienda consultar a un profesional
5. Responde SIEMPRE en español
6. Tus respuestas deben ser CONCISAS y PRÁCTICAS
7. Incluye series, repeticiones y descanso cuando recomendes ejercicios
8. Da alternativas cuando un ejercicio requiera equipo especializado"""


# ─── FastAPI App ──────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Gym IA Backend iniciado")
    yield
    print("👋 Gym IA Backend detenido")

app = FastAPI(title="Gym Recomendador IA", version="2.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ─── Modelos ──────────────────────────────────────────────────────────
class RecommendRequest(BaseModel):
    objetivo: str = "hipertrofia"  # hipertrofia, fuerza, resistencia, definición
    nivel: str = "intermedio"      # principiante, intermedio, avanzado
    musculos: list[str] = []       # grupos musculares a entrenar (vacíos = cuerpo completo)
    equipo: str = "completo"       # completo, básico (mancuernas/barra), peso corporal, mínimo
    duracion_min: int = 45         # duración deseada en minutos
    dias_por_semana: int = 4       # días disponibles
    lesiones: str = ""             # lesiones o limitaciones
    extra: str = ""                # cualquier info adicional

class AdaptRequest(BaseModel):
    ejercicio: str = ""
    dificultad_actual: str = "intermedio"
    dificultad_deseada: str = "principiante"
    equipo_disponible: str = "completo"
    limitaciones: str = ""

class ExplainRequest(BaseModel):
    ejercicio: str = ""
    aspecto: str = "tecnica"  # tecnica, beneficios, variantes, errores

class ChatRequest(BaseModel):
    mensaje: str = ""
    historial: list = []


# ─── Helper ───────────────────────────────────────────────────────────
def _build_context() -> str:
    """Construye contexto con los ejercicios disponibles."""
    ctx = "--- EJERCICIOS DISPONIBLES ---\n"
    for musculo, ejercicios in EJERCICIOS.items():
        ctx += f"\n{musculo}:\n"
        for ej in ejercicios:
            ctx += f"  - {ej['nombre']} ({ej['sets']}×{ej['reps']}, {ej['dificultad']}, equipo: {ej['equipo']})\n"
    ctx += "\n--- RUTINAS PREDEFINIDAS ---\n"
    for r in RUTINAS_PREDEFINIDAS:
        ctx += f"  {r['nombre']}: {r['desc']} ({r['dias']})\n"
    return ctx


def _call_ai(system: str, user: str, temp: float = 0.7) -> str:
    """Llama al modelo DeepSeek vía OpenCode Zen."""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temp,
            max_tokens=4096,
            timeout=120,
            extra_body={"thinking": {"type": "disabled"}},
        )
        content = (resp.choices[0].message.content or "").strip()
        # Si aún está vacío, intentar con reasoning_content
        if not content:
            rc = getattr(resp.choices[0].message, 'reasoning_content', None)
            if rc:
                content = rc.strip()
        print(f"✓ AI response: {len(content)} chars", flush=True)
        return content
    except Exception as e:
        print(f"✗ AI call failed: {e}", flush=True)
        raise HTTPException(status_code=502, detail=f"Error contacting AI model: {str(e)}")


# ─── Endpoints ────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"app": "Gym Recomendador IA", "version": "2.0.0", "status": "online"}


@app.get("/api/ejercicios")
def get_ejercicios():
    """Devuelve la base de datos de ejercicios."""
    return {"grupos": list(EJERCICIOS.keys()), "ejercicios": EJERCICIOS}


@app.get("/api/rutinas")
def get_rutinas():
    """Devuelve las rutinas predefinidas."""
    return {"rutinas": RUTINAS_PREDEFINIDAS}


@app.post("/api/recommend")
def recommend(req: RecommendRequest):
    """Recomendación inteligente de ejercicios usando IA."""
    user_msg = f"""Recomiéndame una rutina de entrenamiento personalizada.

OBJETIVO: {req.objetivo}
NIVEL: {req.nivel}
MÚSCULOS A ENTRENAR: {', '.join(req.musculos) if req.musculos else 'Cuerpo completo'}
EQUIPO DISPONIBLE: {req.equipo}
DURACIÓN POR SESIÓN: {req.duracion_min} minutos
DÍAS POR SEMANA: {req.dias_por_semana}
LESIONES/LIMITACIONES: {req.lesiones or 'Ninguna'}
INFO EXTRA: {req.extra or 'Ninguna'}

{_build_context()}

IMPORTANTE: 
- Usa SOLO los ejercicios de la base de datos disponible arriba
- Devuelve la respuesta en formato JSON con esta estructura:
{{
  "titulo": "Nombre de la rutina",
  "descripcion": "Breve descripción de la rutina y su enfoque",
  "frecuencia": "X días por semana",
  "calentamiento": "Recomendación de calentamiento (2-3 líneas)",
  "dias": [
    {{
      "nombre": "Nombre del día",
      "enfoque": "Qué grupos musculares se trabajan",
      "ejercicios": [
        {{"nombre": "Nombre del ejercicio", "series": "X", "reps": "Y", "descanso": "Z seg", "notas": "nota opcional"}}
      ]
    }}
  ],
  "consejos": ["Consejo 1", "Consejo 2"],
  "progresion": "Cómo progresar en las siguientes semanas"
}}
Responde SOLO el JSON, sin markdown ni explicaciones adicionales."""

    try:
        result = _call_ai(SYSTEM_PROMPT, user_msg, temp=0.7)
        # Intentar parsear como JSON
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        try:
            data = json.loads(result)
            return {"success": True, "data": data}
        except json.JSONDecodeError:
            return {"success": True, "data": {"raw": result, "note": "No se pudo parsear como JSON, mostrando respuesta raw"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adapt")
def adapt(req: AdaptRequest):
    """Adapta un ejercicio a diferente nivel o equipo."""
    user_msg = f"""Necesito adaptar un ejercicio para alguien.

EJERCICIO ORIGINAL: {req.ejercicio}
DIFICULTAD ACTUAL: {req.dificultad_actual}
DIFICULTAD DESEADA: {req.dificultad_deseada}
EQUIPO DISPONIBLE: {req.equipo_disponible}
LIMITACIONES: {req.limitaciones or 'Ninguna'}

{_build_context()}

Devuelve la respuesta en formato JSON:
{{
  "ejercicio_original": "...",
  "ejercicio_adaptado": "...",
  "series": "...",
  "reps": "...",
  "descanso": "...",
  "cambios": ["Cambio 1", "Cambio 2"],
  "consejos_forma": ["Consejo 1", "Consejo 2"],
  "alternativas": ["Alt 1", "Alt 2"]
}}
Responde SOLO el JSON."""

    try:
        result = _call_ai(SYSTEM_PROMPT, user_msg, temp=0.5)
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        try:
            data = json.loads(result)
            return {"success": True, "data": data}
        except json.JSONDecodeError:
            return {"success": True, "data": {"raw": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/explain")
def explain(req: ExplainRequest):
    """Explica un ejercicio en detalle."""
    user_msg = f"""Explica el siguiente ejercicio enfocándote en: {req.aspecto}

EJERCICIO: {req.ejercicio}

{_build_context()}

Devuelve la respuesta en formato JSON:
{{
  "ejercicio": "...",
  "explicacion": "Explicación detallada de 3-5 líneas",
  "puntos_clave": ["Punto 1", "Punto 2", "Punto 3"],
  "errores_comunes": ["Error 1", "Error 2"],
  "beneficios": ["Beneficio 1", "Beneficio 2"]
}}
Responde SOLO el JSON."""

    try:
        result = _call_ai(SYSTEM_PROMPT, user_msg, temp=0.4)
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        try:
            data = json.loads(result)
            return {"success": True, "data": data}
        except json.JSONDecodeError:
            return {"success": True, "data": {"raw": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Chat libre con el entrenador IA."""
    user_msg = req.mensaje
    context = _build_context()
    full_prompt = f"{context}\n\n---\n\nCONSULTA DEL USUARIO:\n{user_msg}"
    
    try:
        result = _call_ai(SYSTEM_PROMPT, full_prompt)
        return {"success": True, "data": {"respuesta": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Main ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("🔥 Gym Recomendador - Backend IA")
    print(f"   Modelo: {MODEL}")
    print(f"   API: {BASE_URL}")
    uvicorn.run(app, host="0.0.0.0", port=8765)

"""
Configuración central del sistema.

Todo lo sensible o que cambia entre instalaciones se lee de variables de
entorno (archivo .env). Copia `.env.example` a `.env` y edítalo.
Nunca subas tu `.env` a GitHub: ya está en .gitignore.
"""

import os
import secrets
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).with_name(".env"))
except ImportError:  # python-dotenv es opcional
    pass


def _bool(nombre, defecto=False):
    valor = os.getenv(nombre)
    if valor is None:
        return defecto
    return valor.strip().lower() in ("1", "true", "si", "sí", "yes", "on")


# ---------- Base de datos ----------
DATABASE = os.getenv("INVENTARIO_DB", "inventario.db")

# ---------- Servidor API ----------
# 127.0.0.1 = solo esta computadora. Usa 0.0.0.0 únicamente si necesitas que
# otro equipo de tu red (por ejemplo n8n en otra PC) llegue a la API.
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "5000"))
# Nunca actives debug en una red: la consola de depuración de Flask permite
# ejecutar código en la máquina.
API_DEBUG = _bool("API_DEBUG", False)

# Token para la API. Si no defines uno, se genera uno aleatorio en cada
# arranque (seguro, pero n8n tendría que actualizarlo cada vez).
API_TOKEN = os.getenv("API_TOKEN") or ""
API_TOKEN_GENERADO = False
if not API_TOKEN:
    API_TOKEN = secrets.token_urlsafe(24)
    API_TOKEN_GENERADO = True

# Orígenes permitidos para CORS (separados por coma). Vacío = sin CORS.
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

# ---------- n8n ----------
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

# ---------- Inteligencia artificial (opcional) ----------
# Ver ai_provider.py. Si AI_PROVIDER está vacío o es "local", el sistema usa
# su motor de reglas sin conexión, sin costo y sin enviar datos a nadie.
AI_PROVIDER = os.getenv("AI_PROVIDER", "local").strip().lower()
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", "")
AI_TIMEOUT = float(os.getenv("AI_TIMEOUT", "30"))

"""
Proveedor de IA conectable.

El sistema funciona en dos modos:

1. Modo básico (por defecto): AI_PROVIDER=local
   Todo se calcula con reglas y estadística en tu computadora. Sin internet,
   sin costo y sin enviar tus datos a nadie.

2. Modo IA: pegas la API key de la IA que prefieras en el archivo .env
   La IA redacta el análisis y el mensaje al proveedor, y puede ajustar la
   cantidad sugerida. Los números base (ventas por día, días para agotarse)
   siempre se calculan localmente, porque un modelo de lenguaje no es
   confiable para hacer cuentas.

Proveedores soportados (AI_PROVIDER):
    openai      -> api.openai.com
    anthropic   -> Claude (api.anthropic.com)
    gemini      -> Google Gemini
    groq, openrouter, deepseek, mistral, together
    ollama      -> modelos locales gratis (http://localhost:11434)
    lmstudio    -> modelos locales gratis (http://localhost:1234)
    compatible  -> cualquier API compatible con OpenAI; define AI_BASE_URL

Si la IA falla (sin internet, key inválida, respuesta rara), el sistema vuelve
solo al modo básico. Nunca se queda sin respuesta.

Prueba tu configuración con:  python ai_provider.py
"""

import json
import re

import requests

import config

# Proveedores que hablan el formato de OpenAI (/chat/completions)
COMPATIBLES_OPENAI = {
    "openai": ("https://api.openai.com/v1", "gpt-4o-mini"),
    "groq": ("https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"),
    "openrouter": ("https://openrouter.ai/api/v1", "openai/gpt-4o-mini"),
    "deepseek": ("https://api.deepseek.com/v1", "deepseek-chat"),
    "mistral": ("https://api.mistral.ai/v1", "mistral-small-latest"),
    "together": ("https://api.together.xyz/v1", "meta-llama/Llama-3.3-70B-Instruct-Turbo"),
    "ollama": ("http://localhost:11434/v1", "llama3.1"),
    "lmstudio": ("http://localhost:1234/v1", "local-model"),
    "compatible": ("", ""),
}
SIN_KEY = {"ollama", "lmstudio"}
PROVEEDORES = sorted(set(COMPATIBLES_OPENAI) | {"anthropic", "gemini", "local"})


class ErrorIA(Exception):
    """La IA externa no pudo responder; quien llama debe usar el modo básico."""


class ProveedorIA:
    """Cliente mínimo. Solo usa `requests`, sin SDKs extra que instalar."""

    def __init__(self, nombre, api_key="", modelo="", base_url="", timeout=30):
        self.nombre = (nombre or "local").lower()
        self.api_key = api_key
        self.timeout = timeout
        if self.nombre in COMPATIBLES_OPENAI:
            url_def, modelo_def = COMPATIBLES_OPENAI[self.nombre]
            self.base_url = (base_url or url_def).rstrip("/")
            self.modelo = modelo or modelo_def
        elif self.nombre == "anthropic":
            self.base_url = (base_url or "https://api.anthropic.com").rstrip("/")
            self.modelo = modelo or "claude-haiku-4-5"
        elif self.nombre == "gemini":
            self.base_url = (base_url or "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
            self.modelo = modelo or "gemini-2.0-flash"
        else:
            self.base_url, self.modelo = "", ""

    # ---------- estado ----------
    @property
    def activo(self):
        """True si hay una IA externa lista para usarse."""
        if self.nombre == "local" or self.nombre not in PROVEEDORES:
            return False
        if self.nombre == "compatible" and not self.base_url:
            return False
        return bool(self.api_key) or self.nombre in SIN_KEY

    @property
    def descripcion(self):
        return f"{self.nombre} · {self.modelo}" if self.activo else "Modo básico (sin conexión)"

    # ---------- llamada ----------
    def completar(self, prompt, sistema="", max_tokens=800):
        """Devuelve el texto de la respuesta o lanza ErrorIA."""
        if not self.activo:
            raise ErrorIA("No hay proveedor de IA configurado")
        try:
            if self.nombre == "anthropic":
                return self._anthropic(prompt, sistema, max_tokens)
            if self.nombre == "gemini":
                return self._gemini(prompt, sistema, max_tokens)
            return self._openai(prompt, sistema, max_tokens)
        except ErrorIA:
            raise
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as e:
            raise ErrorIA(f"{self.nombre}: {type(e).__name__}") from e

    def _post(self, url, headers, cuerpo):
        r = requests.post(url, headers=headers, json=cuerpo, timeout=self.timeout)
        if r.status_code >= 400:
            # No incluimos el cuerpo: algunos proveedores repiten la key en el error.
            raise ErrorIA(f"{self.nombre} respondió HTTP {r.status_code}")
        return r.json()

    def _openai(self, prompt, sistema, max_tokens):
        mensajes = ([{"role": "system", "content": sistema}] if sistema else []) + [
            {"role": "user", "content": prompt}]
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        datos = self._post(f"{self.base_url}/chat/completions", headers, {
            "model": self.modelo, "messages": mensajes,
            "max_tokens": max_tokens, "temperature": 0.2})
        return datos["choices"][0]["message"]["content"]

    def _anthropic(self, prompt, sistema, max_tokens):
        cuerpo = {"model": self.modelo, "max_tokens": max_tokens,
                  "messages": [{"role": "user", "content": prompt}]}
        if sistema:
            cuerpo["system"] = sistema
        datos = self._post(f"{self.base_url}/v1/messages", {
            "x-api-key": self.api_key, "anthropic-version": "2023-06-01",
            "content-type": "application/json"}, cuerpo)
        return "".join(b.get("text", "") for b in datos["content"])

    def _gemini(self, prompt, sistema, max_tokens):
        cuerpo = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                  "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.2}}
        if sistema:
            cuerpo["systemInstruction"] = {"parts": [{"text": sistema}]}
        # La key va en cabecera, no en la URL, para que no quede en logs.
        datos = self._post(f"{self.base_url}/models/{self.modelo}:generateContent",
                           {"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
                           cuerpo)
        return "".join(p.get("text", "") for p in datos["candidates"][0]["content"]["parts"])

    def completar_json(self, prompt, sistema="", max_tokens=800):
        """Pide JSON y lo parsea, tolerando ```json ... ``` alrededor."""
        texto = self.completar(prompt, sistema, max_tokens)
        coincidencia = re.search(r"\{.*\}", texto, re.S)
        if not coincidencia:
            raise ErrorIA("La IA no devolvió JSON")
        try:
            return json.loads(coincidencia.group(0))
        except json.JSONDecodeError as e:
            raise ErrorIA("JSON inválido de la IA") from e


_instancia = None


def obtener_proveedor_ia(recargar=False):
    """Proveedor configurado en .env (una sola instancia compartida)."""
    global _instancia
    if _instancia is None or recargar:
        _instancia = ProveedorIA(config.AI_PROVIDER, config.AI_API_KEY, config.AI_MODEL,
                                 config.AI_BASE_URL, config.AI_TIMEOUT)
    return _instancia


def aplicar_configuracion(proveedor, api_key="", modelo="", base_url=""):
    """Cambia la IA en caliente (desde la pantalla de Configuración)."""
    config.AI_PROVIDER = (proveedor or "local").lower()
    config.AI_API_KEY = api_key
    config.AI_MODEL = modelo
    config.AI_BASE_URL = base_url
    return obtener_proveedor_ia(recargar=True)


if __name__ == "__main__":
    ia = obtener_proveedor_ia()
    print(f"Proveedor: {ia.descripcion}")
    if not ia.activo:
        print("Funcionando en modo básico. Para usar IA, edita AI_PROVIDER y AI_API_KEY en .env")
    else:
        try:
            print("Respuesta:", ia.completar("Responde solo: OK", max_tokens=10).strip())
        except ErrorIA as e:
            print("No se pudo conectar:", e)

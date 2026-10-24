"""
Lee y guarda valores en el archivo .env sin tocar las demás líneas.

Lo usa la pestaña Configuración para que el dueño del negocio pueda pegar su
API key desde la aplicación, sin abrir archivos de texto.
"""

import os
from pathlib import Path

RUTA_ENV = Path(__file__).with_name(".env")
RUTA_EJEMPLO = Path(__file__).with_name(".env.example")


def leer(ruta=RUTA_ENV):
    valores = {}
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                valores[clave.strip()] = valor.strip()
    return valores


def guardar(cambios, ruta=RUTA_ENV):
    """Actualiza (o agrega) las claves indicadas y las aplica al proceso actual."""
    if not ruta.exists() and RUTA_EJEMPLO.exists() and ruta == RUTA_ENV:
        ruta.write_text(RUTA_EJEMPLO.read_text(encoding="utf-8"), encoding="utf-8")
    lineas = ruta.read_text(encoding="utf-8").splitlines() if ruta.exists() else []
    pendientes = dict(cambios)
    for i, linea in enumerate(lineas):
        limpia = linea.strip()
        if limpia and not limpia.startswith("#") and "=" in limpia:
            clave = limpia.split("=", 1)[0].strip()
            if clave in pendientes:
                lineas[i] = f"{clave}={pendientes.pop(clave)}"
    lineas += [f"{c}={v}" for c, v in pendientes.items()]
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    for clave, valor in cambios.items():
        os.environ[clave] = str(valor)

"""Tests de la lógica central: sugerencia de pedidos, IA opcional y seguridad de la API.

Ejecuta:  python -m pytest
"""

import os
import sqlite3
import sys
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def db(tmp_path, monkeypatch):
    ruta = str(tmp_path / "test.db")
    monkeypatch.setenv("INVENTARIO_DB", ruta)
    import config
    monkeypatch.setattr(config, "DATABASE", ruta)
    from database import Database
    return Database(ruta)


def crear_producto(db, stock, minimo, maximo, precio=2.0, ventas=()):
    con = sqlite3.connect(db.db_name)
    cur = con.cursor()
    cur.execute("INSERT INTO proveedores (nombre, contacto, telefono) VALUES ('Prov', 'Ana', '555')")
    prov = cur.lastrowid
    cur.execute(
        "INSERT INTO productos (codigo, nombre, categoria, precio_compra, precio_venta, "
        "stock_actual, stock_minimo, stock_maximo, proveedor_id) VALUES (?,?,?,?,?,?,?,?,?)",
        (f"P{stock}{minimo}{maximo}", "Arroz 1kg", "Abarrotes", precio, precio * 1.4,
         stock, minimo, maximo, prov))
    pid = cur.lastrowid
    for dias_atras, cantidad in ventas:
        fecha = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO movimientos (producto_id, tipo, cantidad, fecha) VALUES (?,?,?,?)",
                    (pid, "SALIDA", cantidad, fecha))
    con.commit()
    con.close()
    return pid


class IAFalsa:
    """Simula una IA externa sin conexión a internet."""

    def __init__(self, respuesta=None, falla=False):
        self.respuesta, self.falla, self.activo = respuesta, falla, True
        self.descripcion = "falsa · test"

    def completar_json(self, prompt, sistema=""):
        from ai_provider import ErrorIA
        if self.falla:
            raise ErrorIA("sin conexión")
        return self.respuesta


class IAApagada:
    activo = False


# ---------- Modo básico ----------

def test_sugerencia_respeta_limites(db):
    from ai_assistant import AIAssistant
    pid = crear_producto(db, stock=5, minimo=20, maximo=100, ventas=[(i, 3) for i in range(30)])
    r = AIAssistant(db, IAApagada()).analizar_producto(pid)
    cantidad = r["sugerencia"]["cantidad"]
    assert 15 <= cantidad <= 95  # llega al mínimo y no pasa del máximo
    assert r["motor"] == "local"


def test_no_supera_maximo_cerca_del_tope(db):
    # Antes el sistema forzaba un mínimo de 10 unidades aunque no cupieran.
    from ai_assistant import AIAssistant
    pid = crear_producto(db, stock=96, minimo=10, maximo=100)
    r = AIAssistant(db, IAApagada()).analizar_producto(pid)
    assert r["sugerencia"]["cantidad"] <= 4


def test_ventas_diarias_sobre_ventana_completa(db):
    # 30 unidades vendidas en un solo día = 1/día, no 30/día.
    from ai_assistant import AIAssistant
    pid = crear_producto(db, stock=10, minimo=5, maximo=50, ventas=[(3, 30)])
    r = AIAssistant(db, IAApagada()).analizar_producto(pid)
    assert r["analisis"]["ventas_diarias_promedio"] == pytest.approx(1.0)


def test_sin_ventas_no_inventa_demanda(db):
    from ai_assistant import AIAssistant
    pid = crear_producto(db, stock=2, minimo=10, maximo=50)
    r = AIAssistant(db, IAApagada()).analizar_producto(pid)
    assert r["analisis"]["ventas_diarias_promedio"] == 0
    assert r["sugerencia"]["cantidad"] >= 8


# ---------- IA externa ----------

def test_ia_mejora_texto_y_se_limita(db):
    from ai_assistant import AIAssistant
    pid = crear_producto(db, stock=5, minimo=20, maximo=100, ventas=[(i, 3) for i in range(30)])
    ia = IAFalsa({"cantidad": 5000, "razonamiento": "Se vende rápido.",
                  "mensaje_proveedor": "Hola Ana, necesito arroz."})
    r = AIAssistant(db, ia).analizar_producto(pid)
    assert r["sugerencia"]["cantidad"] == 95  # 5000 se recorta al máximo que cabe
    assert r["sugerencia"]["razonamiento"] == "Se vende rápido."
    assert r["mensaje_proveedor"] == "Hola Ana, necesito arroz."
    assert r["motor"] == "falsa · test"


def test_ia_falla_vuelve_a_modo_basico(db):
    from ai_assistant import AIAssistant
    pid = crear_producto(db, stock=5, minimo=20, maximo=100)
    r = AIAssistant(db, IAFalsa(falla=True)).analizar_producto(pid)
    assert r["motor"] == "local"
    assert r["sugerencia"]["cantidad"] >= 15


def test_proveedor_sin_key_queda_inactivo():
    from ai_provider import ProveedorIA
    assert not ProveedorIA("openai", api_key="").activo
    assert not ProveedorIA("local").activo
    assert not ProveedorIA("compatible", api_key="x").activo  # falta AI_BASE_URL
    assert ProveedorIA("ollama").activo  # local, no necesita key
    assert ProveedorIA("anthropic", api_key="x").activo


def test_json_tolera_bloque_markdown(monkeypatch):
    from ai_provider import ProveedorIA
    ia = ProveedorIA("openai", api_key="x")
    monkeypatch.setattr(ia, "completar", lambda *a, **k: '```json\n{"cantidad": 7}\n```')
    assert ia.completar_json("x") == {"cantidad": 7}


# ---------- Seguridad de la API ----------

def test_api_requiere_token(db, monkeypatch):
    import config
    monkeypatch.setattr(config, "API_TOKEN", "secreto-test")
    import importlib
    import api_rest
    importlib.reload(api_rest)
    c = api_rest.app.test_client()
    assert c.get("/api/health").status_code == 200
    assert c.get("/api/productos").status_code == 401
    assert c.get("/api/alertas").status_code == 401  # endpoints de n8n también
    assert c.get("/api/productos", headers={"Authorization": "Bearer malo"}).status_code == 401
    ok = c.get("/api/productos", headers={"Authorization": "Bearer secreto-test"})
    assert ok.status_code == 200


def test_config_segura_por_defecto(monkeypatch):
    for v in ("API_HOST", "API_DEBUG", "API_TOKEN"):
        monkeypatch.delenv(v, raising=False)
    import importlib
    import config
    importlib.reload(config)
    assert config.API_HOST == "127.0.0.1"
    assert config.API_DEBUG is False
    assert len(config.API_TOKEN) >= 24


# ---------- Configuración desde la app ----------

def test_env_store_actualiza_sin_borrar_otras_claves(tmp_path):
    import env_store
    ruta = tmp_path / ".env"
    ruta.write_text("# comentario\nAPI_TOKEN=abc\nAI_PROVIDER=local\n", encoding="utf-8")
    env_store.guardar({"AI_PROVIDER": "openai", "AI_API_KEY": "sk-test"}, ruta)
    valores = env_store.leer(ruta)
    assert valores == {"API_TOKEN": "abc", "AI_PROVIDER": "openai", "AI_API_KEY": "sk-test"}
    assert ruta.read_text(encoding="utf-8").startswith("# comentario")


def test_base_nueva_tiene_columnas_de_fechas(db):
    con = sqlite3.connect(db.db_name)
    columnas = {c[1] for c in con.execute("PRAGMA table_info(productos)")}
    assert {"fecha_ingreso", "fecha_vencimiento", "dias_vida_util"} <= columnas


def test_botones_sin_emojis_y_con_rol():
    from ui_kit import limpiar_texto, rol_por_texto
    assert limpiar_texto("💾 Guardar") == "Guardar"
    assert limpiar_texto("🗑️ Eliminar") == "Eliminar"
    assert limpiar_texto("⟳ Actualizar") == "Actualizar"
    assert rol_por_texto("Nuevo Producto") == "principal"
    assert rol_por_texto("Eliminar") == "peligro"
    assert rol_por_texto("Cancelar") == "secundario"

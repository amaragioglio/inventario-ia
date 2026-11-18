import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name=None):
        if db_name is None:
            from config import DATABASE as db_name
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        """Inicializa la base de datos con todas las tablas necesarias"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabla de Proveedores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                contacto TEXT,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                activo INTEGER DEFAULT 1,
                fecha_registro TEXT
            )
        ''')

        # Tabla de Productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                categoria TEXT,
                precio_compra REAL,
                precio_venta REAL,
                stock_actual INTEGER DEFAULT 0,
                stock_minimo INTEGER DEFAULT 10,
                stock_maximo INTEGER DEFAULT 100,
                proveedor_id INTEGER,
                activo INTEGER DEFAULT 1,
                fecha_registro TEXT,
                FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
            )
        ''')

        # Tabla de Movimientos de Inventario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                tipo TEXT,
                cantidad INTEGER,
                motivo TEXT,
                usuario TEXT,
                fecha TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')

        # Tabla de Alertas de Stock
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                tipo_alerta TEXT,
                mensaje TEXT,
                leida INTEGER DEFAULT 0,
                fecha TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')

        # Tabla de Pedidos Automáticos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos_automaticos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                proveedor_id INTEGER,
                cantidad_solicitada INTEGER,
                estado TEXT DEFAULT 'PENDIENTE',
                fecha_pedido TEXT,
                fecha_procesado TEXT,
                notas TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos(id),
                FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
            )
        ''')

        # Tabla de Configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')

        # Columnas añadidas en versiones posteriores. Se agregan al final para no
        # cambiar el orden de las columnas existentes. Así una base nueva o vieja
        # siempre queda al día, sin scripts de migración manuales.
        cursor.execute("PRAGMA table_info(productos)")
        columnas = {col[1] for col in cursor.fetchall()}
        for nombre, tipo in (("fecha_ingreso", "TEXT"),
                             ("fecha_vencimiento", "TEXT"),
                             ("dias_vida_util", "INTEGER DEFAULT 0")):
            if nombre not in columnas:
                cursor.execute(f"ALTER TABLE productos ADD COLUMN {nombre} {tipo}")

        conn.commit()
        conn.close()

    def ejecutar(self, query, params=()):
        """Ejecuta una consulta que modifica datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid

    def consultar(self, query, params=()):
        """Ejecuta una consulta que devuelve datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    def consultar_uno(self, query, params=()):
        """Ejecuta una consulta que devuelve un solo registro"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        resultado = cursor.fetchone()
        conn.close()
        return resultado

import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="inventario.db"):
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

        # Tabla de Pedidos Automaticos
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

        # Tabla de Configuracion
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')

        # ============================================
        # NUEVAS TABLAS PARA ANALISIS CON GOOGLE AI
        # ============================================

        # Tabla de Predicciones de IA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predicciones_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                tipo_prediccion TEXT NOT NULL,
                valor_predicho REAL,
                confianza REAL,
                periodo_dias INTEGER DEFAULT 30,
                datos_entrada TEXT,
                modelo_usado TEXT DEFAULT 'gemini-pro',
                fecha_prediccion TEXT,
                fecha_validez TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')

        # Tabla de Analisis de IA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analisis_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_analisis TEXT NOT NULL,
                producto_id INTEGER,
                categoria TEXT,
                resultado TEXT,
                recomendaciones TEXT,
                insights TEXT,
                score_confianza REAL,
                tokens_usados INTEGER,
                costo_estimado REAL,
                fecha_analisis TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')

        # Tabla de Historial de Consultas a IA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial_consultas_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                respuesta TEXT,
                modelo TEXT DEFAULT 'gemini-pro',
                tokens_entrada INTEGER,
                tokens_salida INTEGER,
                tiempo_respuesta_ms INTEGER,
                exitoso INTEGER DEFAULT 1,
                error TEXT,
                fecha TEXT
            )
        ''')

        # Tabla de Tendencias Detectadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tendencias_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_tendencia TEXT NOT NULL,
                descripcion TEXT,
                productos_afectados TEXT,
                categorias_afectadas TEXT,
                impacto TEXT,
                accion_recomendada TEXT,
                urgencia TEXT DEFAULT 'MEDIA',
                activa INTEGER DEFAULT 1,
                fecha_deteccion TEXT,
                fecha_expiracion TEXT
            )
        ''')

        # Tabla de Configuracion de IA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion_ia (
                clave TEXT PRIMARY KEY,
                valor TEXT,
                descripcion TEXT,
                tipo TEXT DEFAULT 'string',
                fecha_actualizacion TEXT
            )
        ''')

        # Tabla de Reportes Generados por IA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reportes_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_reporte TEXT NOT NULL,
                titulo TEXT,
                contenido TEXT,
                resumen TEXT,
                datos_json TEXT,
                formato TEXT DEFAULT 'markdown',
                generado_por TEXT DEFAULT 'gemini-pro',
                fecha_generacion TEXT,
                fecha_periodo_inicio TEXT,
                fecha_periodo_fin TEXT
            )
        ''')

        # Tabla de Patrones de Demanda
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patrones_demanda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                categoria TEXT,
                patron_tipo TEXT,
                patron_descripcion TEXT,
                dias_semana TEXT,
                estacionalidad TEXT,
                factores_externos TEXT,
                confianza REAL,
                fecha_analisis TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')

        # Crear indices para mejor rendimiento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predicciones_producto ON predicciones_ia(producto_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predicciones_fecha ON predicciones_ia(fecha_prediccion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analisis_tipo ON analisis_ia(tipo_analisis)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analisis_fecha ON analisis_ia(fecha_analisis)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tendencias_activa ON tendencias_ia(activa)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patrones_producto ON patrones_demanda(producto_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_movimientos_fecha ON movimientos(fecha)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_movimientos_producto ON movimientos(producto_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria)')

        # Insertar configuracion por defecto de IA si no existe
        configuraciones_ia_default = [
            ('google_ai_api_key', '', 'API Key de Google AI (Gemini)', 'secret'),
            ('google_ai_modelo', 'gemini-pro', 'Modelo de Google AI a usar', 'string'),
            ('analisis_automatico', '1', 'Habilitar analisis automatico', 'boolean'),
            ('frecuencia_analisis_horas', '24', 'Frecuencia de analisis en horas', 'integer'),
            ('umbral_confianza_minimo', '0.7', 'Umbral minimo de confianza para predicciones', 'float'),
            ('dias_historico_analisis', '90', 'Dias de historico para analisis', 'integer'),
            ('max_tokens_respuesta', '2048', 'Maximo de tokens en respuesta', 'integer'),
            ('idioma_respuestas', 'es', 'Idioma de las respuestas de IA', 'string'),
            ('notificar_predicciones', '1', 'Notificar predicciones importantes', 'boolean'),
            ('guardar_historial_consultas', '1', 'Guardar historial de consultas', 'boolean')
        ]

        for clave, valor, descripcion, tipo in configuraciones_ia_default:
            cursor.execute('''
                INSERT OR IGNORE INTO configuracion_ia (clave, valor, descripcion, tipo, fecha_actualizacion)
                VALUES (?, ?, ?, ?, ?)
            ''', (clave, valor, descripcion, tipo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

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

    def ejecutar_muchos(self, query, lista_params):
        """Ejecuta una consulta multiples veces con diferentes parametros"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, lista_params)
        conn.commit()
        conn.close()

    def obtener_estadisticas_db(self):
        """Obtiene estadisticas generales de la base de datos"""
        stats = {}

        # Contar registros en cada tabla
        tablas = ['productos', 'proveedores', 'movimientos', 'alertas',
                  'pedidos_automaticos', 'predicciones_ia', 'analisis_ia']

        for tabla in tablas:
            try:
                resultado = self.consultar_uno(f"SELECT COUNT(*) FROM {tabla}")
                stats[tabla] = resultado[0] if resultado else 0
            except:
                stats[tabla] = 0

        return stats

"""
Modulo de integracion con Google AI (Gemini) para analisis inteligente de inventarios.

Este modulo proporciona:
- Analisis de stock y prediccion de demanda
- Recomendaciones inteligentes de compras
- Deteccion de patrones y tendencias
- Generacion de reportes con IA
- Optimizacion de inventario
"""

import json
import os
import time
from datetime import datetime, timedelta
from database import Database

# Intentar importar google-generativeai
try:
    import google.generativeai as genai
    GOOGLE_AI_DISPONIBLE = True
except ImportError:
    GOOGLE_AI_DISPONIBLE = False
    print("[AVISO] google-generativeai no instalado. Ejecute: pip install google-generativeai")


class GoogleAIAssistant:
    """Asistente de IA usando Google Gemini para analisis de inventarios"""

    def __init__(self):
        self.db = Database()
        self.modelo = None
        self.configurado = False
        self._inicializar()

    def _inicializar(self):
        """Inicializa la conexion con Google AI"""
        if not GOOGLE_AI_DISPONIBLE:
            return

        # Obtener API key de la configuracion
        api_key = self._obtener_config('google_ai_api_key')

        if not api_key:
            # Intentar obtener de variable de entorno
            api_key = os.environ.get('GOOGLE_AI_API_KEY', '')

        if api_key:
            try:
                genai.configure(api_key=api_key)
                modelo_nombre = self._obtener_config('google_ai_modelo') or 'gemini-pro'
                self.modelo = genai.GenerativeModel(modelo_nombre)
                self.configurado = True
                print(f"[OK] Google AI configurado con modelo: {modelo_nombre}")
            except Exception as e:
                print(f"[ERROR] Error configurando Google AI: {e}")
                self.configurado = False
        else:
            print("[AVISO] API Key de Google AI no configurada")

    def _obtener_config(self, clave):
        """Obtiene un valor de configuracion de IA"""
        resultado = self.db.consultar_uno(
            "SELECT valor FROM configuracion_ia WHERE clave = ?",
            (clave,)
        )
        return resultado[0] if resultado else None

    def _guardar_config(self, clave, valor):
        """Guarda un valor de configuracion de IA"""
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.ejecutar(
            "UPDATE configuracion_ia SET valor = ?, fecha_actualizacion = ? WHERE clave = ?",
            (valor, fecha, clave)
        )

    def configurar_api_key(self, api_key):
        """Configura la API key de Google AI"""
        self._guardar_config('google_ai_api_key', api_key)
        self._inicializar()
        return self.configurado

    def esta_configurado(self):
        """Verifica si Google AI esta configurado correctamente"""
        return self.configurado and GOOGLE_AI_DISPONIBLE

    def _consultar_ia(self, prompt, guardar_historial=True):
        """Realiza una consulta a Google AI"""
        if not self.esta_configurado():
            return {
                'exito': False,
                'error': 'Google AI no esta configurado',
                'respuesta': None
            }

        inicio = time.time()

        try:
            respuesta = self.modelo.generate_content(prompt)
            tiempo_ms = int((time.time() - inicio) * 1000)

            # Guardar en historial
            if guardar_historial and self._obtener_config('guardar_historial_consultas') == '1':
                self.db.ejecutar('''
                    INSERT INTO historial_consultas_ia
                    (prompt, respuesta, modelo, tiempo_respuesta_ms, exitoso, fecha)
                    VALUES (?, ?, ?, ?, 1, ?)
                ''', (
                    prompt[:1000],  # Limitar prompt guardado
                    respuesta.text[:5000] if respuesta.text else '',
                    self._obtener_config('google_ai_modelo') or 'gemini-pro',
                    tiempo_ms,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

            return {
                'exito': True,
                'respuesta': respuesta.text,
                'tiempo_ms': tiempo_ms
            }

        except Exception as e:
            # Guardar error en historial
            if guardar_historial:
                self.db.ejecutar('''
                    INSERT INTO historial_consultas_ia
                    (prompt, error, exitoso, fecha)
                    VALUES (?, ?, 0, ?)
                ''', (
                    prompt[:1000],
                    str(e),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

            return {
                'exito': False,
                'error': str(e),
                'respuesta': None
            }

    # ============================================
    # ANALISIS DE INVENTARIO
    # ============================================

    def analizar_inventario_general(self):
        """Realiza un analisis completo del inventario usando IA"""

        # Obtener datos del inventario
        productos = self.db.consultar('''
            SELECT p.*, pv.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN proveedores pv ON p.proveedor_id = pv.id
            WHERE p.activo = 1
        ''')

        if not productos:
            return {'exito': False, 'error': 'No hay productos en el inventario'}

        # Preparar resumen de datos
        total_productos = len(productos)
        productos_stock_bajo = sum(1 for p in productos if p[7] <= p[8])
        productos_sin_stock = sum(1 for p in productos if p[7] == 0)
        valor_total = sum((p[6] or 0) * (p[7] or 0) for p in productos)

        # Categorias
        categorias = {}
        for p in productos:
            cat = p[4] or 'Sin categoria'
            if cat not in categorias:
                categorias[cat] = {'cantidad': 0, 'valor': 0, 'stock_bajo': 0}
            categorias[cat]['cantidad'] += 1
            categorias[cat]['valor'] += (p[6] or 0) * (p[7] or 0)
            if p[7] <= p[8]:
                categorias[cat]['stock_bajo'] += 1

        # Obtener movimientos recientes
        movimientos = self.db.consultar('''
            SELECT tipo, COUNT(*) as cantidad, SUM(cantidad) as total
            FROM movimientos
            WHERE fecha >= date('now', '-30 days')
            GROUP BY tipo
        ''')

        mov_resumen = {m[0]: {'cantidad': m[1], 'total': m[2]} for m in movimientos}

        # Construir prompt para IA
        prompt = f"""Eres un experto en gestion de inventarios para un minimarket.
Analiza los siguientes datos y proporciona un analisis detallado con recomendaciones accionables.

DATOS DEL INVENTARIO:
- Total de productos activos: {total_productos}
- Productos con stock bajo: {productos_stock_bajo}
- Productos sin stock: {productos_sin_stock}
- Valor total del inventario: ${valor_total:,.2f}

DISTRIBUCION POR CATEGORIA:
{json.dumps(categorias, indent=2, ensure_ascii=False)}

MOVIMIENTOS ULTIMOS 30 DIAS:
{json.dumps(mov_resumen, indent=2, ensure_ascii=False)}

Por favor proporciona:
1. RESUMEN EJECUTIVO (2-3 oraciones)
2. FORTALEZAS del inventario actual
3. AREAS DE MEJORA identificadas
4. RECOMENDACIONES PRIORITARIAS (top 5)
5. ALERTAS IMPORTANTES que requieren accion inmediata
6. PREDICCION para los proximos 30 dias

Responde en espanol, de forma clara y profesional."""

        resultado = self._consultar_ia(prompt)

        if resultado['exito']:
            # Guardar analisis en base de datos
            self.db.ejecutar('''
                INSERT INTO analisis_ia
                (tipo_analisis, resultado, recomendaciones, fecha_analisis)
                VALUES (?, ?, ?, ?)
            ''', (
                'INVENTARIO_GENERAL',
                resultado['respuesta'],
                '',
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

        return resultado

    def analizar_producto(self, producto_id):
        """Analiza un producto especifico con IA"""

        # Obtener datos del producto
        producto = self.db.consultar_uno('''
            SELECT p.*, pv.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN proveedores pv ON p.proveedor_id = pv.id
            WHERE p.id = ?
        ''', (producto_id,))

        if not producto:
            return {'exito': False, 'error': 'Producto no encontrado'}

        # Obtener historial de movimientos
        movimientos = self.db.consultar('''
            SELECT tipo, cantidad, fecha, motivo
            FROM movimientos
            WHERE producto_id = ?
            ORDER BY fecha DESC
            LIMIT 100
        ''', (producto_id,))

        # Calcular metricas
        dias_historico = int(self._obtener_config('dias_historico_analisis') or 90)
        fecha_inicio = (datetime.now() - timedelta(days=dias_historico)).strftime("%Y-%m-%d")

        ventas = self.db.consultar_uno('''
            SELECT COUNT(*), SUM(cantidad), AVG(cantidad)
            FROM movimientos
            WHERE producto_id = ? AND tipo = 'SALIDA' AND fecha >= ?
        ''', (producto_id, fecha_inicio))

        entradas = self.db.consultar_uno('''
            SELECT COUNT(*), SUM(cantidad)
            FROM movimientos
            WHERE producto_id = ? AND tipo = 'ENTRADA' AND fecha >= ?
        ''', (producto_id, fecha_inicio))

        # Construir prompt
        prompt = f"""Analiza este producto de inventario y proporciona recomendaciones:

INFORMACION DEL PRODUCTO:
- Nombre: {producto[2]}
- Codigo: {producto[1]}
- Categoria: {producto[4] or 'Sin categoria'}
- Precio compra: ${producto[5] or 0:.2f}
- Precio venta: ${producto[6] or 0:.2f}
- Stock actual: {producto[7]} unidades
- Stock minimo: {producto[8]} unidades
- Stock maximo: {producto[9]} unidades
- Proveedor: {producto[-1] or 'Sin proveedor'}

METRICAS DE {dias_historico} DIAS:
- Salidas: {ventas[0] or 0} operaciones, {ventas[1] or 0} unidades totales
- Promedio por salida: {ventas[2] or 0:.1f} unidades
- Entradas: {entradas[0] or 0} operaciones, {entradas[1] or 0} unidades totales

ULTIMOS MOVIMIENTOS:
{json.dumps([{'tipo': m[0], 'cantidad': m[1], 'fecha': m[2]} for m in movimientos[:10]], indent=2)}

Proporciona:
1. ESTADO ACTUAL del producto (critico, bajo, normal, exceso)
2. VELOCIDAD DE ROTACION (alta, media, baja)
3. CANTIDAD OPTIMA A PEDIR y cuando
4. MARGEN DE GANANCIA actual y recomendado
5. RIESGO DE DESABASTO en proximos 30 dias
6. RECOMENDACIONES especificas

Responde en espanol."""

        resultado = self._consultar_ia(prompt)

        if resultado['exito']:
            # Guardar analisis
            self.db.ejecutar('''
                INSERT INTO analisis_ia
                (tipo_analisis, producto_id, resultado, fecha_analisis)
                VALUES (?, ?, ?, ?)
            ''', (
                'PRODUCTO_INDIVIDUAL',
                producto_id,
                resultado['respuesta'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

        return resultado

    def predecir_demanda(self, producto_id=None, dias_prediccion=30):
        """Predice la demanda futura de un producto o categoria"""

        if producto_id:
            # Prediccion para producto especifico
            datos = self._obtener_datos_prediccion_producto(producto_id)
        else:
            # Prediccion general
            datos = self._obtener_datos_prediccion_general()

        if not datos:
            return {'exito': False, 'error': 'No hay suficientes datos para prediccion'}

        prompt = f"""Como experto en prediccion de demanda para retail, analiza estos datos historicos
y predice la demanda para los proximos {dias_prediccion} dias.

DATOS HISTORICOS:
{json.dumps(datos, indent=2, ensure_ascii=False)}

Proporciona:
1. PREDICCION DE DEMANDA para los proximos {dias_prediccion} dias
2. NIVEL DE CONFIANZA de la prediccion (0-100%)
3. FACTORES que pueden afectar la prediccion
4. CANTIDAD RECOMENDADA a tener en stock
5. MEJOR MOMENTO para reabastecer
6. RIESGOS identificados

Responde en formato estructurado en espanol."""

        resultado = self._consultar_ia(prompt)

        if resultado['exito'] and producto_id:
            # Guardar prediccion
            self.db.ejecutar('''
                INSERT INTO predicciones_ia
                (producto_id, tipo_prediccion, periodo_dias, datos_entrada, fecha_prediccion)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                producto_id,
                'DEMANDA',
                dias_prediccion,
                json.dumps(datos),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

        return resultado

    def _obtener_datos_prediccion_producto(self, producto_id):
        """Obtiene datos historicos para prediccion de un producto"""

        # Ventas por dia de la semana
        ventas_dia = self.db.consultar('''
            SELECT strftime('%w', fecha) as dia, SUM(cantidad) as total
            FROM movimientos
            WHERE producto_id = ? AND tipo = 'SALIDA'
            AND fecha >= date('now', '-90 days')
            GROUP BY dia
            ORDER BY dia
        ''', (producto_id,))

        # Ventas por semana
        ventas_semana = self.db.consultar('''
            SELECT strftime('%W', fecha) as semana, SUM(cantidad) as total
            FROM movimientos
            WHERE producto_id = ? AND tipo = 'SALIDA'
            AND fecha >= date('now', '-90 days')
            GROUP BY semana
            ORDER BY semana
        ''', (producto_id,))

        # Producto info
        producto = self.db.consultar_uno(
            "SELECT nombre, stock_actual, stock_minimo FROM productos WHERE id = ?",
            (producto_id,)
        )

        return {
            'producto': producto[0] if producto else 'Desconocido',
            'stock_actual': producto[1] if producto else 0,
            'stock_minimo': producto[2] if producto else 0,
            'ventas_por_dia_semana': {v[0]: v[1] for v in ventas_dia},
            'ventas_por_semana': {v[0]: v[1] for v in ventas_semana}
        }

    def _obtener_datos_prediccion_general(self):
        """Obtiene datos historicos generales para prediccion"""

        # Ventas totales por categoria
        ventas_categoria = self.db.consultar('''
            SELECT p.categoria, SUM(m.cantidad) as total
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            WHERE m.tipo = 'SALIDA' AND m.fecha >= date('now', '-90 days')
            GROUP BY p.categoria
        ''')

        # Tendencia semanal
        tendencia = self.db.consultar('''
            SELECT strftime('%W', fecha) as semana, SUM(cantidad) as total
            FROM movimientos
            WHERE tipo = 'SALIDA' AND fecha >= date('now', '-90 days')
            GROUP BY semana
            ORDER BY semana
        ''')

        return {
            'ventas_por_categoria': {v[0] or 'Sin categoria': v[1] for v in ventas_categoria},
            'tendencia_semanal': [{'semana': t[0], 'total': t[1]} for t in tendencia]
        }

    # ============================================
    # RECOMENDACIONES Y OPTIMIZACION
    # ============================================

    def obtener_recomendaciones_compra(self):
        """Genera recomendaciones de compra basadas en IA"""

        # Productos que necesitan reabastecimiento
        productos_bajo = self.db.consultar('''
            SELECT p.id, p.nombre, p.codigo, p.categoria, p.stock_actual,
                   p.stock_minimo, p.stock_maximo, p.precio_compra,
                   pv.nombre as proveedor
            FROM productos p
            LEFT JOIN proveedores pv ON p.proveedor_id = pv.id
            WHERE p.activo = 1 AND p.stock_actual <= p.stock_minimo * 1.5
            ORDER BY (p.stock_actual * 1.0 / p.stock_minimo) ASC
        ''')

        if not productos_bajo:
            return {
                'exito': True,
                'respuesta': 'No hay productos que requieran reabastecimiento urgente.',
                'productos': []
            }

        # Calcular velocidad de venta para cada producto
        productos_info = []
        for p in productos_bajo:
            ventas = self.db.consultar_uno('''
                SELECT SUM(cantidad), COUNT(*)
                FROM movimientos
                WHERE producto_id = ? AND tipo = 'SALIDA'
                AND fecha >= date('now', '-30 days')
            ''', (p[0],))

            productos_info.append({
                'id': p[0],
                'nombre': p[1],
                'codigo': p[2],
                'categoria': p[3],
                'stock_actual': p[4],
                'stock_minimo': p[5],
                'stock_maximo': p[6],
                'precio_compra': p[7],
                'proveedor': p[8],
                'ventas_30_dias': ventas[0] or 0,
                'frecuencia_ventas': ventas[1] or 0
            })

        prompt = f"""Como experto en compras para retail, analiza estos productos que necesitan reabastecimiento
y genera recomendaciones de compra optimizadas.

PRODUCTOS QUE NECESITAN REABASTECIMIENTO:
{json.dumps(productos_info, indent=2, ensure_ascii=False)}

Para cada producto proporciona:
1. CANTIDAD RECOMENDADA a comprar
2. URGENCIA (critica, alta, media, baja)
3. JUSTIFICACION de la cantidad
4. PROVEEDOR SUGERIDO (si aplica)

Tambien incluye:
- PRESUPUESTO ESTIMADO total
- ORDEN DE PRIORIDAD para compras
- OPTIMIZACIONES sugeridas (combinar pedidos, negociar descuentos, etc.)

Responde en espanol de forma estructurada."""

        resultado = self._consultar_ia(prompt)
        resultado['productos'] = productos_info

        return resultado

    def optimizar_precios(self):
        """Analiza y sugiere optimizacion de precios"""

        # Obtener productos con margenes
        productos = self.db.consultar('''
            SELECT p.id, p.nombre, p.categoria, p.precio_compra, p.precio_venta,
                   p.stock_actual,
                   (SELECT SUM(cantidad) FROM movimientos
                    WHERE producto_id = p.id AND tipo = 'SALIDA'
                    AND fecha >= date('now', '-30 days')) as ventas_mes
            FROM productos p
            WHERE p.activo = 1 AND p.precio_compra > 0 AND p.precio_venta > 0
        ''')

        productos_analisis = []
        for p in productos:
            margen = ((p[4] - p[3]) / p[3] * 100) if p[3] > 0 else 0
            productos_analisis.append({
                'nombre': p[1],
                'categoria': p[2],
                'precio_compra': p[3],
                'precio_venta': p[4],
                'margen_actual': round(margen, 2),
                'stock': p[5],
                'ventas_mes': p[6] or 0
            })

        prompt = f"""Como experto en pricing para retail, analiza estos productos y sugiere optimizaciones de precio.

PRODUCTOS Y MARGENES ACTUALES:
{json.dumps(productos_analisis, indent=2, ensure_ascii=False)}

Proporciona:
1. PRODUCTOS CON MARGEN BAJO que necesitan ajuste
2. PRODUCTOS CON OPORTUNIDAD de subir precio
3. PRODUCTOS CON PRECIO ALTO que pueden afectar ventas
4. ESTRATEGIAS DE PRICING por categoria
5. PROMOCIONES SUGERIDAS para mover inventario lento
6. IMPACTO ESTIMADO en ingresos

Responde en espanol con recomendaciones accionables."""

        return self._consultar_ia(prompt)

    def detectar_tendencias(self):
        """Detecta tendencias en el inventario usando IA"""

        # Obtener datos de tendencias
        ventas_categoria = self.db.consultar('''
            SELECT p.categoria,
                   strftime('%W', m.fecha) as semana,
                   SUM(m.cantidad) as total
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            WHERE m.tipo = 'SALIDA' AND m.fecha >= date('now', '-60 days')
            GROUP BY p.categoria, semana
            ORDER BY p.categoria, semana
        ''')

        # Productos mas vendidos
        top_productos = self.db.consultar('''
            SELECT p.nombre, p.categoria, SUM(m.cantidad) as total
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            WHERE m.tipo = 'SALIDA' AND m.fecha >= date('now', '-30 days')
            GROUP BY m.producto_id
            ORDER BY total DESC
            LIMIT 10
        ''')

        # Productos menos vendidos
        bajo_rotacion = self.db.consultar('''
            SELECT p.nombre, p.categoria, p.stock_actual,
                   COALESCE(SUM(m.cantidad), 0) as ventas
            FROM productos p
            LEFT JOIN movimientos m ON m.producto_id = p.id
                AND m.tipo = 'SALIDA' AND m.fecha >= date('now', '-30 days')
            WHERE p.activo = 1 AND p.stock_actual > 0
            GROUP BY p.id
            HAVING ventas < 5
            ORDER BY ventas ASC
            LIMIT 10
        ''')

        datos = {
            'ventas_por_categoria_semana': [
                {'categoria': v[0], 'semana': v[1], 'total': v[2]}
                for v in ventas_categoria
            ],
            'top_10_productos': [
                {'nombre': p[0], 'categoria': p[1], 'ventas': p[2]}
                for p in top_productos
            ],
            'productos_baja_rotacion': [
                {'nombre': p[0], 'categoria': p[1], 'stock': p[2], 'ventas': p[3]}
                for p in bajo_rotacion
            ]
        }

        prompt = f"""Como analista de datos para retail, identifica tendencias importantes en estos datos de inventario.

DATOS DE VENTAS Y ROTACION:
{json.dumps(datos, indent=2, ensure_ascii=False)}

Identifica:
1. TENDENCIAS AL ALZA - categorias o productos creciendo
2. TENDENCIAS A LA BAJA - categorias o productos decreciendo
3. ESTACIONALIDAD detectada
4. PRODUCTOS ESTRELLA que impulsan ventas
5. PRODUCTOS PROBLEMA con baja rotacion
6. OPORTUNIDADES DE MERCADO
7. RIESGOS IDENTIFICADOS

Para cada tendencia indica:
- Descripcion
- Productos/categorias afectadas
- Impacto estimado
- Accion recomendada
- Urgencia

Responde en espanol de forma estructurada."""

        resultado = self._consultar_ia(prompt)

        if resultado['exito']:
            # Guardar tendencias detectadas
            self.db.ejecutar('''
                INSERT INTO tendencias_ia
                (tipo_tendencia, descripcion, fecha_deteccion)
                VALUES (?, ?, ?)
            ''', (
                'ANALISIS_GENERAL',
                resultado['respuesta'][:2000],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

        return resultado

    # ============================================
    # REPORTES INTELIGENTES
    # ============================================

    def generar_reporte_ejecutivo(self, periodo_dias=30):
        """Genera un reporte ejecutivo completo con IA"""

        fecha_inicio = (datetime.now() - timedelta(days=periodo_dias)).strftime("%Y-%m-%d")

        # Metricas generales
        total_ventas = self.db.consultar_uno('''
            SELECT SUM(m.cantidad * p.precio_venta)
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            WHERE m.tipo = 'SALIDA' AND m.fecha >= ?
        ''', (fecha_inicio,))

        total_compras = self.db.consultar_uno('''
            SELECT SUM(m.cantidad * p.precio_compra)
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            WHERE m.tipo = 'ENTRADA' AND m.fecha >= ?
        ''', (fecha_inicio,))

        productos_vendidos = self.db.consultar_uno('''
            SELECT COUNT(DISTINCT producto_id), SUM(cantidad)
            FROM movimientos
            WHERE tipo = 'SALIDA' AND fecha >= ?
        ''', (fecha_inicio,))

        alertas = self.db.consultar_uno('''
            SELECT COUNT(*) FROM alertas WHERE fecha >= ?
        ''', (fecha_inicio,))

        pedidos = self.db.consultar_uno('''
            SELECT COUNT(*), SUM(cantidad_solicitada)
            FROM pedidos_automaticos
            WHERE fecha_pedido >= ?
        ''', (fecha_inicio,))

        # Valor actual del inventario
        valor_inventario = self.db.consultar_uno('''
            SELECT SUM(stock_actual * precio_venta)
            FROM productos WHERE activo = 1
        ''')

        datos = {
            'periodo_dias': periodo_dias,
            'total_ventas': total_ventas[0] or 0,
            'total_compras': total_compras[0] or 0,
            'margen_bruto': (total_ventas[0] or 0) - (total_compras[0] or 0),
            'productos_distintos_vendidos': productos_vendidos[0] or 0,
            'unidades_vendidas': productos_vendidos[1] or 0,
            'alertas_generadas': alertas[0] or 0,
            'pedidos_automaticos': pedidos[0] or 0,
            'unidades_pedidas': pedidos[1] or 0,
            'valor_inventario_actual': valor_inventario[0] or 0
        }

        prompt = f"""Genera un reporte ejecutivo profesional para un minimarket basado en estos datos.

METRICAS DEL PERIODO ({periodo_dias} dias):
{json.dumps(datos, indent=2, ensure_ascii=False)}

El reporte debe incluir:

1. RESUMEN EJECUTIVO (3-4 oraciones clave)

2. INDICADORES CLAVE (KPIs)
   - Rotacion de inventario
   - Margen de ganancia
   - Eficiencia operativa

3. LOGROS DEL PERIODO

4. AREAS DE ATENCION

5. COMPARATIVA (interpreta si los numeros son buenos/malos)

6. PROYECCION PARA PROXIMO PERIODO

7. RECOMENDACIONES ESTRATEGICAS (top 3)

8. PLAN DE ACCION INMEDIATO

Formato profesional, en espanol, listo para presentar a gerencia."""

        resultado = self._consultar_ia(prompt)

        if resultado['exito']:
            # Guardar reporte
            self.db.ejecutar('''
                INSERT INTO reportes_ia
                (tipo_reporte, titulo, contenido, datos_json, fecha_generacion,
                 fecha_periodo_inicio, fecha_periodo_fin)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                'EJECUTIVO',
                f'Reporte Ejecutivo - {periodo_dias} dias',
                resultado['respuesta'],
                json.dumps(datos),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                fecha_inicio,
                datetime.now().strftime("%Y-%m-%d")
            ))

        return resultado

    def generar_reporte_proveedor(self, proveedor_id):
        """Genera un reporte de desempeno de proveedor"""

        # Datos del proveedor
        proveedor = self.db.consultar_uno(
            "SELECT * FROM proveedores WHERE id = ?",
            (proveedor_id,)
        )

        if not proveedor:
            return {'exito': False, 'error': 'Proveedor no encontrado'}

        # Productos del proveedor
        productos = self.db.consultar('''
            SELECT nombre, stock_actual, stock_minimo, precio_compra
            FROM productos
            WHERE proveedor_id = ? AND activo = 1
        ''', (proveedor_id,))

        # Pedidos al proveedor
        pedidos = self.db.consultar('''
            SELECT estado, COUNT(*), SUM(cantidad_solicitada)
            FROM pedidos_automaticos
            WHERE proveedor_id = ?
            GROUP BY estado
        ''', (proveedor_id,))

        datos = {
            'proveedor': {
                'nombre': proveedor[1],
                'contacto': proveedor[2],
                'telefono': proveedor[3],
                'email': proveedor[4]
            },
            'productos': [
                {'nombre': p[0], 'stock': p[1], 'minimo': p[2], 'precio': p[3]}
                for p in productos
            ],
            'pedidos': {p[0]: {'cantidad': p[1], 'unidades': p[2]} for p in pedidos}
        }

        prompt = f"""Genera un analisis de proveedor para evaluacion.

DATOS DEL PROVEEDOR:
{json.dumps(datos, indent=2, ensure_ascii=False)}

Incluye:
1. RESUMEN del proveedor
2. PRODUCTOS SUMINISTRADOS y su estado
3. HISTORIAL DE PEDIDOS
4. PUNTOS FUERTES del proveedor
5. AREAS DE MEJORA
6. RECOMENDACIONES para la relacion comercial
7. RIESGO de dependencia

Responde en espanol."""

        return self._consultar_ia(prompt)

    # ============================================
    # CONSULTAS PERSONALIZADAS
    # ============================================

    def consulta_libre(self, pregunta):
        """Permite hacer consultas libres sobre el inventario"""

        # Obtener contexto basico
        stats = self.db.obtener_estadisticas_db()

        productos_ejemplo = self.db.consultar('''
            SELECT nombre, categoria, stock_actual, precio_venta
            FROM productos WHERE activo = 1
            LIMIT 5
        ''')

        prompt = f"""Eres un asistente experto en gestion de inventarios para un minimarket.

CONTEXTO DEL SISTEMA:
- Total productos: {stats.get('productos', 0)}
- Total proveedores: {stats.get('proveedores', 0)}
- Movimientos registrados: {stats.get('movimientos', 0)}
- Alertas activas: {stats.get('alertas', 0)}

EJEMPLOS DE PRODUCTOS:
{json.dumps([{'nombre': p[0], 'categoria': p[1], 'stock': p[2], 'precio': p[3]} for p in productos_ejemplo], indent=2)}

PREGUNTA DEL USUARIO:
{pregunta}

Responde de forma clara, util y en espanol. Si necesitas mas informacion especifica,
indica que datos adicionales necesitarias para dar una mejor respuesta."""

        return self._consultar_ia(prompt)

    def sugerir_mensaje_proveedor(self, producto_id, cantidad):
        """Genera un mensaje profesional para enviar al proveedor"""

        producto = self.db.consultar_uno('''
            SELECT p.nombre, p.codigo, p.stock_actual, pv.nombre, pv.contacto
            FROM productos p
            LEFT JOIN proveedores pv ON p.proveedor_id = pv.id
            WHERE p.id = ?
        ''', (producto_id,))

        if not producto:
            return {'exito': False, 'error': 'Producto no encontrado'}

        prompt = f"""Genera un mensaje profesional de pedido para enviar al proveedor.

DATOS:
- Producto: {producto[0]} (Codigo: {producto[1]})
- Stock actual: {producto[2]} unidades
- Cantidad a pedir: {cantidad} unidades
- Proveedor: {producto[3] or 'Sin nombre'}
- Contacto: {producto[4] or 'Sin contacto'}

El mensaje debe ser:
- Profesional y cordial
- Incluir detalles del producto
- Solicitar confirmacion de disponibilidad
- Preguntar por tiempo de entrega
- Breve pero completo

Genera el mensaje en espanol, listo para enviar por email o WhatsApp."""

        return self._consultar_ia(prompt)

    # ============================================
    # UTILIDADES
    # ============================================

    def obtener_historial_analisis(self, limite=20):
        """Obtiene el historial de analisis realizados"""
        return self.db.consultar('''
            SELECT id, tipo_analisis, producto_id, fecha_analisis,
                   substr(resultado, 1, 200) as resumen
            FROM analisis_ia
            ORDER BY fecha_analisis DESC
            LIMIT ?
        ''', (limite,))

    def obtener_predicciones_activas(self):
        """Obtiene predicciones que aun estan vigentes"""
        return self.db.consultar('''
            SELECT pi.*, p.nombre as producto_nombre
            FROM predicciones_ia pi
            JOIN productos p ON pi.producto_id = p.id
            WHERE pi.fecha_validez >= date('now')
            ORDER BY pi.fecha_prediccion DESC
        ''')

    def obtener_tendencias_activas(self):
        """Obtiene tendencias detectadas que siguen activas"""
        return self.db.consultar('''
            SELECT * FROM tendencias_ia
            WHERE activa = 1
            ORDER BY fecha_deteccion DESC
        ''')

    def obtener_reportes(self, tipo=None, limite=10):
        """Obtiene reportes generados por IA"""
        if tipo:
            return self.db.consultar('''
                SELECT id, tipo_reporte, titulo, fecha_generacion,
                       substr(resumen, 1, 200) as resumen_corto
                FROM reportes_ia
                WHERE tipo_reporte = ?
                ORDER BY fecha_generacion DESC
                LIMIT ?
            ''', (tipo, limite))
        else:
            return self.db.consultar('''
                SELECT id, tipo_reporte, titulo, fecha_generacion,
                       substr(resumen, 1, 200) as resumen_corto
                FROM reportes_ia
                ORDER BY fecha_generacion DESC
                LIMIT ?
            ''', (limite,))

    def obtener_estadisticas_uso(self):
        """Obtiene estadisticas de uso de la IA"""
        consultas = self.db.consultar_uno('''
            SELECT COUNT(*), AVG(tiempo_respuesta_ms),
                   SUM(CASE WHEN exitoso = 1 THEN 1 ELSE 0 END)
            FROM historial_consultas_ia
        ''')

        return {
            'total_consultas': consultas[0] or 0,
            'tiempo_promedio_ms': round(consultas[1] or 0, 2),
            'consultas_exitosas': consultas[2] or 0,
            'tasa_exito': round((consultas[2] or 0) / max(consultas[0] or 1, 1) * 100, 2)
        }


# Funcion de conveniencia para uso rapido
def crear_asistente_ia():
    """Crea y retorna una instancia del asistente de IA"""
    return GoogleAIAssistant()

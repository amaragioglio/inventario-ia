"""
Sistema de Análisis IA Avanzado para Inventario
Detecta patrones, sugiere acciones y genera recomendaciones inteligentes
"""

from datetime import datetime, timedelta
from models import Producto, Movimiento
from database import Database

class AnalizadorIA:
    """Análisis inteligente de inventario con sugerencias automatizadas"""

    def __init__(self):
        self.db = Database()
        self.producto_model = Producto()
        self.movimiento_model = Movimiento()

    # ==================== ANÁLISIS DE MOVIMIENTOS ====================

    def analizar_movimientos_diarios(self, dias=30):
        """
        Analiza movimientos por día para identificar patrones
        Devuelve días con más actividad y estadísticas
        """
        fecha_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")

        query = '''
            SELECT
                DATE(fecha) as dia,
                tipo,
                SUM(cantidad) as total,
                COUNT(*) as num_movimientos
            FROM movimientos
            WHERE fecha >= ?
            GROUP BY DATE(fecha), tipo
            ORDER BY DATE(fecha) DESC
        '''

        resultados = self.db.consultar(query, (fecha_inicio,))

        # Agrupar por día
        dias_dict = {}
        for row in resultados:
            dia, tipo, total, num_mov = row
            if dia not in dias_dict:
                dias_dict[dia] = {'entradas': 0, 'salidas': 0, 'num_movimientos': 0}

            if tipo == 'ENTRADA':
                dias_dict[dia]['entradas'] = total
            else:
                dias_dict[dia]['salidas'] = total

            dias_dict[dia]['num_movimientos'] += num_mov

        # Calcular actividad total y ordenar
        dias_actividad = []
        for dia, datos in dias_dict.items():
            actividad = datos['entradas'] + datos['salidas']
            dias_actividad.append({
                'fecha': dia,
                'entradas': datos['entradas'],
                'salidas': datos['salidas'],
                'total_actividad': actividad,
                'num_movimientos': datos['num_movimientos']
            })

        # Ordenar por actividad
        dias_actividad.sort(key=lambda x: x['total_actividad'], reverse=True)

        # Detectar día de la semana más activo
        dias_semana = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
                       4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
        actividad_semanal = {i: 0 for i in range(7)}

        for dia_data in dias_actividad:
            fecha = datetime.strptime(dia_data['fecha'], "%Y-%m-%d")
            dia_semana = fecha.weekday()
            actividad_semanal[dia_semana] += dia_data['total_actividad']

        dia_mas_activo = max(actividad_semanal, key=actividad_semanal.get)

        return {
            'dias_top': dias_actividad[:10],  # Top 10 días
            'dia_semana_mas_activo': dias_semana[dia_mas_activo],
            'actividad_por_dia_semana': {dias_semana[k]: v for k, v in actividad_semanal.items()},
            'total_dias_analizados': len(dias_actividad)
        }

    def analizar_categoria(self, categoria, dias=30):
        """Analiza el rendimiento de una categoría específica"""
        fecha_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")

        query = '''
            SELECT
                p.id, p.nombre, p.stock_actual, p.stock_minimo,
                COALESCE(SUM(CASE WHEN m.tipo = 'SALIDA' THEN m.cantidad ELSE 0 END), 0) as total_vendido,
                COUNT(CASE WHEN m.tipo = 'SALIDA' THEN 1 END) as num_ventas
            FROM productos p
            LEFT JOIN movimientos m ON p.id = m.producto_id AND m.fecha >= ?
            WHERE p.activo = 1 AND p.categoria = ?
            GROUP BY p.id, p.nombre, p.stock_actual, p.stock_minimo
            ORDER BY total_vendido DESC
        '''

        productos = self.db.consultar(query, (fecha_inicio, categoria))

        if not productos:
            return None

        total_vendido = sum(p[4] for p in productos)
        promedio_diario = total_vendido / dias

        # Top 3 productos de la categoría
        top_productos = [
            {
                'id': p[0],
                'nombre': p[1],
                'vendido': p[4],
                'num_ventas': p[5],
                'promedio_diario': round(p[4] / dias, 2)
            }
            for p in productos[:3]
        ]

        # Productos con riesgo de agotarse
        productos_riesgo = [
            {'id': p[0], 'nombre': p[1], 'stock': p[2]}
            for p in productos if p[2] <= p[3]
        ]

        return {
            'categoria': categoria,
            'total_productos': len(productos),
            'total_vendido': total_vendido,
            'promedio_diario': round(promedio_diario, 2),
            'top_productos': top_productos,
            'productos_riesgo': productos_riesgo,
            'rendimiento': 'ALTO' if promedio_diario >= 10 else 'MEDIO' if promedio_diario >= 5 else 'BAJO'
        }

    # ==================== SUGERENCIAS DE PROMOCIONES ====================

    def sugerir_promociones(self):
        """
        Genera sugerencias inteligentes de promociones basadas en:
        - Productos próximos a vencer
        - Productos con baja rotación
        - Productos con exceso de stock
        """
        sugerencias = []

        # 1. Productos próximos a vencer (urgente)
        proximos_vencer = self.producto_model.obtener_productos_proximos_vencer(15)
        for producto in proximos_vencer:
            dias_venc = self.producto_model.calcular_dias_hasta_vencimiento(producto)
            if dias_venc and dias_venc <= 15:
                urgencia = 'URGENTE' if dias_venc <= 7 else 'ALTA'
                descuento = '50%' if dias_venc <= 7 else '30%'

                sugerencias.append({
                    'tipo': 'VENCIMIENTO',
                    'urgencia': urgencia,
                    'producto_id': producto[0],
                    'producto_nombre': producto[2],
                    'razon': f'Vence en {dias_venc} días',
                    'accion': f'Promoción {descuento} de descuento',
                    'dias_restantes': dias_venc,
                    'stock': producto[7],
                    'descuento_sugerido': descuento
                })

        # 2. Productos con baja rotación (últimos 30 días)
        query = '''
            SELECT
                p.id, p.nombre, p.stock_actual, p.categoria,
                COALESCE(SUM(CASE WHEN m.tipo = 'SALIDA' THEN m.cantidad ELSE 0 END), 0) as total_vendido
            FROM productos p
            LEFT JOIN movimientos m ON p.id = m.producto_id
                AND m.fecha >= date('now', '-30 days')
            WHERE p.activo = 1
            GROUP BY p.id, p.nombre, p.stock_actual, p.categoria
            HAVING total_vendido < 5 AND p.stock_actual > 10
            ORDER BY p.stock_actual DESC
            LIMIT 10
        '''

        productos_baja_rotacion = self.db.consultar(query)
        for producto in productos_baja_rotacion:
            pid, nombre, stock, categoria, vendido = producto

            sugerencias.append({
                'tipo': 'BAJA_ROTACION',
                'urgencia': 'MEDIA',
                'producto_id': pid,
                'producto_nombre': nombre,
                'razon': f'Solo {vendido} vendidos en 30 días, stock: {stock}',
                'accion': '2x1 o descuento del 25%',
                'stock': stock,
                'categoria': categoria,
                'descuento_sugerido': '25%'
            })

        # 3. Productos con exceso de stock
        query = '''
            SELECT id, nombre, stock_actual, stock_maximo, categoria
            FROM productos
            WHERE activo = 1 AND stock_actual > stock_maximo
            ORDER BY (stock_actual - stock_maximo) DESC
            LIMIT 5
        '''

        productos_exceso = self.db.consultar(query)
        for producto in productos_exceso:
            pid, nombre, stock, max_stock, categoria = producto
            exceso = stock - max_stock

            sugerencias.append({
                'tipo': 'EXCESO_STOCK',
                'urgencia': 'MEDIA',
                'producto_id': pid,
                'producto_nombre': nombre,
                'razon': f'Exceso de {exceso} unidades sobre el máximo',
                'accion': f'Combo o descuento del 20%',
                'stock': stock,
                'exceso': exceso,
                'categoria': categoria,
                'descuento_sugerido': '20%'
            })

        # Ordenar por urgencia
        orden_urgencia = {'URGENTE': 0, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}
        sugerencias.sort(key=lambda x: (orden_urgencia.get(x['urgencia'], 4), -x['stock']))

        return sugerencias

    # ==================== ANÁLISIS PREDICTIVO ====================

    def predecir_demanda(self, producto_id, dias_futuro=7):
        """
        Predice la demanda futura basándose en histórico
        Usa promedio móvil simple
        """
        # Obtener ventas de los últimos 30 días
        analisis = self.producto_model.obtener_analisis_rotacion(producto_id, 30)
        if not analisis:
            return None

        promedio_diario = analisis['promedio_diario']

        # Calcular demanda predicha
        demanda_predicha = promedio_diario * dias_futuro

        producto = self.producto_model.obtener_por_id(producto_id)
        if not producto:
            return None

        stock_actual = producto[7]
        stock_minimo = producto[8]

        # Determinar si habrá desabastecimiento
        stock_futuro = stock_actual - demanda_predicha
        desabastecimiento = stock_futuro < stock_minimo

        return {
            'producto_id': producto_id,
            'producto_nombre': producto[2],
            'promedio_diario': round(promedio_diario, 2),
            'demanda_predicha': round(demanda_predicha, 1),
            'stock_actual': stock_actual,
            'stock_futuro_estimado': round(stock_futuro, 1),
            'dias_hasta_agotarse': analisis['dias_restantes'],
            'requiere_reabastecimiento': desabastecimiento,
            'cantidad_sugerida': max(0, stock_minimo - stock_futuro) if desabastecimiento else 0
        }

    def analizar_tendencias_categoria(self):
        """Analiza tendencias de todas las categorías"""
        query = '''
            SELECT
                p.categoria,
                COUNT(DISTINCT p.id) as num_productos,
                SUM(p.stock_actual) as stock_total,
                COALESCE(SUM(CASE WHEN m.tipo = 'SALIDA' THEN m.cantidad ELSE 0 END), 0) as total_vendido,
                COALESCE(SUM(CASE WHEN m.tipo = 'ENTRADA' THEN m.cantidad ELSE 0 END), 0) as total_entradas
            FROM productos p
            LEFT JOIN movimientos m ON p.id = m.producto_id
                AND m.fecha >= date('now', '-30 days')
            WHERE p.activo = 1 AND p.categoria IS NOT NULL AND p.categoria != ''
            GROUP BY p.categoria
            ORDER BY total_vendido DESC
        '''

        resultados = self.db.consultar(query)

        categorias = []
        for row in resultados:
            categoria, num_prod, stock, vendido, entradas = row

            # Calcular métricas
            rotacion = vendido / 30 if vendido > 0 else 0

            categorias.append({
                'categoria': categoria,
                'num_productos': num_prod,
                'stock_total': stock,
                'vendido_30dias': vendido,
                'entradas_30dias': entradas,
                'rotacion_diaria': round(rotacion, 2),
                'rendimiento': 'ALTO' if rotacion >= 5 else 'MEDIO' if rotacion >= 2 else 'BAJO'
            })

        return categorias

    # ==================== ANÁLISIS COMPLETO PARA DASHBOARD ====================

    def generar_reporte_completo(self):
        """
        Genera un reporte completo con todas las métricas y sugerencias
        Ideal para enviar a n8n
        """
        return {
            'fecha_generacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'movimientos_diarios': self.analizar_movimientos_diarios(30),
            'sugerencias_promociones': self.sugerir_promociones(),
            'tendencias_categorias': self.analizar_tendencias_categoria(),
            'productos_proximos_vencer': len(self.producto_model.obtener_productos_proximos_vencer(7)),
            'productos_vencidos': len(self.producto_model.obtener_productos_vencidos()),
            'productos_stock_bajo': len(self.producto_model.obtener_productos_stock_bajo())
        }

    def generar_alertas_automaticas(self):
        """
        Genera alertas que deben enviarse automáticamente
        Para procesamiento por n8n
        """
        alertas = []

        # Alerta 1: Productos próximos a vencer (7 días)
        proximos_vencer = self.producto_model.obtener_productos_proximos_vencer(7)
        if proximos_vencer:
            alertas.append({
                'tipo': 'VENCIMIENTO_URGENTE',
                'prioridad': 'ALTA',
                'titulo': f'{len(proximos_vencer)} productos vencen en menos de 7 días',
                'productos': [
                    {
                        'id': p[0],
                        'nombre': p[2],
                        'fecha_vencimiento': p[14] if len(p) > 14 else None,
                        'dias_restantes': self.producto_model.calcular_dias_hasta_vencimiento(p),
                        'stock': p[7]
                    }
                    for p in proximos_vencer
                ],
                'accion_recomendada': 'Crear promociones urgentes'
            })

        # Alerta 2: Día de alta actividad (comparado con promedio)
        mov_diarios = self.analizar_movimientos_diarios(7)
        if mov_diarios['dias_top']:
            actividad_hoy = mov_diarios['dias_top'][0]['total_actividad']
            promedio = sum(d['total_actividad'] for d in mov_diarios['dias_top']) / len(mov_diarios['dias_top'])

            if actividad_hoy > promedio * 1.5:
                alertas.append({
                    'tipo': 'ALTA_ACTIVIDAD',
                    'prioridad': 'INFO',
                    'titulo': 'Actividad inusualmente alta detectada',
                    'detalles': {
                        'actividad_hoy': actividad_hoy,
                        'promedio': round(promedio, 2),
                        'incremento': f'{round((actividad_hoy / promedio - 1) * 100, 1)}%'
                    },
                    'accion_recomendada': 'Revisar stock de productos populares'
                })

        # Alerta 3: Categoría con bajo rendimiento
        tendencias = self.analizar_tendencias_categoria()
        categorias_bajo = [c for c in tendencias if c['rendimiento'] == 'BAJO']
        if categorias_bajo:
            alertas.append({
                'tipo': 'CATEGORIA_BAJO_RENDIMIENTO',
                'prioridad': 'MEDIA',
                'titulo': f'{len(categorias_bajo)} categorías con bajo rendimiento',
                'categorias': categorias_bajo,
                'accion_recomendada': 'Considerar promociones o reducir stock'
            })

        return alertas

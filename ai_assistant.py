"""
Asistente de reabastecimiento.

Cómo decide (siempre, con o sin IA externa):
  1. Ventas por día = unidades vendidas en los últimos 30 días / 30
  2. Días para agotarse = stock actual / ventas por día
  3. Cantidad sugerida = llenar hasta ~85% del stock máximo, ajustada por
     rotación y urgencia, y siempre dentro de [lo necesario para llegar al
     mínimo, lo que cabe hasta el máximo].

Si hay una IA configurada en .env (ver ai_provider.py), además redacta un
análisis más natural, el mensaje al proveedor, y puede ajustar la cantidad
dentro de esos mismos límites. Si la IA falla, se usa el resultado local.
"""

import json
from datetime import datetime, timedelta

from ai_provider import ErrorIA, obtener_proveedor_ia
from database import Database

DIAS_HISTORIAL = 30

SISTEMA_IA = (
    "Eres el asistente de compras de un negocio pequeño (minimarket, bodega, "
    "tienda). Hablas español claro y breve, sin tecnicismos. Responde SOLO con "
    "un objeto JSON válido, sin texto adicional."
)


class AIAssistant:
    """Analiza un producto y sugiere cuánto pedir y a quién."""

    def __init__(self, db=None, ia=None, usar_ia=True):
        self.db = db or Database()
        if not usar_ia:
            self.ia = None
        else:
            self.ia = ia if ia is not None else obtener_proveedor_ia()

    def analizar_producto(self, producto_id):
        """
        Análisis completo de un producto para tomar decisiones inteligentes
        Retorna un diccionario con toda la información y sugerencias
        """
        producto = self.db.consultar_uno("SELECT * FROM productos WHERE id=?", (producto_id,))
        if not producto:
            return None

        # Obtener proveedor
        proveedor = None
        if producto[10]:  # proveedor_id
            proveedor = self.db.consultar_uno("SELECT * FROM proveedores WHERE id=?", (producto[10],))

        # Analizar historial de movimientos (últimos 30 días)
        movimientos = self._obtener_movimientos_recientes(producto_id, dias=30)

        # Calcular métricas
        ventas_diarias = self._calcular_ventas_diarias(movimientos)
        dias_para_agotar = self._calcular_dias_para_agotar(producto[7], ventas_diarias)
        cantidad_sugerida = self._calcular_cantidad_sugerida(producto, ventas_diarias, proveedor)
        urgencia = self._calcular_urgencia(dias_para_agotar, producto[7], producto[8])
        mensaje_proveedor = self._generar_mensaje_proveedor(producto, proveedor, cantidad_sugerida)

        resultado = {
            'producto': {
                'id': producto[0],
                'codigo': producto[1],
                'nombre': producto[2],
                'descripcion': producto[3],
                'categoria': producto[4],
                'precio_compra': producto[5],
                'precio_venta': producto[6],
                'stock_actual': producto[7],
                'stock_minimo': producto[8],
                'stock_maximo': producto[9],
            },
            'proveedor': {
                'id': proveedor[0] if proveedor else None,
                'nombre': proveedor[1] if proveedor else 'Sin proveedor',
                'contacto': proveedor[2] if proveedor else '',
                'telefono': proveedor[3] if proveedor else '',
                'email': proveedor[4] if proveedor else '',
                'direccion': proveedor[5] if proveedor else '',
            } if proveedor else None,
            'analisis': {
                'ventas_diarias_promedio': ventas_diarias,
                'dias_para_agotar': dias_para_agotar,
                'total_movimientos_30d': len(movimientos),
                'salidas_30d': len([m for m in movimientos if m[2] == 'SALIDA']),
                'entradas_30d': len([m for m in movimientos if m[2] == 'ENTRADA']),
            },
            'sugerencia': {
                'cantidad': cantidad_sugerida,
                'urgencia': urgencia,  # 'CRÍTICA', 'ALTA', 'MEDIA', 'BAJA'
                'razonamiento': self._generar_razonamiento(producto, ventas_diarias, dias_para_agotar, cantidad_sugerida),
                'costo_estimado': producto[5] * cantidad_sugerida if producto[5] else 0,
            },
            'mensaje_proveedor': mensaje_proveedor,
            'motor': 'local',
        }
        return self._mejorar_con_ia(resultado, producto)

    # ---------- IA externa opcional ----------
    def _limites_cantidad(self, producto):
        stock_actual, stock_minimo, stock_maximo = producto[7], producto[8], producto[9]
        tope = max(stock_maximo - stock_actual, 0)
        piso = min(max(stock_minimo - stock_actual, 0), tope)
        return piso, tope

    def _mejorar_con_ia(self, resultado, producto):
        """Pide a la IA configurada un análisis mejor. Ante cualquier fallo, devuelve el local."""
        if not self.ia or not self.ia.activo:
            return resultado
        piso, tope = self._limites_cantidad(producto)
        datos = {
            "producto": resultado["producto"],
            "proveedor": (resultado["proveedor"] or {}).get("nombre"),
            "analisis": resultado["analisis"],
            "sugerencia_local": resultado["sugerencia"]["cantidad"],
            "urgencia": resultado["sugerencia"]["urgencia"],
            "cantidad_minima_permitida": piso,
            "cantidad_maxima_permitida": tope,
        }
        prompt = (
            "Datos del producto (JSON):\n" + json.dumps(datos, ensure_ascii=False, default=str) +
            "\n\nDevuelve este JSON:\n"
            '{"cantidad": entero entre cantidad_minima_permitida y cantidad_maxima_permitida, '
            '"razonamiento": "2 o 3 frases explicando la decisión al dueño", '
            '"mensaje_proveedor": "mensaje corto y cordial para pedir el producto por WhatsApp"}'
        )
        try:
            respuesta = self.ia.completar_json(prompt, SISTEMA_IA)
            cantidad = int(respuesta.get("cantidad", resultado["sugerencia"]["cantidad"]))
        except (ErrorIA, TypeError, ValueError):
            return resultado

        cantidad = max(piso, min(cantidad, tope))  # la IA no puede salirse de los límites
        sugerencia = resultado["sugerencia"]
        sugerencia["cantidad"] = cantidad
        sugerencia["costo_estimado"] = (producto[5] or 0) * cantidad
        if isinstance(respuesta.get("razonamiento"), str) and respuesta["razonamiento"].strip():
            sugerencia["razonamiento"] = respuesta["razonamiento"].strip()
        if resultado["proveedor"] and isinstance(respuesta.get("mensaje_proveedor"), str) \
                and respuesta["mensaje_proveedor"].strip():
            resultado["mensaje_proveedor"] = respuesta["mensaje_proveedor"].strip()
        resultado["motor"] = self.ia.descripcion
        return resultado

    def _obtener_movimientos_recientes(self, producto_id, dias=30):
        """Obtiene los movimientos de los últimos N días"""
        fecha_desde = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
        # producto_id y fecha van como parámetros (?), nunca concatenados
        query = """
            SELECT * FROM movimientos
            WHERE producto_id=? AND fecha >= ?
            ORDER BY fecha DESC
        """
        return self.db.consultar(query, (producto_id, fecha_desde))

    def _calcular_ventas_diarias(self, movimientos, dias=DIAS_HISTORIAL):
        """Promedio de unidades vendidas por día en la ventana analizada.

        Se divide entre todos los días de la ventana (no solo los días con
        movimientos); si no, un producto que se vende 1 vez al mes parecería
        venderse todos los días.
        """
        salidas = [m[3] for m in movimientos if m[2] == 'SALIDA']
        if not salidas:
            return 0.0
        return sum(salidas) / dias

    def _calcular_dias_para_agotar(self, stock_actual, ventas_diarias):
        """Calcula en cuántos días se agotará el stock actual"""
        if ventas_diarias <= 0:
            return 999  # Sin ventas recientes: no se agota pronto

        return stock_actual / ventas_diarias

    def _calcular_cantidad_sugerida(self, producto, ventas_diarias, proveedor):
        """
        Calcula la cantidad óptima a pedir basándose en múltiples factores
        Esta es la MAGIA del sistema
        """
        stock_actual = producto[7]
        stock_minimo = producto[8]
        stock_maximo = producto[9]

        # Estrategia base: llenar hasta el 85% del máximo
        cantidad_base = int((stock_maximo * 0.85) - stock_actual)

        # Ajustar por velocidad de ventas
        if ventas_diarias > 5:  # Producto de alta rotación
            cantidad_base = int(cantidad_base * 1.2)  # Pedir 20% más
        elif ventas_diarias > 2:  # Rotación media
            cantidad_base = int(cantidad_base * 1.0)  # Mantener
        else:  # Baja rotación
            cantidad_base = int(cantidad_base * 0.7)  # Pedir 30% menos

        # Ajustar por urgencia
        if stock_actual == 0:  # Stock agotado
            cantidad_base = int(cantidad_base * 1.3)  # Pedir 30% más
        elif stock_actual <= stock_minimo * 0.5:  # Muy bajo
            cantidad_base = int(cantidad_base * 1.15)  # Pedir 15% más

        # Nunca menos de lo necesario para llegar al mínimo,
        # nunca más de lo que cabe hasta el máximo.
        piso, tope = self._limites_cantidad(producto)
        return max(piso, min(cantidad_base, tope))

    def _calcular_urgencia(self, dias_para_agotar, stock_actual, stock_minimo):
        """Determina el nivel de urgencia del pedido"""
        if stock_actual == 0:
            return 'CRÍTICA'
        elif dias_para_agotar <= 2 or stock_actual <= stock_minimo * 0.3:
            return 'CRÍTICA'
        elif dias_para_agotar <= 5 or stock_actual <= stock_minimo * 0.5:
            return 'ALTA'
        elif dias_para_agotar <= 10 or stock_actual <= stock_minimo:
            return 'MEDIA'
        else:
            return 'BAJA'

    def _generar_razonamiento(self, producto, ventas_diarias, dias_para_agotar, cantidad_sugerida):
        """Genera una explicación del razonamiento de la IA"""
        razonamientos = []

        # Análisis de stock actual
        stock_actual = producto[7]
        stock_minimo = producto[8]

        if stock_actual == 0:
            razonamientos.append("El producto está AGOTADO. Se sugiere pedido urgente.")
        elif stock_actual <= stock_minimo * 0.5:
            razonamientos.append(f"Stock crítico: {stock_actual} unidades (muy por debajo del mínimo {stock_minimo}).")
        elif stock_actual <= stock_minimo:
            razonamientos.append(f"Stock bajo: {stock_actual} unidades (mínimo: {stock_minimo}).")

        if ventas_diarias == 0:
            razonamientos.append("Sin ventas en los últimos 30 días: pedido mínimo para cubrir el stock mínimo.")
            razonamientos.append(f"Cantidad sugerida: {cantidad_sugerida} unidades.")
            return " ".join(razonamientos)

        # Análisis de ventas
        if ventas_diarias > 5:
            razonamientos.append(f"Alta rotación: ~{ventas_diarias:.1f} unidades/día. Se recomienda stock adicional.")
        elif ventas_diarias > 2:
            razonamientos.append(f"Rotación media: ~{ventas_diarias:.1f} unidades/día.")
        else:
            razonamientos.append(f"Baja rotación: ~{ventas_diarias:.1f} unidades/día. Pedido conservador.")

        # Análisis de tiempo
        if dias_para_agotar <= 3:
            razonamientos.append(f"El stock se agotará en ~{dias_para_agotar:.1f} días si continúa la tendencia.")
        elif dias_para_agotar <= 7:
            razonamientos.append(f"Tiempo estimado de agotamiento: ~{dias_para_agotar:.1f} días.")

        # Recomendación final
        razonamientos.append(f"Cantidad óptima sugerida: {cantidad_sugerida} unidades.")

        return " ".join(razonamientos)

    def _generar_mensaje_proveedor(self, producto, proveedor, cantidad):
        """Genera un mensaje profesional para enviar al proveedor"""
        if not proveedor:
            return "No hay proveedor asignado para generar mensaje."

        fecha = datetime.now().strftime("%d de %B de %Y")

        mensaje = f"""Estimado/a {proveedor[2] or proveedor[1]},

Espero que se encuentre bien. Me comunico con usted desde el sistema de inventario para solicitar una cotización y confirmar disponibilidad del siguiente producto:

Producto solicitado:
- Nombre: {producto[2]}
- Código: {producto[1]}
- Categoría: {producto[4]}
- Cantidad: {cantidad} unidades

Información adicional:
- Stock actual: {producto[7]} unidades
- Precio de compra anterior: ${producto[5]:.2f}/unidad

Por favor, confirme:
- Disponibilidad del producto
- Precio actualizado
- Tiempo estimado de entrega
- Condiciones de pago

Agradecería una pronta respuesta debido a nuestro nivel actual de inventario.

Saludos cordiales,
Sistema Automático de Inventario
Fecha: {fecha}
"""
        return mensaje

    def sugerir_productos_criticos(self, limite=10):
        """
        Retorna los productos más críticos que necesitan atención
        Ordenados por urgencia
        """
        query = """
            SELECT id, codigo, nombre, stock_actual, stock_minimo
            FROM productos
            WHERE activo=1 AND stock_actual <= stock_minimo
            ORDER BY (stock_actual * 1.0 / NULLIF(stock_minimo, 1)) ASC
            LIMIT ?
        """
        productos_criticos = self.db.consultar(query, (limite,))

        analisis_completo = []
        for prod in productos_criticos:
            analisis = self.analizar_producto(prod[0])
            if analisis:
                analisis_completo.append(analisis)

        # Ordenar por urgencia
        orden_urgencia = {'CRÍTICA': 0, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}
        analisis_completo.sort(key=lambda x: orden_urgencia.get(x['sugerencia']['urgencia'], 4))

        return analisis_completo

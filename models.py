from datetime import datetime
from database import Database

class Producto:
    def __init__(self):
        self.db = Database()

    def crear(self, codigo, nombre, descripcion, categoria, precio_compra, precio_venta,
              stock_actual, stock_minimo, stock_maximo, proveedor_id, fecha_ingreso=None,
              fecha_vencimiento=None, dias_vida_util=0):
        """Crea un nuevo producto"""
        query = '''
            INSERT INTO productos (codigo, nombre, descripcion, categoria, precio_compra,
                                   precio_venta, stock_actual, stock_minimo, stock_maximo,
                                   proveedor_id, fecha_registro, fecha_ingreso,
                                   fecha_vencimiento, dias_vida_util)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Si no se proporciona fecha_ingreso, usar la fecha actual
        if not fecha_ingreso:
            fecha_ingreso = datetime.now().strftime("%Y-%m-%d")
        return self.db.ejecutar(query, (codigo, nombre, descripcion, categoria, precio_compra,
                                        precio_venta, stock_actual, stock_minimo, stock_maximo,
                                        proveedor_id, fecha, fecha_ingreso, fecha_vencimiento,
                                        dias_vida_util))

    def actualizar(self, id, codigo, nombre, descripcion, categoria, precio_compra, precio_venta,
                   stock_actual, stock_minimo, stock_maximo, proveedor_id, fecha_ingreso=None,
                   fecha_vencimiento=None, dias_vida_util=0):
        """Actualiza un producto existente"""
        query = '''
            UPDATE productos
            SET codigo=?, nombre=?, descripcion=?, categoria=?, precio_compra=?,
                precio_venta=?, stock_actual=?, stock_minimo=?, stock_maximo=?, proveedor_id=?,
                fecha_ingreso=?, fecha_vencimiento=?, dias_vida_util=?
            WHERE id=?
        '''
        self.db.ejecutar(query, (codigo, nombre, descripcion, categoria, precio_compra,
                                 precio_venta, stock_actual, stock_minimo, stock_maximo,
                                 proveedor_id, fecha_ingreso, fecha_vencimiento, dias_vida_util,
                                 id))

    def eliminar(self, id):
        """Marca un producto como inactivo"""
        query = "UPDATE productos SET activo=0 WHERE id=?"
        self.db.ejecutar(query, (id,))

    def obtener_todos(self, incluir_inactivos=False):
        """Obtiene todos los productos"""
        if incluir_inactivos:
            query = "SELECT * FROM productos ORDER BY nombre"
        else:
            query = "SELECT * FROM productos WHERE activo=1 ORDER BY nombre"
        return self.db.consultar(query)

    def obtener_por_id(self, id):
        """Obtiene un producto por su ID"""
        query = "SELECT * FROM productos WHERE id=?"
        return self.db.consultar_uno(query, (id,))

    def buscar(self, termino):
        """Busca productos por código o nombre"""
        query = '''
            SELECT * FROM productos
            WHERE activo=1 AND (codigo LIKE ? OR nombre LIKE ?)
            ORDER BY nombre
        '''
        termino_busqueda = f"%{termino}%"
        return self.db.consultar(query, (termino_busqueda, termino_busqueda))

    def actualizar_stock(self, id, cantidad, tipo, motivo, usuario="Sistema"):
        """Actualiza el stock de un producto y registra el movimiento"""
        # Obtener stock actual
        producto = self.obtener_por_id(id)
        if not producto:
            return False

        stock_actual = producto[7]  # stock_actual está en la posición 7

        # Calcular nuevo stock
        if tipo == "ENTRADA":
            nuevo_stock = stock_actual + cantidad
        else:  # SALIDA
            nuevo_stock = stock_actual - cantidad
            if nuevo_stock < 0:
                return False

        # Actualizar stock
        query = "UPDATE productos SET stock_actual=? WHERE id=?"
        self.db.ejecutar(query, (nuevo_stock, id))

        # Registrar movimiento
        Movimiento().crear(id, tipo, cantidad, motivo, usuario)

        # Verificar si hay que crear alerta
        self._verificar_alertas(id, nuevo_stock)

        return True

    def _verificar_alertas(self, producto_id, stock_actual):
        """Verifica si el stock está bajo el mínimo y crea alertas + pedido automático + notifica"""
        producto = self.obtener_por_id(producto_id)
        if not producto:
            return

        stock_minimo = producto[8]  # stock_minimo está en la posición 8
        stock_maximo = producto[9]  # stock_maximo está en la posición 9
        proveedor_id = producto[10]  # proveedor_id está en la posición 10

        if stock_actual <= stock_minimo:
            # Crear alerta
            Alerta().crear(producto_id, "STOCK_BAJO",
                          f"El producto '{producto[2]}' tiene stock bajo: {stock_actual} unidades")

            # Obtener información del proveedor
            proveedor = None
            if proveedor_id:
                proveedor = Proveedor().obtener_por_id(proveedor_id)

            # Enviar webhook a n8n con análisis de rotación
            try:
                from webhook_client import WebhookClient
                webhook = WebhookClient()

                # Obtener análisis de rotación para enviar más información
                analisis_rotacion = self.obtener_analisis_rotacion(producto_id, 30)

                # Usar el nuevo método mejorado
                if stock_actual == 0:
                    webhook.evento_stock_critico(producto, proveedor)
                else:
                    webhook.evento_stock_bajo(producto, proveedor, analisis_rotacion)

                # Notificar al dueño
                if stock_actual == 0:
                    tipo_notif = 'critico'
                    mensaje = f"🚨 CRÍTICO: {producto[2]} está AGOTADO"
                elif stock_actual <= stock_minimo * 0.5:
                    tipo_notif = 'advertencia'
                    mensaje = f"⚠️ URGENTE: {producto[2]} tiene stock muy bajo ({stock_actual} unidades)"
                else:
                    tipo_notif = 'info'
                    mensaje = f"📊 Stock bajo: {producto[2]} ({stock_actual} unidades)"

                webhook.notificar_dueno(tipo_notif, mensaje, {
                    'producto': producto[2],
                    'stock_actual': stock_actual,
                    'stock_minimo': stock_minimo,
                    'proveedor': proveedor[1] if proveedor else 'Sin proveedor',
                    'analisis_rotacion': analisis_rotacion
                })
            except Exception as e:
                print(f"[ERROR] Webhook: {e}")

            # Crear pedido automático al proveedor si tiene uno asignado
            if proveedor_id:
                # Calcular cantidad a pedir (llenar hasta el 80% del stock máximo)
                cantidad_a_pedir = int((stock_maximo * 0.8) - stock_actual)

                if cantidad_a_pedir > 0:
                    # Verificar si ya existe un pedido pendiente para este producto
                    pedido_existente = PedidoAutomatico().db.consultar_uno(
                        "SELECT id FROM pedidos_automaticos WHERE producto_id=? AND estado='PENDIENTE'",
                        (producto_id,)
                    )

                    if not pedido_existente:
                        # Crear pedido automático
                        pedido_id = PedidoAutomatico().crear(
                            producto_id,
                            proveedor_id,
                            cantidad_a_pedir,
                            f"Pedido automático generado por stock bajo ({stock_actual} unidades)"
                        )

                        # Notificar creación de pedido con el nuevo método
                        try:
                            from webhook_client import WebhookClient
                            webhook = WebhookClient()
                            webhook.evento_pedido_creado({
                                'pedido_id': pedido_id,
                                'producto_id': producto_id,
                                'producto_codigo': producto[1],
                                'producto_nombre': producto[2],
                                'categoria': producto[4],
                                'proveedor_id': proveedor_id,
                                'proveedor_nombre': proveedor[1] if proveedor else 'Desconocido',
                                'cantidad_solicitada': cantidad_a_pedir,
                                'stock_actual': stock_actual,
                                'stock_minimo': stock_minimo,
                                'motivo': 'Stock bajo'
                            })
                        except Exception as e:
                            print(f"[ERROR] Webhook pedido: {e}")

    def obtener_productos_stock_bajo(self):
        """Obtiene productos con stock por debajo del mínimo"""
        query = '''
            SELECT * FROM productos
            WHERE activo=1 AND stock_actual <= stock_minimo
            ORDER BY stock_actual ASC
        '''
        return self.db.consultar(query)

    def obtener_productos_proximos_vencer(self, dias_alerta=7):
        """Obtiene productos que vencen en los próximos N días"""
        from datetime import datetime, timedelta
        fecha_limite = (datetime.now() + timedelta(days=dias_alerta)).strftime("%Y-%m-%d")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        query = '''
            SELECT * FROM productos
            WHERE activo=1
              AND fecha_vencimiento IS NOT NULL
              AND fecha_vencimiento != ''
              AND fecha_vencimiento >= ?
              AND fecha_vencimiento <= ?
            ORDER BY fecha_vencimiento ASC
        '''
        return self.db.consultar(query, (fecha_hoy, fecha_limite))

    def obtener_productos_vencidos(self):
        """Obtiene productos ya vencidos"""
        from datetime import datetime
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        query = '''
            SELECT * FROM productos
            WHERE activo=1
              AND fecha_vencimiento IS NOT NULL
              AND fecha_vencimiento != ''
              AND fecha_vencimiento < ?
            ORDER BY fecha_vencimiento ASC
        '''
        return self.db.consultar(query, (fecha_hoy,))

    def calcular_dias_en_stock(self, producto):
        """Calcula cuántos días lleva un producto en stock"""
        from datetime import datetime
        if not producto or len(producto) < 14 or not producto[13]:  # fecha_ingreso
            return 0

        try:
            fecha_ingreso = datetime.strptime(producto[13], "%Y-%m-%d")
            dias = (datetime.now() - fecha_ingreso).days
            return max(0, dias)
        except:
            return 0

    def calcular_dias_hasta_vencimiento(self, producto):
        """Calcula cuántos días faltan para que venza un producto"""
        from datetime import datetime
        if not producto or len(producto) < 15 or not producto[14]:  # fecha_vencimiento
            return None

        try:
            fecha_venc = datetime.strptime(producto[14], "%Y-%m-%d")
            dias = (fecha_venc - datetime.now()).days
            return dias
        except:
            return None

    def obtener_analisis_rotacion(self, producto_id, dias=30):
        """Obtiene análisis de rotación de un producto en los últimos N días"""
        from datetime import datetime, timedelta

        # Obtener movimientos de salida del producto en los últimos N días
        fecha_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")

        query = '''
            SELECT SUM(cantidad) as total_vendido
            FROM movimientos
            WHERE producto_id = ?
              AND tipo = 'SALIDA'
              AND fecha >= ?
        '''
        resultado = self.db.consultar_uno(query, (producto_id, fecha_inicio))
        total_vendido = resultado[0] if resultado and resultado[0] else 0

        # Calcular promedio diario
        promedio_diario = total_vendido / dias if dias > 0 else 0

        # Obtener producto actual
        producto = self.obtener_por_id(producto_id)
        if not producto:
            return None

        stock_actual = producto[7]

        # Calcular días restantes
        dias_restantes = stock_actual / promedio_diario if promedio_diario > 0 else 999

        return {
            'total_vendido': total_vendido,
            'promedio_diario': round(promedio_diario, 2),
            'dias_restantes': round(dias_restantes, 1),
            'stock_actual': stock_actual
        }


class Proveedor:
    def __init__(self):
        self.db = Database()

    def crear(self, nombre, contacto, telefono, email, direccion):
        """Crea un nuevo proveedor"""
        query = '''
            INSERT INTO proveedores (nombre, contacto, telefono, email, direccion, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.db.ejecutar(query, (nombre, contacto, telefono, email, direccion, fecha))

    def actualizar(self, id, nombre, contacto, telefono, email, direccion):
        """Actualiza un proveedor existente"""
        query = '''
            UPDATE proveedores
            SET nombre=?, contacto=?, telefono=?, email=?, direccion=?
            WHERE id=?
        '''
        self.db.ejecutar(query, (nombre, contacto, telefono, email, direccion, id))

    def eliminar(self, id):
        """Marca un proveedor como inactivo"""
        query = "UPDATE proveedores SET activo=0 WHERE id=?"
        self.db.ejecutar(query, (id,))

    def obtener_todos(self, incluir_inactivos=False):
        """Obtiene todos los proveedores"""
        if incluir_inactivos:
            query = "SELECT * FROM proveedores ORDER BY nombre"
        else:
            query = "SELECT * FROM proveedores WHERE activo=1 ORDER BY nombre"
        return self.db.consultar(query)

    def obtener_por_id(self, id):
        """Obtiene un proveedor por su ID"""
        query = "SELECT * FROM proveedores WHERE id=?"
        return self.db.consultar_uno(query, (id,))


class Movimiento:
    def __init__(self):
        self.db = Database()

    def crear(self, producto_id, tipo, cantidad, motivo, usuario):
        """Registra un movimiento de inventario"""
        query = '''
            INSERT INTO movimientos (producto_id, tipo, cantidad, motivo, usuario, fecha)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.db.ejecutar(query, (producto_id, tipo, cantidad, motivo, usuario, fecha))

    def obtener_por_producto(self, producto_id, limite=50):
        """Obtiene los movimientos de un producto"""
        query = '''
            SELECT * FROM movimientos
            WHERE producto_id=?
            ORDER BY fecha DESC
            LIMIT ?
        '''
        return self.db.consultar(query, (producto_id, limite))

    def obtener_todos(self, limite=100):
        """Obtiene todos los movimientos recientes"""
        query = "SELECT * FROM movimientos ORDER BY fecha DESC LIMIT ?"
        return self.db.consultar(query, (limite,))


class Alerta:
    def __init__(self):
        self.db = Database()

    def crear(self, producto_id, tipo_alerta, mensaje):
        """Crea una nueva alerta"""
        # Verificar si ya existe una alerta no leída para este producto
        query_verificar = '''
            SELECT id FROM alertas
            WHERE producto_id=? AND tipo_alerta=? AND leida=0
        '''
        existe = self.db.consultar_uno(query_verificar, (producto_id, tipo_alerta))

        if not existe:
            query = '''
                INSERT INTO alertas (producto_id, tipo_alerta, mensaje, fecha)
                VALUES (?, ?, ?, ?)
            '''
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return self.db.ejecutar(query, (producto_id, tipo_alerta, mensaje, fecha))

    def marcar_leida(self, id):
        """Marca una alerta como leída"""
        query = "UPDATE alertas SET leida=1 WHERE id=?"
        self.db.ejecutar(query, (id,))

    def obtener_no_leidas(self):
        """Obtiene todas las alertas no leídas"""
        query = '''
            SELECT a.*, p.nombre as producto_nombre
            FROM alertas a
            JOIN productos p ON a.producto_id = p.id
            WHERE a.leida=0
            ORDER BY a.fecha DESC
        '''
        return self.db.consultar(query)

    def obtener_todas(self, limite=50):
        """Obtiene todas las alertas recientes"""
        query = '''
            SELECT a.*, p.nombre as producto_nombre
            FROM alertas a
            JOIN productos p ON a.producto_id = p.id
            ORDER BY a.fecha DESC
            LIMIT ?
        '''
        return self.db.consultar(query, (limite,))

    def contar_no_leidas(self):
        """Cuenta las alertas no leídas"""
        query = "SELECT COUNT(*) FROM alertas WHERE leida=0"
        resultado = self.db.consultar_uno(query)
        return resultado[0] if resultado else 0


class PedidoAutomatico:
    def __init__(self):
        self.db = Database()

    def crear(self, producto_id, proveedor_id, cantidad_solicitada, notas=""):
        """Crea un nuevo pedido automático"""
        query = '''
            INSERT INTO pedidos_automaticos
            (producto_id, proveedor_id, cantidad_solicitada, fecha_pedido, notas, estado)
            VALUES (?, ?, ?, ?, ?, 'PENDIENTE')
        '''
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.db.ejecutar(query, (producto_id, proveedor_id, cantidad_solicitada, fecha, notas))

    def obtener_todos(self, solo_pendientes=False):
        """Obtiene todos los pedidos automáticos"""
        if solo_pendientes:
            query = '''
                SELECT p.*, prod.nombre as producto_nombre, prod.codigo as producto_codigo,
                       prov.nombre as proveedor_nombre
                FROM pedidos_automaticos p
                JOIN productos prod ON p.producto_id = prod.id
                JOIN proveedores prov ON p.proveedor_id = prov.id
                WHERE p.estado = 'PENDIENTE'
                ORDER BY p.fecha_pedido DESC
            '''
        else:
            query = '''
                SELECT p.*, prod.nombre as producto_nombre, prod.codigo as producto_codigo,
                       prov.nombre as proveedor_nombre
                FROM pedidos_automaticos p
                JOIN productos prod ON p.producto_id = prod.id
                JOIN proveedores prov ON p.proveedor_id = prov.id
                ORDER BY p.fecha_pedido DESC
            '''
        return self.db.consultar(query)

    def marcar_procesado(self, id):
        """Marca un pedido como procesado"""
        query = '''
            UPDATE pedidos_automaticos
            SET estado='PROCESADO', fecha_procesado=?
            WHERE id=?
        '''
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.ejecutar(query, (fecha, id))

    def marcar_recibido(self, id):
        """Marca un pedido como recibido y actualiza el stock"""
        # Obtener información del pedido
        query = "SELECT producto_id, cantidad_solicitada FROM pedidos_automaticos WHERE id=?"
        pedido = self.db.consultar_uno(query, (id,))

        if pedido:
            producto_id, cantidad = pedido
            # Actualizar stock
            Producto().actualizar_stock(producto_id, cantidad, "ENTRADA",
                                       f"Pedido automático recibido (Pedido #{id})", "Sistema")

            # Marcar como recibido
            query = '''
                UPDATE pedidos_automaticos
                SET estado='RECIBIDO', fecha_procesado=?
                WHERE id=?
            '''
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.ejecutar(query, (fecha, id))

    def cancelar(self, id):
        """Cancela un pedido"""
        query = "UPDATE pedidos_automaticos SET estado='CANCELADO' WHERE id=?"
        self.db.ejecutar(query, (id,))

    def contar_pendientes(self):
        """Cuenta los pedidos pendientes"""
        query = "SELECT COUNT(*) FROM pedidos_automaticos WHERE estado='PENDIENTE'"
        resultado = self.db.consultar_uno(query)
        return resultado[0] if resultado else 0

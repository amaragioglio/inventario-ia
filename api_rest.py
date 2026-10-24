"""
API REST para Sistema de Inventario
Permite integración con otros sistemas
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import hmac
import sqlite3
from datetime import datetime
from functools import wraps

import config

app = Flask(__name__)
if config.CORS_ORIGINS:
    CORS(app, origins=config.CORS_ORIGINS)

DATABASE = config.DATABASE
API_TOKEN = config.API_TOKEN
RUTAS_PUBLICAS = {'/api/health', '/api/docs'}

# ==================== UTILIDADES ====================

def get_db_connection():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def _token_valido(cabecera):
    """Compara el token en tiempo constante para no filtrar información."""
    return hmac.compare_digest(cabecera.encode(), f'Bearer {API_TOKEN}'.encode())


@app.before_request
def proteger_api():
    """Todas las rutas requieren token salvo health y docs."""
    if request.method == 'OPTIONS' or request.path in RUTAS_PUBLICAS:
        return None
    if not _token_valido(request.headers.get('Authorization', '')):
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    return None


def require_token(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not _token_valido(request.headers.get('Authorization', '')):
            return jsonify({'error': 'No autorizado'}), 401

        return f(*args, **kwargs)

    return decorated

def response_success(data, message=None, status=200):
    """Respuesta exitosa estándar"""
    return jsonify({
        'success': True,
        'data': data,
        'message': message
    }), status

def response_error(message, status=400):
    """Respuesta de error estándar"""
    return jsonify({
        'success': False,
        'error': message
    }), status

# ==================== ENDPOINTS - PRODUCTOS ====================

@app.route('/api/productos', methods=['GET'])
def get_productos():
    """
    GET /api/productos
    Obtiene todos los productos

    Query params:
    - categoria: Filtrar por categoría
    - stock_bajo: true/false - Solo productos con stock bajo
    - limit: Número de resultados (default: 100)
    - offset: Offset para paginación (default: 0)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Construir query con filtros
        query = """
            SELECT p.*, pr.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            WHERE 1=1
        """
        params = []

        # Filtro por categoría
        if request.args.get('categoria'):
            query += " AND p.categoria = ?"
            params.append(request.args.get('categoria'))

        # Filtro por stock bajo
        if request.args.get('stock_bajo') == 'true':
            query += " AND p.stock_actual <= p.stock_minimo"

        # Paginación
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        query += f" LIMIT {limit} OFFSET {offset}"

        cursor.execute(query, params)
        productos = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return response_success(productos)

    except Exception as e:
        app.logger.exception(e)
        return response_error('Error interno del servidor', 500)

@app.route('/api/productos/<int:id>', methods=['GET'])
def get_producto(id):
    """
    GET /api/productos/{id}
    Obtiene un producto específico
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.*, pr.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            WHERE p.id = ?
        """, (id,))

        producto = cursor.fetchone()
        conn.close()

        if producto:
            return response_success(dict(producto))
        else:
            return response_error('Producto no encontrado', 404)

    except Exception as e:
        app.logger.exception(e)
        return response_error('Error interno del servidor', 500)

@app.route('/api/productos', methods=['POST'])
@require_token
def create_producto():
    """
    POST /api/productos
    Crea un nuevo producto

    Body (JSON):
    {
        "codigo": "PROD001",
        "nombre": "Producto",
        "categoria": "Categoría",
        "precio_compra": 10.0,
        "precio_venta": 15.0,
        "stock_actual": 50,
        "stock_minimo": 10,
        "stock_maximo": 100,
        "proveedor_id": 1 (opcional)
    }
    """
    try:
        data = request.get_json()

        # Validaciones
        required = ['codigo', 'nombre', 'precio_compra', 'precio_venta']
        for field in required:
            if field not in data:
                return response_error(f'Campo requerido: {field}', 400)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si ya existe
        cursor.execute("SELECT id FROM productos WHERE codigo = ?", (data['codigo'],))
        if cursor.fetchone():
            conn.close()
            return response_error('Código de producto ya existe', 400)

        # Insertar
        cursor.execute("""
            INSERT INTO productos
            (codigo, nombre, categoria, precio_compra, precio_venta,
             stock_actual, stock_minimo, stock_maximo, proveedor_id,
             fecha_ingreso)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['codigo'],
            data['nombre'],
            data.get('categoria', 'General'),
            data['precio_compra'],
            data['precio_venta'],
            data.get('stock_actual', 0),
            data.get('stock_minimo', 10),
            data.get('stock_maximo', 100),
            data.get('proveedor_id'),
            datetime.now().strftime('%Y-%m-%d')
        ))

        conn.commit()
        producto_id = cursor.lastrowid
        conn.close()

        return response_success({'id': producto_id}, 'Producto creado', 201)

    except Exception as e:
        app.logger.exception(e)
        return response_error('Error interno del servidor', 500)

@app.route('/api/productos/<int:id>', methods=['PUT'])
@require_token
def update_producto(id):
    """
    PUT /api/productos/{id}
    Actualiza un producto existente
    """
    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar que existe
        cursor.execute("SELECT id FROM productos WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return response_error('Producto no encontrado', 404)

        # Construir UPDATE dinámico
        campos_permitidos = [
            'nombre', 'categoria', 'precio_compra', 'precio_venta',
            'stock_actual', 'stock_minimo', 'stock_maximo', 'proveedor_id',
            'fecha_vencimiento', 'dias_vida_util'
        ]

        updates = []
        valores = []

        for campo in campos_permitidos:
            if campo in data:
                updates.append(f"{campo} = ?")
                valores.append(data[campo])

        if not updates:
            conn.close()
            return response_error('No hay campos para actualizar', 400)

        valores.append(id)
        query = f"UPDATE productos SET {', '.join(updates)} WHERE id = ?"

        cursor.execute(query, valores)
        conn.commit()
        conn.close()

        return response_success({'id': id}, 'Producto actualizado')

    except Exception as e:
        app.logger.exception(e)
        return response_error('Error interno del servidor', 500)

@app.route('/api/productos/<int:id>', methods=['DELETE'])
@require_token
def delete_producto(id):
    """
    DELETE /api/productos/{id}
    Elimina un producto
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM productos WHERE id = ?", (id,))
        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return response_error('Producto no encontrado', 404)

        conn.close()
        return response_success(None, 'Producto eliminado')

    except Exception as e:
        app.logger.exception(e)
        return response_error('Error interno del servidor', 500)

# ==================== ENDPOINTS - PROVEEDORES ====================

@app.route('/api/proveedores', methods=['GET'])
def get_proveedores():
    """GET /api/proveedores - Lista todos los proveedores"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM proveedores")
        proveedores = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return response_success(proveedores)

    except Exception as e:
        app.logger.exception(e)
        return response_error('Error interno del servidor', 500)

@app.route('/api/proveedores', methods=['POST'])
@require_token
def create_proveedor():
    """POST /api/proveedores - Crea un nuevo proveedor"""
    try:
        data = request.get_json()

        if 'nombre' not in data:
            return response_error('Campo requerido: nombre', 400)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO proveedores (nombre, contacto, telefono, email, direccion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data['nombre'],
            data.get('contacto', ''),
            data.get('telefono', ''),
            data.get('email', ''),
            data.get('direccion', '')
        ))

        conn.commit()
        proveedor_id = cursor.lastrowid
        conn.close()

        return response_success({'id': proveedor_id}, 'Proveedor creado', 201)

    except Exception as e:
        app.logger.exception(e)
        return response_error('Error interno del servidor', 500)

# ==================== ENDPOINTS - MOVIMIENTOS ====================

@app.route('/api/movimientos', methods=['GET'])
def get_movimientos():
    """
    GET /api/movimientos
    Obtiene historial de movimientos

    Query params:
    - producto_id: Filtrar por producto
    - tipo: ENTRADA/SALIDA
    - fecha_desde: YYYY-MM-DD
    - fecha_hasta: YYYY-MM-DD
    - limit: default 50
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT m.*, p.codigo as producto_codigo, p.nombre as producto_nombre
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            WHERE 1=1
        """
        params = []

        if request.args.get('producto_id'):
            query += " AND m.producto_id = ?"
            params.append(request.args.get('producto_id'))

        if request.args.get('tipo'):
            query += " AND m.tipo = ?"
            params.append(request.args.get('tipo').upper())

        if request.args.get('fecha_desde'):
            query += " AND m.fecha >= ?"
            params.append(request.args.get('fecha_desde'))

        if request.args.get('fecha_hasta'):
            query += " AND m.fecha <= ?"
            params.append(request.args.get('fecha_hasta'))

        query += " ORDER BY m.fecha DESC LIMIT ?"
        params.append(int(request.args.get('limit', 50)))

        cursor.execute(query, params)
        movimientos = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return response_success(movimientos)

    except Exception as e:
        app.logger.exception(e)
        return response_error('Error interno del servidor', 500)

@app.route('/api/movimientos', methods=['POST'])
@require_token
def create_movimiento():
    """
    POST /api/movimientos
    Registra un nuevo movimiento (entrada/salida)

    Body:
    {
        "producto_id": 1,
        "tipo": "ENTRADA|SALIDA",
        "cantidad": 10,
        "motivo": "Compra a proveedor"
    }
    """
    try:
        data = request.get_json()

        required = ['producto_id', 'tipo', 'cantidad']
        for field in required:
            if field not in data:
                return response_error(f'Campo requerido: {field}', 400)

        if data['tipo'] not in ['ENTRADA', 'SALIDA']:
            return response_error('Tipo debe ser ENTRADA o SALIDA', 400)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar que producto existe
        cursor.execute("SELECT stock_actual FROM productos WHERE id = ?",
                      (data['producto_id'],))
        producto = cursor.fetchone()

        if not producto:
            conn.close()
            return response_error('Producto no encontrado', 404)

        # Insertar movimiento
        cursor.execute("""
            INSERT INTO movimientos (producto_id, tipo, cantidad, motivo, fecha)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data['producto_id'],
            data['tipo'],
            data['cantidad'],
            data.get('motivo', ''),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))

        # Actualizar stock
        if data['tipo'] == 'ENTRADA':
            cursor.execute("UPDATE productos SET stock_actual = stock_actual + ? WHERE id = ?",
                         (data['cantidad'], data['producto_id']))
        else:
            cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?",
                         (data['cantidad'], data['producto_id']))

        conn.commit()
        movimiento_id = cursor.lastrowid
        conn.close()

        return response_success({'id': movimiento_id}, 'Movimiento registrado', 201)

    except Exception as e:
        app.logger.exception(e)
        return response_error('Error interno del servidor', 500)

# ==================== ENDPOINTS - ESTADÍSTICAS ====================

@app.route('/api/estadisticas', methods=['GET'])
def get_estadisticas():
    """
    GET /api/estadisticas
    Obtiene estadísticas generales del inventario
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total de productos
        cursor.execute("SELECT COUNT(*) as total FROM productos")
        total_productos = cursor.fetchone()['total']

        # Productos con stock bajo
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM productos
            WHERE stock_actual <= stock_minimo AND stock_actual > 0
        """)
        stock_bajo = cursor.fetchone()['total']

        # Productos agotados
        cursor.execute("SELECT COUNT(*) as total FROM productos WHERE stock_actual = 0")
        agotados = cursor.fetchone()['total']

        # Valor total del inventario
        cursor.execute("""
            SELECT SUM(stock_actual * precio_venta) as valor_total
            FROM productos
        """)
        valor_total = cursor.fetchone()['valor_total'] or 0

        # Movimientos hoy
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM movimientos
            WHERE DATE(fecha) = DATE('now')
        """)
        movimientos_hoy = cursor.fetchone()['total']

        conn.close()

        return response_success({
            'total_productos': total_productos,
            'stock_bajo': stock_bajo,
            'agotados': agotados,
            'valor_total_inventario': round(valor_total, 2),
            'movimientos_hoy': movimientos_hoy
        })

    except Exception as e:
        app.logger.exception(e)
        return response_error('Error interno del servidor', 500)

# ==================== ENDPOINTS - SALUD ====================

@app.route('/api/health', methods=['GET'])
def health():
    """GET /api/health - Verifica que el API esté funcionando"""
    return response_success({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/docs', methods=['GET'])
def docs():
    """GET /api/docs - Documentación del API"""
    documentacion = {
        'title': 'API REST - Sistema de Inventario',
        'version': '1.0.0',
        'base_url': request.host_url + 'api/',
        'autenticacion': {
            'tipo': 'Bearer Token',
            'header': 'Authorization: Bearer <token>',
            'nota': 'Requerido en todos los endpoints excepto /api/health y /api/docs'
        },
        'endpoints': {
            'productos': {
                'GET /api/productos': 'Listar productos',
                'GET /api/productos/{id}': 'Obtener producto',
                'POST /api/productos': 'Crear producto (requiere auth)',
                'PUT /api/productos/{id}': 'Actualizar producto (requiere auth)',
                'DELETE /api/productos/{id}': 'Eliminar producto (requiere auth)'
            },
            'proveedores': {
                'GET /api/proveedores': 'Listar proveedores',
                'POST /api/proveedores': 'Crear proveedor (requiere auth)'
            },
            'movimientos': {
                'GET /api/movimientos': 'Listar movimientos',
                'POST /api/movimientos': 'Registrar movimiento (requiere auth)'
            },
            'estadisticas': {
                'GET /api/estadisticas': 'Obtener estadísticas generales'
            },
            'utilidades': {
                'GET /api/health': 'Verificar salud del API',
                'GET /api/docs': 'Esta documentación'
            }
        }
    }

    return jsonify(documentacion)

# ==================== ENDPOINTS DE N8N / PEDIDOS ====================

from webhook_server import bp as webhooks_bp  # noqa: E402
app.register_blueprint(webhooks_bp)


@app.errorhandler(500)
def error_interno(_e):
    return response_error('Error interno del servidor', 500)


# ==================== INICIAR SERVIDOR ====================

def iniciar():
    print("=" * 60)
    print("API REST - Sistema de Inventario")
    print("=" * 60)
    print(f"Servidor: http://{config.API_HOST}:{config.API_PORT}")
    print(f"Documentacion: http://{config.API_HOST}:{config.API_PORT}/api/docs")
    if config.API_TOKEN_GENERADO:
        print("Token temporal (define API_TOKEN en .env para fijarlo):")
        print(f"  {API_TOKEN}")
    else:
        print("Token: el definido en API_TOKEN de tu archivo .env")
    print("=" * 60)
    try:
        from waitress import serve
        serve(app, host=config.API_HOST, port=config.API_PORT)
    except ImportError:
        app.run(host=config.API_HOST, port=config.API_PORT, debug=config.API_DEBUG)


if __name__ == '__main__':
    iniciar()

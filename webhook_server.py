"""
Servidor de API REST para integración con n8n
Expone endpoints para consultar productos, stock y crear pedidos automáticos
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from models import Producto, Proveedor, PedidoAutomatico, Alerta
import json

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde n8n

# ==================== ENDPOINTS DE CONSULTA ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar que el servidor está funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'Servidor de webhooks activo'
    }), 200


@app.route('/api/productos/stock-bajo', methods=['GET'])
def obtener_stock_bajo():
    """Obtiene productos con stock bajo para n8n"""
    try:
        producto_model = Producto()
        proveedor_model = Proveedor()
        productos = producto_model.obtener_productos_stock_bajo()

        resultado = []
        for p in productos:
            proveedor_info = None
            if p[10]:  # proveedor_id
                prov = proveedor_model.obtener_por_id(p[10])
                if prov:
                    proveedor_info = {
                        'id': prov[0],
                        'nombre': prov[1],
                        'contacto': prov[2],
                        'telefono': prov[3],
                        'email': prov[4]
                    }

            resultado.append({
                'id': p[0],
                'codigo': p[1],
                'nombre': p[2],
                'categoria': p[4],
                'stock_actual': p[7],
                'stock_minimo': p[8],
                'stock_maximo': p[9],
                'precio_compra': float(p[5]) if p[5] else 0,
                'precio_venta': float(p[6]) if p[6] else 0,
                'proveedor': proveedor_info,
                'necesita': int((p[9] * 0.8) - p[7])  # Cantidad recomendada a pedir
            })

        return jsonify({
            'success': True,
            'count': len(resultado),
            'productos': resultado
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/pedidos/pendientes', methods=['GET'])
def obtener_pedidos_pendientes():
    """Obtiene pedidos pendientes para n8n"""
    try:
        pedido_model = PedidoAutomatico()
        pedidos = pedido_model.obtener_todos(solo_pendientes=True)

        resultado = []
        for p in pedidos:
            resultado.append({
                'id': p[0],
                'producto': {
                    'id': p[1],
                    'nombre': p[8],
                    'codigo': p[9]
                },
                'proveedor': {
                    'id': p[2],
                    'nombre': p[10]
                },
                'cantidad_solicitada': p[3],
                'estado': p[4],
                'fecha_pedido': p[5],
                'notas': p[7]
            })

        return jsonify({
            'success': True,
            'count': len(resultado),
            'pedidos': resultado
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/alertas', methods=['GET'])
def obtener_alertas():
    """Obtiene alertas no leídas para n8n"""
    try:
        alerta_model = Alerta()
        alertas = alerta_model.obtener_no_leidas()

        resultado = []
        for a in alertas:
            resultado.append({
                'id': a[0],
                'producto_id': a[1],
                'producto_nombre': a[7],
                'tipo': a[2],
                'mensaje': a[3],
                'fecha': a[5]
            })

        return jsonify({
            'success': True,
            'count': len(resultado),
            'alertas': resultado
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== ENDPOINTS DE ACCIÓN ====================

@app.route('/api/pedidos/crear', methods=['POST'])
def crear_pedido():
    """Crea un pedido automático desde n8n"""
    try:
        data = request.get_json()

        producto_id = data.get('producto_id')
        proveedor_id = data.get('proveedor_id')
        cantidad = data.get('cantidad')
        notas = data.get('notas', 'Pedido creado desde n8n')

        if not all([producto_id, proveedor_id, cantidad]):
            return jsonify({
                'success': False,
                'error': 'Faltan campos requeridos: producto_id, proveedor_id, cantidad'
            }), 400

        pedido_model = PedidoAutomatico()
        pedido_id = pedido_model.crear(producto_id, proveedor_id, cantidad, notas)

        return jsonify({
            'success': True,
            'pedido_id': pedido_id,
            'message': 'Pedido creado correctamente'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/pedidos/<int:pedido_id>/procesar', methods=['POST'])
def procesar_pedido(pedido_id):
    """Marca un pedido como procesado desde n8n"""
    try:
        pedido_model = PedidoAutomatico()
        pedido_model.marcar_procesado(pedido_id)

        return jsonify({
            'success': True,
            'message': f'Pedido {pedido_id} marcado como procesado'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/pedidos/<int:pedido_id>/recibir', methods=['POST'])
def recibir_pedido(pedido_id):
    """Marca un pedido como recibido y actualiza stock desde n8n"""
    try:
        pedido_model = PedidoAutomatico()
        pedido_model.marcar_recibido(pedido_id)

        return jsonify({
            'success': True,
            'message': f'Pedido {pedido_id} recibido y stock actualizado'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/notificar/dueno', methods=['POST'])
def notificar_dueno():
    """Endpoint para que n8n notifique al dueño"""
    try:
        data = request.get_json()
        tipo = data.get('tipo', 'info')
        mensaje = data.get('mensaje', '')

        # Aquí puedes agregar lógica para enviar email, WhatsApp, etc.
        print(f"[NOTIFICACIÓN AL DUEÑO] {tipo.upper()}: {mensaje}")

        return jsonify({
            'success': True,
            'message': 'Notificación enviada'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== WEBHOOK PARA N8N ====================

@app.route('/webhook/stock-bajo', methods=['POST'])
def webhook_stock_bajo():
    """
    Webhook que n8n puede llamar cuando detecta stock bajo
    N8n puede enviar una petición con IA para decidir qué hacer
    """
    try:
        data = request.get_json()

        # N8n enviará la decisión de la IA
        accion = data.get('accion')  # 'crear_pedido', 'notificar', 'ignorar'
        producto_id = data.get('producto_id')
        cantidad_sugerida = data.get('cantidad_sugerida')

        if accion == 'crear_pedido':
            producto_model = Producto()
            producto = producto_model.obtener_por_id(producto_id)

            if producto and producto[10]:  # Tiene proveedor
                pedido_model = PedidoAutomatico()
                pedido_id = pedido_model.crear(
                    producto_id,
                    producto[10],  # proveedor_id
                    cantidad_sugerida,
                    f"Pedido automático con IA - n8n (Cantidad sugerida: {cantidad_sugerida})"
                )

                return jsonify({
                    'success': True,
                    'accion': 'pedido_creado',
                    'pedido_id': pedido_id,
                    'producto': producto[2]
                }), 200

        return jsonify({
            'success': True,
            'accion': accion,
            'message': 'Acción procesada'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVIDOR DE WEBHOOKS PARA N8N")
    print("="*60)
    print("\n📡 Endpoints disponibles:")
    print("  GET  /api/health                     - Health check")
    print("  GET  /api/productos/stock-bajo       - Productos con stock bajo")
    print("  GET  /api/pedidos/pendientes         - Pedidos pendientes")
    print("  GET  /api/alertas                    - Alertas no leídas")
    print("  POST /api/pedidos/crear              - Crear pedido")
    print("  POST /api/pedidos/<id>/procesar      - Marcar procesado")
    print("  POST /api/pedidos/<id>/recibir       - Marcar recibido")
    print("  POST /api/notificar/dueno            - Notificar al dueño")
    print("  POST /webhook/stock-bajo             - Webhook con IA")
    print("\n🌐 Servidor escuchando en: http://localhost:5000")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)

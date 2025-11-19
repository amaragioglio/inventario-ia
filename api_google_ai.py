"""
API REST para integracion con Google AI (Gemini)

Endpoints para analisis de inventarios con inteligencia artificial.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from google_ai import GoogleAIAssistant, GOOGLE_AI_DISPONIBLE

# Crear blueprint para las rutas de IA
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Instancia global del asistente
_asistente = None

def obtener_asistente():
    """Obtiene o crea la instancia del asistente de IA"""
    global _asistente
    if _asistente is None:
        _asistente = GoogleAIAssistant()
    return _asistente


# ============================================
# ENDPOINTS DE CONFIGURACION
# ============================================

@ai_bp.route('/status', methods=['GET'])
def estado_ia():
    """Obtiene el estado de la configuracion de IA"""
    asistente = obtener_asistente()

    return jsonify({
        'exito': True,
        'datos': {
            'google_ai_disponible': GOOGLE_AI_DISPONIBLE,
            'configurado': asistente.esta_configurado(),
            'modelo': asistente._obtener_config('google_ai_modelo'),
            'analisis_automatico': asistente._obtener_config('analisis_automatico') == '1'
        }
    })


@ai_bp.route('/configurar', methods=['POST'])
def configurar_ia():
    """Configura la API key de Google AI"""
    datos = request.get_json()

    if not datos or 'api_key' not in datos:
        return jsonify({
            'exito': False,
            'error': 'Se requiere api_key en el cuerpo de la solicitud'
        }), 400

    asistente = obtener_asistente()
    exito = asistente.configurar_api_key(datos['api_key'])

    return jsonify({
        'exito': exito,
        'mensaje': 'API key configurada correctamente' if exito else 'Error al configurar API key'
    })


@ai_bp.route('/configuracion', methods=['GET'])
def obtener_configuracion():
    """Obtiene la configuracion actual de IA (sin mostrar API key)"""
    from database import Database
    db = Database()

    configs = db.consultar('''
        SELECT clave, valor, descripcion, tipo
        FROM configuracion_ia
        WHERE clave != 'google_ai_api_key'
    ''')

    return jsonify({
        'exito': True,
        'configuracion': [
            {
                'clave': c[0],
                'valor': c[1],
                'descripcion': c[2],
                'tipo': c[3]
            }
            for c in configs
        ]
    })


@ai_bp.route('/configuracion', methods=['PUT'])
def actualizar_configuracion():
    """Actualiza una configuracion de IA"""
    datos = request.get_json()

    if not datos or 'clave' not in datos or 'valor' not in datos:
        return jsonify({
            'exito': False,
            'error': 'Se requiere clave y valor'
        }), 400

    asistente = obtener_asistente()
    asistente._guardar_config(datos['clave'], datos['valor'])

    return jsonify({
        'exito': True,
        'mensaje': f"Configuracion '{datos['clave']}' actualizada"
    })


# ============================================
# ENDPOINTS DE ANALISIS
# ============================================

@ai_bp.route('/analisis/inventario', methods=['GET'])
def analizar_inventario():
    """Realiza un analisis completo del inventario"""
    asistente = obtener_asistente()

    if not asistente.esta_configurado():
        return jsonify({
            'exito': False,
            'error': 'Google AI no esta configurado. Configure la API key primero.'
        }), 400

    resultado = asistente.analizar_inventario_general()

    return jsonify({
        'exito': resultado['exito'],
        'analisis': resultado.get('respuesta'),
        'error': resultado.get('error'),
        'tiempo_ms': resultado.get('tiempo_ms')
    })


@ai_bp.route('/analisis/producto/<int:producto_id>', methods=['GET'])
def analizar_producto(producto_id):
    """Analiza un producto especifico"""
    asistente = obtener_asistente()

    if not asistente.esta_configurado():
        return jsonify({
            'exito': False,
            'error': 'Google AI no esta configurado'
        }), 400

    resultado = asistente.analizar_producto(producto_id)

    return jsonify({
        'exito': resultado['exito'],
        'analisis': resultado.get('respuesta'),
        'error': resultado.get('error'),
        'tiempo_ms': resultado.get('tiempo_ms')
    })


@ai_bp.route('/analisis/tendencias', methods=['GET'])
def detectar_tendencias():
    """Detecta tendencias en el inventario"""
    asistente = obtener_asistente()

    if not asistente.esta_configurado():
        return jsonify({
            'exito': False,
            'error': 'Google AI no esta configurado'
        }), 400

    resultado = asistente.detectar_tendencias()

    return jsonify({
        'exito': resultado['exito'],
        'tendencias': resultado.get('respuesta'),
        'error': resultado.get('error'),
        'tiempo_ms': resultado.get('tiempo_ms')
    })


# ============================================
# ENDPOINTS DE PREDICCION
# ============================================

@ai_bp.route('/prediccion/demanda', methods=['GET'])
def predecir_demanda_general():
    """Predice la demanda general"""
    asistente = obtener_asistente()

    if not asistente.esta_configurado():
        return jsonify({
            'exito': False,
            'error': 'Google AI no esta configurado'
        }), 400

    dias = request.args.get('dias', 30, type=int)
    resultado = asistente.predecir_demanda(dias_prediccion=dias)

    return jsonify({
        'exito': resultado['exito'],
        'prediccion': resultado.get('respuesta'),
        'error': resultado.get('error'),
        'tiempo_ms': resultado.get('tiempo_ms')
    })


@ai_bp.route('/prediccion/producto/<int:producto_id>', methods=['GET'])
def predecir_demanda_producto(producto_id):
    """Predice la demanda de un producto especifico"""
    asistente = obtener_asistente()

    if not asistente.esta_configurado():
        return jsonify({
            'exito': False,
            'error': 'Google AI no esta configurado'
        }), 400

    dias = request.args.get('dias', 30, type=int)
    resultado = asistente.predecir_demanda(producto_id=producto_id, dias_prediccion=dias)

    return jsonify({
        'exito': resultado['exito'],
        'prediccion': resultado.get('respuesta'),
        'error': resultado.get('error'),
        'tiempo_ms': resultado.get('tiempo_ms')
    })


# ============================================
# ENDPOINTS DE RECOMENDACIONES
# ============================================

@ai_bp.route('/recomendaciones/compra', methods=['GET'])
def recomendaciones_compra():
    """Obtiene recomendaciones de compra"""
    asistente = obtener_asistente()

    if not asistente.esta_configurado():
        return jsonify({
            'exito': False,
            'error': 'Google AI no esta configurado'
        }), 400

    resultado = asistente.obtener_recomendaciones_compra()

    return jsonify({
        'exito': resultado['exito'],
        'recomendaciones': resultado.get('respuesta'),
        'productos': resultado.get('productos', []),
        'error': resultado.get('error'),
        'tiempo_ms': resultado.get('tiempo_ms')
    })


@ai_bp.route('/recomendaciones/precios', methods=['GET'])
def optimizar_precios():
    """Obtiene recomendaciones para optimizar precios"""
    asistente = obtener_asistente()

    if not asistente.esta_configurado():
        return jsonify({
            'exito': False,
            'error': 'Google AI no esta configurado'
        }), 400

    resultado = asistente.optimizar_precios()

    return jsonify({
        'exito': resultado['exito'],
        'recomendaciones': resultado.get('respuesta'),
        'error': resultado.get('error'),
        'tiempo_ms': resultado.get('tiempo_ms')
    })


# ============================================
# ENDPOINTS DE REPORTES
# ============================================

@ai_bp.route('/reportes/ejecutivo', methods=['GET'])
def generar_reporte_ejecutivo():
    """Genera un reporte ejecutivo"""
    asistente = obtener_asistente()

    if not asistente.esta_configurado():
        return jsonify({
            'exito': False,
            'error': 'Google AI no esta configurado'
        }), 400

    dias = request.args.get('dias', 30, type=int)
    resultado = asistente.generar_reporte_ejecutivo(periodo_dias=dias)

    return jsonify({
        'exito': resultado['exito'],
        'reporte': resultado.get('respuesta'),
        'error': resultado.get('error'),
        'tiempo_ms': resultado.get('tiempo_ms')
    })


@ai_bp.route('/reportes/proveedor/<int:proveedor_id>', methods=['GET'])
def reporte_proveedor(proveedor_id):
    """Genera un reporte de proveedor"""
    asistente = obtener_asistente()

    if not asistente.esta_configurado():
        return jsonify({
            'exito': False,
            'error': 'Google AI no esta configurado'
        }), 400

    resultado = asistente.generar_reporte_proveedor(proveedor_id)

    return jsonify({
        'exito': resultado['exito'],
        'reporte': resultado.get('respuesta'),
        'error': resultado.get('error'),
        'tiempo_ms': resultado.get('tiempo_ms')
    })


@ai_bp.route('/reportes/historial', methods=['GET'])
def historial_reportes():
    """Obtiene el historial de reportes generados"""
    asistente = obtener_asistente()

    tipo = request.args.get('tipo')
    limite = request.args.get('limite', 10, type=int)

    reportes = asistente.obtener_reportes(tipo=tipo, limite=limite)

    return jsonify({
        'exito': True,
        'reportes': [
            {
                'id': r[0],
                'tipo': r[1],
                'titulo': r[2],
                'fecha': r[3],
                'resumen': r[4]
            }
            for r in reportes
        ]
    })


# ============================================
# ENDPOINTS DE CONSULTAS
# ============================================

@ai_bp.route('/consulta', methods=['POST'])
def consulta_libre():
    """Realiza una consulta libre a la IA"""
    asistente = obtener_asistente()

    if not asistente.esta_configurado():
        return jsonify({
            'exito': False,
            'error': 'Google AI no esta configurado'
        }), 400

    datos = request.get_json()

    if not datos or 'pregunta' not in datos:
        return jsonify({
            'exito': False,
            'error': 'Se requiere una pregunta'
        }), 400

    resultado = asistente.consulta_libre(datos['pregunta'])

    return jsonify({
        'exito': resultado['exito'],
        'respuesta': resultado.get('respuesta'),
        'error': resultado.get('error'),
        'tiempo_ms': resultado.get('tiempo_ms')
    })


@ai_bp.route('/mensaje-proveedor', methods=['POST'])
def generar_mensaje_proveedor():
    """Genera un mensaje para enviar al proveedor"""
    asistente = obtener_asistente()

    if not asistente.esta_configurado():
        return jsonify({
            'exito': False,
            'error': 'Google AI no esta configurado'
        }), 400

    datos = request.get_json()

    if not datos or 'producto_id' not in datos or 'cantidad' not in datos:
        return jsonify({
            'exito': False,
            'error': 'Se requiere producto_id y cantidad'
        }), 400

    resultado = asistente.sugerir_mensaje_proveedor(
        datos['producto_id'],
        datos['cantidad']
    )

    return jsonify({
        'exito': resultado['exito'],
        'mensaje': resultado.get('respuesta'),
        'error': resultado.get('error'),
        'tiempo_ms': resultado.get('tiempo_ms')
    })


# ============================================
# ENDPOINTS DE ESTADISTICAS
# ============================================

@ai_bp.route('/estadisticas', methods=['GET'])
def estadisticas_uso():
    """Obtiene estadisticas de uso de la IA"""
    asistente = obtener_asistente()
    stats = asistente.obtener_estadisticas_uso()

    return jsonify({
        'exito': True,
        'estadisticas': stats
    })


@ai_bp.route('/historial/analisis', methods=['GET'])
def historial_analisis():
    """Obtiene el historial de analisis realizados"""
    asistente = obtener_asistente()

    limite = request.args.get('limite', 20, type=int)
    analisis = asistente.obtener_historial_analisis(limite)

    return jsonify({
        'exito': True,
        'analisis': [
            {
                'id': a[0],
                'tipo': a[1],
                'producto_id': a[2],
                'fecha': a[3],
                'resumen': a[4]
            }
            for a in analisis
        ]
    })


@ai_bp.route('/tendencias/activas', methods=['GET'])
def tendencias_activas():
    """Obtiene las tendencias detectadas que siguen activas"""
    asistente = obtener_asistente()
    tendencias = asistente.obtener_tendencias_activas()

    return jsonify({
        'exito': True,
        'tendencias': [
            {
                'id': t[0],
                'tipo': t[1],
                'descripcion': t[2],
                'urgencia': t[7],
                'fecha_deteccion': t[9]
            }
            for t in tendencias
        ]
    })


@ai_bp.route('/predicciones/activas', methods=['GET'])
def predicciones_activas():
    """Obtiene las predicciones que aun estan vigentes"""
    asistente = obtener_asistente()
    predicciones = asistente.obtener_predicciones_activas()

    return jsonify({
        'exito': True,
        'predicciones': [
            {
                'id': p[0],
                'producto_id': p[1],
                'producto_nombre': p[-1],
                'tipo': p[2],
                'valor_predicho': p[3],
                'confianza': p[4],
                'fecha': p[8]
            }
            for p in predicciones
        ]
    })


# ============================================
# FUNCION PARA REGISTRAR BLUEPRINT
# ============================================

def registrar_api_ia(app):
    """Registra el blueprint de IA en la aplicacion Flask"""
    app.register_blueprint(ai_bp)
    print("[OK] API de Google AI registrada en /api/ai")

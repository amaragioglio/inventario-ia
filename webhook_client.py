"""
Cliente de Webhooks para n8n - Sistema de Automatización Completo
Envía eventos inteligentes a n8n para procesamiento con IA
"""

import requests
import json
from datetime import datetime
from database import Database

class WebhookClient:
    """Cliente mejorado de webhooks con todos los eventos del sistema"""

    def __init__(self):
        self.db = Database()
        self.n8n_webhook_url = self.get_config('n8n_webhook_url', '')
        self.notificaciones_activas = self.get_config('notificaciones_activas', 'true') == 'true'

    def get_config(self, clave, default=''):
        """Obtiene configuración de la BD"""
        query = "SELECT valor FROM configuracion WHERE clave=?"
        resultado = self.db.consultar_uno(query, (clave,))
        return resultado[0] if resultado else default

    def set_config(self, clave, valor):
        """Guarda configuración en la BD"""
        query = '''
            INSERT OR REPLACE INTO configuracion (clave, valor)
            VALUES (?, ?)
        '''
        self.db.ejecutar(query, (clave, valor))

    def _enviar_webhook(self, payload):
        """Método interno para enviar webhooks"""
        if not self.notificaciones_activas or not self.n8n_webhook_url:
            return False

        try:
            # Añadir timestamp a todos los eventos
            payload['timestamp'] = datetime.now().isoformat()
            payload['sistema'] = 'inventario_minimarket'

            response = requests.post(
                self.n8n_webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                print(f"[WEBHOOK] ✅ Enviado: {payload.get('evento', 'desconocido')}")
                return True
            else:
                print(f"[WEBHOOK] ⚠️ Error {response.status_code}: {payload.get('evento')}")
                return False

        except requests.exceptions.Timeout:
            print(f"[WEBHOOK] ⏱️ Timeout en: {payload.get('evento')}")
            return False
        except Exception as e:
            print(f"[WEBHOOK] ❌ Error: {str(e)}")
            return False

    # ==================== EVENTOS DE STOCK ====================

    def evento_stock_bajo(self, producto, proveedor=None, analisis_rotacion=None):
        """
        Evento: Stock bajo detectado
        n8n puede: Analizar con IA, crear pedido, notificar proveedor
        """
        payload = {
            'evento': 'stock_bajo',
            'prioridad': 'ALTA' if producto[7] == 0 else 'MEDIA',
            'producto': {
                'id': producto[0],
                'codigo': producto[1],
                'nombre': producto[2],
                'descripcion': producto[3],
                'categoria': producto[4],
                'precio_compra': float(producto[5]) if producto[5] else 0,
                'precio_venta': float(producto[6]) if producto[6] else 0,
                'stock_actual': producto[7],
                'stock_minimo': producto[8],
                'stock_maximo': producto[9],
                'fecha_ingreso': producto[13] if len(producto) > 13 else None,
            },
            'proveedor': {
                'id': proveedor[0],
                'nombre': proveedor[1],
                'contacto': proveedor[2],
                'telefono': proveedor[3],
                'email': proveedor[4],
                'direccion': proveedor[5]
            } if proveedor else None,
            'analisis': analisis_rotacion,
            'recomendaciones': {
                'cantidad_sugerida': int((producto[9] * 0.8) - producto[7]),
                'urgencia': 'URGENTE' if producto[7] <= producto[8] * 0.5 else 'NORMAL'
            }
        }
        return self._enviar_webhook(payload)

    def evento_stock_critico(self, producto, proveedor=None):
        """Evento: Stock en nivel crítico (0 unidades)"""
        payload = {
            'evento': 'stock_critico',
            'prioridad': 'CRITICA',
            'producto': {
                'id': producto[0],
                'codigo': producto[1],
                'nombre': producto[2],
                'categoria': producto[4],
                'stock_actual': producto[7],
            },
            'proveedor': {
                'id': proveedor[0] if proveedor else None,
                'nombre': proveedor[1] if proveedor else None,
                'telefono': proveedor[3] if proveedor else None,
            },
            'mensaje': f"🚨 URGENTE: {producto[2]} está AGOTADO",
            'accion_recomendada': 'Crear pedido urgente o contactar proveedor inmediatamente'
        }
        return self._enviar_webhook(payload)

    # ==================== EVENTOS DE VENCIMIENTO ====================

    def evento_producto_proximo_vencer(self, producto, dias_restantes):
        """Evento: Producto próximo a vencer"""
        urgencia = 'URGENTE' if dias_restantes <= 7 else 'ALTA' if dias_restantes <= 15 else 'MEDIA'

        payload = {
            'evento': 'producto_proximo_vencer',
            'prioridad': urgencia,
            'producto': {
                'id': producto[0],
                'codigo': producto[1],
                'nombre': producto[2],
                'categoria': producto[4],
                'stock_actual': producto[7],
                'fecha_vencimiento': producto[14] if len(producto) > 14 else None,
                'dias_restantes': dias_restantes
            },
            'sugerencias': {
                'accion': 'Crear promoción urgente' if dias_restantes <= 7 else 'Preparar promoción',
                'descuento_sugerido': '50%' if dias_restantes <= 7 else '30%' if dias_restantes <= 15 else '20%',
                'tipo_promocion': '2x1' if dias_restantes <= 7 else 'Descuento'
            },
            'mensaje': f"⏰ {producto[2]} vence en {dias_restantes} días - Stock: {producto[7]} unidades"
        }
        return self._enviar_webhook(payload)

    def evento_producto_vencido(self, producto):
        """Evento: Producto ya vencido"""
        payload = {
            'evento': 'producto_vencido',
            'prioridad': 'CRITICA',
            'producto': {
                'id': producto[0],
                'codigo': producto[1],
                'nombre': producto[2],
                'categoria': producto[4],
                'stock_actual': producto[7],
                'fecha_vencimiento': producto[14] if len(producto) > 14 else None,
            },
            'mensaje': f"❌ CRÍTICO: {producto[2]} está VENCIDO - {producto[7]} unidades en stock",
            'accion_recomendada': 'Retirar del inventario inmediatamente y registrar pérdida'
        }
        return self._enviar_webhook(payload)

    # ==================== EVENTOS DE PEDIDOS ====================

    def evento_pedido_creado(self, pedido_data):
        """Evento: Pedido automático creado"""
        payload = {
            'evento': 'pedido_creado',
            'prioridad': 'MEDIA',
            'pedido': pedido_data,
            'mensaje': f"📋 Nuevo pedido automático creado: {pedido_data.get('producto', 'Producto')}",
            'accion_recomendada': 'Revisar y confirmar con proveedor'
        }
        return self._enviar_webhook(payload)

    def evento_pedido_procesado(self, pedido_id, producto_nombre):
        """Evento: Pedido marcado como procesado"""
        payload = {
            'evento': 'pedido_procesado',
            'prioridad': 'INFO',
            'pedido_id': pedido_id,
            'producto': producto_nombre,
            'mensaje': f"✓ Pedido procesado: {producto_nombre}"
        }
        return self._enviar_webhook(payload)

    # ==================== EVENTOS DE ANÁLISIS ====================

    def evento_analisis_diario(self, reporte_completo):
        """
        Evento: Análisis diario completo
        Se envía automáticamente cada día con todas las métricas
        """
        payload = {
            'evento': 'analisis_diario',
            'prioridad': 'INFO',
            'reporte': reporte_completo,
            'mensaje': 'Reporte diario de inventario generado'
        }
        return self._enviar_webhook(payload)

    def evento_dia_alta_actividad(self, actividad_datos):
        """Evento: Día con actividad inusualmente alta"""
        payload = {
            'evento': 'dia_alta_actividad',
            'prioridad': 'INFO',
            'actividad': actividad_datos,
            'mensaje': f"📈 Actividad alta detectada: {actividad_datos.get('total_actividad', 0)} movimientos",
            'accion_recomendada': 'Revisar stock de productos más vendidos'
        }
        return self._enviar_webhook(payload)

    def evento_categoria_bajo_rendimiento(self, categoria, analisis):
        """Evento: Categoría con bajo rendimiento"""
        payload = {
            'evento': 'categoria_bajo_rendimiento',
            'prioridad': 'MEDIA',
            'categoria': categoria,
            'analisis': analisis,
            'mensaje': f"📉 Categoría {categoria} tiene bajo rendimiento",
            'accion_recomendada': 'Considerar promociones o reducir pedidos de esta categoría'
        }
        return self._enviar_webhook(payload)

    # ==================== EVENTOS DE PROMOCIONES ====================

    def evento_sugerencia_promocion(self, sugerencias):
        """
        Evento: Sugerencias de promociones generadas por IA
        n8n puede: Crear campañas automáticas, enviar a redes sociales
        """
        payload = {
            'evento': 'sugerencias_promocion',
            'prioridad': 'ALTA' if any(s['urgencia'] == 'URGENTE' for s in sugerencias) else 'MEDIA',
            'sugerencias': sugerencias,
            'total_sugerencias': len(sugerencias),
            'mensaje': f"💡 {len(sugerencias)} sugerencias de promoción disponibles",
            'accion_recomendada': 'Revisar y crear campañas de promoción'
        }
        return self._enviar_webhook(payload)

    # ==================== EVENTOS DEL SISTEMA ====================

    def evento_sistema_iniciado(self):
        """Evento: Sistema de inventario iniciado"""
        payload = {
            'evento': 'sistema_iniciado',
            'prioridad': 'INFO',
            'mensaje': 'Sistema de inventario iniciado correctamente',
            'hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return self._enviar_webhook(payload)

    def evento_backup_creado(self, archivo_backup):
        """Evento: Backup de base de datos creado"""
        payload = {
            'evento': 'backup_creado',
            'prioridad': 'INFO',
            'archivo': archivo_backup,
            'mensaje': f"💾 Backup creado: {archivo_backup}"
        }
        return self._enviar_webhook(payload)

    def evento_error_sistema(self, error_descripcion, nivel='ERROR'):
        """Evento: Error en el sistema"""
        payload = {
            'evento': 'error_sistema',
            'prioridad': 'ALTA',
            'nivel': nivel,
            'descripcion': error_descripcion,
            'mensaje': f"⚠️ Error detectado: {error_descripcion}"
        }
        return self._enviar_webhook(payload)

    # ==================== NOTIFICACIONES AL DUEÑO ====================

    def notificar_dueno(self, tipo, mensaje, detalles=None):
        """
        Notificación directa al dueño
        tipos: 'critico', 'advertencia', 'info', 'exito'
        """
        iconos = {
            'critico': '🚨',
            'advertencia': '⚠️',
            'info': 'ℹ️',
            'exito': '✅'
        }

        payload = {
            'evento': 'notificacion_dueno',
            'prioridad': 'ALTA' if tipo == 'critico' else 'MEDIA' if tipo == 'advertencia' else 'INFO',
            'tipo': tipo,
            'icono': iconos.get(tipo, 'ℹ️'),
            'mensaje': mensaje,
            'detalles': detalles,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return self._enviar_webhook(payload)

    # ==================== MÉTODO PARA PROBAR CONEXIÓN ====================

    def probar_conexion(self):
        """Prueba la conexión con n8n"""
        if not self.n8n_webhook_url:
            return False, "URL de webhook no configurada"

        payload = {
            'evento': 'test_conexion',
            'prioridad': 'INFO',
            'mensaje': 'Prueba de conexión desde el sistema de inventario',
            'timestamp': datetime.now().isoformat()
        }

        try:
            response = requests.post(
                self.n8n_webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                return True, "Conexión exitosa con n8n"
            else:
                return False, f"Error {response.status_code}: {response.text[:100]}"

        except requests.exceptions.Timeout:
            return False, "Timeout: n8n no responde"
        except requests.exceptions.ConnectionError:
            return False, "Error de conexión: Verifica que n8n esté funcionando"
        except Exception as e:
            return False, f"Error: {str(e)}"


# ==================== FUNCIONES DE CONFIGURACIÓN ====================

def configurar_n8n(webhook_url, activar_notificaciones=True):
    """
    Configura la URL de webhook de n8n

    Ejemplo de uso:
    >>> from webhook_client import configurar_n8n
    >>> configurar_n8n('https://tu-n8n.com/webhook/inventario')
    """
    client = WebhookClient()
    client.set_config('n8n_webhook_url', webhook_url)
    client.set_config('notificaciones_activas', 'true' if activar_notificaciones else 'false')

    # Probar conexión
    exito, mensaje = client.probar_conexion()

    print("="*60)
    print("CONFIGURACIÓN DE N8N")
    print("="*60)
    print(f"URL: {webhook_url}")
    print(f"Notificaciones: {'Activas' if activar_notificaciones else 'Inactivas'}")
    print(f"Estado: {mensaje}")
    print("="*60)

    return exito

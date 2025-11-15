"""
Sistema de Tareas Automáticas
Ejecuta análisis periódicos y envía eventos a n8n
"""

import threading
import time
from datetime import datetime, timedelta
from analizador_ia import AnalizadorIA
from webhook_client import WebhookClient
from models import Producto

class TareasAutomaticas:
    """Gestiona tareas automáticas del sistema"""

    def __init__(self):
        self.analizador = AnalizadorIA()
        self.webhook = WebhookClient()
        self.producto_model = Producto()
        self.running = False
        self.thread = None

        # Configuración de tareas (en segundos)
        self.INTERVALO_VERIFICACION_VENCIMIENTOS = 3600  # 1 hora
        self.INTERVALO_ANALISIS_DIARIO = 86400  # 24 horas
        self.INTERVALO_SUGERENCIAS_PROMOCIONES = 7200  # 2 horas
        self.INTERVALO_VERIFICACION_ACTIVIDAD = 1800  # 30 minutos

        # Timestamps de última ejecución
        self.ultima_verificacion_vencimientos = datetime.now() - timedelta(hours=2)
        self.ultimo_analisis_diario = datetime.now() - timedelta(days=2)
        self.ultimas_sugerencias = datetime.now() - timedelta(hours=3)
        self.ultima_verificacion_actividad = datetime.now() - timedelta(minutes=45)

    def iniciar(self):
        """Inicia el sistema de tareas automáticas"""
        if self.running:
            print("[TAREAS] Ya está en ejecución")
            return

        self.running = True
        self.thread = threading.Thread(target=self._ejecutar_ciclo, daemon=True)
        self.thread.start()
        print("[TAREAS] [OK] Sistema de tareas automaticas iniciado")

        # Enviar evento de sistema iniciado
        try:
            self.webhook.evento_sistema_iniciado()
        except:
            pass

    def detener(self):
        """Detiene el sistema de tareas automáticas"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[TAREAS] [STOP] Sistema de tareas automaticas detenido")

    def _ejecutar_ciclo(self):
        """Ciclo principal de ejecución"""
        while self.running:
            try:
                ahora = datetime.now()

                # Tarea 1: Verificar productos próximos a vencer
                if (ahora - self.ultima_verificacion_vencimientos).total_seconds() >= self.INTERVALO_VERIFICACION_VENCIMIENTOS:
                    self._verificar_vencimientos()
                    self.ultima_verificacion_vencimientos = ahora

                # Tarea 2: Análisis diario completo
                if (ahora - self.ultimo_analisis_diario).total_seconds() >= self.INTERVALO_ANALISIS_DIARIO:
                    self._enviar_analisis_diario()
                    self.ultimo_analisis_diario = ahora

                # Tarea 3: Sugerencias de promociones
                if (ahora - self.ultimas_sugerencias).total_seconds() >= self.INTERVALO_SUGERENCIAS_PROMOCIONES:
                    self._enviar_sugerencias_promociones()
                    self.ultimas_sugerencias = ahora

                # Tarea 4: Verificar actividad inusual
                if (ahora - self.ultima_verificacion_actividad).total_seconds() >= self.INTERVALO_VERIFICACION_ACTIVIDAD:
                    self._verificar_actividad()
                    self.ultima_verificacion_actividad = ahora

            except Exception as e:
                print(f"[TAREAS] [ERROR] Error en ciclo: {e}")
                # Notificar error
                try:
                    self.webhook.evento_error_sistema(str(e))
                except:
                    pass

            # Esperar 60 segundos antes de la próxima verificación
            time.sleep(60)

    def _verificar_vencimientos(self):
        """Verifica productos próximos a vencer y envía notificaciones"""
        print("[TAREAS] [CHECK] Verificando vencimientos...")

        # Productos que vencen en 7 días
        proximos_7dias = self.producto_model.obtener_productos_proximos_vencer(7)
        for producto in proximos_7dias:
            dias_restantes = self.producto_model.calcular_dias_hasta_vencimiento(producto)
            if dias_restantes and dias_restantes <= 7:
                try:
                    self.webhook.evento_producto_proximo_vencer(producto, dias_restantes)
                except Exception as e:
                    print(f"[TAREAS] Error webhook vencimiento: {e}")

        # Productos vencidos
        productos_vencidos = self.producto_model.obtener_productos_vencidos()
        for producto in productos_vencidos:
            try:
                self.webhook.evento_producto_vencido(producto)
            except Exception as e:
                print(f"[TAREAS] Error webhook vencido: {e}")

        if proximos_7dias or productos_vencidos:
            print(f"[TAREAS] [ALERT] {len(proximos_7dias)} proximos a vencer, {len(productos_vencidos)} vencidos")

    def _enviar_analisis_diario(self):
        """Genera y envía análisis diario completo"""
        print("[TAREAS] [INFO] Generando analisis diario...")

        try:
            reporte = self.analizador.generar_reporte_completo()
            self.webhook.evento_analisis_diario(reporte)
            print("[TAREAS] [OK] Analisis diario enviado")
        except Exception as e:
            print(f"[TAREAS] Error análisis diario: {e}")

    def _enviar_sugerencias_promociones(self):
        """Genera y envía sugerencias de promociones"""
        print("[TAREAS] [INFO] Generando sugerencias de promociones...")

        try:
            sugerencias = self.analizador.sugerir_promociones()
            if sugerencias:
                self.webhook.evento_sugerencia_promocion(sugerencias)
                print(f"[TAREAS] [OK] {len(sugerencias)} sugerencias de promocion enviadas")
        except Exception as e:
            print(f"[TAREAS] Error sugerencias: {e}")

    def _verificar_actividad(self):
        """Verifica si hay actividad inusual"""
        print("[TAREAS] [INFO] Verificando actividad...")

        try:
            movimientos = self.analizador.analizar_movimientos_diarios(7)

            if movimientos['dias_top']:
                # Obtener actividad de hoy (primer elemento)
                hoy = movimientos['dias_top'][0]
                promedio = sum(d['total_actividad'] for d in movimientos['dias_top']) / len(movimientos['dias_top'])

                # Si la actividad de hoy es 50% mayor al promedio, notificar
                if hoy['total_actividad'] > promedio * 1.5:
                    self.webhook.evento_dia_alta_actividad(hoy)
                    print(f"[TAREAS] [ALERT] Alta actividad detectada: {hoy['total_actividad']} movimientos")

            # Verificar categorías con bajo rendimiento
            tendencias = self.analizador.analizar_tendencias_categoria()
            for categoria_data in tendencias:
                if categoria_data['rendimiento'] == 'BAJO':
                    try:
                        self.webhook.evento_categoria_bajo_rendimiento(
                            categoria_data['categoria'],
                            categoria_data
                        )
                    except:
                        pass

        except Exception as e:
            print(f"[TAREAS] Error verificando actividad: {e}")

    # ==================== EJECUCIÓN MANUAL ====================

    def ejecutar_analisis_completo(self):
        """Ejecuta un análisis completo inmediato (llamado manualmente)"""
        print("[TAREAS] [RUN] Ejecutando analisis completo manual...")

        self._verificar_vencimientos()
        self._enviar_analisis_diario()
        self._enviar_sugerencias_promociones()
        self._verificar_actividad()

        print("[TAREAS] [OK] Analisis completo finalizado")

    def generar_alertas_urgentes(self):
        """Genera y envía alertas urgentes"""
        print("[TAREAS] [ALERT] Generando alertas urgentes...")

        try:
            alertas = self.analizador.generar_alertas_automaticas()
            for alerta in alertas:
                # Enviar cada alerta como notificación al dueño
                tipo = 'critico' if alerta['prioridad'] == 'ALTA' else 'advertencia'
                self.webhook.notificar_dueno(
                    tipo,
                    alerta['titulo'],
                    alerta
                )
            print(f"[TAREAS] [OK] {len(alertas)} alertas urgentes enviadas")
            return alertas
        except Exception as e:
            print(f"[TAREAS] Error alertas: {e}")
            return []


# Instancia global
_tareas_automaticas = None

def obtener_tareas_automaticas():
    """Obtiene la instancia global de tareas automáticas"""
    global _tareas_automaticas
    if _tareas_automaticas is None:
        _tareas_automaticas = TareasAutomaticas()
    return _tareas_automaticas

def iniciar_tareas_automaticas():
    """Inicia el sistema de tareas automáticas"""
    tareas = obtener_tareas_automaticas()
    tareas.iniciar()
    return tareas

def detener_tareas_automaticas():
    """Detiene el sistema de tareas automáticas"""
    global _tareas_automaticas
    if _tareas_automaticas:
        _tareas_automaticas.detener()


# Para pruebas
if __name__ == "__main__":
    print("="*60)
    print("SISTEMA DE TAREAS AUTOMÁTICAS - MODO PRUEBA")
    print("="*60)

    tareas = TareasAutomaticas()

    print("\n1. Ejecutando análisis completo...")
    tareas.ejecutar_analisis_completo()

    print("\n2. Generando alertas urgentes...")
    alertas = tareas.generar_alertas_urgentes()
    print(f"\nAlertas generadas: {len(alertas)}")
    for alerta in alertas:
        print(f"  - [{alerta['prioridad']}] {alerta['titulo']}")

    print("\n" + "="*60)
    print("Prueba completada")
    print("="*60)

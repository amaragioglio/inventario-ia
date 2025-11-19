"""
Ventana de integracion con Google AI para el Sistema de Inventario.

Proporciona una interfaz grafica para:
- Configurar Google AI
- Ejecutar analisis de inventarios
- Ver predicciones y tendencias
- Generar reportes con IA
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime

try:
    from google_ai import GoogleAIAssistant, GOOGLE_AI_DISPONIBLE
except ImportError:
    GOOGLE_AI_DISPONIBLE = False


class VentanaIA:
    """Ventana para interactuar con Google AI"""

    def __init__(self, parent, tema_actual='claro'):
        self.parent = parent
        self.tema = tema_actual
        self.asistente = None
        self.procesando = False

        if GOOGLE_AI_DISPONIBLE:
            self.asistente = GoogleAIAssistant()

    def crear_pestana(self, notebook):
        """Crea la pestana de IA en el notebook principal"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="  Google AI  ")

        # Dividir en dos columnas
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=2)
        frame.rowconfigure(0, weight=1)

        # Panel izquierdo - Acciones
        self._crear_panel_acciones(frame)

        # Panel derecho - Resultados
        self._crear_panel_resultados(frame)

        return frame

    def _crear_panel_acciones(self, parent):
        """Crea el panel de acciones a la izquierda"""
        panel = ttk.LabelFrame(parent, text="Acciones de IA", padding=10)
        panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Estado de configuracion
        estado_frame = ttk.Frame(panel)
        estado_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_estado = ttk.Label(
            estado_frame,
            text="Estado: Verificando...",
            font=('Segoe UI', 9)
        )
        self.lbl_estado.pack(side=tk.LEFT)

        ttk.Button(
            estado_frame,
            text="Configurar",
            command=self._mostrar_configuracion,
            width=10
        ).pack(side=tk.RIGHT)

        # Separador
        ttk.Separator(panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Seccion: Analisis
        ttk.Label(panel, text="Analisis", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)

        btn_frame1 = ttk.Frame(panel)
        btn_frame1.pack(fill=tk.X, pady=5)

        ttk.Button(
            btn_frame1,
            text="Analizar Inventario",
            command=self._analizar_inventario,
            width=20
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_frame1,
            text="Detectar Tendencias",
            command=self._detectar_tendencias,
            width=20
        ).pack(side=tk.LEFT, padx=2)

        # Seccion: Predicciones
        ttk.Label(panel, text="Predicciones", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))

        btn_frame2 = ttk.Frame(panel)
        btn_frame2.pack(fill=tk.X, pady=5)

        ttk.Button(
            btn_frame2,
            text="Predecir Demanda",
            command=self._predecir_demanda,
            width=20
        ).pack(side=tk.LEFT, padx=2)

        # Seccion: Recomendaciones
        ttk.Label(panel, text="Recomendaciones", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))

        btn_frame3 = ttk.Frame(panel)
        btn_frame3.pack(fill=tk.X, pady=5)

        ttk.Button(
            btn_frame3,
            text="Recomendaciones Compra",
            command=self._recomendaciones_compra,
            width=20
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_frame3,
            text="Optimizar Precios",
            command=self._optimizar_precios,
            width=20
        ).pack(side=tk.LEFT, padx=2)

        # Seccion: Reportes
        ttk.Label(panel, text="Reportes", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))

        btn_frame4 = ttk.Frame(panel)
        btn_frame4.pack(fill=tk.X, pady=5)

        ttk.Button(
            btn_frame4,
            text="Reporte Ejecutivo",
            command=self._generar_reporte,
            width=20
        ).pack(side=tk.LEFT, padx=2)

        # Separador
        ttk.Separator(panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Consulta libre
        ttk.Label(panel, text="Consulta Libre", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)

        self.txt_consulta = ttk.Entry(panel)
        self.txt_consulta.pack(fill=tk.X, pady=5)
        self.txt_consulta.bind('<Return>', lambda e: self._consulta_libre())

        ttk.Button(
            panel,
            text="Consultar",
            command=self._consulta_libre
        ).pack(fill=tk.X)

        # Indicador de progreso
        self.progress = ttk.Progressbar(panel, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))

        # Estadisticas de uso
        ttk.Separator(panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        self.lbl_stats = ttk.Label(
            panel,
            text="Consultas: 0 | Exito: 0%",
            font=('Segoe UI', 8)
        )
        self.lbl_stats.pack(anchor=tk.W)

        # Verificar estado inicial
        self._verificar_estado()

    def _crear_panel_resultados(self, parent):
        """Crea el panel de resultados a la derecha"""
        panel = ttk.LabelFrame(parent, text="Resultados", padding=10)
        panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Toolbar
        toolbar = ttk.Frame(panel)
        toolbar.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(
            toolbar,
            text="Limpiar",
            command=self._limpiar_resultados,
            width=10
        ).pack(side=tk.LEFT)

        ttk.Button(
            toolbar,
            text="Copiar",
            command=self._copiar_resultados,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        self.lbl_tiempo = ttk.Label(toolbar, text="")
        self.lbl_tiempo.pack(side=tk.RIGHT)

        # Area de texto con scroll
        self.txt_resultados = scrolledtext.ScrolledText(
            panel,
            wrap=tk.WORD,
            font=('Consolas', 10),
            height=30
        )
        self.txt_resultados.pack(fill=tk.BOTH, expand=True)

        # Mensaje inicial
        self._mostrar_mensaje_bienvenida()

    def _mostrar_mensaje_bienvenida(self):
        """Muestra mensaje de bienvenida"""
        mensaje = """
ASISTENTE DE IA PARA INVENTARIOS
================================

Bienvenido al asistente de inteligencia artificial integrado con Google Gemini.

FUNCIONALIDADES DISPONIBLES:

1. ANALISIS DE INVENTARIO
   - Analisis completo del estado del inventario
   - Deteccion de tendencias y patrones
   - Identificacion de problemas y oportunidades

2. PREDICCIONES
   - Prediccion de demanda futura
   - Estimacion de reabastecimiento
   - Analisis de estacionalidad

3. RECOMENDACIONES
   - Sugerencias de compra inteligentes
   - Optimizacion de precios
   - Mejora de margenes

4. REPORTES
   - Reportes ejecutivos automaticos
   - Analisis de proveedores
   - KPIs y metricas

5. CONSULTA LIBRE
   - Pregunte cualquier cosa sobre su inventario
   - Obtenga respuestas personalizadas

PARA COMENZAR:
1. Configure su API key de Google AI
2. Seleccione una accion del panel izquierdo
3. Los resultados apareceran aqui

"""
        self.txt_resultados.insert(tk.END, mensaje)

    def _verificar_estado(self):
        """Verifica el estado de configuracion de IA"""
        if not GOOGLE_AI_DISPONIBLE:
            self.lbl_estado.config(
                text="Estado: No disponible",
                foreground='red'
            )
            return

        if self.asistente and self.asistente.esta_configurado():
            self.lbl_estado.config(
                text="Estado: Configurado",
                foreground='green'
            )
            self._actualizar_estadisticas()
        else:
            self.lbl_estado.config(
                text="Estado: No configurado",
                foreground='orange'
            )

    def _actualizar_estadisticas(self):
        """Actualiza las estadisticas de uso"""
        if self.asistente:
            stats = self.asistente.obtener_estadisticas_uso()
            self.lbl_stats.config(
                text=f"Consultas: {stats['total_consultas']} | Exito: {stats['tasa_exito']}%"
            )

    def _mostrar_configuracion(self):
        """Muestra ventana de configuracion"""
        ventana = tk.Toplevel(self.parent)
        ventana.title("Configurar Google AI")
        ventana.geometry("450x300")
        ventana.resizable(False, False)
        ventana.transient(self.parent)
        ventana.grab_set()

        # Frame principal
        frame = ttk.Frame(ventana, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Titulo
        ttk.Label(
            frame,
            text="Configuracion de Google AI",
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor=tk.W)

        ttk.Label(
            frame,
            text="Configure su API key de Google AI (Gemini) para habilitar\nlas funciones de inteligencia artificial.",
            font=('Segoe UI', 9)
        ).pack(anchor=tk.W, pady=(5, 15))

        # API Key
        ttk.Label(frame, text="API Key:").pack(anchor=tk.W)
        entry_key = ttk.Entry(frame, width=50, show="*")
        entry_key.pack(fill=tk.X, pady=(5, 10))

        # Modelo
        ttk.Label(frame, text="Modelo:").pack(anchor=tk.W)
        combo_modelo = ttk.Combobox(
            frame,
            values=['gemini-pro', 'gemini-pro-vision', 'gemini-1.5-pro'],
            state='readonly'
        )
        combo_modelo.set('gemini-pro')
        combo_modelo.pack(fill=tk.X, pady=(5, 15))

        # Informacion
        info_frame = ttk.LabelFrame(frame, text="Como obtener API Key", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(
            info_frame,
            text="1. Visite: https://makersuite.google.com/app/apikey\n"
                 "2. Inicie sesion con su cuenta de Google\n"
                 "3. Cree una nueva API key\n"
                 "4. Copie y pegue la key aqui",
            font=('Segoe UI', 8)
        ).pack(anchor=tk.W)

        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        def guardar():
            api_key = entry_key.get().strip()
            if not api_key:
                messagebox.showwarning("Aviso", "Ingrese una API key")
                return

            if self.asistente:
                # Guardar modelo
                self.asistente._guardar_config('google_ai_modelo', combo_modelo.get())

                # Configurar API key
                if self.asistente.configurar_api_key(api_key):
                    messagebox.showinfo("Exito", "API key configurada correctamente")
                    self._verificar_estado()
                    ventana.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo configurar la API key")

        ttk.Button(
            btn_frame,
            text="Guardar",
            command=guardar
        ).pack(side=tk.RIGHT)

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=ventana.destroy
        ).pack(side=tk.RIGHT, padx=5)

    def _ejecutar_en_hilo(self, funcion, titulo):
        """Ejecuta una funcion en un hilo separado"""
        if self.procesando:
            messagebox.showinfo("Aviso", "Ya hay una operacion en progreso")
            return

        if not self.asistente or not self.asistente.esta_configurado():
            messagebox.showwarning(
                "Aviso",
                "Google AI no esta configurado.\nConfigure su API key primero."
            )
            return

        self.procesando = True
        self.progress.start()
        self._limpiar_resultados()
        self.txt_resultados.insert(tk.END, f"Procesando: {titulo}...\n\n")

        def worker():
            try:
                resultado = funcion()
                self.parent.after(0, lambda: self._mostrar_resultado(resultado, titulo))
            except Exception as e:
                self.parent.after(0, lambda: self._mostrar_error(str(e)))
            finally:
                self.parent.after(0, self._finalizar_proceso)

        threading.Thread(target=worker, daemon=True).start()

    def _finalizar_proceso(self):
        """Finaliza el indicador de proceso"""
        self.procesando = False
        self.progress.stop()
        self._actualizar_estadisticas()

    def _mostrar_resultado(self, resultado, titulo):
        """Muestra el resultado en el panel"""
        self._limpiar_resultados()

        if resultado.get('exito'):
            self.txt_resultados.insert(tk.END, f"{'='*60}\n")
            self.txt_resultados.insert(tk.END, f"{titulo.upper()}\n")
            self.txt_resultados.insert(tk.END, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.txt_resultados.insert(tk.END, f"{'='*60}\n\n")
            self.txt_resultados.insert(tk.END, resultado.get('respuesta', 'Sin respuesta'))

            if resultado.get('tiempo_ms'):
                self.lbl_tiempo.config(text=f"Tiempo: {resultado['tiempo_ms']}ms")
        else:
            self.txt_resultados.insert(
                tk.END,
                f"ERROR: {resultado.get('error', 'Error desconocido')}"
            )

    def _mostrar_error(self, error):
        """Muestra un error"""
        self._limpiar_resultados()
        self.txt_resultados.insert(tk.END, f"ERROR: {error}")

    def _limpiar_resultados(self):
        """Limpia el area de resultados"""
        self.txt_resultados.delete(1.0, tk.END)
        self.lbl_tiempo.config(text="")

    def _copiar_resultados(self):
        """Copia los resultados al portapapeles"""
        contenido = self.txt_resultados.get(1.0, tk.END)
        self.parent.clipboard_clear()
        self.parent.clipboard_append(contenido)
        messagebox.showinfo("Copiado", "Contenido copiado al portapapeles")

    # Funciones de analisis
    def _analizar_inventario(self):
        """Analiza el inventario general"""
        self._ejecutar_en_hilo(
            self.asistente.analizar_inventario_general,
            "Analisis de Inventario"
        )

    def _detectar_tendencias(self):
        """Detecta tendencias"""
        self._ejecutar_en_hilo(
            self.asistente.detectar_tendencias,
            "Deteccion de Tendencias"
        )

    def _predecir_demanda(self):
        """Predice la demanda"""
        self._ejecutar_en_hilo(
            lambda: self.asistente.predecir_demanda(dias_prediccion=30),
            "Prediccion de Demanda (30 dias)"
        )

    def _recomendaciones_compra(self):
        """Obtiene recomendaciones de compra"""
        self._ejecutar_en_hilo(
            self.asistente.obtener_recomendaciones_compra,
            "Recomendaciones de Compra"
        )

    def _optimizar_precios(self):
        """Optimiza precios"""
        self._ejecutar_en_hilo(
            self.asistente.optimizar_precios,
            "Optimizacion de Precios"
        )

    def _generar_reporte(self):
        """Genera reporte ejecutivo"""
        self._ejecutar_en_hilo(
            lambda: self.asistente.generar_reporte_ejecutivo(periodo_dias=30),
            "Reporte Ejecutivo"
        )

    def _consulta_libre(self):
        """Realiza una consulta libre"""
        pregunta = self.txt_consulta.get().strip()
        if not pregunta:
            messagebox.showinfo("Aviso", "Ingrese una pregunta")
            return

        self._ejecutar_en_hilo(
            lambda: self.asistente.consulta_libre(pregunta),
            "Consulta: " + pregunta[:30] + "..."
        )
        self.txt_consulta.delete(0, tk.END)


def crear_pestana_ia(notebook, parent, tema='claro'):
    """Funcion de conveniencia para crear la pestana de IA"""
    ventana_ia = VentanaIA(parent, tema)
    return ventana_ia.crear_pestana(notebook)

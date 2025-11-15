import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from models import Producto, Proveedor, Movimiento, Alerta, PedidoAutomatico
from notifications import NotificationManager
from ai_assistant import AIAssistant
from theme_manager import ThemeManager
from tareas_automaticas import iniciar_tareas_automaticas, detener_tareas_automaticas, obtener_tareas_automaticas
from analizador_ia import AnalizadorIA
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# ==================== THEME (Legacy - Para compatibilidad) ====================
class Theme:
    """Tema centralizado - Ahora dinámico con ThemeManager"""
    # Fuentes
    FONT_BASE = ("Segoe UI", 11)
    FONT_TITLE = ("Segoe UI Semibold", 18)
    FONT_SUBTITLE = ("Segoe UI Semibold", 14)
    FONT_BUTTON = ("Segoe UI Semibold", 10)
    FONT_LABEL = ("Segoe UI", 10)

    # Colores (serán actualizados por ThemeManager)
    COLOR_BG = "#F5F5F7"
    COLOR_PANEL = "#FFFFFF"
    COLOR_TEXT = "#1C1C1E"
    COLOR_MUTED = "#6E6E73"
    COLOR_PRIMARY = "#0A84FF"
    COLOR_SUCCESS = "#30D158"
    COLOR_WARNING = "#FFD60A"
    COLOR_DANGER = "#FF3B30"
    COLOR_SECONDARY = "#5E5CE6"

    # Estilos adicionales
    PADDING = 20
    SHADOW_COLOR = "#E5E5EA"

    @staticmethod
    def update_from_theme_manager(tm):
        """Actualiza los colores desde el ThemeManager"""
        Theme.COLOR_BG = tm.get_color('bg')
        Theme.COLOR_PANEL = tm.get_color('panel')
        Theme.COLOR_TEXT = tm.get_color('text')
        Theme.COLOR_MUTED = tm.get_color('text_secondary')
        Theme.COLOR_PRIMARY = tm.get_color('primary')
        Theme.COLOR_SUCCESS = tm.get_color('success')
        Theme.COLOR_WARNING = tm.get_color('warning')
        Theme.COLOR_DANGER = tm.get_color('danger')
        Theme.COLOR_SECONDARY = tm.get_color('info')
        Theme.SHADOW_COLOR = tm.get_color('shadow')


class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Inventario - Minimarket")
        self.root.geometry("1400x900")

        # Gestor de temas
        self.theme_manager = ThemeManager()
        Theme.update_from_theme_manager(self.theme_manager)
        self.theme_manager.register_callback(self.on_theme_changed)

        self.root.configure(bg=Theme.COLOR_BG)

        # Modelos
        self.producto_model = Producto()
        self.proveedor_model = Proveedor()
        self.movimiento_model = Movimiento()
        self.alerta_model = Alerta()
        self.pedido_model = PedidoAutomatico()

        # Sistema de notificaciones
        self.notification_manager = NotificationManager(self.root)

        # Analizador IA
        self.analizador_ia = AnalizadorIA()

        # Crear menú
        self.crear_menu()

        # Configurar estilo
        self.configurar_estilos()

        # Crear interfaz
        self.crear_interfaz()

        # Cargar datos iniciales
        self.cargar_dashboard()

        # Iniciar verificación de alertas
        self.notification_manager.verificar_alertas()

        # Iniciar tareas automáticas
        print("[SISTEMA] Iniciando tareas automáticas...")
        self.tareas_automaticas = iniciar_tareas_automaticas()

        # Configurar cierre de la aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def crear_menu(self):
        """Crea la barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menú Ver
        menu_ver = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=menu_ver)

        # Submenú de Tema
        self.tema_var = tk.StringVar(value=self.theme_manager.mode)
        menu_ver.add_radiobutton(label="🌞 Tema Claro", variable=self.tema_var,
                                value="light", command=lambda: self.cambiar_tema("light"))
        menu_ver.add_radiobutton(label="🌙 Tema Oscuro", variable=self.tema_var,
                                value="dark", command=lambda: self.cambiar_tema("dark"))
        menu_ver.add_radiobutton(label="⚡ Auto (Sistema)", variable=self.tema_var,
                                value="auto", command=lambda: self.cambiar_tema("auto"))

        menu_ver.add_separator()
        menu_ver.add_command(label="🔄 Actualizar Dashboard", command=self.cargar_dashboard)

        # Menú Integración
        menu_integracion = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Integración", menu=menu_integracion)
        menu_integracion.add_command(label="📥 Importar Datos", command=self.abrir_ventana_integracion)
        menu_integracion.add_command(label="📤 Exportar Datos", command=self.abrir_ventana_integracion)
        menu_integracion.add_separator()
        menu_integracion.add_command(label="🔗 API REST", command=self.abrir_info_api)

        # Menú Configuración
        menu_config = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configuración", menu=menu_config)
        menu_config.add_command(label="⚙️ Configurar n8n", command=self.abrir_configuracion_n8n)
        menu_config.add_command(label="📊 Ejecutar Análisis Completo", command=self.ejecutar_analisis_manual)

        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="📘 Documentación n8n", command=self.abrir_documentacion_n8n)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)

    def cambiar_tema(self, modo):
        """Cambia el tema de la aplicación"""
        self.theme_manager.set_mode(modo)

    def on_theme_changed(self):
        """Callback cuando cambia el tema"""
        # Actualizar colores estáticos
        Theme.update_from_theme_manager(self.theme_manager)

        # Reconfigurar estilos
        self.configurar_estilos()

        # Actualizar colores de fondo
        self.root.configure(bg=Theme.COLOR_BG)

        # Reconfigurar todas las tablas existentes
        self.actualizar_colores_tablas()

        # Recargar dashboard para actualizar gráficas
        self.cargar_dashboard()

        # Recargar productos para aplicar nuevos colores
        self.cargar_productos()

        # Mostrar mensaje
        modo_texto = {"light": "Claro", "dark": "Oscuro", "auto": "Automático"}
        messagebox.showinfo("Tema", f"✅ Tema cambiado a: {modo_texto[self.theme_manager.mode]}")

    def mostrar_acerca_de(self):
        """Muestra información sobre la aplicación"""
        tema = "🌙 Oscuro" if self.theme_manager.is_dark() else "🌞 Claro"
        messagebox.showinfo("Acerca de",
                          f"Sistema de Inventario - Minimarket\n\n"
                          f"Versión 2.0\n"
                          f"Con IA Inteligente y Análisis Predictivo\n\n"
                          f"Tema actual: {tema}\n"
                          f"Modo: {self.theme_manager.mode.capitalize()}")

    def abrir_configuracion_n8n(self):
        """Abre ventana de configuración de n8n"""
        # Crear ventana modal
        ventana = tk.Toplevel(self.root)
        ventana.title("Configuración de n8n")
        ventana.geometry("650x400")
        ventana.configure(bg=Theme.COLOR_BG)
        ventana.transient(self.root)
        ventana.grab_set()

        # Centrar ventana
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (650 // 2)
        y = (ventana.winfo_screenheight() // 2) - (400 // 2)
        ventana.geometry(f"650x400+{x}+{y}")

        # Frame principal con padding
        frame_main = tk.Frame(ventana, bg=Theme.COLOR_BG)
        frame_main.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Título
        tk.Label(frame_main, text="⚙️ Configuración de n8n",
                font=("Segoe UI", 16, "bold"),
                bg=Theme.COLOR_BG,
                fg=Theme.COLOR_TEXT).pack(pady=(0, 10))

        tk.Label(frame_main, text="Configura la URL de tu webhook de n8n para automatizaciones",
                font=Theme.FONT_BASE,
                bg=Theme.COLOR_BG,
                fg=Theme.COLOR_MUTED).pack(pady=(0, 20))

        # Frame del formulario
        frame_form = tk.Frame(frame_main, bg=Theme.COLOR_PANEL, relief=tk.FLAT)
        frame_form.pack(fill=tk.BOTH, expand=True, pady=10)

        # Padding interno
        frame_content = tk.Frame(frame_form, bg=Theme.COLOR_PANEL)
        frame_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Label y Entry para URL
        tk.Label(frame_content, text="URL del Webhook:",
                font=Theme.FONT_LABEL,
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT).pack(anchor='w', pady=(0, 5))

        # Leer configuración actual
        from webhook_client import WebhookClient
        webhook = WebhookClient()
        url_actual = webhook.webhook_url if webhook.webhook_url else ""

        entry_url = tk.Entry(frame_content,
                            font=Theme.FONT_BASE,
                            bg=Theme.COLOR_BG,
                            fg=Theme.COLOR_TEXT,
                            relief=tk.FLAT,
                            insertbackground=Theme.COLOR_TEXT)
        entry_url.pack(fill=tk.X, pady=(0, 5), ipady=8)
        entry_url.insert(0, url_actual)

        # Texto de ayuda
        tk.Label(frame_content,
                text="Ejemplo: https://tu-n8n.com/webhook/inventario",
                font=("Segoe UI", 9),
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_MUTED).pack(anchor='w', pady=(0, 15))

        # Label de estado
        label_estado = tk.Label(frame_content, text="",
                               font=Theme.FONT_BASE,
                               bg=Theme.COLOR_PANEL,
                               wraplength=550)
        label_estado.pack(pady=10)

        # Frame para botones
        frame_botones = tk.Frame(frame_content, bg=Theme.COLOR_PANEL)
        frame_botones.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))

        def probar_conexion():
            """Prueba la conexión con n8n"""
            url = entry_url.get().strip()
            if not url:
                label_estado.config(text="⚠️ Por favor ingresa una URL",
                                  fg=Theme.COLOR_WARNING)
                return

            label_estado.config(text="🔄 Probando conexión...",
                              fg=Theme.COLOR_TEXT)
            ventana.update()

            try:
                from webhook_client import WebhookClient
                webhook_temp = WebhookClient()
                webhook_temp.webhook_url = url
                exito = webhook_temp.probar_conexion()

                if exito:
                    label_estado.config(text="✅ Conexión exitosa con n8n",
                                      fg=Theme.COLOR_SUCCESS)
                else:
                    label_estado.config(text="❌ No se pudo conectar. Verifica la URL",
                                      fg=Theme.COLOR_ERROR)
            except Exception as e:
                label_estado.config(text=f"❌ Error: {str(e)}",
                                  fg=Theme.COLOR_ERROR)

        def guardar_configuracion():
            """Guarda la configuración de n8n"""
            url = entry_url.get().strip()
            if not url:
                messagebox.showwarning("Advertencia", "Por favor ingresa una URL")
                return

            try:
                from webhook_client import configurar_n8n
                configurar_n8n(url)
                messagebox.showinfo("Éxito", "Configuración guardada correctamente")
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

        # Botones
        btn_probar = self.crear_boton(frame_botones, "🔍 Probar Conexión",
                                      probar_conexion,
                                      Theme.COLOR_PRIMARY)
        btn_probar.pack(side=tk.LEFT, padx=(0, 10))

        btn_guardar = self.crear_boton(frame_botones, "💾 Guardar",
                                       guardar_configuracion,
                                       Theme.COLOR_SUCCESS)
        btn_guardar.pack(side=tk.LEFT, padx=(0, 10))

        btn_cancelar = self.crear_boton(frame_botones, "❌ Cancelar",
                                        ventana.destroy,
                                        Theme.COLOR_MUTED,
                                        Theme.COLOR_TEXT)
        btn_cancelar.pack(side=tk.LEFT)

    def ejecutar_analisis_manual(self):
        """Ejecuta un análisis completo manualmente"""
        respuesta = messagebox.askyesno("Análisis Completo",
                                       "¿Deseas ejecutar un análisis completo ahora?\n\n"
                                       "Esto incluye:\n"
                                       "• Verificación de vencimientos\n"
                                       "• Análisis diario\n"
                                       "• Sugerencias de promociones\n"
                                       "• Verificación de actividad\n\n"
                                       "Los resultados se enviarán a n8n si está configurado.")
        if respuesta:
            try:
                if hasattr(self, 'tareas_automaticas') and self.tareas_automaticas:
                    tareas = obtener_tareas_automaticas()
                    tareas.ejecutar_analisis_completo()
                    messagebox.showinfo("Éxito", "Análisis completo ejecutado correctamente.\n"
                                                 "Revisa n8n para ver los resultados.")
                else:
                    messagebox.showerror("Error", "Sistema de tareas no disponible")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo ejecutar el análisis:\n{str(e)}")

    def abrir_documentacion_n8n(self):
        """Abre la documentación de n8n"""
        import os
        import subprocess

        doc_path = os.path.join(os.getcwd(), "DOCUMENTACION_N8N.md")

        if os.path.exists(doc_path):
            try:
                # Intentar abrir con el editor predeterminado
                os.startfile(doc_path)
            except:
                messagebox.showinfo("Documentación",
                                  f"Abre el archivo:\n{doc_path}\n\n"
                                  f"Con tu editor de texto favorito.")
        else:
            messagebox.showerror("Error",
                               f"No se encontró el archivo de documentación:\n{doc_path}")

    def abrir_ventana_integracion(self):
        """Abre la ventana de integración de datos"""
        try:
            from ventana_integracion import VentanaIntegracion
            VentanaIntegracion(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir ventana de integración:\n{str(e)}")

    def abrir_info_api(self):
        """Muestra información sobre el API REST"""
        mensaje = """API REST - Sistema de Inventario

El sistema incluye un API REST para integración con otros sistemas.

Características:
• Endpoints CRUD para productos, proveedores y movimientos
• Autenticación por token
• Documentación Swagger integrada
• Soporte JSON

Para activar el API:
1. Ejecuta: python api_rest.py
2. El servidor iniciará en: http://localhost:5000
3. Documentación: http://localhost:5000/docs

Endpoints principales:
• GET /api/productos - Listar productos
• POST /api/productos - Crear producto
• GET /api/productos/{id} - Obtener producto
• PUT /api/productos/{id} - Actualizar producto
• DELETE /api/productos/{id} - Eliminar producto

Ver documentación completa en DOCUMENTACION_API.md"""

        messagebox.showinfo("API REST", mensaje)

    def configurar_estilos(self):
        """Configura los estilos de la aplicación con tema Apple/macOS"""
        style = ttk.Style()
        style.theme_use('clam')

        # Estilo para Notebook (pestañas) - Planas y minimalistas
        style.configure('TNotebook',
                       background=Theme.COLOR_BG,
                       borderwidth=0,
                       tabmargins=[0, 0, 0, 0])

        style.configure('TNotebook.Tab',
                       padding=[24, 14],
                       font=Theme.FONT_BASE,
                       borderwidth=0,
                       relief='flat',
                       focuscolor='none')

        # Pestaña activa: texto azul con línea inferior
        # Pestaña inactiva: texto gris
        style.map('TNotebook.Tab',
                 background=[('selected', Theme.COLOR_BG), ('!selected', Theme.COLOR_BG)],
                 foreground=[('selected', Theme.COLOR_PRIMARY), ('!selected', Theme.COLOR_MUTED)],
                 bordercolor=[('selected', Theme.COLOR_PRIMARY), ('!selected', Theme.COLOR_BG)])

        # Estilo para Treeview (tablas) - Minimalista con filas alternadas
        style.configure("Treeview",
                       font=Theme.FONT_BASE,
                       rowheight=36,
                       background=Theme.COLOR_PANEL,
                       fieldbackground=Theme.COLOR_PANEL,
                       foreground=Theme.COLOR_TEXT,
                       borderwidth=0)

        # Encabezados de tabla con colores dinámicos
        tree_header_color = self.theme_manager.get_color('tree_header')
        style.configure("Treeview.Heading",
                       font=Theme.FONT_LABEL,
                       background=tree_header_color,
                       foreground=Theme.COLOR_TEXT,
                       borderwidth=0,
                       relief='flat')

        style.map("Treeview.Heading",
                 background=[('active', tree_header_color)],
                 foreground=[('active', Theme.COLOR_TEXT)])

        # Selección con colores dinámicos
        tree_selected_color = self.theme_manager.get_color('tree_selected')
        selected_text = '#FFFFFF' if self.theme_manager.is_dark() else Theme.COLOR_TEXT
        style.map('Treeview',
                 background=[('selected', tree_selected_color)],
                 foreground=[('selected', selected_text)])

        # Scrollbar minimalista
        style.configure("Vertical.TScrollbar",
                       background=Theme.COLOR_BG,
                       troughcolor=Theme.COLOR_BG,
                       borderwidth=0,
                       arrowsize=12)

        style.map("Vertical.TScrollbar",
                 background=[('active', Theme.SHADOW_COLOR), ('!active', '#D1D1D6')])

    def crear_interfaz(self):
        """Crea la interfaz principal"""
        # Frame superior con título y alertas (estilo macOS)
        frame_header = tk.Frame(self.root, bg=Theme.COLOR_PANEL, height=70)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)

        # Agregar sombra visual (línea inferior)
        separator = tk.Frame(self.root, bg=Theme.SHADOW_COLOR, height=1)
        separator.pack(fill=tk.X)

        # Título
        label_titulo = tk.Label(frame_header, text="Sistema de Inventario",
                               font=Theme.FONT_TITLE,
                               bg=Theme.COLOR_PANEL,
                               fg=Theme.COLOR_TEXT)
        label_titulo.pack(side=tk.LEFT, padx=30, pady=20)

        # Botón de alertas (se actualizará dinámicamente)
        self.btn_alertas = tk.Button(frame_header, text="🔔 Alertas (0)",
                                     command=self.mostrar_alertas,
                                     bg=Theme.COLOR_WARNING,
                                     fg=Theme.COLOR_TEXT,
                                     font=Theme.FONT_BUTTON,
                                     relief=tk.FLAT,
                                     padx=24,
                                     pady=12,
                                     cursor="hand2",
                                     borderwidth=0,
                                     highlightthickness=0)

        # Efectos hover para botón de alertas
        def on_enter_alertas(e):
            self.btn_alertas['background'] = self._oscurecer_color(self.btn_alertas['bg'])

        def on_leave_alertas(e):
            # Restaurar color según estado
            cantidad = self.alerta_model.contar_no_leidas()
            if cantidad > 0:
                self.btn_alertas['background'] = Theme.COLOR_DANGER
            else:
                self.btn_alertas['background'] = Theme.COLOR_WARNING

        self.btn_alertas.bind("<Enter>", on_enter_alertas)
        self.btn_alertas.bind("<Leave>", on_leave_alertas)
        self.btn_alertas.pack(side=tk.RIGHT, padx=30, pady=20)

        # Frame principal con pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Crear pestañas
        self.tab_dashboard = tk.Frame(self.notebook, bg=Theme.COLOR_BG)
        self.tab_productos = tk.Frame(self.notebook, bg=Theme.COLOR_BG)
        self.tab_proveedores = tk.Frame(self.notebook, bg=Theme.COLOR_BG)
        self.tab_pedidos = tk.Frame(self.notebook, bg=Theme.COLOR_BG)
        self.tab_movimientos = tk.Frame(self.notebook, bg=Theme.COLOR_BG)
        self.tab_reportes = tk.Frame(self.notebook, bg=Theme.COLOR_BG)
        self.tab_configuracion = tk.Frame(self.notebook, bg=Theme.COLOR_BG)

        self.notebook.add(self.tab_dashboard, text="  Dashboard  ")
        self.notebook.add(self.tab_productos, text="  Productos  ")
        self.notebook.add(self.tab_proveedores, text="  Proveedores  ")
        self.notebook.add(self.tab_pedidos, text="  Pedidos Auto  ")
        self.notebook.add(self.tab_movimientos, text="  Movimientos  ")
        self.notebook.add(self.tab_reportes, text="  Reportes  ")
        self.notebook.add(self.tab_configuracion, text="  ⚙️ Configuración  ")

        # Construir cada pestaña
        self.construir_dashboard()
        self.construir_productos()
        self.construir_proveedores()
        self.construir_pedidos()
        self.construir_movimientos()
        self.construir_reportes()
        self.construir_configuracion()

        # Actualizar contador de alertas
        self.actualizar_contador_alertas()

    # ==================== DASHBOARD ====================
    def construir_dashboard(self):
        """Construye dashboard simplificado con categorías y proyecciones IA"""
        # Canvas principal con scroll
        canvas = tk.Canvas(self.tab_dashboard, bg=Theme.COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_dashboard, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Theme.COLOR_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame principal
        frame = tk.Frame(scrollable_frame, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # === TARJETAS KPI ===
        frame_stats = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_stats.pack(fill=tk.X, pady=(0, 25))

        self.card_total_productos = self.crear_tarjeta_stat(frame_stats, "📦 Total Productos", "0", Theme.COLOR_PRIMARY)
        self.card_stock_bajo = self.crear_tarjeta_stat(frame_stats, "⚠️ Stock Bajo", "0", Theme.COLOR_DANGER)
        self.card_valor_total = self.crear_tarjeta_stat(frame_stats, "💰 Valor Total", "$0", Theme.COLOR_SUCCESS)
        self.card_pedidos = self.crear_tarjeta_stat(frame_stats, "📋 Pedidos", "0", Theme.COLOR_SECONDARY)

        # === SECCIÓN PRINCIPAL: CATEGORÍAS Y PROYECCIONES ===
        frame_principal = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_principal.pack(fill=tk.X, pady=(0, 25))

        # Frame izquierdo - Gráfica de categorías (altura fija)
        frame_grafica_izq = tk.Frame(frame_principal, bg=Theme.COLOR_PANEL, width=400, height=350)
        frame_grafica_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        frame_grafica_izq.pack_propagate(False)

        label_cat = tk.Label(frame_grafica_izq, text="📊 Productos por Categoría",
                            font=Theme.FONT_SUBTITLE,
                            bg=Theme.COLOR_PANEL,
                            fg=Theme.COLOR_TEXT)
        label_cat.pack(pady=(15, 5))

        # Contenedor para la gráfica de categorías
        self.frame_grafica_categorias = tk.Frame(frame_grafica_izq, bg=Theme.COLOR_PANEL)
        self.frame_grafica_categorias.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # Frame derecho - Proyecciones IA (altura fija)
        frame_proyecciones_container = tk.Frame(frame_principal, bg=Theme.COLOR_PANEL, width=400, height=350)
        frame_proyecciones_container.pack(side=tk.LEFT, fill=tk.Y, padx=(12, 0))
        frame_proyecciones_container.pack_propagate(False)

        label_ia = tk.Label(frame_proyecciones_container, text="🤖 Proyecciones Inteligentes",
                            font=Theme.FONT_SUBTITLE,
                            bg=Theme.COLOR_PANEL,
                            fg=Theme.COLOR_TEXT)
        label_ia.pack(pady=(15, 5))

        # Contenedor para proyecciones IA
        self.frame_proyecciones = tk.Frame(frame_proyecciones_container, bg=Theme.COLOR_PANEL)
        self.frame_proyecciones.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # === PRODUCTOS CRÍTICOS (Stock Bajo) ===
        frame_stock_bajo = tk.Frame(frame, bg=Theme.COLOR_PANEL)
        frame_stock_bajo.pack(fill=tk.X, pady=(0, 25))

        label_stock_bajo = tk.Label(frame_stock_bajo, text="⚠️ Productos Críticos - Requieren Atención",
                                    font=Theme.FONT_SUBTITLE,
                                    bg=Theme.COLOR_PANEL,
                                    fg=Theme.COLOR_TEXT)
        label_stock_bajo.pack(anchor="w", padx=20, pady=(15, 10))

        # Treeview para productos con stock bajo
        frame_tree = tk.Frame(frame_stock_bajo, bg=Theme.COLOR_PANEL)
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        scroll_y = tk.Scrollbar(frame_tree)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_stock_bajo = ttk.Treeview(frame_tree, columns=("codigo", "nombre", "stock", "minimo", "categoria"),
                                           show="headings", yscrollcommand=scroll_y.set, height=6)

        self.tree_stock_bajo.heading("codigo", text="Código")
        self.tree_stock_bajo.heading("nombre", text="Nombre")
        self.tree_stock_bajo.heading("stock", text="Stock")
        self.tree_stock_bajo.heading("minimo", text="Mínimo")
        self.tree_stock_bajo.heading("categoria", text="Categoría")

        self.tree_stock_bajo.column("codigo", width=100)
        self.tree_stock_bajo.column("nombre", width=250)
        self.tree_stock_bajo.column("stock", width=80)
        self.tree_stock_bajo.column("minimo", width=80)
        self.tree_stock_bajo.column("categoria", width=150)

        self.tree_stock_bajo.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.tree_stock_bajo.yview)

        # Configurar scrolling con mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # === PRODUCTOS PRÓXIMOS A VENCER ===
        frame_vencimiento = tk.Frame(frame, bg=self.theme_manager.get_color('panel'))
        frame_vencimiento.pack(fill=tk.X, pady=(0, 25))

        label_vencimiento = tk.Label(frame_vencimiento, text="⏰ Productos Próximos a Vencer",
                                    font=Theme.FONT_SUBTITLE,
                                    bg=self.theme_manager.get_color('panel'),
                                    fg=self.theme_manager.get_color('text'))
        label_vencimiento.pack(anchor="w", padx=20, pady=(15, 10))

        # Treeview para productos próximos a vencer
        frame_tree_venc = tk.Frame(frame_vencimiento, bg=self.theme_manager.get_color('panel'))
        frame_tree_venc.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        scroll_y_venc = tk.Scrollbar(frame_tree_venc)
        scroll_y_venc.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_vencimiento = ttk.Treeview(frame_tree_venc,
                                            columns=("codigo", "nombre", "fecha_venc", "dias_restantes", "stock"),
                                            show="headings", yscrollcommand=scroll_y_venc.set, height=6)

        self.tree_vencimiento.heading("codigo", text="Código")
        self.tree_vencimiento.heading("nombre", text="Nombre")
        self.tree_vencimiento.heading("fecha_venc", text="Fecha Vencimiento")
        self.tree_vencimiento.heading("dias_restantes", text="Días Restantes")
        self.tree_vencimiento.heading("stock", text="Stock")

        self.tree_vencimiento.column("codigo", width=100)
        self.tree_vencimiento.column("nombre", width=250)
        self.tree_vencimiento.column("fecha_venc", width=150)
        self.tree_vencimiento.column("dias_restantes", width=120)
        self.tree_vencimiento.column("stock", width=80)

        self.tree_vencimiento.pack(fill=tk.BOTH, expand=True)
        scroll_y_venc.config(command=self.tree_vencimiento.yview)

    def crear_tarjeta_stat(self, parent, titulo, valor, color):
        """Crea una tarjeta de estadística estilo macOS con esquinas redondeadas"""
        # Contenedor con padding
        container = tk.Frame(parent, bg=Theme.COLOR_BG)
        container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)

        # Simular sombra con un frame gris claro ligeramente desplazado
        shadow_frame = tk.Frame(container, bg="#E5E5EA")
        shadow_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.98)

        # Tarjeta principal con fondo blanco
        card_frame = tk.Frame(container, bg=Theme.COLOR_PANEL, relief=tk.FLAT, borderwidth=0)
        card_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Barra lateral izquierda de color (delgada)
        color_bar = tk.Frame(card_frame, bg=color, width=4)
        color_bar.pack(side=tk.LEFT, fill=tk.Y)

        # Contenido
        content = tk.Frame(card_frame, bg=Theme.COLOR_PANEL)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=12)

        # Título pequeño en gris
        label_titulo = tk.Label(content, text=titulo,
                               font=("Segoe UI", 9),
                               bg=Theme.COLOR_PANEL,
                               fg=Theme.COLOR_MUTED)
        label_titulo.pack(anchor='w', pady=(0, 4))

        # Valor grande y destacado
        label_valor = tk.Label(content, text=valor,
                              font=("Segoe UI", 20, "bold"),
                              bg=Theme.COLOR_PANEL,
                              fg=Theme.COLOR_TEXT)
        label_valor.pack(anchor='w')

        return label_valor

    def crear_boton(self, parent, texto, comando, color_bg, color_fg="white"):
        """Crea un botón con estilo macOS y efectos hover"""
        btn = tk.Button(parent,
                       text=texto,
                       command=comando,
                       bg=color_bg,
                       fg=color_fg,
                       font=Theme.FONT_BUTTON,
                       relief=tk.FLAT,
                       padx=24,
                       pady=12,
                       cursor="hand2",
                       borderwidth=0,
                       highlightthickness=0,
                       activebackground=self._oscurecer_color(color_bg),
                       activeforeground=color_fg)

        # Efectos hover
        def on_enter(e):
            btn['background'] = self._oscurecer_color(color_bg)

        def on_leave(e):
            btn['background'] = color_bg

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def _oscurecer_color(self, hex_color):
        """Oscurece un color hex en un 10% para efecto hover"""
        # Remover el #
        hex_color = hex_color.lstrip('#')
        # Convertir a RGB
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Oscurecer 10%
        r = int(r * 0.85)
        g = int(g * 0.85)
        b = int(b * 0.85)
        # Convertir de vuelta a hex
        return f'#{r:02x}{g:02x}{b:02x}'

    def configurar_treeview_alternado(self, tree):
        """Configura un Treeview con filas alternadas usando colores dinámicos"""
        odd_color = self.theme_manager.get_color('tree_odd_row')
        even_color = self.theme_manager.get_color('tree_even_row')
        text_color = Theme.COLOR_TEXT
        tree.tag_configure('oddrow', background=odd_color, foreground=text_color)
        tree.tag_configure('evenrow', background=even_color, foreground=text_color)

    def actualizar_colores_tablas(self):
        """Actualiza los colores de todas las tablas cuando cambia el tema"""
        # Lista de todas las tablas del sistema
        tablas = []

        # Verificar si las tablas existen antes de añadirlas
        if hasattr(self, 'tree_stock_bajo'):
            tablas.append(self.tree_stock_bajo)
        if hasattr(self, 'tree_vencimiento'):
            tablas.append(self.tree_vencimiento)
        if hasattr(self, 'tree_productos'):
            tablas.append(self.tree_productos)
        if hasattr(self, 'tree_proveedores'):
            tablas.append(self.tree_proveedores)
        if hasattr(self, 'tree_pedidos'):
            tablas.append(self.tree_pedidos)
        if hasattr(self, 'tree_movimientos'):
            tablas.append(self.tree_movimientos)

        # Reconfigurar colores de cada tabla
        for tabla in tablas:
            self.configurar_treeview_alternado(tabla)

    def cargar_dashboard(self):
        """Carga los datos del dashboard con proyecciones IA"""
        # Total productos
        productos = self.producto_model.obtener_todos()
        self.card_total_productos.config(text=str(len(productos)))

        # Productos con stock bajo
        productos_stock_bajo = self.producto_model.obtener_productos_stock_bajo()
        self.card_stock_bajo.config(text=str(len(productos_stock_bajo)))

        # Total pedidos automáticos pendientes
        pedidos = self.pedido_model.obtener_todos(solo_pendientes=True)
        self.card_pedidos.config(text=str(len(pedidos)))

        # Valor total del inventario
        valor_total = sum(p[6] * p[7] for p in productos if p[6] and p[7])  # precio_venta * stock
        self.card_valor_total.config(text=f"${valor_total:,.2f}")

        # Generar gráfica de categorías y proyecciones IA
        self.actualizar_grafica_categorias(productos)
        self.actualizar_proyecciones_ia(productos, productos_stock_bajo)

        # Cargar productos con stock bajo en la tabla
        self.tree_stock_bajo.delete(*self.tree_stock_bajo.get_children())
        self.configurar_treeview_alternado(self.tree_stock_bajo)

        for idx, producto in enumerate(productos_stock_bajo):
            categoria = producto[3] if producto[3] else "Sin categoría"

            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_stock_bajo.insert("", "end", values=(
                producto[1],  # codigo
                producto[2],  # nombre
                producto[7],  # stock_actual
                producto[8],  # stock_minimo
                categoria     # categoria
            ), tags=(tag,))

        # Cargar productos próximos a vencer en la tabla
        self.tree_vencimiento.delete(*self.tree_vencimiento.get_children())
        self.configurar_treeview_alternado(self.tree_vencimiento)

        productos_vencimiento = self.producto_model.obtener_productos_proximos_vencer(30)  # Próximos 30 días

        for idx, producto in enumerate(productos_vencimiento):
            dias_restantes = self.producto_model.calcular_dias_hasta_vencimiento(producto)

            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_vencimiento.insert("", "end", values=(
                producto[1],  # codigo
                producto[2],  # nombre
                producto[14] if len(producto) > 14 else "N/A",  # fecha_vencimiento
                f"{dias_restantes} días" if dias_restantes is not None else "N/A",
                producto[7]   # stock_actual
            ), tags=(tag,))

    def agrupar_categoria(self, categoria):
        """Agrupa categorías individuales en grupos más amplios para simplificar el dashboard"""
        if not categoria:
            return "Otros"

        categoria_lower = categoria.lower()

        # Mapeo de palabras clave a grupos amplios
        mapeo_grupos = {
            'Lácteos': ['leche', 'yogurt', 'queso', 'mantequilla', 'crema', 'lácteo', 'lacteo'],
            'Bebidas': ['coca', 'pepsi', 'gaseosa', 'refresco', 'jugo', 'agua', 'bebida', 'té', 'te', 'café', 'cafe', 'energizante'],
            'Snacks': ['papa', 'galleta', 'chocolate', 'caramelo', 'dulce', 'snack', 'golosina', 'chizito', 'doritos'],
            'Abarrotes': ['arroz', 'fideo', 'pasta', 'aceite', 'azúcar', 'azucar', 'sal', 'harina', 'conserva', 'atún', 'atun', 'menestra'],
            'Limpieza': ['detergente', 'jabón', 'jabon', 'limpiador', 'cloro', 'lejía', 'lejia', 'limpiavidrio', 'desinfectante'],
            'Cuidado Personal': ['shampoo', 'champú', 'champu', 'pasta dental', 'cepillo', 'jabón de tocador', 'desodorante', 'crema dental'],
            'Panadería': ['pan', 'tostada', 'bizcocho', 'pastel', 'panadería', 'panaderia'],
            'Carnes': ['carne', 'pollo', 'res', 'cerdo', 'embutido', 'salchicha', 'jamón', 'jamon'],
            'Frutas y Verduras': ['fruta', 'verdura', 'vegetal', 'manzana', 'plátano', 'platano', 'tomate', 'lechuga', 'zanahoria'],
            'Congelados': ['helado', 'congelado', 'ice cream']
        }

        # Buscar coincidencia en el mapeo
        for grupo, palabras_clave in mapeo_grupos.items():
            for palabra in palabras_clave:
                if palabra in categoria_lower:
                    return grupo

        # Si no encuentra coincidencia, usar la categoría original si es corta, sino "Otros"
        return categoria if len(categoria) < 20 else "Otros"

    def actualizar_grafica_categorias(self, productos):
        """Genera gráfica de productos por categoría con tema dinámico"""
        # Limpiar frame anterior
        for widget in self.frame_grafica_categorias.winfo_children():
            widget.destroy()

        # Contar productos por categoría AGRUPADA
        categorias = {}
        for p in productos:
            cat_original = p[3] if p[3] else "Sin categoría"
            cat_agrupada = self.agrupar_categoria(cat_original)
            categorias[cat_agrupada] = categorias.get(cat_agrupada, 0) + 1

        if not categorias:
            # Mostrar mensaje si no hay datos
            label = tk.Label(self.frame_grafica_categorias,
                           text="No hay datos para mostrar",
                           font=Theme.FONT_BASE,
                           bg=Theme.COLOR_PANEL,
                           fg=Theme.COLOR_MUTED)
            label.pack(expand=True)
            return

        # Crear figura de matplotlib con tema
        bg_color = self.theme_manager.get_color('chart_bg')
        text_color = self.theme_manager.get_color('text')

        fig = Figure(figsize=(5, 4), dpi=100, facecolor=bg_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)

        # Título del gráfico
        ax.set_title('Distribución por Grupos de Categorías',
                    fontsize=12,
                    color=text_color,
                    pad=15,
                    weight='semibold')

        # Colores del tema
        colores = self.theme_manager.get_chart_colors()

        # Crear gráfica de pastel
        wedges, texts, autotexts = ax.pie(categorias.values(),
                                           labels=categorias.keys(),
                                           autopct='%1.1f%%',
                                           startangle=90,
                                           colors=colores[:len(categorias)],
                                           textprops={'color': text_color})

        # Estilo de texto
        for text in texts:
            text.set_fontsize(10)
            text.set_color(text_color)

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_weight('bold')

        ax.axis('equal')

        # Integrar con tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica_categorias)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def actualizar_proyecciones_ia(self, productos, productos_stock_bajo):
        """Genera proyecciones estadísticas con IA basado en la base de datos"""
        # Limpiar frame anterior
        for widget in self.frame_proyecciones.winfo_children():
            widget.destroy()

        # Crear canvas con scroll para proyecciones
        canvas_proy = tk.Canvas(self.frame_proyecciones, bg=Theme.COLOR_PANEL, highlightthickness=0)
        scrollbar_proy = ttk.Scrollbar(self.frame_proyecciones, orient="vertical", command=canvas_proy.yview)
        frame_proy_scroll = tk.Frame(canvas_proy, bg=Theme.COLOR_PANEL)

        frame_proy_scroll.bind(
            "<Configure>",
            lambda e: canvas_proy.configure(scrollregion=canvas_proy.bbox("all"))
        )

        canvas_proy.create_window((0, 0), window=frame_proy_scroll, anchor="nw")
        canvas_proy.configure(yscrollcommand=scrollbar_proy.set)

        canvas_proy.pack(side="left", fill="both", expand=True)
        scrollbar_proy.pack(side="right", fill="y")

        # === ANÁLISIS CON IA ===
        ai_assistant = AIAssistant()

        # 1. Productos que se agotarán pronto
        # Colores adaptativos según tema
        if self.theme_manager.is_dark():
            bg_warning = "#4A3800"
            fg_warning = "#FFD60A"
        else:
            bg_warning = "#FFF3CD"
            fg_warning = "#856404"

        frame_agotamiento = tk.Frame(frame_proy_scroll, bg=bg_warning, relief=tk.FLAT)
        frame_agotamiento.pack(fill=tk.X, padx=10, pady=(10, 10))

        tk.Label(frame_agotamiento, text="⚠️ SE AGOTARÁN PRONTO",
                font=("Segoe UI Semibold", 11),
                bg=bg_warning, fg=fg_warning).pack(anchor="w", padx=10, pady=(8, 5))

        productos_agotarse = []
        for p in productos:
            if p[7] > 0:  # Si tiene stock
                # Analizar movimientos de los últimos 30 días
                movimientos = self.movimiento_model.obtener_por_producto(p[0])
                salidas_30_dias = [m for m in movimientos if m[3] == 'SALIDA']

                if salidas_30_dias:
                    total_salidas = sum(m[2] for m in salidas_30_dias)
                    ventas_diarias = total_salidas / 30

                    if ventas_diarias > 0:
                        dias_restantes = p[7] / ventas_diarias

                        # Si se agotará en menos de 7 días
                        if dias_restantes < 7:
                            productos_agotarse.append((p[2], dias_restantes, ventas_diarias))

        if productos_agotarse:
            productos_agotarse.sort(key=lambda x: x[1])  # Ordenar por días restantes
            for nombre, dias, ventas_dia in productos_agotarse[:5]:
                tk.Label(frame_agotamiento,
                        text=f"• {nombre}: ~{dias:.1f} días ({ventas_dia:.1f} und/día)",
                        font=Theme.FONT_BASE,
                        bg=bg_warning, fg=fg_warning).pack(anchor="w", padx=20, pady=2)
        else:
            fg_success = Theme.COLOR_SUCCESS
            tk.Label(frame_agotamiento, text="✓ Ningún producto en riesgo inmediato",
                    font=Theme.FONT_BASE,
                    bg=bg_warning, fg=fg_success).pack(anchor="w", padx=20, pady=5)

        frame_agotamiento.pack_configure(pady=(0, 5))

        # 2. Recomendaciones de pedido
        if self.theme_manager.is_dark():
            bg_info = "#0D3A52"
            fg_info = "#5AC8FA"
        else:
            bg_info = "#D1ECF1"
            fg_info = "#0C5460"

        frame_recomendaciones = tk.Frame(frame_proy_scroll, bg=bg_info, relief=tk.FLAT)
        frame_recomendaciones.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_recomendaciones, text="💡 RECOMENDACIONES INTELIGENTES",
                font=("Segoe UI Semibold", 11),
                bg=bg_info, fg=fg_info).pack(anchor="w", padx=10, pady=(8, 5))

        # Analizar productos con stock bajo y calcular cantidad sugerida
        recomendaciones = []
        for p in productos_stock_bajo[:5]:  # Top 5 críticos
            stock_actual = p[7]
            stock_minimo = p[8]
            stock_maximo = p[9]

            # Calcular cantidad sugerida básica
            cantidad_sugerida = int((stock_maximo - stock_actual) * 0.7)

            # Obtener velocidad de ventas
            movimientos = self.movimiento_model.obtener_por_producto(p[0])
            salidas = [m for m in movimientos if m[3] == 'SALIDA']

            if salidas:
                total_salidas = sum(m[2] for m in salidas[-10:])  # Últimas 10 salidas
                promedio_salida = total_salidas / min(len(salidas), 10)

                # Ajustar por velocidad
                if promedio_salida > 10:
                    cantidad_sugerida = int(cantidad_sugerida * 1.3)  # +30% si es rápido
                    velocidad = "Alta rotación"
                elif promedio_salida > 5:
                    velocidad = "Rotación media"
                else:
                    cantidad_sugerida = int(cantidad_sugerida * 0.7)  # -30% si es lento
                    velocidad = "Baja rotación"

                recomendaciones.append((p[2], cantidad_sugerida, velocidad))

        if recomendaciones:
            for nombre, cantidad, velocidad in recomendaciones:
                tk.Label(frame_recomendaciones,
                        text=f"• {nombre}: Pedir {cantidad} unidades ({velocidad})",
                        font=Theme.FONT_BASE,
                        bg=bg_info, fg=fg_info).pack(anchor="w", padx=20, pady=2)
        else:
            tk.Label(frame_recomendaciones, text="✓ Stock en niveles óptimos",
                    font=Theme.FONT_BASE,
                    bg=bg_info, fg=Theme.COLOR_SUCCESS).pack(anchor="w", padx=20, pady=5)

        frame_recomendaciones.pack_configure(pady=5)

        # 3. Tendencias detectadas
        if self.theme_manager.is_dark():
            bg_success = "#1A3D2E"
            fg_success_text = "#30D158"
        else:
            bg_success = "#D4EDDA"
            fg_success_text = "#155724"

        frame_tendencias = tk.Frame(frame_proy_scroll, bg=bg_success, relief=tk.FLAT)
        frame_tendencias.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_tendencias, text="📈 TENDENCIAS DETECTADAS",
                font=("Segoe UI Semibold", 11),
                bg=bg_success, fg=fg_success_text).pack(anchor="w", padx=10, pady=(8, 5))

        # Analizar categorías con más movimiento
        categorias_movimiento = {}
        for p in productos:
            cat = p[3] if p[3] else "Sin categoría"
            movimientos = self.movimiento_model.obtener_por_producto(p[0])
            salidas = [m for m in movimientos if m[3] == 'SALIDA']
            categorias_movimiento[cat] = categorias_movimiento.get(cat, 0) + len(salidas)

        if categorias_movimiento:
            cat_top = sorted(categorias_movimiento.items(), key=lambda x: x[1], reverse=True)[:3]
            for cat, mov in cat_top:
                tk.Label(frame_tendencias,
                        text=f"• {cat}: {mov} movimientos registrados",
                        font=Theme.FONT_BASE,
                        bg=bg_success, fg=fg_success_text).pack(anchor="w", padx=20, pady=2)
        else:
            tk.Label(frame_tendencias, text="• Sin movimientos registrados aún",
                    font=Theme.FONT_BASE,
                    bg=bg_success, fg=Theme.COLOR_MUTED).pack(anchor="w", padx=20, pady=5)

        frame_tendencias.pack_configure(pady=(5, 10))

    # ==================== PRODUCTOS ====================
    def construir_productos(self):
        """Construye la pestaña de productos"""
        frame = tk.Frame(self.tab_productos, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Frame superior con búsqueda y botones
        frame_top = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_top.pack(fill=tk.X, pady=(0, 20))

        # Búsqueda con mejor contraste
        label_buscar = tk.Label(frame_top, text="🔍",
                               font=("Segoe UI", 14),
                               bg=Theme.COLOR_BG,
                               fg=Theme.COLOR_TEXT)
        label_buscar.pack(side=tk.LEFT, padx=(0, 8))

        self.entry_buscar_producto = tk.Entry(frame_top,
                                              font=Theme.FONT_BASE,
                                              width=35,
                                              relief=tk.FLAT,
                                              bg=Theme.COLOR_PANEL,
                                              fg=Theme.COLOR_TEXT,
                                              insertbackground=Theme.COLOR_PRIMARY,
                                              borderwidth=2,
                                              highlightthickness=2,
                                              highlightbackground="#D1D1D6",
                                              highlightcolor=Theme.COLOR_PRIMARY)
        self.entry_buscar_producto.pack(side=tk.LEFT, padx=(0, 15), ipady=8)
        self.entry_buscar_producto.bind('<KeyRelease>', lambda e: self.buscar_productos())

        # Placeholder text
        self.entry_buscar_producto.insert(0, "Buscar productos...")
        self.entry_buscar_producto.config(fg=Theme.COLOR_MUTED)

        def on_focus_in(e):
            if self.entry_buscar_producto.get() == "Buscar productos...":
                self.entry_buscar_producto.delete(0, tk.END)
                self.entry_buscar_producto.config(fg=Theme.COLOR_TEXT)

        def on_focus_out(e):
            if not self.entry_buscar_producto.get():
                self.entry_buscar_producto.insert(0, "Buscar productos...")
                self.entry_buscar_producto.config(fg=Theme.COLOR_MUTED)

        self.entry_buscar_producto.bind('<FocusIn>', on_focus_in)
        self.entry_buscar_producto.bind('<FocusOut>', on_focus_out)

        # Botones con iconos
        btn_nuevo = self.crear_boton(frame_top, "➕ Nuevo Producto",
                                     self.nuevo_producto,
                                     Theme.COLOR_SUCCESS)
        btn_nuevo.pack(side=tk.RIGHT, padx=5)

        btn_ia = self.crear_boton(frame_top, "🤖 Análisis IA",
                                 self.analisis_ia_producto,
                                 Theme.COLOR_SECONDARY)
        btn_ia.pack(side=tk.RIGHT, padx=5)

        btn_analisis_detallado = self.crear_boton(frame_top, "📊 Análisis Detallado",
                                                  self.mostrar_analisis_detallado,
                                                  "#FF9F0A")  # Color accent
        btn_analisis_detallado.pack(side=tk.RIGHT, padx=5)

        btn_actualizar = self.crear_boton(frame_top, "⟳ Actualizar",
                                          self.cargar_productos,
                                          Theme.COLOR_PRIMARY)
        btn_actualizar.pack(side=tk.RIGHT, padx=5)

        # Tabla de productos
        frame_tree = tk.Frame(frame, bg=Theme.COLOR_PANEL)
        frame_tree.pack(fill=tk.BOTH, expand=True)

        scroll_y = tk.Scrollbar(frame_tree)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_x = tk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree_productos = ttk.Treeview(frame_tree,
                                          columns=("id", "codigo", "nombre", "categoria",
                                                  "precio_compra", "precio_venta", "stock",
                                                  "minimo", "maximo"),
                                          show="headings",
                                          yscrollcommand=scroll_y.set,
                                          xscrollcommand=scroll_x.set)

        self.tree_productos.heading("id", text="ID")
        self.tree_productos.heading("codigo", text="Código")
        self.tree_productos.heading("nombre", text="Nombre")
        self.tree_productos.heading("categoria", text="Categoría")
        self.tree_productos.heading("precio_compra", text="P. Compra")
        self.tree_productos.heading("precio_venta", text="P. Venta")
        self.tree_productos.heading("stock", text="Stock")
        self.tree_productos.heading("minimo", text="Mínimo")
        self.tree_productos.heading("maximo", text="Máximo")

        self.tree_productos.column("id", width=50)
        self.tree_productos.column("codigo", width=100)
        self.tree_productos.column("nombre", width=200)
        self.tree_productos.column("categoria", width=120)
        self.tree_productos.column("precio_compra", width=100)
        self.tree_productos.column("precio_venta", width=100)
        self.tree_productos.column("stock", width=80)
        self.tree_productos.column("minimo", width=80)
        self.tree_productos.column("maximo", width=80)

        self.tree_productos.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.tree_productos.yview)
        scroll_x.config(command=self.tree_productos.xview)

        # Frame inferior con botones de acciones
        frame_bottom = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_bottom.pack(fill=tk.X, pady=(15, 0))

        btn_editar = self.crear_boton(frame_bottom, "✏️ Editar",
                                      self.editar_producto,
                                      Theme.COLOR_PRIMARY)
        btn_editar.pack(side=tk.LEFT, padx=5)

        btn_eliminar = self.crear_boton(frame_bottom, "🗑️ Eliminar",
                                        self.eliminar_producto,
                                        Theme.COLOR_DANGER)
        btn_eliminar.pack(side=tk.LEFT, padx=5)

        btn_entrada = self.crear_boton(frame_bottom, "📥 Entrada Stock",
                                       self.entrada_stock,
                                       Theme.COLOR_SUCCESS)
        btn_entrada.pack(side=tk.LEFT, padx=5)

        btn_salida = self.crear_boton(frame_bottom, "📤 Salida Stock",
                                      self.salida_stock,
                                      Theme.COLOR_WARNING,
                                      Theme.COLOR_TEXT)
        btn_salida.pack(side=tk.LEFT, padx=5)

        # Configurar doble clic para editar
        self.tree_productos.bind("<Double-1>", lambda e: self.editar_producto())

        # Cargar productos
        self.cargar_productos()

    def cargar_productos(self):
        """Carga todos los productos en la tabla"""
        self.tree_productos.delete(*self.tree_productos.get_children())
        self.configurar_treeview_alternado(self.tree_productos)
        productos = self.producto_model.obtener_todos()

        for idx, producto in enumerate(productos):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_productos.insert("", "end", values=(
                producto[0],  # id
                producto[1],  # codigo
                producto[2],  # nombre
                producto[4],  # categoria
                f"${float(producto[5]):.2f}" if producto[5] else "$0.00",  # precio_compra
                f"${float(producto[6]):.2f}" if producto[6] else "$0.00",  # precio_venta
                producto[7],  # stock_actual
                producto[8],  # stock_minimo
                producto[9]   # stock_maximo
            ), tags=(tag,))

    def buscar_productos(self):
        """Busca productos por código o nombre"""
        termino = self.entry_buscar_producto.get()

        # Ignorar si es el placeholder
        if not termino or termino == "Buscar productos...":
            self.cargar_productos()
            return

        self.tree_productos.delete(*self.tree_productos.get_children())
        self.configurar_treeview_alternado(self.tree_productos)
        productos = self.producto_model.buscar(termino)

        for idx, producto in enumerate(productos):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_productos.insert("", "end", values=(
                producto[0],
                producto[1],
                producto[2],
                producto[4],
                f"${float(producto[5]):.2f}" if producto[5] else "$0.00",
                f"${float(producto[6]):.2f}" if producto[6] else "$0.00",
                producto[7],
                producto[8],
                producto[9]
            ), tags=(tag,))

    def nuevo_producto(self):
        """Abre ventana para crear nuevo producto"""
        FormularioProducto(self.root, self, None)

    def editar_producto(self):
        """Edita el producto seleccionado"""
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return

        item = self.tree_productos.item(seleccion[0])
        producto_id = item['values'][0]

        FormularioProducto(self.root, self, producto_id)

    def analisis_ia_producto(self):
        """Muestra el análisis de IA del producto seleccionado"""
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para analizar")
            return

        item = self.tree_productos.item(seleccion[0])
        producto_id = item['values'][0]

        VentanaAnalisisIA(self.root, self, producto_id)

    def mostrar_analisis_detallado(self):
        """Muestra el análisis detallado del producto con información de fechas y rotación"""
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para analizar")
            return

        item = self.tree_productos.item(seleccion[0])
        producto_id = item['values'][0]

        VentanaAnalisisProducto(self.root, self, producto_id)

    def eliminar_producto(self):
        """Elimina el producto seleccionado"""
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return

        item = self.tree_productos.item(seleccion[0])
        producto_id = item['values'][0]
        producto_nombre = item['values'][2]

        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el producto '{producto_nombre}'?"):
            self.producto_model.eliminar(producto_id)
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
            self.cargar_productos()
            self.cargar_dashboard()

    def entrada_stock(self):
        """Registra entrada de stock"""
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return

        item = self.tree_productos.item(seleccion[0])
        producto_id = item['values'][0]
        producto_nombre = item['values'][2]
        stock_actual = item['values'][6]

        DialogoMovimientoStock(self.root, self, producto_id, producto_nombre, stock_actual, "ENTRADA")

    def salida_stock(self):
        """Registra salida de stock"""
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return

        item = self.tree_productos.item(seleccion[0])
        producto_id = item['values'][0]
        producto_nombre = item['values'][2]
        stock_actual = item['values'][6]

        DialogoMovimientoStock(self.root, self, producto_id, producto_nombre, stock_actual, "SALIDA")

    # ==================== PROVEEDORES ====================
    def construir_proveedores(self):
        """Construye la pestaña de proveedores"""
        frame = tk.Frame(self.tab_proveedores, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Frame superior con botones
        frame_top = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_top.pack(fill=tk.X, pady=(0, 20))

        btn_nuevo = self.crear_boton(frame_top, "➕ Nuevo Proveedor",
                                     self.nuevo_proveedor,
                                     Theme.COLOR_SUCCESS)
        btn_nuevo.pack(side=tk.RIGHT, padx=5)

        btn_actualizar = self.crear_boton(frame_top, "⟳ Actualizar",
                                          self.cargar_proveedores,
                                          Theme.COLOR_PRIMARY)
        btn_actualizar.pack(side=tk.RIGHT, padx=5)

        # Tabla de proveedores
        frame_tree = tk.Frame(frame, bg=Theme.COLOR_PANEL)
        frame_tree.pack(fill=tk.BOTH, expand=True)

        scroll_y = tk.Scrollbar(frame_tree)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_proveedores = ttk.Treeview(frame_tree,
                                            columns=("id", "nombre", "contacto", "telefono",
                                                    "email", "direccion"),
                                            show="headings",
                                            yscrollcommand=scroll_y.set)

        self.tree_proveedores.heading("id", text="ID")
        self.tree_proveedores.heading("nombre", text="Nombre")
        self.tree_proveedores.heading("contacto", text="Contacto")
        self.tree_proveedores.heading("telefono", text="Teléfono")
        self.tree_proveedores.heading("email", text="Email")
        self.tree_proveedores.heading("direccion", text="Dirección")

        self.tree_proveedores.column("id", width=50)
        self.tree_proveedores.column("nombre", width=200)
        self.tree_proveedores.column("contacto", width=150)
        self.tree_proveedores.column("telefono", width=120)
        self.tree_proveedores.column("email", width=200)
        self.tree_proveedores.column("direccion", width=250)

        self.tree_proveedores.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.tree_proveedores.yview)

        # Frame inferior con botones
        frame_bottom = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_bottom.pack(fill=tk.X, pady=(15, 0))

        btn_editar = self.crear_boton(frame_bottom, "✏️ Editar",
                                      self.editar_proveedor,
                                      Theme.COLOR_PRIMARY)
        btn_editar.pack(side=tk.LEFT, padx=5)

        btn_eliminar = self.crear_boton(frame_bottom, "🗑️ Eliminar",
                                        self.eliminar_proveedor,
                                        Theme.COLOR_DANGER)
        btn_eliminar.pack(side=tk.LEFT, padx=5)

        btn_ver_productos = self.crear_boton(frame_bottom, "📦 Ver Productos",
                                             self.ver_productos_proveedor,
                                             Theme.COLOR_SECONDARY)
        btn_ver_productos.pack(side=tk.LEFT, padx=5)

        # Configurar doble clic para editar
        self.tree_proveedores.bind("<Double-1>", lambda e: self.editar_proveedor())

        # Cargar proveedores
        self.cargar_proveedores()

    def cargar_proveedores(self):
        """Carga todos los proveedores en la tabla"""
        self.tree_proveedores.delete(*self.tree_proveedores.get_children())
        self.configurar_treeview_alternado(self.tree_proveedores)
        proveedores = self.proveedor_model.obtener_todos()

        for idx, proveedor in enumerate(proveedores):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_proveedores.insert("", "end", values=(
                proveedor[0],  # id
                proveedor[1],  # nombre
                proveedor[2],  # contacto
                proveedor[3],  # telefono
                proveedor[4],  # email
                proveedor[5]   # direccion
            ), tags=(tag,))

    def nuevo_proveedor(self):
        """Abre ventana para crear nuevo proveedor"""
        FormularioProveedor(self.root, self, None)

    def editar_proveedor(self):
        """Edita el proveedor seleccionado"""
        seleccion = self.tree_proveedores.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor para editar")
            return

        item = self.tree_proveedores.item(seleccion[0])
        proveedor_id = item['values'][0]

        FormularioProveedor(self.root, self, proveedor_id)

    def eliminar_proveedor(self):
        """Elimina el proveedor seleccionado"""
        seleccion = self.tree_proveedores.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor para eliminar")
            return

        item = self.tree_proveedores.item(seleccion[0])
        proveedor_id = item['values'][0]
        proveedor_nombre = item['values'][1]

        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el proveedor '{proveedor_nombre}'?"):
            self.proveedor_model.eliminar(proveedor_id)
            messagebox.showinfo("Éxito", "Proveedor eliminado correctamente")
            self.cargar_proveedores()
            self.cargar_dashboard()

    def ver_productos_proveedor(self):
        """Muestra los productos del proveedor seleccionado"""
        seleccion = self.tree_proveedores.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor")
            return

        item = self.tree_proveedores.item(seleccion[0])
        proveedor_id = item['values'][0]
        proveedor_nombre = item['values'][1]

        # Obtener productos del proveedor
        productos = [p for p in self.producto_model.obtener_todos() if p[10] == proveedor_id]

        # Crear ventana
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Productos de {proveedor_nombre}")
        ventana.geometry("800x500")
        ventana.configure(bg=Theme.COLOR_BG)

        frame = tk.Frame(ventana, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        label = tk.Label(frame, text=f"Productos de {proveedor_nombre}",
                        font=Theme.FONT_SUBTITLE,
                        bg=Theme.COLOR_BG,
                        fg=Theme.COLOR_TEXT)
        label.pack(pady=(0, 20))

        # Tabla
        tree = ttk.Treeview(frame, columns=("codigo", "nombre", "stock", "precio"),
                           show="headings")

        tree.heading("codigo", text="Código")
        tree.heading("nombre", text="Nombre")
        tree.heading("stock", text="Stock")
        tree.heading("precio", text="Precio Venta")

        tree.column("codigo", width=100)
        tree.column("nombre", width=300)
        tree.column("stock", width=100)
        tree.column("precio", width=120)

        self.configurar_treeview_alternado(tree)

        for idx, producto in enumerate(productos):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=(
                producto[1],
                producto[2],
                producto[7],
                f"${float(producto[5]):.2f}" if producto[5] else "$0.00"
            ), tags=(tag,))

        tree.pack(fill=tk.BOTH, expand=True)

    # ==================== PEDIDOS AUTOMÁTICOS ====================
    def construir_pedidos(self):
        """Construye la pestaña de pedidos automáticos"""
        frame = tk.Frame(self.tab_pedidos, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Frame superior con título y botones
        frame_top = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_top.pack(fill=tk.X, pady=(0, 20))

        label = tk.Label(frame_top, text="🤖 Pedidos Automáticos al Proveedor",
                        font=Theme.FONT_SUBTITLE,
                        bg=Theme.COLOR_BG,
                        fg=Theme.COLOR_TEXT)
        label.pack(side=tk.LEFT)

        # Badge con cantidad de pendientes
        self.label_pedidos_pendientes = tk.Label(frame_top,
                                                 text="0 pendientes",
                                                 font=Theme.FONT_LABEL,
                                                 bg=Theme.COLOR_WARNING,
                                                 fg=Theme.COLOR_TEXT,
                                                 padx=12,
                                                 pady=6)
        self.label_pedidos_pendientes.pack(side=tk.LEFT, padx=15)

        btn_actualizar = self.crear_boton(frame_top, "⟳ Actualizar",
                                          self.cargar_pedidos,
                                          Theme.COLOR_PRIMARY)
        btn_actualizar.pack(side=tk.RIGHT)

        # Descripción
        desc = tk.Label(frame,
                       text="Los pedidos se generan automáticamente cuando un producto alcanza su stock mínimo",
                       font=("Segoe UI", 9),
                       bg=Theme.COLOR_BG,
                       fg=Theme.COLOR_MUTED)
        desc.pack(anchor="w", pady=(0, 15))

        # Tabla de pedidos
        frame_tree = tk.Frame(frame, bg=Theme.COLOR_PANEL)
        frame_tree.pack(fill=tk.BOTH, expand=True)

        scroll_y = tk.Scrollbar(frame_tree)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_pedidos = ttk.Treeview(frame_tree,
                                         columns=("id", "producto", "proveedor", "cantidad",
                                                 "estado", "fecha"),
                                         show="headings",
                                         yscrollcommand=scroll_y.set)

        self.tree_pedidos.heading("id", text="ID")
        self.tree_pedidos.heading("producto", text="Producto")
        self.tree_pedidos.heading("proveedor", text="Proveedor")
        self.tree_pedidos.heading("cantidad", text="Cantidad")
        self.tree_pedidos.heading("estado", text="Estado")
        self.tree_pedidos.heading("fecha", text="Fecha Pedido")

        self.tree_pedidos.column("id", width=50)
        self.tree_pedidos.column("producto", width=250)
        self.tree_pedidos.column("proveedor", width=200)
        self.tree_pedidos.column("cantidad", width=100)
        self.tree_pedidos.column("estado", width=120)
        self.tree_pedidos.column("fecha", width=150)

        self.tree_pedidos.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.tree_pedidos.yview)

        # Frame inferior con botones
        frame_bottom = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_bottom.pack(fill=tk.X, pady=(15, 0))

        btn_procesar = self.crear_boton(frame_bottom, "✓ Marcar Procesado",
                                        self.procesar_pedido,
                                        Theme.COLOR_PRIMARY)
        btn_procesar.pack(side=tk.LEFT, padx=5)

        btn_recibido = self.crear_boton(frame_bottom, "📥 Marcar Recibido",
                                        self.recibir_pedido,
                                        Theme.COLOR_SUCCESS)
        btn_recibido.pack(side=tk.LEFT, padx=5)

        btn_cancelar = self.crear_boton(frame_bottom, "✕ Cancelar Pedido",
                                        self.cancelar_pedido,
                                        Theme.COLOR_DANGER)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        # Cargar pedidos
        self.cargar_pedidos()

    def cargar_pedidos(self):
        """Carga todos los pedidos en la tabla"""
        self.tree_pedidos.delete(*self.tree_pedidos.get_children())
        self.configurar_treeview_alternado(self.tree_pedidos)
        pedidos = self.pedido_model.obtener_todos()

        # Actualizar badge de pendientes
        pendientes = self.pedido_model.contar_pendientes()
        self.label_pedidos_pendientes.config(text=f"{pendientes} pendientes")

        for idx, pedido in enumerate(pedidos):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_pedidos.insert("", "end", values=(
                pedido[0],  # id
                pedido[8],  # producto_nombre
                pedido[10], # proveedor_nombre
                pedido[3],  # cantidad_solicitada
                pedido[4],  # estado
                pedido[5]   # fecha_pedido
            ), tags=(tag,))

    def procesar_pedido(self):
        """Marca un pedido como procesado"""
        seleccion = self.tree_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un pedido")
            return

        item = self.tree_pedidos.item(seleccion[0])
        pedido_id = item['values'][0]
        estado = item['values'][4]

        if estado != "PENDIENTE":
            messagebox.showwarning("Advertencia", "Solo se pueden procesar pedidos pendientes")
            return

        if messagebox.askyesno("Confirmar", "¿Marcar este pedido como procesado?\n\nEsto indica que ya enviaste el pedido al proveedor."):
            self.pedido_model.marcar_procesado(pedido_id)
            messagebox.showinfo("Éxito", "Pedido marcado como procesado")
            self.cargar_pedidos()

    def recibir_pedido(self):
        """Marca un pedido como recibido y actualiza el stock"""
        seleccion = self.tree_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un pedido")
            return

        item = self.tree_pedidos.item(seleccion[0])
        pedido_id = item['values'][0]
        producto = item['values'][1]
        cantidad = item['values'][3]
        estado = item['values'][4]

        if estado == "RECIBIDO":
            messagebox.showwarning("Advertencia", "Este pedido ya fue recibido")
            return

        if messagebox.askyesno("Confirmar",
                              f"¿Confirmar recepción del pedido?\n\n"
                              f"Producto: {producto}\n"
                              f"Cantidad: {cantidad} unidades\n\n"
                              f"El stock se actualizará automáticamente."):
            self.pedido_model.marcar_recibido(pedido_id)
            messagebox.showinfo("Éxito",
                              f"Pedido recibido y stock actualizado\n\n"
                              f"+{cantidad} unidades agregadas al inventario")
            self.cargar_pedidos()
            self.cargar_dashboard()
            self.cargar_productos()

    def cancelar_pedido(self):
        """Cancela un pedido"""
        seleccion = self.tree_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un pedido")
            return

        item = self.tree_pedidos.item(seleccion[0])
        pedido_id = item['values'][0]
        estado = item['values'][4]

        if estado not in ["PENDIENTE", "PROCESADO"]:
            messagebox.showwarning("Advertencia", "No se puede cancelar este pedido")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de cancelar este pedido?"):
            self.pedido_model.cancelar(pedido_id)
            messagebox.showinfo("Éxito", "Pedido cancelado")
            self.cargar_pedidos()

    # ==================== MOVIMIENTOS ====================
    def construir_movimientos(self):
        """Construye la pestaña de movimientos"""
        frame = tk.Frame(self.tab_movimientos, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Frame superior
        frame_top = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_top.pack(fill=tk.X, pady=(0, 20))

        label = tk.Label(frame_top, text="Historial de Movimientos",
                        font=Theme.FONT_SUBTITLE,
                        bg=Theme.COLOR_BG,
                        fg=Theme.COLOR_TEXT)
        label.pack(side=tk.LEFT)

        btn_actualizar = self.crear_boton(frame_top, "⟳ Actualizar",
                                          self.cargar_movimientos,
                                          Theme.COLOR_PRIMARY)
        btn_actualizar.pack(side=tk.RIGHT)

        # Tabla de movimientos
        frame_tree = tk.Frame(frame, bg=Theme.COLOR_PANEL)
        frame_tree.pack(fill=tk.BOTH, expand=True)

        scroll_y = tk.Scrollbar(frame_tree)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_movimientos = ttk.Treeview(frame_tree,
                                            columns=("id", "producto", "tipo", "cantidad",
                                                    "motivo", "usuario", "fecha"),
                                            show="headings",
                                            yscrollcommand=scroll_y.set)

        self.tree_movimientos.heading("id", text="ID")
        self.tree_movimientos.heading("producto", text="Producto")
        self.tree_movimientos.heading("tipo", text="Tipo")
        self.tree_movimientos.heading("cantidad", text="Cantidad")
        self.tree_movimientos.heading("motivo", text="Motivo")
        self.tree_movimientos.heading("usuario", text="Usuario")
        self.tree_movimientos.heading("fecha", text="Fecha")

        self.tree_movimientos.column("id", width=50)
        self.tree_movimientos.column("producto", width=200)
        self.tree_movimientos.column("tipo", width=100)
        self.tree_movimientos.column("cantidad", width=100)
        self.tree_movimientos.column("motivo", width=200)
        self.tree_movimientos.column("usuario", width=120)
        self.tree_movimientos.column("fecha", width=180)

        self.tree_movimientos.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.tree_movimientos.yview)

        # Cargar movimientos
        self.cargar_movimientos()

    def cargar_movimientos(self):
        """Carga todos los movimientos en la tabla"""
        self.tree_movimientos.delete(*self.tree_movimientos.get_children())
        self.configurar_treeview_alternado(self.tree_movimientos)
        movimientos = self.movimiento_model.obtener_todos()

        for idx, movimiento in enumerate(movimientos):
            producto = self.producto_model.obtener_por_id(movimiento[1])
            producto_nombre = producto[2] if producto else "Desconocido"

            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_movimientos.insert("", "end", values=(
                movimiento[0],  # id
                producto_nombre,
                movimiento[2],  # tipo
                movimiento[3],  # cantidad
                movimiento[4],  # motivo
                movimiento[5],  # usuario
                movimiento[6]   # fecha
            ), tags=(tag,))

    # ==================== REPORTES ====================
    def construir_reportes(self):
        """Construye la pestaña de reportes"""
        frame = tk.Frame(self.tab_reportes, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        label = tk.Label(frame, text="Reportes y Estadísticas",
                        font=Theme.FONT_TITLE,
                        bg=Theme.COLOR_BG,
                        fg=Theme.COLOR_TEXT)
        label.pack(pady=30)

        # Botones de reportes
        frame_botones = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_botones.pack(pady=20, padx=100)

        btn_reporte_stock = self.crear_boton(frame_botones, "📊 Reporte de Stock",
                                             self.generar_reporte_stock,
                                             Theme.COLOR_PRIMARY)
        btn_reporte_stock.config(font=("Segoe UI Semibold", 12), padx=40, pady=18)
        btn_reporte_stock.pack(pady=12, fill=tk.X)

        btn_reporte_valor = self.crear_boton(frame_botones, "💰 Reporte de Valor de Inventario",
                                             self.generar_reporte_valor,
                                             Theme.COLOR_SUCCESS)
        btn_reporte_valor.config(font=("Segoe UI Semibold", 12), padx=40, pady=18)
        btn_reporte_valor.pack(pady=12, fill=tk.X)

        btn_reporte_movimientos = self.crear_boton(frame_botones, "📋 Reporte de Movimientos",
                                                   self.generar_reporte_movimientos,
                                                   Theme.COLOR_SECONDARY)
        btn_reporte_movimientos.config(font=("Segoe UI Semibold", 12), padx=40, pady=18)
        btn_reporte_movimientos.pack(pady=12, fill=tk.X)

    def generar_reporte_stock(self):
        """Genera reporte de stock"""
        productos = self.producto_model.obtener_todos()

        ventana = tk.Toplevel(self.root)
        ventana.title("Reporte de Stock")
        ventana.geometry("900x600")
        ventana.configure(bg=Theme.COLOR_BG)

        frame = tk.Frame(ventana, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        label = tk.Label(frame, text="Reporte de Stock",
                        font=Theme.FONT_SUBTITLE,
                        bg=Theme.COLOR_BG,
                        fg=Theme.COLOR_TEXT)
        label.pack(pady=(0, 20))

        # Tabla
        tree = ttk.Treeview(frame, columns=("codigo", "nombre", "stock", "minimo", "maximo", "estado"),
                           show="headings")

        tree.heading("codigo", text="Código")
        tree.heading("nombre", text="Nombre")
        tree.heading("stock", text="Stock Actual")
        tree.heading("minimo", text="Stock Mínimo")
        tree.heading("maximo", text="Stock Máximo")
        tree.heading("estado", text="Estado")

        self.configurar_treeview_alternado(tree)

        for idx, producto in enumerate(productos):
            stock = producto[7]
            minimo = producto[8]
            maximo = producto[9]

            if stock <= minimo:
                estado = "CRÍTICO"
            elif stock >= maximo:
                estado = "ALTO"
            else:
                estado = "NORMAL"

            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=(
                producto[1],
                producto[2],
                stock,
                minimo,
                maximo,
                estado
            ), tags=(tag,))

        tree.pack(fill=tk.BOTH, expand=True)

    def generar_reporte_valor(self):
        """Genera reporte de valor de inventario"""
        productos = self.producto_model.obtener_todos()

        valor_total_compra = sum(p[4] * p[7] for p in productos if p[4] and p[7])
        valor_total_venta = sum(p[5] * p[7] for p in productos if p[5] and p[7])
        ganancia_potencial = valor_total_venta - valor_total_compra

        mensaje = f"""
REPORTE DE VALOR DE INVENTARIO
=====================================

Total de Productos: {len(productos)}

Valor Total de Compra: ${valor_total_compra:,.2f}
Valor Total de Venta: ${valor_total_venta:,.2f}
Ganancia Potencial: ${ganancia_potencial:,.2f}

Margen de Ganancia: {(ganancia_potencial/valor_total_compra*100):.2f}%
        """

        messagebox.showinfo("Reporte de Valor", mensaje)

    def generar_reporte_movimientos(self):
        """Genera reporte de movimientos"""
        movimientos = self.movimiento_model.obtener_todos()

        entradas = sum(1 for m in movimientos if m[2] == "ENTRADA")
        salidas = sum(1 for m in movimientos if m[2] == "SALIDA")

        mensaje = f"""
REPORTE DE MOVIMIENTOS
=====================================

Total de Movimientos: {len(movimientos)}

Entradas: {entradas}
Salidas: {salidas}

Últimos 10 movimientos mostrados en la pestaña Movimientos
        """

        messagebox.showinfo("Reporte de Movimientos", mensaje)

    # ==================== CONFIGURACIÓN ====================
    def construir_configuracion(self):
        """Construye la pestaña de configuración"""
        from webhook_client import WebhookClient

        frame = tk.Frame(self.tab_configuracion, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Título
        label_titulo = tk.Label(frame, text="⚙️ Configuración de n8n e IA",
                               font=Theme.FONT_TITLE,
                               bg=Theme.COLOR_BG,
                               fg=Theme.COLOR_TEXT)
        label_titulo.pack(pady=(0, 30))

        # Panel principal de configuración
        panel = tk.Frame(frame, bg=Theme.COLOR_PANEL)
        panel.pack(fill=tk.BOTH, expand=True)

        # Frame interior con padding
        frame_config = tk.Frame(panel, bg=Theme.COLOR_PANEL)
        frame_config.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        # ===== Webhook URL =====
        label_webhook = tk.Label(frame_config, text="🔗 URL del Webhook de n8n",
                                font=Theme.FONT_SUBTITLE,
                                bg=Theme.COLOR_PANEL,
                                fg=Theme.COLOR_TEXT)
        label_webhook.pack(anchor=tk.W, pady=(0, 10))

        desc_webhook = tk.Label(frame_config,
                               text="Ingresa la URL del webhook de n8n para enviar eventos de stock bajo y notificaciones",
                               font=Theme.FONT_LABEL,
                               bg=Theme.COLOR_PANEL,
                               fg=Theme.COLOR_MUTED,
                               wraplength=700,
                               justify=tk.LEFT)
        desc_webhook.pack(anchor=tk.W, pady=(0, 10))

        self.entry_webhook_url = tk.Entry(frame_config,
                                          font=Theme.FONT_BASE,
                                          bg="white",
                                          fg=Theme.COLOR_TEXT,
                                          relief=tk.FLAT,
                                          borderwidth=1,
                                          highlightthickness=1,
                                          highlightbackground=Theme.SHADOW_COLOR,
                                          highlightcolor=Theme.COLOR_PRIMARY)
        self.entry_webhook_url.pack(fill=tk.X, pady=(0, 10), ipady=8)

        # Cargar valor actual
        webhook_client = WebhookClient()
        url_actual = webhook_client.get_config('n8n_webhook_url', '')
        if url_actual:
            self.entry_webhook_url.insert(0, url_actual)
        else:
            self.entry_webhook_url.insert(0, "https://tu-n8n.com/webhook/inventario")
            self.entry_webhook_url.config(fg=Theme.COLOR_MUTED)

        # Placeholder behavior
        def on_focus_in_webhook(e):
            if self.entry_webhook_url.get() == "https://tu-n8n.com/webhook/inventario":
                self.entry_webhook_url.delete(0, tk.END)
                self.entry_webhook_url.config(fg=Theme.COLOR_TEXT)

        def on_focus_out_webhook(e):
            if not self.entry_webhook_url.get():
                self.entry_webhook_url.insert(0, "https://tu-n8n.com/webhook/inventario")
                self.entry_webhook_url.config(fg=Theme.COLOR_MUTED)

        self.entry_webhook_url.bind("<FocusIn>", on_focus_in_webhook)
        self.entry_webhook_url.bind("<FocusOut>", on_focus_out_webhook)

        # ===== Activar/Desactivar Notificaciones =====
        separator1 = tk.Frame(frame_config, bg=Theme.SHADOW_COLOR, height=1)
        separator1.pack(fill=tk.X, pady=30)

        label_notif = tk.Label(frame_config, text="🔔 Notificaciones Automáticas",
                              font=Theme.FONT_SUBTITLE,
                              bg=Theme.COLOR_PANEL,
                              fg=Theme.COLOR_TEXT)
        label_notif.pack(anchor=tk.W, pady=(0, 10))

        desc_notif = tk.Label(frame_config,
                             text="Activa o desactiva el envío automático de notificaciones cuando el stock esté bajo",
                             font=Theme.FONT_LABEL,
                             bg=Theme.COLOR_PANEL,
                             fg=Theme.COLOR_MUTED,
                             wraplength=700,
                             justify=tk.LEFT)
        desc_notif.pack(anchor=tk.W, pady=(0, 15))

        self.var_notificaciones = tk.BooleanVar()
        notif_activas = webhook_client.get_config('notificaciones_activas', 'true') == 'true'
        self.var_notificaciones.set(notif_activas)

        frame_toggle = tk.Frame(frame_config, bg=Theme.COLOR_PANEL)
        frame_toggle.pack(anchor=tk.W, pady=(0, 10))

        check_notif = tk.Checkbutton(frame_toggle,
                                     text="Activar notificaciones automáticas",
                                     variable=self.var_notificaciones,
                                     font=Theme.FONT_BASE,
                                     bg=Theme.COLOR_PANEL,
                                     fg=Theme.COLOR_TEXT,
                                     selectcolor="white",
                                     activebackground=Theme.COLOR_PANEL,
                                     activeforeground=Theme.COLOR_TEXT,
                                     cursor="hand2")
        check_notif.pack(side=tk.LEFT)

        # ===== Botones de Acción =====
        separator2 = tk.Frame(frame_config, bg=Theme.SHADOW_COLOR, height=1)
        separator2.pack(fill=tk.X, pady=30)

        frame_botones = tk.Frame(frame_config, bg=Theme.COLOR_PANEL)
        frame_botones.pack(fill=tk.X, pady=(0, 20))

        btn_guardar = self.crear_boton(frame_botones, "💾 Guardar Configuración",
                                       self.guardar_configuracion,
                                       Theme.COLOR_SUCCESS)
        btn_guardar.pack(side=tk.LEFT, padx=(0, 15))

        btn_probar = self.crear_boton(frame_botones, "🧪 Probar Conexión",
                                     self.probar_webhook,
                                     Theme.COLOR_PRIMARY)
        btn_probar.pack(side=tk.LEFT, padx=(0, 15))

        btn_abrir_guia = self.crear_boton(frame_botones, "📖 Ver Guía de Integración",
                                         self.abrir_guia_n8n,
                                         Theme.COLOR_SECONDARY)
        btn_abrir_guia.pack(side=tk.LEFT)

        # ===== Estado Actual =====
        separator3 = tk.Frame(frame_config, bg=Theme.SHADOW_COLOR, height=1)
        separator3.pack(fill=tk.X, pady=30)

        label_estado = tk.Label(frame_config, text="📊 Estado del Sistema",
                               font=Theme.FONT_SUBTITLE,
                               bg=Theme.COLOR_PANEL,
                               fg=Theme.COLOR_TEXT)
        label_estado.pack(anchor=tk.W, pady=(0, 15))

        # Panel de estado
        panel_estado = tk.Frame(frame_config, bg="#F9F9FB")
        panel_estado.pack(fill=tk.X, pady=(0, 20))

        frame_estado_inner = tk.Frame(panel_estado, bg="#F9F9FB")
        frame_estado_inner.pack(fill=tk.X, padx=20, pady=20)

        self.label_estado_webhook = tk.Label(frame_estado_inner,
                                             text="🔴 Webhook: No configurado",
                                             font=Theme.FONT_BASE,
                                             bg="#F9F9FB",
                                             fg=Theme.COLOR_TEXT,
                                             anchor=tk.W)
        self.label_estado_webhook.pack(anchor=tk.W, pady=5)

        self.label_estado_notif = tk.Label(frame_estado_inner,
                                           text=f"{'🟢' if notif_activas else '🔴'} Notificaciones: {'Activas' if notif_activas else 'Desactivadas'}",
                                           font=Theme.FONT_BASE,
                                           bg="#F9F9FB",
                                           fg=Theme.COLOR_TEXT,
                                           anchor=tk.W)
        self.label_estado_notif.pack(anchor=tk.W, pady=5)

        # Actualizar estado inicial
        if url_actual and url_actual != "https://tu-n8n.com/webhook/inventario":
            self.label_estado_webhook.config(text=f"🟢 Webhook: Configurado")

    def guardar_configuracion(self):
        """Guarda la configuración de n8n"""
        from webhook_client import WebhookClient

        url = self.entry_webhook_url.get().strip()
        if url == "https://tu-n8n.com/webhook/inventario":
            url = ""

        if url and not url.startswith("http"):
            messagebox.showerror("Error", "La URL debe comenzar con http:// o https://")
            return

        notif_activas = self.var_notificaciones.get()

        webhook_client = WebhookClient()
        webhook_client.set_config('n8n_webhook_url', url)
        webhook_client.set_config('notificaciones_activas', 'true' if notif_activas else 'false')

        # Actualizar estado visual
        if url:
            self.label_estado_webhook.config(text="🟢 Webhook: Configurado")
        else:
            self.label_estado_webhook.config(text="🔴 Webhook: No configurado")

        self.label_estado_notif.config(
            text=f"{'🟢' if notif_activas else '🔴'} Notificaciones: {'Activas' if notif_activas else 'Desactivadas'}"
        )

        messagebox.showinfo("Éxito", "✅ Configuración guardada correctamente")

    def probar_webhook(self):
        """Prueba la conexión con el webhook de n8n"""
        import requests

        url = self.entry_webhook_url.get().strip()
        if url == "https://tu-n8n.com/webhook/inventario" or not url:
            messagebox.showwarning("Advertencia", "Debes configurar una URL de webhook primero")
            return

        try:
            # Enviar webhook de prueba
            payload = {
                'evento': 'test',
                'mensaje': 'Prueba de conexión desde el Sistema de Inventario',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                messagebox.showinfo("Éxito",
                                   "✅ Conexión exitosa con n8n!\n\n"
                                   "El webhook está funcionando correctamente.")
            else:
                messagebox.showwarning("Advertencia",
                                      f"⚠️ El servidor respondió con código {response.status_code}\n\n"
                                      f"Verifica tu configuración de n8n.")
        except requests.exceptions.Timeout:
            messagebox.showerror("Error",
                               "❌ Timeout: El servidor no respondió a tiempo\n\n"
                               "Verifica que la URL sea correcta y que n8n esté corriendo.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error",
                               "❌ Error de conexión\n\n"
                               "No se pudo conectar con el servidor.\n"
                               "Verifica la URL y que n8n esté accesible.")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error inesperado:\n\n{str(e)}")

    def abrir_guia_n8n(self):
        """Abre la guía de integración con n8n"""
        import os
        import sys

        guia_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "INTEGRACION_N8N.md")

        if os.path.exists(guia_path):
            try:
                if sys.platform == "win32":
                    os.startfile(guia_path)
                elif sys.platform == "darwin":
                    os.system(f"open '{guia_path}'")
                else:
                    os.system(f"xdg-open '{guia_path}'")
                messagebox.showinfo("Guía", "📖 Abriendo guía de integración...")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la guía:\n{str(e)}")
        else:
            messagebox.showerror("Error", "No se encontró el archivo INTEGRACION_N8N.md")

    # ==================== ALERTAS ====================
    def mostrar_alertas(self):
        """Muestra las alertas no leídas"""
        alertas = self.alerta_model.obtener_no_leidas()

        if not alertas:
            messagebox.showinfo("Alertas", "No hay alertas pendientes")
            return

        self.notification_manager.mostrar_ventana_alertas(alertas)
        self.actualizar_contador_alertas()
        self.cargar_dashboard()

    def actualizar_contador_alertas(self):
        """Actualiza el contador de alertas en el botón"""
        cantidad = self.alerta_model.contar_no_leidas()
        self.btn_alertas.config(text=f"🔔 Alertas ({cantidad})")

        # Cambiar color según cantidad de alertas
        if cantidad > 0:
            self.btn_alertas.config(bg=Theme.COLOR_DANGER, fg="white")
        else:
            self.btn_alertas.config(bg=Theme.COLOR_WARNING, fg=Theme.COLOR_TEXT)

    def cerrar_aplicacion(self):
        """Cierra la aplicación correctamente"""
        try:
            print("[SISTEMA] Cerrando aplicacion...")

            # Detener tareas automáticas
            if hasattr(self, 'tareas_automaticas'):
                detener_tareas_automaticas()
                print("[SISTEMA] Tareas automaticas detenidas")

            # Cerrar ventana
            self.root.destroy()
            print("[SISTEMA] [OK] Aplicacion cerrada correctamente")

        except Exception as e:
            print(f"[SISTEMA] Error al cerrar: {e}")
            self.root.destroy()

# ==================== FORMULARIOS ====================

class DialogoMovimientoStock:
    """Diálogo moderno para registrar entrada o salida de stock"""
    def __init__(self, parent, app, producto_id, producto_nombre, stock_actual, tipo):
        self.app = app
        self.producto_id = producto_id
        self.producto_nombre = producto_nombre
        self.stock_actual = stock_actual
        self.tipo = tipo  # "ENTRADA" o "SALIDA"
        self.producto_model = Producto()

        self.ventana = tk.Toplevel(parent)
        titulo = "📥 Entrada de Stock" if tipo == "ENTRADA" else "📤 Salida de Stock"
        self.ventana.title(titulo)
        self.ventana.geometry("550x450")
        self.ventana.configure(bg=Theme.COLOR_BG)

        self.crear_interfaz()

        self.ventana.transient(parent)
        self.ventana.grab_set()

        # Focus en el campo de cantidad
        self.entry_cantidad.focus()

    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        frame = tk.Frame(self.ventana, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        # Header con color según tipo
        color_header = Theme.COLOR_SUCCESS if self.tipo == "ENTRADA" else Theme.COLOR_WARNING
        header_frame = tk.Frame(frame, bg=color_header)
        header_frame.pack(fill=tk.X, pady=(0, 25))

        header_inner = tk.Frame(header_frame, bg=color_header)
        header_inner.pack(fill=tk.X, padx=25, pady=20)

        icono = "📥" if self.tipo == "ENTRADA" else "📤"
        texto_tipo = "Entrada de Stock" if self.tipo == "ENTRADA" else "Salida de Stock"

        tk.Label(header_inner, text=f"{icono} {texto_tipo}",
                font=("Segoe UI Semibold", 16),
                bg=color_header,
                fg="white").pack()

        # Información del producto
        info_frame = tk.Frame(frame, bg=Theme.COLOR_PANEL)
        info_frame.pack(fill=tk.X, pady=(0, 25))

        info_inner = tk.Frame(info_frame, bg=Theme.COLOR_PANEL)
        info_inner.pack(fill=tk.X, padx=25, pady=20)

        tk.Label(info_inner, text="📦 Producto:",
                font=("Segoe UI Semibold", 11),
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_MUTED).pack(anchor=tk.W)

        tk.Label(info_inner, text=self.producto_nombre,
                font=("Segoe UI", 14),
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT).pack(anchor=tk.W, pady=(5, 10))

        tk.Label(info_inner, text=f"Stock actual: {self.stock_actual} unidades",
                font=Theme.FONT_BASE,
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_MUTED).pack(anchor=tk.W)

        # Entrada config
        entry_config = {
            'font': ("Segoe UI", 12),
            'relief': tk.FLAT,
            'bg': Theme.COLOR_PANEL,
            'fg': Theme.COLOR_TEXT,
            'insertbackground': Theme.COLOR_PRIMARY,
            'borderwidth': 1,
            'highlightthickness': 2,
            'highlightbackground': Theme.SHADOW_COLOR,
            'highlightcolor': Theme.COLOR_PRIMARY
        }

        # Cantidad
        tk.Label(frame, text="Cantidad:",
                font=("Segoe UI Semibold", 11),
                bg=Theme.COLOR_BG,
                fg=Theme.COLOR_TEXT).pack(anchor=tk.W, pady=(0, 8))

        self.entry_cantidad = tk.Entry(frame, **entry_config)
        self.entry_cantidad.pack(fill=tk.X, ipady=10, pady=(0, 20))

        # Validación para que solo acepte números
        vcmd = (self.ventana.register(self.validar_numero), '%P')
        self.entry_cantidad.config(validate='key', validatecommand=vcmd)

        # Motivo
        tk.Label(frame, text="Motivo:",
                font=("Segoe UI Semibold", 11),
                bg=Theme.COLOR_BG,
                fg=Theme.COLOR_TEXT).pack(anchor=tk.W, pady=(0, 8))

        self.entry_motivo = tk.Entry(frame, **entry_config)
        self.entry_motivo.pack(fill=tk.X, ipady=10, pady=(0, 25))

        # Botones
        botones_frame = tk.Frame(frame, bg=Theme.COLOR_BG)
        botones_frame.pack()

        btn_guardar = tk.Button(botones_frame,
                               text=f"✓ Registrar {texto_tipo}",
                               command=self.guardar,
                               bg=Theme.COLOR_SUCCESS, fg="white",
                               font=("Segoe UI Semibold", 12),
                               relief=tk.FLAT, padx=40, pady=16,
                               cursor="hand2",
                               borderwidth=0,
                               highlightthickness=0)
        btn_guardar.pack(side=tk.LEFT, padx=(0, 10))

        # Hover effect
        def on_enter(e):
            btn_guardar['background'] = '#28A03F'
        def on_leave(e):
            btn_guardar['background'] = Theme.COLOR_SUCCESS
        btn_guardar.bind("<Enter>", on_enter)
        btn_guardar.bind("<Leave>", on_leave)

        btn_cancelar = tk.Button(botones_frame, text="Cancelar",
                                command=self.ventana.destroy,
                                bg="#8E8E93", fg="white",
                                font=("Segoe UI Semibold", 12),
                                relief=tk.FLAT, padx=40, pady=16,
                                cursor="hand2",
                                borderwidth=0,
                                highlightthickness=0)
        btn_cancelar.pack(side=tk.LEFT)

        # Hover effect
        def on_enter_cancel(e):
            btn_cancelar['background'] = '#6E6E73'
        def on_leave_cancel(e):
            btn_cancelar['background'] = '#8E8E93'
        btn_cancelar.bind("<Enter>", on_enter_cancel)
        btn_cancelar.bind("<Leave>", on_leave_cancel)

        # Enter para guardar
        self.ventana.bind('<Return>', lambda e: self.guardar())

    def validar_numero(self, valor):
        """Valida que solo se ingresen números"""
        if valor == "":
            return True
        try:
            int(valor)
            return True
        except ValueError:
            return False

    def guardar(self):
        """Guarda el movimiento de stock"""
        try:
            cantidad_str = self.entry_cantidad.get().strip()
            motivo = self.entry_motivo.get().strip()

            if not cantidad_str:
                messagebox.showwarning("Advertencia", "Ingrese la cantidad")
                self.entry_cantidad.focus()
                return

            if not motivo:
                messagebox.showwarning("Advertencia", "Ingrese el motivo del movimiento")
                self.entry_motivo.focus()
                return

            cantidad = int(cantidad_str)

            if cantidad <= 0:
                messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a 0")
                self.entry_cantidad.focus()
                return

            # Validar stock suficiente para salidas
            if self.tipo == "SALIDA" and cantidad > self.stock_actual:
                messagebox.showerror("Error",
                                   f"Stock insuficiente\n\n"
                                   f"Stock actual: {self.stock_actual} unidades\n"
                                   f"Cantidad solicitada: {cantidad} unidades")
                self.entry_cantidad.focus()
                return

            # Registrar movimiento
            resultado = self.producto_model.actualizar_stock(
                self.producto_id,
                cantidad,
                self.tipo,
                motivo,
                "Usuario"
            )

            if resultado:
                tipo_texto = "entrada" if self.tipo == "ENTRADA" else "salida"
                nuevo_stock = self.stock_actual + cantidad if self.tipo == "ENTRADA" else self.stock_actual - cantidad

                messagebox.showinfo("Éxito",
                                  f"✅ {tipo_texto.capitalize()} registrada correctamente\n\n"
                                  f"Cantidad: {cantidad} unidades\n"
                                  f"Stock anterior: {self.stock_actual}\n"
                                  f"Stock nuevo: {nuevo_stock}")

                self.app.cargar_productos()
                self.app.cargar_dashboard()
                self.ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo registrar el movimiento")

        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")


class FormularioProducto:
    def __init__(self, parent, app, producto_id):
        self.app = app
        self.producto_id = producto_id
        self.producto_model = Producto()
        self.proveedor_model = Proveedor()

        self.ventana = tk.Toplevel(parent)
        titulo = "Nuevo Producto" if producto_id is None else "Editar Producto"
        self.ventana.title(titulo)
        self.ventana.geometry("600x750")
        self.ventana.configure(bg=Theme.COLOR_BG)

        self.crear_formulario()

        if producto_id:
            self.cargar_datos()

        self.ventana.transient(parent)
        self.ventana.grab_set()

    def crear_formulario(self):
        """Crea el formulario de producto con scroll"""
        # Canvas para scroll
        canvas = tk.Canvas(self.ventana, bg=Theme.COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.ventana, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Theme.COLOR_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=580)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame principal dentro del scroll
        frame = tk.Frame(scrollable_frame, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=35, pady=35)

        # Estilo de entrada
        entry_config = {
            'font': Theme.FONT_BASE,
            'relief': tk.FLAT,
            'bg': Theme.COLOR_PANEL,
            'fg': Theme.COLOR_TEXT,
            'insertbackground': Theme.COLOR_TEXT,
            'borderwidth': 1,
            'highlightthickness': 1,
            'highlightbackground': Theme.SHADOW_COLOR,
            'highlightcolor': Theme.COLOR_PRIMARY
        }

        # Código
        tk.Label(frame, text="Código:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_codigo = tk.Entry(frame, **entry_config)
        self.entry_codigo.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Nombre
        tk.Label(frame, text="Nombre:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_nombre = tk.Entry(frame, **entry_config)
        self.entry_nombre.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Descripción
        tk.Label(frame, text="Descripción:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_descripcion = tk.Entry(frame, **entry_config)
        self.entry_descripcion.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Categoría
        tk.Label(frame, text="Categoría:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_categoria = tk.Entry(frame, **entry_config)
        self.entry_categoria.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Precio Compra
        tk.Label(frame, text="Precio de Compra:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_precio_compra = tk.Entry(frame, **entry_config)
        self.entry_precio_compra.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Precio Venta
        tk.Label(frame, text="Precio de Venta:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_precio_venta = tk.Entry(frame, **entry_config)
        self.entry_precio_venta.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Stock Actual
        tk.Label(frame, text="Stock Actual:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_stock_actual = tk.Entry(frame, **entry_config)
        self.entry_stock_actual.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Stock Mínimo
        tk.Label(frame, text="Stock Mínimo:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_stock_minimo = tk.Entry(frame, **entry_config)
        self.entry_stock_minimo.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Stock Máximo
        tk.Label(frame, text="Stock Máximo:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_stock_maximo = tk.Entry(frame, **entry_config)
        self.entry_stock_maximo.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Proveedor
        tk.Label(frame, text="Proveedor:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.combo_proveedor = ttk.Combobox(frame, font=Theme.FONT_BASE, state="readonly")
        self.cargar_proveedores()
        self.combo_proveedor.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Separador visual
        tk.Label(frame, text="─" * 60, font=("Segoe UI", 8), bg=Theme.COLOR_BG, fg=Theme.SHADOW_COLOR).pack(pady=10)
        tk.Label(frame, text="📅 Información de Fechas (Opcional)", font=("Segoe UI Semibold", 10),
                bg=Theme.COLOR_BG, fg=Theme.COLOR_PRIMARY).pack(anchor="w", pady=(0, 10))

        # Fecha de Ingreso
        tk.Label(frame, text="Fecha de Ingreso (YYYY-MM-DD):", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        fecha_frame_ingreso = tk.Frame(frame, bg=Theme.COLOR_BG)
        fecha_frame_ingreso.pack(fill=tk.X, pady=(5, 15))
        self.entry_fecha_ingreso = tk.Entry(fecha_frame_ingreso, **entry_config)
        self.entry_fecha_ingreso.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        btn_hoy_ingreso = tk.Button(fecha_frame_ingreso, text="Hoy", command=self.establecer_fecha_hoy_ingreso,
                                     bg=Theme.COLOR_PRIMARY, fg="white", font=("Segoe UI", 9),
                                     relief=tk.FLAT, padx=12, pady=6, cursor="hand2")
        btn_hoy_ingreso.pack(side=tk.LEFT, padx=(5, 0))

        # Fecha de Vencimiento
        tk.Label(frame, text="Fecha de Vencimiento (YYYY-MM-DD):", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        fecha_frame_venc = tk.Frame(frame, bg=Theme.COLOR_BG)
        fecha_frame_venc.pack(fill=tk.X, pady=(5, 15))
        self.entry_fecha_vencimiento = tk.Entry(fecha_frame_venc, **entry_config)
        self.entry_fecha_vencimiento.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        btn_limpiar_venc = tk.Button(fecha_frame_venc, text="Limpiar", command=lambda: self.entry_fecha_vencimiento.delete(0, tk.END),
                                      bg="#8E8E93", fg="white", font=("Segoe UI", 9),
                                      relief=tk.FLAT, padx=12, pady=6, cursor="hand2")
        btn_limpiar_venc.pack(side=tk.LEFT, padx=(5, 0))

        # Días de vida útil (informativo)
        tk.Label(frame, text="Días de Vida Útil (0 = no perecedero):", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_dias_vida_util = tk.Entry(frame, **entry_config)
        self.entry_dias_vida_util.pack(fill=tk.X, pady=(5, 25), ipady=6)

        # Botones grandes y llamativos
        frame_botones = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_botones.pack(pady=10)

        btn_guardar = tk.Button(frame_botones,
                               text="💾 Guardar" if self.producto_id is None else "✓ Actualizar",
                               command=self.guardar,
                               bg=Theme.COLOR_SUCCESS, fg="white",
                               font=("Segoe UI Semibold", 12),
                               relief=tk.FLAT, padx=40, pady=16,
                               cursor="hand2",
                               borderwidth=0,
                               highlightthickness=0)
        btn_guardar.pack(side=tk.LEFT, padx=10)

        # Efectos hover para botón guardar
        def on_enter_guardar(e):
            btn_guardar['background'] = '#28A03F'  # Más oscuro

        def on_leave_guardar(e):
            btn_guardar['background'] = Theme.COLOR_SUCCESS

        btn_guardar.bind("<Enter>", on_enter_guardar)
        btn_guardar.bind("<Leave>", on_leave_guardar)

        btn_cancelar = tk.Button(frame_botones, text="✕ Cancelar",
                                command=self.ventana.destroy,
                                bg="#8E8E93", fg="white",
                                font=("Segoe UI Semibold", 12),
                                relief=tk.FLAT, padx=40, pady=16,
                                cursor="hand2",
                                borderwidth=0,
                                highlightthickness=0)
        btn_cancelar.pack(side=tk.LEFT, padx=10)

        # Efectos hover para botón cancelar
        def on_enter_cancelar(e):
            btn_cancelar['background'] = '#6E6E73'  # Más oscuro

        def on_leave_cancelar(e):
            btn_cancelar['background'] = '#8E8E93'

        btn_cancelar.bind("<Enter>", on_enter_cancelar)
        btn_cancelar.bind("<Leave>", on_leave_cancelar)

    def establecer_fecha_hoy_ingreso(self):
        """Establece la fecha de hoy en el campo de fecha de ingreso"""
        from datetime import datetime
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        self.entry_fecha_ingreso.delete(0, tk.END)
        self.entry_fecha_ingreso.insert(0, fecha_hoy)

    def cargar_proveedores(self):
        """Carga los proveedores en el combobox"""
        proveedores = self.proveedor_model.obtener_todos()
        self.proveedores_dict = {f"{p[1]}": p[0] for p in proveedores}
        self.combo_proveedor['values'] = ["Sin proveedor"] + list(self.proveedores_dict.keys())
        self.combo_proveedor.current(0)

    def cargar_datos(self):
        """Carga los datos del producto a editar"""
        producto = self.producto_model.obtener_por_id(self.producto_id)

        if producto:
            self.entry_codigo.insert(0, producto[1])
            self.entry_nombre.insert(0, producto[2])
            self.entry_descripcion.insert(0, producto[3] or "")
            self.entry_categoria.insert(0, producto[4] or "")
            self.entry_precio_compra.insert(0, str(producto[5] or 0))
            self.entry_precio_venta.insert(0, str(producto[6] or 0))
            self.entry_stock_actual.insert(0, str(producto[7]))
            self.entry_stock_minimo.insert(0, str(producto[8]))
            self.entry_stock_maximo.insert(0, str(producto[9]))

            if producto[10]:
                proveedor = self.proveedor_model.obtener_por_id(producto[10])
                if proveedor:
                    self.combo_proveedor.set(proveedor[1])

            # Cargar nuevos campos de fecha
            if len(producto) > 13 and producto[13]:
                self.entry_fecha_ingreso.insert(0, producto[13])
            if len(producto) > 14 and producto[14]:
                self.entry_fecha_vencimiento.insert(0, producto[14])
            if len(producto) > 15 and producto[15]:
                self.entry_dias_vida_util.insert(0, str(producto[15]))

    def guardar(self):
        """Guarda el producto"""
        try:
            codigo = self.entry_codigo.get().strip()
            nombre = self.entry_nombre.get().strip()
            descripcion = self.entry_descripcion.get().strip()
            categoria = self.entry_categoria.get().strip()

            if not codigo or not nombre:
                messagebox.showwarning("Advertencia", "Código y Nombre son obligatorios")
                return

            precio_compra = float(self.entry_precio_compra.get() or 0)
            precio_venta = float(self.entry_precio_venta.get() or 0)
            stock_actual = int(self.entry_stock_actual.get() or 0)
            stock_minimo = int(self.entry_stock_minimo.get() or 10)
            stock_maximo = int(self.entry_stock_maximo.get() or 100)

            # Obtener proveedor_id correctamente
            proveedor_nombre = self.combo_proveedor.get()
            proveedor_id = None
            if proveedor_nombre and proveedor_nombre != "Sin proveedor":
                proveedor_id = self.proveedores_dict.get(proveedor_nombre)

            # Obtener nuevos campos de fecha
            fecha_ingreso = self.entry_fecha_ingreso.get().strip() or None
            fecha_vencimiento = self.entry_fecha_vencimiento.get().strip() or None
            dias_vida_util = int(self.entry_dias_vida_util.get() or 0)

            if self.producto_id is None:
                # Crear nuevo producto
                self.producto_model.crear(codigo, nombre, descripcion, categoria,
                                         precio_compra, precio_venta, stock_actual,
                                         stock_minimo, stock_maximo, proveedor_id,
                                         fecha_ingreso, fecha_vencimiento, dias_vida_util)
                messagebox.showinfo("Éxito", "✅ Producto creado correctamente")
            else:
                # Actualizar producto existente
                producto_anterior = self.producto_model.obtener_por_id(self.producto_id)
                stock_anterior = producto_anterior[7] if producto_anterior else stock_actual

                self.producto_model.actualizar(self.producto_id, codigo, nombre, descripcion,
                                              categoria, precio_compra, precio_venta,
                                              stock_actual, stock_minimo, stock_maximo, proveedor_id,
                                              fecha_ingreso, fecha_vencimiento, dias_vida_util)

                # Si cambió el stock, registrar el movimiento
                if stock_actual != stock_anterior:
                    diferencia = stock_actual - stock_anterior
                    if diferencia > 0:
                        self.producto_model.actualizar_stock(
                            self.producto_id, diferencia, "ENTRADA",
                            "Ajuste manual desde edición", "Usuario"
                        )
                    else:
                        self.producto_model.actualizar_stock(
                            self.producto_id, abs(diferencia), "SALIDA",
                            "Ajuste manual desde edición", "Usuario"
                        )

                messagebox.showinfo("Éxito", "✅ Producto actualizado correctamente")

            self.app.cargar_productos()
            self.app.cargar_dashboard()
            self.ventana.destroy()

        except ValueError as e:
            messagebox.showerror("Error", f"Error en los valores numéricos:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")


class FormularioProveedor:
    def __init__(self, parent, app, proveedor_id):
        self.app = app
        self.proveedor_id = proveedor_id
        self.proveedor_model = Proveedor()

        self.ventana = tk.Toplevel(parent)
        titulo = "Nuevo Proveedor" if proveedor_id is None else "Editar Proveedor"
        self.ventana.title(titulo)
        self.ventana.geometry("600x550")
        self.ventana.configure(bg=Theme.COLOR_BG)

        self.crear_formulario()

        if proveedor_id:
            self.cargar_datos()

        self.ventana.transient(parent)
        self.ventana.grab_set()

    def crear_formulario(self):
        """Crea el formulario de proveedor"""
        frame = tk.Frame(self.ventana, bg=Theme.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=35, pady=35)

        # Estilo de entrada
        entry_config = {
            'font': Theme.FONT_BASE,
            'relief': tk.FLAT,
            'bg': Theme.COLOR_PANEL,
            'fg': Theme.COLOR_TEXT,
            'insertbackground': Theme.COLOR_TEXT,
            'borderwidth': 1,
            'highlightthickness': 1,
            'highlightbackground': Theme.SHADOW_COLOR,
            'highlightcolor': Theme.COLOR_PRIMARY
        }

        # Nombre
        tk.Label(frame, text="Nombre:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_nombre = tk.Entry(frame, **entry_config)
        self.entry_nombre.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Contacto
        tk.Label(frame, text="Persona de Contacto:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_contacto = tk.Entry(frame, **entry_config)
        self.entry_contacto.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Teléfono
        tk.Label(frame, text="Teléfono:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_telefono = tk.Entry(frame, **entry_config)
        self.entry_telefono.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Email
        tk.Label(frame, text="Email:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_email = tk.Entry(frame, **entry_config)
        self.entry_email.pack(fill=tk.X, pady=(5, 15), ipady=6)

        # Dirección
        tk.Label(frame, text="Dirección:", font=Theme.FONT_LABEL, bg=Theme.COLOR_BG, fg=Theme.COLOR_TEXT).pack(anchor="w")
        self.entry_direccion = tk.Entry(frame, **entry_config)
        self.entry_direccion.pack(fill=tk.X, pady=(5, 25), ipady=6)

        # Botones grandes y llamativos
        frame_botones = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_botones.pack(pady=10)

        btn_guardar = tk.Button(frame_botones,
                               text="💾 Guardar" if self.proveedor_id is None else "✓ Actualizar",
                               command=self.guardar,
                               bg=Theme.COLOR_SUCCESS, fg="white",
                               font=("Segoe UI Semibold", 12),
                               relief=tk.FLAT, padx=40, pady=16,
                               cursor="hand2",
                               borderwidth=0,
                               highlightthickness=0)
        btn_guardar.pack(side=tk.LEFT, padx=10)

        # Efectos hover para botón guardar
        def on_enter_guardar(e):
            btn_guardar['background'] = '#28A03F'  # Más oscuro

        def on_leave_guardar(e):
            btn_guardar['background'] = Theme.COLOR_SUCCESS

        btn_guardar.bind("<Enter>", on_enter_guardar)
        btn_guardar.bind("<Leave>", on_leave_guardar)

        btn_cancelar = tk.Button(frame_botones, text="✕ Cancelar",
                                command=self.ventana.destroy,
                                bg="#8E8E93", fg="white",
                                font=("Segoe UI Semibold", 12),
                                relief=tk.FLAT, padx=40, pady=16,
                                cursor="hand2",
                                borderwidth=0,
                                highlightthickness=0)
        btn_cancelar.pack(side=tk.LEFT, padx=10)

        # Efectos hover para botón cancelar
        def on_enter_cancelar(e):
            btn_cancelar['background'] = '#6E6E73'  # Más oscuro

        def on_leave_cancelar(e):
            btn_cancelar['background'] = '#8E8E93'

        btn_cancelar.bind("<Enter>", on_enter_cancelar)
        btn_cancelar.bind("<Leave>", on_leave_cancelar)

    def cargar_datos(self):
        """Carga los datos del proveedor a editar"""
        proveedor = self.proveedor_model.obtener_por_id(self.proveedor_id)

        if proveedor:
            self.entry_nombre.insert(0, proveedor[1])
            self.entry_contacto.insert(0, proveedor[2] or "")
            self.entry_telefono.insert(0, proveedor[3] or "")
            self.entry_email.insert(0, proveedor[4] or "")
            self.entry_direccion.insert(0, proveedor[5] or "")

    def guardar(self):
        """Guarda el proveedor"""
        try:
            nombre = self.entry_nombre.get().strip()
            contacto = self.entry_contacto.get().strip()
            telefono = self.entry_telefono.get().strip()
            email = self.entry_email.get().strip()
            direccion = self.entry_direccion.get().strip()

            if not nombre:
                messagebox.showwarning("Advertencia", "El nombre es obligatorio")
                return

            if self.proveedor_id is None:
                self.proveedor_model.crear(nombre, contacto, telefono, email, direccion)
                messagebox.showinfo("Éxito", "✅ Proveedor creado correctamente")
            else:
                self.proveedor_model.actualizar(self.proveedor_id, nombre, contacto,
                                               telefono, email, direccion)
                messagebox.showinfo("Éxito", "✅ Proveedor actualizado correctamente")

            self.app.cargar_proveedores()
            self.app.cargar_dashboard()
            self.ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el proveedor:\n{str(e)}")


class VentanaAnalisisIA:
    """Ventana que muestra el análisis de IA de un producto - LA CARACTERÍSTICA ÚNICA DEL SISTEMA"""
    def __init__(self, parent, app, producto_id):
        self.app = app
        self.producto_id = producto_id
        self.ai_assistant = AIAssistant()

        self.ventana = tk.Toplevel(parent)
        self.ventana.title("🤖 Análisis Inteligente con IA")
        self.ventana.geometry("900x700")
        self.ventana.configure(bg=Theme.COLOR_BG)

        # Realizar análisis
        self.analisis = self.ai_assistant.analizar_producto(producto_id)

        if not self.analisis:
            messagebox.showerror("Error", "No se pudo analizar el producto")
            self.ventana.destroy()
            return

        self.crear_interfaz()

        self.ventana.transient(parent)
        self.ventana.grab_set()

    def crear_interfaz(self):
        """Crea la interfaz del análisis de IA"""
        # Frame principal con scroll
        main_canvas = tk.Canvas(self.ventana, bg=Theme.COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.ventana, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=Theme.COLOR_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = scrollable_frame
        frame_inner = tk.Frame(frame, bg=Theme.COLOR_BG)
        frame_inner.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # === HEADER ===
        header_frame = tk.Frame(frame_inner, bg=Theme.COLOR_PANEL)
        header_frame.pack(fill=tk.X, pady=(0, 25))

        header_inner = tk.Frame(header_frame, bg=Theme.COLOR_PANEL)
        header_inner.pack(fill=tk.X, padx=30, pady=25)

        tk.Label(header_inner, text="🤖 Análisis Inteligente con IA",
                font=("Segoe UI Semibold", 20),
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT).pack(anchor=tk.W)

        tk.Label(header_inner, text=self.analisis['producto']['nombre'],
                font=("Segoe UI", 14),
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_MUTED).pack(anchor=tk.W, pady=(5, 0))

        # === URGENCIA BADGE ===
        urgencia = self.analisis['sugerencia']['urgencia']
        colores_urgencia = {
            'CRÍTICA': Theme.COLOR_DANGER,
            'ALTA': Theme.COLOR_WARNING,
            'MEDIA': '#FFB341',  # Naranja
            'BAJA': Theme.COLOR_SUCCESS
        }

        urgencia_frame = tk.Frame(frame_inner, bg=colores_urgencia[urgencia])
        urgencia_frame.pack(fill=tk.X, pady=(0, 25))

        urgencia_inner = tk.Frame(urgencia_frame, bg=colores_urgencia[urgencia])
        urgencia_inner.pack(fill=tk.X, padx=30, pady=20)

        emoji_urgencia = {'CRÍTICA': '🚨', 'ALTA': '⚠️', 'MEDIA': '📊', 'BAJA': '✅'}
        tk.Label(urgencia_inner, text=f"{emoji_urgencia[urgencia]} URGENCIA: {urgencia}",
                font=("Segoe UI Semibold", 16),
                bg=colores_urgencia[urgencia],
                fg="white").pack()

        # === MÉTRICAS ===
        metricas_frame = tk.Frame(frame_inner, bg=Theme.COLOR_BG)
        metricas_frame.pack(fill=tk.X, pady=(0, 25))

        # Crear 3 columnas de métricas
        for i, (titulo, valor, subtitulo) in enumerate([
            ("Stock Actual", f"{self.analisis['producto']['stock_actual']}", f"Mínimo: {self.analisis['producto']['stock_minimo']}"),
            ("Ventas/Día", f"{self.analisis['analisis']['ventas_diarias_promedio']:.1f}", "Promedio últimos 30 días"),
            ("Días Restantes", f"{self.analisis['analisis']['dias_para_agotar']:.1f}", "Hasta agotarse")
        ]):
            metric_card = tk.Frame(metricas_frame, bg=Theme.COLOR_PANEL)
            metric_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8 if i == 1 else 0)

            metric_inner = tk.Frame(metric_card, bg=Theme.COLOR_PANEL)
            metric_inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

            tk.Label(metric_inner, text=titulo,
                    font=Theme.FONT_LABEL,
                    bg=Theme.COLOR_PANEL,
                    fg=Theme.COLOR_MUTED).pack()

            tk.Label(metric_inner, text=valor,
                    font=("Segoe UI Semibold", 24),
                    bg=Theme.COLOR_PANEL,
                    fg=Theme.COLOR_TEXT).pack(pady=(5, 0))

            tk.Label(metric_inner, text=subtitulo,
                    font=("Segoe UI", 9),
                    bg=Theme.COLOR_PANEL,
                    fg=Theme.COLOR_MUTED).pack()

        # === RAZONAMIENTO DE IA ===
        razon_frame = tk.Frame(frame_inner, bg=Theme.COLOR_PANEL)
        razon_frame.pack(fill=tk.X, pady=(0, 25))

        razon_inner = tk.Frame(razon_frame, bg=Theme.COLOR_PANEL)
        razon_inner.pack(fill=tk.X, padx=30, pady=25)

        tk.Label(razon_inner, text="💡 Análisis y Razonamiento",
                font=Theme.FONT_SUBTITLE,
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT).pack(anchor=tk.W, pady=(0, 15))

        tk.Label(razon_inner, text=self.analisis['sugerencia']['razonamiento'],
                font=Theme.FONT_BASE,
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT,
                wraplength=780,
                justify=tk.LEFT).pack(anchor=tk.W)

        # === SUGERENCIA ===
        sugerencia_frame = tk.Frame(frame_inner, bg="#E3F2FD")
        sugerencia_frame.pack(fill=tk.X, pady=(0, 25))

        sugerencia_inner = tk.Frame(sugerencia_frame, bg="#E3F2FD")
        sugerencia_inner.pack(fill=tk.X, padx=30, pady=25)

        tk.Label(sugerencia_inner, text="🎯 Recomendación de Pedido",
                font=Theme.FONT_SUBTITLE,
                bg="#E3F2FD",
                fg=Theme.COLOR_TEXT).pack(anchor=tk.W, pady=(0, 10))

        cantidad_frame = tk.Frame(sugerencia_inner, bg="#E3F2FD")
        cantidad_frame.pack(anchor=tk.W)

        tk.Label(cantidad_frame, text="Cantidad sugerida:",
                font=Theme.FONT_BASE,
                bg="#E3F2FD",
                fg=Theme.COLOR_TEXT).pack(side=tk.LEFT)

        tk.Label(cantidad_frame, text=f" {self.analisis['sugerencia']['cantidad']} unidades",
                font=("Segoe UI Semibold", 14),
                bg="#E3F2FD",
                fg=Theme.COLOR_PRIMARY).pack(side=tk.LEFT)

        costo_frame = tk.Frame(sugerencia_inner, bg="#E3F2FD")
        costo_frame.pack(anchor=tk.W, pady=(5, 0))

        tk.Label(costo_frame, text="Costo estimado:",
                font=Theme.FONT_BASE,
                bg="#E3F2FD",
                fg=Theme.COLOR_TEXT).pack(side=tk.LEFT)

        tk.Label(costo_frame, text=f" ${self.analisis['sugerencia']['costo_estimado']:.2f}",
                font=("Segoe UI Semibold", 14),
                bg="#E3F2FD",
                fg=Theme.COLOR_SUCCESS).pack(side=tk.LEFT)

        # === PROVEEDOR ===
        if self.analisis['proveedor']:
            prov_frame = tk.Frame(frame_inner, bg=Theme.COLOR_PANEL)
            prov_frame.pack(fill=tk.X, pady=(0, 25))

            prov_inner = tk.Frame(prov_frame, bg=Theme.COLOR_PANEL)
            prov_inner.pack(fill=tk.X, padx=30, pady=25)

            tk.Label(prov_inner, text="🏢 Información del Proveedor",
                    font=Theme.FONT_SUBTITLE,
                    bg=Theme.COLOR_PANEL,
                    fg=Theme.COLOR_TEXT).pack(anchor=tk.W, pady=(0, 15))

            for campo, valor in [
                ("Nombre:", self.analisis['proveedor']['nombre']),
                ("Contacto:", self.analisis['proveedor']['contacto']),
                ("Teléfono:", self.analisis['proveedor']['telefono']),
                ("Email:", self.analisis['proveedor']['email'])
            ]:
                if valor:
                    info_frame = tk.Frame(prov_inner, bg=Theme.COLOR_PANEL)
                    info_frame.pack(anchor=tk.W, pady=3)

                    tk.Label(info_frame, text=campo,
                            font=("Segoe UI Semibold", 11),
                            bg=Theme.COLOR_PANEL,
                            fg=Theme.COLOR_MUTED).pack(side=tk.LEFT)

                    tk.Label(info_frame, text=f" {valor}",
                            font=Theme.FONT_BASE,
                            bg=Theme.COLOR_PANEL,
                            fg=Theme.COLOR_TEXT).pack(side=tk.LEFT)

        # === MENSAJE PARA PROVEEDOR ===
        if self.analisis['proveedor']:
            mensaje_frame = tk.Frame(frame_inner, bg=Theme.COLOR_PANEL)
            mensaje_frame.pack(fill=tk.X, pady=(0, 25))

            mensaje_inner = tk.Frame(mensaje_frame, bg=Theme.COLOR_PANEL)
            mensaje_inner.pack(fill=tk.X, padx=30, pady=25)

            tk.Label(mensaje_inner, text="✉️ Mensaje Generado para el Proveedor",
                    font=Theme.FONT_SUBTITLE,
                    bg=Theme.COLOR_PANEL,
                    fg=Theme.COLOR_TEXT).pack(anchor=tk.W, pady=(0, 15))

            # Text widget con scroll para el mensaje
            mensaje_text = tk.Text(mensaje_inner,
                                  font=("Consolas", 10),
                                  bg="#F9F9FB",
                                  fg=Theme.COLOR_TEXT,
                                  relief=tk.FLAT,
                                  borderwidth=1,
                                  highlightthickness=1,
                                  highlightbackground=Theme.SHADOW_COLOR,
                                  wrap=tk.WORD,
                                  height=12)
            mensaje_text.pack(fill=tk.X, pady=(0, 10))
            mensaje_text.insert("1.0", self.analisis['mensaje_proveedor'])
            mensaje_text.config(state=tk.DISABLED)

            btn_copiar = tk.Button(mensaje_inner, text="📋 Copiar Mensaje",
                                   command=lambda: self.copiar_mensaje(self.analisis['mensaje_proveedor']),
                                   bg=Theme.COLOR_PRIMARY, fg="white",
                                   font=Theme.FONT_BUTTON,
                                   relief=tk.FLAT, padx=20, pady=10,
                                   cursor="hand2")
            btn_copiar.pack(anchor=tk.W)

        # === BOTONES DE ACCIÓN ===
        botones_frame = tk.Frame(frame_inner, bg=Theme.COLOR_BG)
        botones_frame.pack(fill=tk.X, pady=(10, 0))

        btn_crear_pedido = tk.Button(botones_frame, text="✅ Crear Pedido Automático",
                                     command=self.crear_pedido,
                                     bg=Theme.COLOR_SUCCESS, fg="white",
                                     font=("Segoe UI Semibold", 12),
                                     relief=tk.FLAT, padx=40, pady=16,
                                     cursor="hand2")
        btn_crear_pedido.pack(side=tk.LEFT, padx=(0, 15))

        btn_cerrar = tk.Button(botones_frame, text="Cerrar",
                              command=self.ventana.destroy,
                              bg="#8E8E93", fg="white",
                              font=("Segoe UI Semibold", 12),
                              relief=tk.FLAT, padx=40, pady=16,
                              cursor="hand2")
        btn_cerrar.pack(side=tk.LEFT)

    def copiar_mensaje(self, mensaje):
        """Copia el mensaje al portapapeles"""
        self.ventana.clipboard_clear()
        self.ventana.clipboard_append(mensaje)
        messagebox.showinfo("Éxito", "✅ Mensaje copiado al portapapeles")

    def crear_pedido(self):
        """Crea un pedido automático con la cantidad sugerida"""
        if not self.analisis['proveedor']:
            messagebox.showwarning("Advertencia", "El producto no tiene proveedor asignado")
            return

        from models import PedidoAutomatico

        cantidad = self.analisis['sugerencia']['cantidad']
        pedido_model = PedidoAutomatico()

        pedido_id = pedido_model.crear(
            self.producto_id,
            self.analisis['proveedor']['id'],
            cantidad,
            f"Pedido creado desde Análisis IA - Urgencia: {self.analisis['sugerencia']['urgencia']}"
        )

        messagebox.showinfo("Éxito",
                          f"✅ Pedido creado correctamente\n\n"
                          f"ID del Pedido: {pedido_id}\n"
                          f"Cantidad: {cantidad} unidades\n"
                          f"Proveedor: {self.analisis['proveedor']['nombre']}")

        self.app.cargar_dashboard()
        self.ventana.destroy()


class VentanaAnalisisProducto:
    """Ventana de análisis detallado de productos con información de fechas y rotación"""
    def __init__(self, parent, app, producto_id):
        self.app = app
        self.producto_id = producto_id
        self.producto_model = Producto()

        # Obtener datos del producto
        self.producto = self.producto_model.obtener_por_id(producto_id)
        if not self.producto:
            messagebox.showerror("Error", "Producto no encontrado")
            return

        self.ventana = tk.Toplevel(parent)
        self.ventana.title(f"Análisis: {self.producto[2]}")
        self.ventana.geometry("700x800")
        self.ventana.configure(bg=app.theme_manager.get_color('bg'))

        self.crear_interfaz()

        self.ventana.transient(parent)
        self.ventana.grab_set()

    def crear_interfaz(self):
        """Crea la interfaz de análisis"""
        # Canvas con scroll
        canvas = tk.Canvas(self.ventana, bg=self.app.theme_manager.get_color('bg'), highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.ventana, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.app.theme_manager.get_color('bg'))

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=680)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = tk.Frame(scrollable_frame, bg=self.app.theme_manager.get_color('bg'))
        frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        # Título
        tk.Label(frame, text=f"Análisis Completo: {self.producto[2]}",
                font=("Segoe UI Semibold", 16),
                bg=self.app.theme_manager.get_color('bg'),
                fg=self.app.theme_manager.get_color('text')).pack(pady=(0, 20))

        # Panel de información básica
        self.crear_panel_info_basica(frame)

        # Panel de fechas y tiempo
        self.crear_panel_fechas(frame)

        # Panel de rotación
        self.crear_panel_rotacion(frame)

        # Panel de recomendaciones
        self.crear_panel_recomendaciones(frame)

        # Botón cerrar
        btn_cerrar = tk.Button(frame, text="Cerrar", command=self.ventana.destroy,
                              bg=self.app.theme_manager.get_color('primary'), fg="white",
                              font=("Segoe UI Semibold", 11),
                              relief=tk.FLAT, padx=30, pady=12, cursor="hand2")
        btn_cerrar.pack(pady=20)

    def crear_panel_info_basica(self, parent):
        """Panel con información básica del producto"""
        panel = tk.Frame(parent, bg=self.app.theme_manager.get_color('panel'),
                        relief=tk.FLAT, borderwidth=1)
        panel.pack(fill=tk.X, pady=(0, 15))

        tk.Label(panel, text="Información Básica",
                font=("Segoe UI Semibold", 12),
                bg=self.app.theme_manager.get_color('panel'),
                fg=self.app.theme_manager.get_color('text')).pack(anchor="w", padx=20, pady=(15, 10))

        info = [
            ("Código:", self.producto[1]),
            ("Categoría:", self.producto[4] or "Sin categoría"),
            ("Precio Compra:", f"${self.producto[5]:.2f}" if self.producto[5] else "N/A"),
            ("Precio Venta:", f"${self.producto[6]:.2f}" if self.producto[6] else "N/A"),
            ("Stock Actual:", f"{self.producto[7]} unidades"),
            ("Stock Mínimo:", f"{self.producto[8]} unidades"),
            ("Stock Máximo:", f"{self.producto[9]} unidades"),
        ]

        for label, valor in info:
            frame_row = tk.Frame(panel, bg=self.app.theme_manager.get_color('panel'))
            frame_row.pack(fill=tk.X, padx=20, pady=3)
            tk.Label(frame_row, text=label, font=("Segoe UI", 10),
                    bg=self.app.theme_manager.get_color('panel'),
                    fg=self.app.theme_manager.get_color('text_secondary'),
                    width=15, anchor="w").pack(side=tk.LEFT)
            tk.Label(frame_row, text=valor, font=("Segoe UI Semibold", 10),
                    bg=self.app.theme_manager.get_color('panel'),
                    fg=self.app.theme_manager.get_color('text')).pack(side=tk.LEFT)

        tk.Label(panel, text="", bg=self.app.theme_manager.get_color('panel')).pack(pady=5)

    def crear_panel_fechas(self, parent):
        """Panel con información de fechas"""
        panel = tk.Frame(parent, bg=self.app.theme_manager.get_color('panel'),
                        relief=tk.FLAT, borderwidth=1)
        panel.pack(fill=tk.X, pady=(0, 15))

        tk.Label(panel, text="Análisis Temporal",
                font=("Segoe UI Semibold", 12),
                bg=self.app.theme_manager.get_color('panel'),
                fg=self.app.theme_manager.get_color('text')).pack(anchor="w", padx=20, pady=(15, 10))

        # Días en stock
        dias_en_stock = self.producto_model.calcular_dias_en_stock(self.producto)
        fecha_ingreso = self.producto[13] if len(self.producto) > 13 else None

        frame_row = tk.Frame(panel, bg=self.app.theme_manager.get_color('panel'))
        frame_row.pack(fill=tk.X, padx=20, pady=3)
        tk.Label(frame_row, text="Fecha de Ingreso:", font=("Segoe UI", 10),
                bg=self.app.theme_manager.get_color('panel'),
                fg=self.app.theme_manager.get_color('text_secondary'),
                width=18, anchor="w").pack(side=tk.LEFT)
        tk.Label(frame_row, text=fecha_ingreso or "No registrada",
                font=("Segoe UI Semibold", 10),
                bg=self.app.theme_manager.get_color('panel'),
                fg=self.app.theme_manager.get_color('text')).pack(side=tk.LEFT)

        frame_row = tk.Frame(panel, bg=self.app.theme_manager.get_color('panel'))
        frame_row.pack(fill=tk.X, padx=20, pady=3)
        tk.Label(frame_row, text="Días en Stock:", font=("Segoe UI", 10),
                bg=self.app.theme_manager.get_color('panel'),
                fg=self.app.theme_manager.get_color('text_secondary'),
                width=18, anchor="w").pack(side=tk.LEFT)
        tk.Label(frame_row, text=f"{dias_en_stock} días",
                font=("Segoe UI Semibold", 10),
                bg=self.app.theme_manager.get_color('panel'),
                fg=self.app.theme_manager.get_color('success')).pack(side=tk.LEFT)

        # Días hasta vencimiento
        dias_venc = self.producto_model.calcular_dias_hasta_vencimiento(self.producto)
        fecha_venc = self.producto[14] if len(self.producto) > 14 else None

        frame_row = tk.Frame(panel, bg=self.app.theme_manager.get_color('panel'))
        frame_row.pack(fill=tk.X, padx=20, pady=3)
        tk.Label(frame_row, text="Fecha de Vencimiento:", font=("Segoe UI", 10),
                bg=self.app.theme_manager.get_color('panel'),
                fg=self.app.theme_manager.get_color('text_secondary'),
                width=18, anchor="w").pack(side=tk.LEFT)
        tk.Label(frame_row, text=fecha_venc or "No aplica",
                font=("Segoe UI Semibold", 10),
                bg=self.app.theme_manager.get_color('panel'),
                fg=self.app.theme_manager.get_color('text')).pack(side=tk.LEFT)

        if dias_venc is not None:
            frame_row = tk.Frame(panel, bg=self.app.theme_manager.get_color('panel'))
            frame_row.pack(fill=tk.X, padx=20, pady=3)
            tk.Label(frame_row, text="Días hasta Vencimiento:", font=("Segoe UI", 10),
                    bg=self.app.theme_manager.get_color('panel'),
                    fg=self.app.theme_manager.get_color('text_secondary'),
                    width=18, anchor="w").pack(side=tk.LEFT)

            if dias_venc < 0:
                texto = f"VENCIDO (hace {abs(dias_venc)} días)"
                color = self.app.theme_manager.get_color('danger')
            elif dias_venc <= 7:
                texto = f"{dias_venc} días (¡URGENTE!)"
                color = self.app.theme_manager.get_color('warning')
            else:
                texto = f"{dias_venc} días"
                color = self.app.theme_manager.get_color('success')

            tk.Label(frame_row, text=texto,
                    font=("Segoe UI Semibold", 10),
                    bg=self.app.theme_manager.get_color('panel'),
                    fg=color).pack(side=tk.LEFT)

        tk.Label(panel, text="", bg=self.app.theme_manager.get_color('panel')).pack(pady=5)

    def crear_panel_rotacion(self, parent):
        """Panel con análisis de rotación"""
        panel = tk.Frame(parent, bg=self.app.theme_manager.get_color('panel'),
                        relief=tk.FLAT, borderwidth=1)
        panel.pack(fill=tk.X, pady=(0, 15))

        tk.Label(panel, text="Análisis de Rotación (Últimos 30 días)",
                font=("Segoe UI Semibold", 12),
                bg=self.app.theme_manager.get_color('panel'),
                fg=self.app.theme_manager.get_color('text')).pack(anchor="w", padx=20, pady=(15, 10))

        analisis = self.producto_model.obtener_analisis_rotacion(self.producto_id, 30)

        if analisis:
            info = [
                ("Total Vendido:", f"{analisis['total_vendido']} unidades"),
                ("Promedio Diario:", f"{analisis['promedio_diario']} und/día"),
                ("Días Restantes:", f"~{analisis['dias_restantes']} días" if analisis['dias_restantes'] < 999 else "Stock suficiente"),
            ]

            for label, valor in info:
                frame_row = tk.Frame(panel, bg=self.app.theme_manager.get_color('panel'))
                frame_row.pack(fill=tk.X, padx=20, pady=3)
                tk.Label(frame_row, text=label, font=("Segoe UI", 10),
                        bg=self.app.theme_manager.get_color('panel'),
                        fg=self.app.theme_manager.get_color('text_secondary'),
                        width=18, anchor="w").pack(side=tk.LEFT)
                tk.Label(frame_row, text=valor, font=("Segoe UI Semibold", 10),
                        bg=self.app.theme_manager.get_color('panel'),
                        fg=self.app.theme_manager.get_color('text')).pack(side=tk.LEFT)

            # Clasificación de rotación
            if analisis['promedio_diario'] >= 5:
                velocidad = "ALTA"
                color = self.app.theme_manager.get_color('success')
            elif analisis['promedio_diario'] >= 2:
                velocidad = "MEDIA"
                color = self.app.theme_manager.get_color('info')
            else:
                velocidad = "BAJA"
                color = self.app.theme_manager.get_color('warning')

            frame_row = tk.Frame(panel, bg=self.app.theme_manager.get_color('panel'))
            frame_row.pack(fill=tk.X, padx=20, pady=3)
            tk.Label(frame_row, text="Velocidad de Rotación:", font=("Segoe UI", 10),
                    bg=self.app.theme_manager.get_color('panel'),
                    fg=self.app.theme_manager.get_color('text_secondary'),
                    width=18, anchor="w").pack(side=tk.LEFT)
            tk.Label(frame_row, text=velocidad, font=("Segoe UI Semibold", 10),
                    bg=self.app.theme_manager.get_color('panel'),
                    fg=color).pack(side=tk.LEFT)
        else:
            tk.Label(panel, text="Sin datos de movimientos disponibles",
                    font=("Segoe UI", 10),
                    bg=self.app.theme_manager.get_color('panel'),
                    fg=self.app.theme_manager.get_color('text_secondary')).pack(padx=20, pady=10)

        tk.Label(panel, text="", bg=self.app.theme_manager.get_color('panel')).pack(pady=5)

    def crear_panel_recomendaciones(self, parent):
        """Panel con recomendaciones"""
        panel = tk.Frame(parent, bg=self.app.theme_manager.get_color('panel'),
                        relief=tk.FLAT, borderwidth=1)
        panel.pack(fill=tk.X, pady=(0, 15))

        tk.Label(panel, text="Recomendaciones",
                font=("Segoe UI Semibold", 12),
                bg=self.app.theme_manager.get_color('panel'),
                fg=self.app.theme_manager.get_color('text')).pack(anchor="w", padx=20, pady=(15, 10))

        recomendaciones = []

        # Recomendaciones basadas en stock
        if self.producto[7] <= self.producto[8]:
            recomendaciones.append(("⚠️", "Stock bajo: Considere reabastecer", self.app.theme_manager.get_color('warning')))

        # Recomendaciones basadas en vencimiento
        dias_venc = self.producto_model.calcular_dias_hasta_vencimiento(self.producto)
        if dias_venc is not None:
            if dias_venc < 0:
                recomendaciones.append(("❌", "Producto VENCIDO: Retirar del inventario", self.app.theme_manager.get_color('danger')))
            elif dias_venc <= 7:
                recomendaciones.append(("⏰", f"Vence en {dias_venc} días: Promocionar urgentemente", self.app.theme_manager.get_color('warning')))
            elif dias_venc <= 30:
                recomendaciones.append(("📅", f"Vence en {dias_venc} días: Monitorear de cerca", self.app.theme_manager.get_color('info')))

        # Recomendaciones basadas en rotación
        analisis = self.producto_model.obtener_analisis_rotacion(self.producto_id, 30)
        if analisis:
            if analisis['dias_restantes'] < 7 and analisis['dias_restantes'] != 999:
                recomendaciones.append(("🔴", f"Se agotará en ~{analisis['dias_restantes']:.1f} días", self.app.theme_manager.get_color('danger')))

            if analisis['promedio_diario'] >= 5:
                recomendaciones.append(("✓", "Alta rotación: Producto popular", self.app.theme_manager.get_color('success')))
            elif analisis['promedio_diario'] < 0.5:
                recomendaciones.append(("💤", "Baja rotación: Evaluar descontinuar", self.app.theme_manager.get_color('text_secondary')))

        if not recomendaciones:
            recomendaciones.append(("✓", "Producto en buen estado", self.app.theme_manager.get_color('success')))

        for icono, texto, color in recomendaciones:
            frame_row = tk.Frame(panel, bg=self.app.theme_manager.get_color('panel'))
            frame_row.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(frame_row, text=icono, font=("Segoe UI", 12),
                    bg=self.app.theme_manager.get_color('panel'),
                    fg=color).pack(side=tk.LEFT, padx=(0, 10))
            tk.Label(frame_row, text=texto, font=("Segoe UI", 10),
                    bg=self.app.theme_manager.get_color('panel'),
                    fg=color, wraplength=550, justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.X)

        tk.Label(panel, text="", bg=self.app.theme_manager.get_color('panel')).pack(pady=5)


# ==================== MAIN ====================

if __name__ == "__main__":
    root = tk.Tk()
    app = InventarioApp(root)
    root.mainloop()

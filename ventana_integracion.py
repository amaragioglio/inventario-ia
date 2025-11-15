"""
Ventana de Integración - GUI para Importar/Exportar Datos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from integrador import Integrador
from theme_manager import ThemeManager

class Theme:
    """Colores del tema"""
    COLOR_BG = "#F5F5F7"
    COLOR_PANEL = "#FFFFFF"
    COLOR_TEXT = "#1C1C1E"
    COLOR_MUTED = "#8E8E93"
    COLOR_PRIMARY = "#007AFF"
    COLOR_SUCCESS = "#34C759"
    COLOR_WARNING = "#FF9500"
    COLOR_ERROR = "#FF3B30"

    FONT_TITLE = ("Segoe UI", 18, "bold")
    FONT_SUBTITLE = ("Segoe UI", 12)
    FONT_BASE = ("Segoe UI", 10)
    FONT_BUTTON = ("Segoe UI", 10)

    @staticmethod
    def update_from_theme_manager(theme_manager):
        """Actualiza colores desde el theme manager"""
        if theme_manager.is_dark():
            Theme.COLOR_BG = "#1C1C1E"
            Theme.COLOR_PANEL = "#2C2C2E"
            Theme.COLOR_TEXT = "#FFFFFF"
            Theme.COLOR_MUTED = "#8E8E93"
        else:
            Theme.COLOR_BG = "#F5F5F7"
            Theme.COLOR_PANEL = "#FFFFFF"
            Theme.COLOR_TEXT = "#1C1C1E"
            Theme.COLOR_MUTED = "#8E8E93"


class VentanaIntegracion:
    """Ventana principal de integración de datos"""

    def __init__(self, parent):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Integrador de Datos")
        self.ventana.geometry("900x700")

        # Theme manager
        self.theme_manager = ThemeManager()
        Theme.update_from_theme_manager(self.theme_manager)

        self.ventana.configure(bg=Theme.COLOR_BG)

        # Centrar ventana
        self.ventana.update_idletasks()
        x = (self.ventana.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (700 // 2)
        self.ventana.geometry(f"900x700+{x}+{y}")

        # Integrador
        self.integrador = Integrador()

        # Crear interfaz
        self.crear_interfaz()

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Frame principal con tabs
        frame_main = tk.Frame(self.ventana, bg=Theme.COLOR_BG)
        frame_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        tk.Label(frame_main,
                text="Integrador de Datos",
                font=Theme.FONT_TITLE,
                bg=Theme.COLOR_BG,
                fg=Theme.COLOR_TEXT).pack(pady=(0, 5))

        tk.Label(frame_main,
                text="Importa y exporta datos desde múltiples fuentes",
                font=Theme.FONT_BASE,
                bg=Theme.COLOR_BG,
                fg=Theme.COLOR_MUTED).pack(pady=(0, 20))

        # Notebook para tabs
        style = ttk.Style()
        style.configure('TNotebook', background=Theme.COLOR_BG, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10], font=Theme.FONT_BASE)

        notebook = ttk.Notebook(frame_main)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Importar
        self.crear_tab_importar(notebook)

        # Tab 2: Exportar
        self.crear_tab_exportar(notebook)

        # Tab 3: Plantillas
        self.crear_tab_plantillas(notebook)

    def crear_tab_importar(self, notebook):
        """Crea el tab de importación"""
        frame = tk.Frame(notebook, bg=Theme.COLOR_PANEL)
        notebook.add(frame, text="  Importar  ")

        # Padding
        container = tk.Frame(frame, bg=Theme.COLOR_PANEL)
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Título
        tk.Label(container,
                text="Importar Datos desde Archivo",
                font=("Segoe UI", 14, "bold"),
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT).pack(anchor='w', pady=(0, 20))

        # Selección de tipo
        frame_tipo = tk.Frame(container, bg=Theme.COLOR_PANEL)
        frame_tipo.pack(fill=tk.X, pady=(0, 15))

        tk.Label(frame_tipo,
                text="Tipo de datos:",
                font=Theme.FONT_BASE,
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT).pack(side=tk.LEFT, padx=(0, 10))

        self.tipo_import_var = tk.StringVar(value="productos")

        tipos = [
            ("Productos", "productos"),
            ("Proveedores", "proveedores"),
            ("Movimientos", "movimientos")
        ]

        for texto, valor in tipos:
            rb = tk.Radiobutton(frame_tipo,
                               text=texto,
                               variable=self.tipo_import_var,
                               value=valor,
                               font=Theme.FONT_BASE,
                               bg=Theme.COLOR_PANEL,
                               fg=Theme.COLOR_TEXT,
                               selectcolor=Theme.COLOR_PANEL,
                               activebackground=Theme.COLOR_PANEL,
                               activeforeground=Theme.COLOR_PRIMARY)
            rb.pack(side=tk.LEFT, padx=10)

        # Selección de archivo
        frame_archivo = tk.Frame(container, bg=Theme.COLOR_PANEL)
        frame_archivo.pack(fill=tk.X, pady=(0, 20))

        tk.Label(frame_archivo,
                text="Archivo:",
                font=Theme.FONT_BASE,
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT).pack(anchor='w', pady=(0, 5))

        frame_input = tk.Frame(frame_archivo, bg=Theme.COLOR_PANEL)
        frame_input.pack(fill=tk.X)

        self.archivo_import_var = tk.StringVar()
        entry = tk.Entry(frame_input,
                        textvariable=self.archivo_import_var,
                        font=Theme.FONT_BASE,
                        bg=Theme.COLOR_BG,
                        fg=Theme.COLOR_TEXT,
                        relief=tk.FLAT)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))

        btn_examinar = self.crear_boton(frame_input, "Examinar",
                                        self.examinar_archivo_importar,
                                        Theme.COLOR_PRIMARY)
        btn_examinar.pack(side=tk.LEFT)

        # Frame de previsualización
        self.frame_preview = tk.Frame(container, bg=Theme.COLOR_BG, relief=tk.FLAT)
        self.frame_preview.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Botones de acción
        frame_botones = tk.Frame(container, bg=Theme.COLOR_PANEL)
        frame_botones.pack(fill=tk.X)

        btn_previsualizar = self.crear_boton(frame_botones, "Previsualizar",
                                             self.previsualizar_importacion,
                                             Theme.COLOR_WARNING)
        btn_previsualizar.pack(side=tk.LEFT, padx=(0, 10))

        btn_importar = self.crear_boton(frame_botones, "Importar",
                                        self.iniciar_importacion,
                                        Theme.COLOR_SUCCESS)
        btn_importar.pack(side=tk.LEFT)

        # Label de estado
        self.label_estado_import = tk.Label(container,
                                           text="",
                                           font=Theme.FONT_BASE,
                                           bg=Theme.COLOR_PANEL,
                                           fg=Theme.COLOR_TEXT)
        self.label_estado_import.pack(pady=(15, 0))

    def crear_tab_exportar(self, notebook):
        """Crea el tab de exportación"""
        frame = tk.Frame(notebook, bg=Theme.COLOR_PANEL)
        notebook.add(frame, text="  Exportar  ")

        container = tk.Frame(frame, bg=Theme.COLOR_PANEL)
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        tk.Label(container,
                text="Exportar Datos a Archivo",
                font=("Segoe UI", 14, "bold"),
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT).pack(anchor='w', pady=(0, 20))

        # Selección de tipo
        frame_tipo = tk.Frame(container, bg=Theme.COLOR_PANEL)
        frame_tipo.pack(fill=tk.X, pady=(0, 15))

        tk.Label(frame_tipo,
                text="Tipo de datos:",
                font=Theme.FONT_BASE,
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT).pack(side=tk.LEFT, padx=(0, 10))

        self.tipo_export_var = tk.StringVar(value="productos")

        tipos = [
            ("Productos", "productos"),
            ("Proveedores", "proveedores"),
            ("Movimientos", "movimientos")
        ]

        for texto, valor in tipos:
            rb = tk.Radiobutton(frame_tipo,
                               text=texto,
                               variable=self.tipo_export_var,
                               value=valor,
                               font=Theme.FONT_BASE,
                               bg=Theme.COLOR_PANEL,
                               fg=Theme.COLOR_TEXT,
                               selectcolor=Theme.COLOR_PANEL,
                               activebackground=Theme.COLOR_PANEL)
            rb.pack(side=tk.LEFT, padx=10)

        # Selección de formato
        frame_formato = tk.Frame(container, bg=Theme.COLOR_PANEL)
        frame_formato.pack(fill=tk.X, pady=(0, 30))

        tk.Label(frame_formato,
                text="Formato:",
                font=Theme.FONT_BASE,
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT).pack(side=tk.LEFT, padx=(0, 10))

        self.formato_export_var = tk.StringVar(value="csv")

        formatos = [
            ("CSV", "csv"),
            ("Excel", "excel"),
            ("JSON", "json")
        ]

        for texto, valor in formatos:
            rb = tk.Radiobutton(frame_formato,
                               text=texto,
                               variable=self.formato_export_var,
                               value=valor,
                               font=Theme.FONT_BASE,
                               bg=Theme.COLOR_PANEL,
                               fg=Theme.COLOR_TEXT,
                               selectcolor=Theme.COLOR_PANEL,
                               activebackground=Theme.COLOR_PANEL)
            rb.pack(side=tk.LEFT, padx=10)

        # Información
        frame_info = tk.Frame(container, bg=Theme.COLOR_BG, relief=tk.FLAT)
        frame_info.pack(fill=tk.X, pady=(0, 20), ipady=15, ipadx=15)

        tk.Label(frame_info,
                text="El archivo se guardará en la carpeta actual del programa",
                font=Theme.FONT_BASE,
                bg=Theme.COLOR_BG,
                fg=Theme.COLOR_MUTED).pack()

        # Botones
        frame_botones = tk.Frame(container, bg=Theme.COLOR_PANEL)
        frame_botones.pack(fill=tk.X)

        btn_exportar = self.crear_boton(frame_botones, "Exportar Ahora",
                                        self.iniciar_exportacion,
                                        Theme.COLOR_SUCCESS)
        btn_exportar.pack(side=tk.LEFT)

        # Label de estado
        self.label_estado_export = tk.Label(container,
                                           text="",
                                           font=Theme.FONT_BASE,
                                           bg=Theme.COLOR_PANEL,
                                           fg=Theme.COLOR_TEXT)
        self.label_estado_export.pack(pady=(15, 0))

    def crear_tab_plantillas(self, notebook):
        """Crea el tab de plantillas"""
        frame = tk.Frame(notebook, bg=Theme.COLOR_PANEL)
        notebook.add(frame, text="  Plantillas  ")

        container = tk.Frame(frame, bg=Theme.COLOR_PANEL)
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        tk.Label(container,
                text="Descargar Plantillas",
                font=("Segoe UI", 14, "bold"),
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_TEXT).pack(anchor='w', pady=(0, 10))

        tk.Label(container,
                text="Descarga plantillas CSV de ejemplo para facilitar la importación de datos",
                font=Theme.FONT_BASE,
                bg=Theme.COLOR_PANEL,
                fg=Theme.COLOR_MUTED,
                wraplength=700,
                justify=tk.LEFT).pack(anchor='w', pady=(0, 30))

        # Opciones de plantillas
        plantillas = [
            ("Productos", "productos", "Incluye: código, nombre, categoría, precios, stock, etc."),
            ("Proveedores", "proveedores", "Incluye: nombre, contacto, teléfono, email, dirección"),
            ("Movimientos", "movimientos", "Incluye: código producto, tipo, cantidad, motivo, fecha")
        ]

        for titulo, tipo, descripcion in plantillas:
            frame_plantilla = tk.Frame(container, bg=Theme.COLOR_BG, relief=tk.FLAT)
            frame_plantilla.pack(fill=tk.X, pady=10, ipady=15, ipadx=15)

            frame_info = tk.Frame(frame_plantilla, bg=Theme.COLOR_BG)
            frame_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            tk.Label(frame_info,
                    text=titulo,
                    font=("Segoe UI", 11, "bold"),
                    bg=Theme.COLOR_BG,
                    fg=Theme.COLOR_TEXT).pack(anchor='w')

            tk.Label(frame_info,
                    text=descripcion,
                    font=Theme.FONT_BASE,
                    bg=Theme.COLOR_BG,
                    fg=Theme.COLOR_MUTED).pack(anchor='w', pady=(2, 0))

            btn = self.crear_boton(frame_plantilla, "Descargar",
                                  lambda t=tipo: self.descargar_plantilla(t),
                                  Theme.COLOR_PRIMARY)
            btn.pack(side=tk.RIGHT, padx=10)

        # Información adicional
        frame_ayuda = tk.Frame(container, bg=Theme.COLOR_BG, relief=tk.FLAT)
        frame_ayuda.pack(fill=tk.X, pady=(30, 0), ipady=20, ipadx=20)

        tk.Label(frame_ayuda,
                text="Consejos:",
                font=("Segoe UI", 11, "bold"),
                bg=Theme.COLOR_BG,
                fg=Theme.COLOR_TEXT).pack(anchor='w')

        consejos = [
            "• Las plantillas incluyen una fila de ejemplo",
            "• Puedes usar Excel o cualquier editor de CSV",
            "• Asegúrate de mantener los nombres de las columnas",
            "• Los campos vacíos se rellenarán con valores por defecto"
        ]

        for consejo in consejos:
            tk.Label(frame_ayuda,
                    text=consejo,
                    font=Theme.FONT_BASE,
                    bg=Theme.COLOR_BG,
                    fg=Theme.COLOR_MUTED,
                    justify=tk.LEFT).pack(anchor='w', pady=2)

    def crear_boton(self, parent, texto, comando, color_bg):
        """Crea un botón con estilo"""
        btn = tk.Button(parent,
                       text=texto,
                       command=comando,
                       bg=color_bg,
                       fg="white",
                       font=Theme.FONT_BUTTON,
                       relief=tk.FLAT,
                       padx=20,
                       pady=10,
                       cursor="hand2",
                       borderwidth=0)

        def on_enter(e):
            btn['background'] = self._oscurecer_color(color_bg)

        def on_leave(e):
            btn['background'] = color_bg

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def _oscurecer_color(self, hex_color):
        """Oscurece un color"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * 0.85)
        g = int(g * 0.85)
        b = int(b * 0.85)
        return f'#{r:02x}{g:02x}{b:02x}'

    def examinar_archivo_importar(self):
        """Abre diálogo para seleccionar archivo"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Archivos CSV", "*.csv"),
                ("Archivos Excel", "*.xlsx *.xls"),
                ("Archivos JSON", "*.json"),
                ("Todos los archivos", "*.*")
            ]
        )

        if archivo:
            self.archivo_import_var.set(archivo)

    def previsualizar_importacion(self):
        """Previsualiza los datos antes de importar"""
        archivo = self.archivo_import_var.get()
        tipo = self.tipo_import_var.get()

        if not archivo:
            messagebox.showwarning("Advertencia", "Selecciona un archivo primero")
            return

        self.label_estado_import.config(text="Validando datos...", fg=Theme.COLOR_WARNING)
        self.ventana.update()

        try:
            resultado = self.integrador.validar_datos_importacion(archivo, tipo)

            if not resultado.get('valido'):
                messagebox.showerror("Error", f"Error al validar:\n{resultado.get('error')}")
                self.label_estado_import.config(text="", fg=Theme.COLOR_TEXT)
                return

            # Limpiar preview anterior
            for widget in self.frame_preview.winfo_children():
                widget.destroy()

            # Mostrar información
            tk.Label(self.frame_preview,
                    text=f"Previsualización ({resultado['total_filas']} filas encontradas)",
                    font=("Segoe UI", 11, "bold"),
                    bg=Theme.COLOR_BG,
                    fg=Theme.COLOR_TEXT).pack(anchor='w', pady=(0, 10))

            # Crear tabla de preview
            frame_tabla = tk.Frame(self.frame_preview, bg=Theme.COLOR_BG)
            frame_tabla.pack(fill=tk.BOTH, expand=True)

            scroll_y = tk.Scrollbar(frame_tabla)
            scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

            scroll_x = tk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
            scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

            columnas = resultado.get('columnas', [])
            tree = ttk.Treeview(frame_tabla,
                               columns=columnas,
                               show="headings",
                               yscrollcommand=scroll_y.set,
                               xscrollcommand=scroll_x.set,
                               height=8)

            for col in columnas:
                tree.heading(col, text=col)
                tree.column(col, width=120)

            for item in resultado.get('preview', []):
                valores = [item.get(col, '') for col in columnas]
                tree.insert('', tk.END, values=valores)

            tree.pack(fill=tk.BOTH, expand=True)
            scroll_y.config(command=tree.yview)
            scroll_x.config(command=tree.xview)

            self.label_estado_import.config(text="Datos validados correctamente",
                                          fg=Theme.COLOR_SUCCESS)

        except Exception as e:
            messagebox.showerror("Error", f"Error al previsualizar:\n{str(e)}")
            self.label_estado_import.config(text="", fg=Theme.COLOR_TEXT)

    def iniciar_importacion(self):
        """Inicia el proceso de importación"""
        archivo = self.archivo_import_var.get()
        tipo = self.tipo_import_var.get()

        if not archivo:
            messagebox.showwarning("Advertencia", "Selecciona un archivo primero")
            return

        respuesta = messagebox.askyesno("Confirmar",
                                       f"¿Deseas importar {tipo} desde:\n{archivo}?\n\n"
                                       f"Los datos duplicados se actualizarán.")

        if not respuesta:
            return

        self.label_estado_import.config(text="Importando datos...", fg=Theme.COLOR_WARNING)
        self.ventana.update()

        # Ejecutar en thread para no bloquear UI
        def importar():
            try:
                # Detectar formato
                if archivo.endswith('.csv'):
                    resultado = self.integrador.importar_desde_csv(archivo, tipo)
                elif archivo.endswith(('.xlsx', '.xls')):
                    resultado = self.integrador.importar_desde_excel(archivo, tipo)
                elif archivo.endswith('.json'):
                    resultado = self.integrador.importar_desde_json(archivo, tipo)
                else:
                    resultado = {
                        'exitosos': 0,
                        'fallidos': 0,
                        'errores': ['Formato no soportado'],
                        'total': 0
                    }

                # Actualizar UI en el thread principal
                self.ventana.after(0, lambda: self.mostrar_resultado_importacion(resultado))

            except Exception as e:
                self.ventana.after(0, lambda: messagebox.showerror("Error", f"Error al importar:\n{str(e)}"))
                self.ventana.after(0, lambda: self.label_estado_import.config(text="", fg=Theme.COLOR_TEXT))

        thread = threading.Thread(target=importar, daemon=True)
        thread.start()

    def mostrar_resultado_importacion(self, resultado):
        """Muestra el resultado de la importación"""
        mensaje = f"Importación completada:\n\n"
        mensaje += f"Total de filas: {resultado['total']}\n"
        mensaje += f"Exitosos: {resultado['exitosos']}\n"
        mensaje += f"Fallidos: {resultado['fallidos']}\n"

        if resultado['errores']:
            mensaje += f"\nPrimeros errores:\n"
            for error in resultado['errores'][:5]:
                mensaje += f"• {error}\n"

        if resultado['fallidos'] > 0:
            messagebox.showwarning("Importación con Errores", mensaje)
            self.label_estado_import.config(text=f"{resultado['exitosos']} importados, {resultado['fallidos']} errores",
                                          fg=Theme.COLOR_WARNING)
        else:
            messagebox.showinfo("Éxito", mensaje)
            self.label_estado_import.config(text=f"{resultado['exitosos']} registros importados correctamente",
                                          fg=Theme.COLOR_SUCCESS)

    def iniciar_exportacion(self):
        """Inicia el proceso de exportación"""
        tipo = self.tipo_export_var.get()
        formato = self.formato_export_var.get()

        # Generar nombre de archivo
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if formato == 'csv':
            extension = '.csv'
        elif formato == 'excel':
            extension = '.xlsx'
        else:
            extension = '.json'

        archivo = f"export_{tipo}_{timestamp}{extension}"

        respuesta = messagebox.askyesno("Confirmar",
                                       f"¿Deseas exportar {tipo} a:\n{archivo}?")

        if not respuesta:
            return

        self.label_estado_export.config(text="Exportando datos...", fg=Theme.COLOR_WARNING)
        self.ventana.update()

        try:
            if formato == 'csv':
                exito = self.integrador.exportar_a_csv(archivo, tipo)
            elif formato == 'excel':
                exito = self.integrador.exportar_a_excel(archivo, tipo)
            else:
                exito = self.integrador.exportar_a_json(archivo, tipo)

            if exito:
                import os
                ruta_completa = os.path.abspath(archivo)
                messagebox.showinfo("Éxito",
                                  f"Datos exportados correctamente a:\n{ruta_completa}")
                self.label_estado_export.config(text=f"Exportado: {archivo}",
                                              fg=Theme.COLOR_SUCCESS)
            else:
                messagebox.showerror("Error", "No se pudo exportar los datos")
                self.label_estado_export.config(text="", fg=Theme.COLOR_TEXT)

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")
            self.label_estado_export.config(text="", fg=Theme.COLOR_TEXT)

    def descargar_plantilla(self, tipo):
        """Descarga una plantilla CSV"""
        try:
            archivo = self.integrador.obtener_plantilla_csv(tipo)

            if archivo:
                import os
                ruta_completa = os.path.abspath(archivo)
                messagebox.showinfo("Éxito",
                                  f"Plantilla creada:\n{ruta_completa}\n\n"
                                  f"Puedes editarla con Excel o cualquier editor de CSV")
            else:
                messagebox.showerror("Error", "No se pudo crear la plantilla")

        except Exception as e:
            messagebox.showerror("Error", f"Error al crear plantilla:\n{str(e)}")


# Para pruebas
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    ventana = VentanaIntegracion(root)
    root.mainloop()

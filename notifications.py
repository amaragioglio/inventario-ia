import tkinter as tk
from tkinter import messagebox
from models import Alerta, Producto

class NotificationManager:
    def __init__(self, root):
        self.root = root
        self.alerta_model = Alerta()
        self.producto_model = Producto()

    def verificar_alertas(self):
        """Verifica y muestra alertas de stock bajo"""
        alertas = self.alerta_model.obtener_no_leidas()

        if alertas:
            # Crear ventana de notificaciones
            self.mostrar_ventana_alertas(alertas)

        # Programar próxima verificación (cada 5 minutos)
        self.root.after(300000, self.verificar_alertas)

    def mostrar_ventana_alertas(self, alertas):
        """Muestra una ventana con todas las alertas"""
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Alertas de Inventario ({len(alertas)})")
        ventana.geometry("600x400")
        ventana.configure(bg="#f8f9fa")

        # Frame principal
        frame_principal = tk.Frame(ventana, bg="#f8f9fa")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(frame_principal, text="⚠️ ALERTAS DE STOCK",
                         font=("Segoe UI", 16, "bold"), bg="#f8f9fa", fg="#dc3545")
        titulo.pack(pady=(0, 15))

        # Frame con scroll para alertas
        frame_scroll = tk.Frame(frame_principal, bg="#f8f9fa")
        frame_scroll.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame_scroll)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas = tk.Canvas(frame_scroll, bg="#f8f9fa", yscrollcommand=scrollbar.set,
                          highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=canvas.yview)

        frame_alertas = tk.Frame(canvas, bg="#f8f9fa")
        canvas.create_window((0, 0), window=frame_alertas, anchor="nw")

        # Mostrar cada alerta
        for alerta in alertas:
            self._crear_tarjeta_alerta(frame_alertas, alerta)

        frame_alertas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Botones
        frame_botones = tk.Frame(frame_principal, bg="#f8f9fa")
        frame_botones.pack(pady=(15, 0))

        btn_marcar_leidas = tk.Button(frame_botones, text="Marcar todas como leídas",
                                      command=lambda: self._marcar_todas_leidas(alertas, ventana),
                                      bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"),
                                      relief=tk.FLAT, padx=20, pady=8, cursor="hand2")
        btn_marcar_leidas.pack(side=tk.LEFT, padx=5)

        btn_cerrar = tk.Button(frame_botones, text="Cerrar",
                              command=ventana.destroy,
                              bg="#6c757d", fg="white", font=("Segoe UI", 10, "bold"),
                              relief=tk.FLAT, padx=20, pady=8, cursor="hand2")
        btn_cerrar.pack(side=tk.LEFT, padx=5)

        # Centrar ventana
        ventana.transient(self.root)
        ventana.grab_set()

    def _crear_tarjeta_alerta(self, parent, alerta):
        """Crea una tarjeta visual para cada alerta"""
        frame = tk.Frame(parent, bg="white", relief=tk.SOLID, borderwidth=1)
        frame.pack(fill=tk.X, pady=5, padx=5)

        # Contenido de la alerta
        frame_contenido = tk.Frame(frame, bg="white")
        frame_contenido.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Producto (índice 6 = producto_nombre del JOIN)
        producto_label = tk.Label(frame_contenido, text=f"Producto: {alerta[6]}",
                                  font=("Segoe UI", 11, "bold"), bg="white", anchor="w")
        producto_label.pack(fill=tk.X)

        # Mensaje (índice 3)
        mensaje_label = tk.Label(frame_contenido, text=alerta[3],
                                font=("Segoe UI", 9), bg="white", anchor="w", fg="#6c757d")
        mensaje_label.pack(fill=tk.X, pady=(3, 0))

        # Fecha (índice 5)
        fecha_label = tk.Label(frame_contenido, text=f"Fecha: {alerta[5]}",
                              font=("Segoe UI", 8), bg="white", anchor="w", fg="#adb5bd")
        fecha_label.pack(fill=tk.X, pady=(3, 0))

    def _marcar_todas_leidas(self, alertas, ventana):
        """Marca todas las alertas como leídas"""
        for alerta in alertas:
            self.alerta_model.marcar_leida(alerta[0])

        messagebox.showinfo("Éxito", "Todas las alertas han sido marcadas como leídas")
        ventana.destroy()

    def verificar_stock_productos(self):
        """Verifica manualmente el stock de todos los productos"""
        productos_stock_bajo = self.producto_model.obtener_productos_stock_bajo()

        for producto in productos_stock_bajo:
            self.alerta_model.crear(
                producto[0],
                "STOCK_BAJO",
                f"El producto '{producto[2]}' tiene stock bajo: {producto[7]} unidades (Mínimo: {producto[8]})"
            )

        return len(productos_stock_bajo)

    def mostrar_notificacion_simple(self, titulo, mensaje, tipo="info"):
        """Muestra una notificación simple"""
        if tipo == "info":
            messagebox.showinfo(titulo, mensaje)
        elif tipo == "warning":
            messagebox.showwarning(titulo, mensaje)
        elif tipo == "error":
            messagebox.showerror(titulo, mensaje)
        elif tipo == "success":
            messagebox.showinfo(titulo, mensaje)

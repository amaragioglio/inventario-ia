"""
Script para generar datos de prueba realistas para un minimarket latino
Simula 3 meses de operación con productos, proveedores y movimientos
"""

import sqlite3
from datetime import datetime, timedelta
import random
import sys
import io

# Configurar encoding UTF-8 para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Conectar a la base de datos
from config import DATABASE
from database import Database
Database(DATABASE)  # crea las tablas si la base es nueva
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

print("🗑️  Limpiando datos existentes...")
# Limpiar datos existentes para empezar de cero
cursor.execute("DELETE FROM movimientos")
cursor.execute("DELETE FROM pedidos_automaticos")
cursor.execute("DELETE FROM alertas")
cursor.execute("DELETE FROM productos")
cursor.execute("DELETE FROM proveedores")
conn.commit()
print("✅ Base de datos limpiada")

print("📦 Creando proveedores...")
proveedores = [
    ("Distribuidora La Bodega", "Carlos Méndez", "555-1001", "carlos@labodega.com", "Av. Principal 123"),
    ("Abarrotes El Sabor Latino", "María González", "555-1002", "maria@sabor.com", "Calle Comercio 456"),
    ("Bebidas Universal", "José Rodríguez", "555-1003", "jose@universal.com", "Jr. Industrial 789"),
    ("Lácteos San José", "Laura Sánchez", "555-1004", "laura@sanjose.com", "Av. Lácteos 321"),
    ("Limpieza Total SAC", "Roberto Díaz", "555-1005", "roberto@total.com", "Calle Limpia 654"),
    ("Snacks y Golosinas Express", "Ana Torres", "555-1006", "ana@express.com", "Av. Dulce 987"),
]

proveedor_ids = {}
for nombre, contacto, telefono, email, direccion in proveedores:
    cursor.execute("""
        INSERT INTO proveedores (nombre, contacto, telefono, email, direccion)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, contacto, telefono, email, direccion))
    proveedor_ids[nombre] = cursor.lastrowid

print(f"✅ {len(proveedores)} proveedores creados")

print("🛒 Creando productos típicos de minimarket latino...")
productos = [
    # BEBIDAS (alta rotación)
    ("BEB001", "Coca Cola 2L", "Gaseosa cola 2 litros", "Bebidas", 2.50, 3.50, 45, 20, 150, "Bebidas Universal"),
    ("BEB002", "Inca Kola 2L", "Gaseosa nacional 2 litros", "Bebidas", 2.30, 3.20, 38, 15, 120, "Bebidas Universal"),
    ("BEB003", "Pepsi 2L", "Gaseosa cola 2 litros", "Bebidas", 2.40, 3.40, 28, 15, 100, "Bebidas Universal"),
    ("BEB004", "Sprite 2L", "Gaseosa lima-limón", "Bebidas", 2.40, 3.40, 22, 15, 100, "Bebidas Universal"),
    ("BEB005", "Agua San Luis 2.5L", "Agua mineral sin gas", "Bebidas", 1.20, 2.00, 65, 30, 200, "Bebidas Universal"),
    ("BEB006", "Jugo Pulp Durazno 1L", "Jugo néctar durazno", "Bebidas", 2.80, 4.00, 18, 12, 80, "Bebidas Universal"),
    ("BEB007", "Chicha Morada Selva 1L", "Bebida tradicional", "Bebidas", 2.50, 3.50, 15, 10, 60, "Bebidas Universal"),

    # ALIMENTOS BÁSICOS (rotación media-alta)
    ("ALI001", "Arroz Superior 5kg", "Arroz extra", "Alimentos", 12.00, 15.00, 42, 15, 80, "Distribuidora La Bodega"),
    ("ALI002", "Fideos Don Vittorio 1kg", "Pasta italiana", "Alimentos", 3.50, 5.00, 35, 20, 100, "Distribuidora La Bodega"),
    ("ALI003", "Aceite Primor 1L", "Aceite vegetal", "Alimentos", 8.50, 11.00, 28, 15, 70, "Distribuidora La Bodega"),
    ("ALI004", "Azúcar Blanca 1kg", "Azúcar refinada", "Alimentos", 2.80, 4.00, 55, 25, 120, "Distribuidora La Bodega"),
    ("ALI005", "Sal Marina 1kg", "Sal de mesa", "Alimentos", 1.50, 2.50, 68, 20, 100, "Distribuidora La Bodega"),
    ("ALI006", "Frijol Canario 1kg", "Frijol peruano", "Alimentos", 6.50, 9.00, 32, 15, 60, "Distribuidora La Bodega"),
    ("ALI007", "Lentejas 1kg", "Menestras", "Alimentos", 5.50, 8.00, 25, 10, 50, "Distribuidora La Bodega"),
    ("ALI008", "Harina Blanca Flor 1kg", "Harina de trigo", "Alimentos", 3.20, 5.00, 38, 15, 70, "Distribuidora La Bodega"),

    # LÁCTEOS (alta rotación, perecederos)
    ("LAC001", "Leche Gloria 1L", "Leche UHT entera", "Lácteos", 3.80, 5.50, 52, 30, 150, "Lácteos San José"),
    ("LAC002", "Yogurt Gloria Fresa 1L", "Yogurt bebible", "Lácteos", 6.50, 9.00, 24, 15, 80, "Lácteos San José"),
    ("LAC003", "Queso Fresco 500g", "Queso blanco", "Lácteos", 8.00, 12.00, 18, 10, 50, "Lácteos San José"),
    ("LAC004", "Mantequilla Gloria 100g", "Mantequilla con sal", "Lácteos", 4.50, 7.00, 32, 15, 60, "Lácteos San José"),

    # SNACKS (rotación media)
    ("SNK001", "Papas Lays Clásicas 180g", "Papas fritas", "Snacks", 3.20, 5.00, 45, 20, 100, "Snacks y Golosinas Express"),
    ("SNK002", "Galletas Soda Field 6un", "Galletas saladas", "Snacks", 2.50, 4.00, 38, 15, 80, "Snacks y Golosinas Express"),
    ("SNK003", "Chocolate Sublime 30g", "Chocolate con leche", "Snacks", 1.50, 2.50, 62, 30, 150, "Snacks y Golosinas Express"),
    ("SNK004", "Chizitos 140g", "Snack queso", "Snacks", 3.00, 4.50, 28, 15, 70, "Snacks y Golosinas Express"),
    ("SNK005", "Piqueo Snax 180g", "Mix frutos secos", "Snacks", 4.50, 7.00, 22, 10, 50, "Snacks y Golosinas Express"),

    # LIMPIEZA (rotación baja-media)
    ("LIM001", "Detergente Ariel 1kg", "Detergente polvo", "Limpieza", 12.00, 18.00, 35, 15, 60, "Limpieza Total SAC"),
    ("LIM002", "Papel Higiénico Elite 4un", "Papel suave", "Limpieza", 5.50, 8.50, 48, 20, 100, "Limpieza Total SAC"),
    ("LIM003", "Lejía Clorox 1L", "Desinfectante", "Limpieza", 3.50, 5.50, 42, 20, 80, "Limpieza Total SAC"),
    ("LIM004", "Jabón Líquido Bolivar 900ml", "Jabón manos", "Limpieza", 6.00, 9.00, 28, 12, 50, "Limpieza Total SAC"),
    ("LIM005", "Lavavajilla Sapolio 900ml", "Detergente líquido", "Limpieza", 5.50, 8.00, 32, 15, 60, "Limpieza Total SAC"),

    # PANADERÍA (muy alta rotación)
    ("PAN001", "Pan Francés unidad", "Pan blanco", "Panadería", 0.30, 0.60, 85, 50, 200, "Abarrotes El Sabor Latino"),
    ("PAN002", "Pan Integral unidad", "Pan integral", "Panadería", 0.50, 1.00, 42, 30, 150, "Abarrotes El Sabor Latino"),
    ("PAN003", "Tostadas Bimbo 250g", "Pan tostado", "Panadería", 3.80, 6.00, 28, 15, 70, "Abarrotes El Sabor Latino"),

    # EMBUTIDOS (rotación media)
    ("EMB001", "Jamón Inglés Laive 250g", "Jamón cocido", "Embutidos", 8.50, 13.00, 22, 10, 50, "Abarrotes El Sabor Latino"),
    ("EMB002", "Salchicha Huachana 500g", "Salchicha hot dog", "Embutidos", 6.50, 10.00, 18, 8, 40, "Abarrotes El Sabor Latino"),
    ("EMB003", "Mortadela Laive 250g", "Embutido", "Embutidos", 5.50, 8.50, 15, 8, 35, "Abarrotes El Sabor Latino"),

    # ENLATADOS (rotación baja)
    ("ENL001", "Atún Florida Light 170g", "Atún en agua", "Enlatados", 4.50, 7.00, 38, 15, 70, "Distribuidora La Bodega"),
    ("ENL002", "Duraznos en Conserva 820g", "Fruta enlatada", "Enlatados", 6.50, 10.00, 25, 10, 50, "Distribuidora La Bodega"),
    ("ENL003", "Leche Condensada Nestlé 397g", "Leche dulce", "Enlatados", 5.50, 8.50, 32, 12, 60, "Distribuidora La Bodega"),
]

producto_ids = {}
for codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock, minimo, maximo, proveedor_nombre in productos:
    proveedor_id = proveedor_ids[proveedor_nombre]
    cursor.execute("""
        INSERT INTO productos (codigo, nombre, descripcion, categoria, precio_compra, precio_venta,
                              stock_actual, stock_minimo, stock_maximo, proveedor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock, minimo, maximo, proveedor_id))
    producto_ids[codigo] = cursor.lastrowid

print(f"✅ {len(productos)} productos creados")

print("📊 Generando movimientos de stock (3 meses)...")

# Definir patrones de venta por categoría (promedio diario)
patrones_venta = {
    "Bebidas": (8, 15),      # entre 8 y 15 unidades por día
    "Alimentos": (5, 12),    # entre 5 y 12 unidades por día
    "Lácteos": (6, 14),      # entre 6 y 14 unidades por día (perecederos)
    "Snacks": (4, 10),       # entre 4 y 10 unidades por día
    "Limpieza": (2, 6),      # entre 2 y 6 unidades por día
    "Panadería": (15, 30),   # entre 15 y 30 unidades por día (muy alta rotación)
    "Embutidos": (3, 8),     # entre 3 y 8 unidades por día
    "Enlatados": (2, 5),     # entre 2 y 5 unidades por día
}

# Fecha inicial: 3 meses atrás
fecha_inicio = datetime.now() - timedelta(days=90)
total_movimientos = 0

# Simulación con una política de reposición realista: se vende lo que hay y,
# cuando el stock baja del mínimo, llega un pedido 2 días después. Unos pocos
# productos dejan de reponerse al final para que la demo muestre alertas.
random.seed(42)
stock_sim = {p[0]: p[6] for p in productos}           # codigo -> stock
pedido_llega = {}                                       # codigo -> día de llegada
sin_reponer_al_final = {"BEB002", "ALI003", "LAC002", "SNK001", "LIM001"}

for dia in range(90):
    fecha_actual = fecha_inicio + timedelta(days=dia)

    for codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock, minimo, maximo, proveedor_nombre in productos:
        producto_id = producto_ids[codigo]
        hora = fecha_actual.replace(hour=random.randint(8, 20), minute=random.randint(0, 59))

        # Llega un pedido pendiente
        if pedido_llega.get(codigo) == dia:
            entrada = max(int(maximo * 0.9) - stock_sim[codigo], 0)
            if entrada:
                stock_sim[codigo] += entrada
                cursor.execute("""
                    INSERT INTO movimientos (producto_id, tipo, cantidad, motivo, usuario, fecha)
                    VALUES (?, 'ENTRADA', ?, 'Pedido a proveedor', 'Sistema', ?)
                """, (producto_id, entrada, fecha_actual.replace(hour=7).strftime("%Y-%m-%d %H:%M:%S")))
                total_movimientos += 1
            del pedido_llega[codigo]

        # Ventas del día (más los fines de semana), nunca más de lo que hay
        min_venta, max_venta = patrones_venta.get(categoria, (1, 5))
        if random.random() < 0.8:
            ventas_dia = random.randint(min_venta, max_venta)
            if fecha_actual.weekday() >= 5:
                ventas_dia = int(ventas_dia * 1.5)
            ventas_dia = min(ventas_dia, stock_sim[codigo])
            if ventas_dia > 0:
                stock_sim[codigo] -= ventas_dia
                cursor.execute("""
                    INSERT INTO movimientos (producto_id, tipo, cantidad, motivo, usuario, fecha)
                    VALUES (?, 'SALIDA', ?, 'Venta del día', 'Sistema', ?)
                """, (producto_id, ventas_dia, hora.strftime("%Y-%m-%d %H:%M:%S")))
                total_movimientos += 1

        # Reposición antes de llegar al mínimo
        ultimos_dias = dia >= 80 and codigo in sin_reponer_al_final
        punto_pedido = minimo + 3 * (min_venta + max_venta) // 2  # cubre los 2 días de espera
        if stock_sim[codigo] <= punto_pedido and codigo not in pedido_llega and not ultimos_dias:
            pedido_llega[codigo] = dia + 2

    if (dia + 1) % 30 == 0:
        print(f"  Procesando día {dia + 1}/90...")

print(f"✅ {total_movimientos} movimientos generados")

print("🔔 Generando alertas y pedidos automáticos...")

# Generar algunas alertas de stock bajo
productos_bajo_stock = [
    (producto_ids["BEB002"], "STOCK_BAJO", "Stock bajo detectado - Requiere reabastecimiento"),
    (producto_ids["ALI003"], "STOCK_CRITICO", "Stock crítico - Pedido urgente recomendado"),
    (producto_ids["LAC002"], "STOCK_BAJO", "Stock por debajo del mínimo"),
]

for producto_id, tipo_alerta, mensaje in productos_bajo_stock:
    cursor.execute("""
        INSERT INTO alertas (producto_id, tipo_alerta, mensaje, leida, fecha)
        VALUES (?, ?, ?, 0, ?)
    """, (producto_id, tipo_alerta, mensaje, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

print(f"✅ {len(productos_bajo_stock)} alertas generadas")

# Generar algunos pedidos automáticos
pedidos = [
    (producto_ids["BEB002"], proveedor_ids["Bebidas Universal"], 80, "Pedido generado por IA - Alta rotación detectada"),
    (producto_ids["ALI003"], proveedor_ids["Distribuidora La Bodega"], 45, "Pedido generado por IA - Stock crítico"),
    (producto_ids["LAC001"], proveedor_ids["Lácteos San José"], 100, "Pedido generado por IA - Producto de alta demanda"),
]

for producto_id, proveedor_id, cantidad, notas in pedidos:
    cursor.execute("""
        INSERT INTO pedidos_automaticos (producto_id, proveedor_id, cantidad_solicitada, fecha_pedido, notas, estado)
        VALUES (?, ?, ?, ?, ?, 'PENDIENTE')
    """, (producto_id, proveedor_id, cantidad, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), notas))

print(f"✅ {len(pedidos)} pedidos automáticos creados")

# Stock actual = resultado de la simulación
print("Guardando stock final...")
for codigo, producto_id in producto_ids.items():
    cursor.execute("UPDATE productos SET stock_actual = ? WHERE id = ?", (stock_sim[codigo], producto_id))

# Confirmar cambios
conn.commit()
conn.close()

print("\n" + "="*60)
print("🎉 ¡DATOS DE PRUEBA GENERADOS EXITOSAMENTE!")
print("="*60)
print(f"""
📊 RESUMEN:
   • {len(proveedores)} Proveedores creados
   • {len(productos)} Productos típicos latinos
   • {total_movimientos} Movimientos de stock (3 meses)
   • {len(productos_bajo_stock)} Alertas generadas
   • {len(pedidos)} Pedidos automáticos pendientes

💡 CATEGORÍAS:
   • Bebidas (alta rotación)
   • Alimentos básicos (rotación media-alta)
   • Lácteos (alta rotación, perecederos)
   • Snacks (rotación media)
   • Limpieza (rotación baja-media)
   • Panadería (muy alta rotación)
   • Embutidos (rotación media)
   • Enlatados (rotación baja)

🚀 Ahora puedes ejecutar: python main.py
   El dashboard mostrará proyecciones basadas en 3 meses de datos reales!
""")

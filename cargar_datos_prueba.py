"""
Script para cargar datos de prueba en el sistema
Útil para demostrar funcionalidades
"""

from models import Producto, Proveedor
from database import Database

def cargar_datos_prueba():
    """Carga datos de ejemplo en el sistema"""
    print("\n" + "="*60)
    print("CARGANDO DATOS DE PRUEBA")
    print("="*60 + "\n")

    # Inicializar base de datos
    db = Database()
    producto_model = Producto()
    proveedor_model = Proveedor()

    print("Creando proveedores de minimarket...")

    # Crear proveedores de ejemplo (minimarket)
    proveedores = [
        ("Alimentos Don José S.A.", "José Rodríguez", "555-1001", "ventas@alimentosdonjose.com", "Mercado Central #450"),
        ("Distribuidora Bebidas Premium", "Laura Sánchez", "555-1002", "pedidos@bebidaspremium.com", "Av. Industrial 789"),
        ("Limpieza y Hogar Total", "Carlos Méndez", "555-1003", "contacto@limpiezatotal.com", "Zona Comercial B-12"),
        ("Lácteos La Granja", "María Fernández", "555-1004", "info@lacteoslagranja.com", "Carretera Norte Km 5"),
        ("Snacks y Golosinas Express", "Pedro Gutiérrez", "555-1005", "ventas@snacksexpress.com", "Centro Dist. 234"),
    ]

    proveedores_ids = []
    for proveedor in proveedores:
        try:
            proveedor_id = proveedor_model.crear(*proveedor)
            proveedores_ids.append(proveedor_id)
            print(f"  [OK] Proveedor '{proveedor[0]}' creado")
        except Exception as e:
            print(f"  [ERROR] Error al crear proveedor '{proveedor[0]}': {str(e)}")

    print(f"\n[OK] {len(proveedores_ids)} proveedores creados\n")

    print("Creando productos de minimarket...")

    # Crear productos de ejemplo (minimarket)
    productos = [
        # Código, Nombre, Descripción, Categoría, P.Compra, P.Venta, Stock, Mín, Máx, Proveedor
        # BEBIDAS
        ("BEB001", "Coca Cola 2L", "Gaseosa Coca Cola 2 litros", "Bebidas", 1.20, 2.50, 8, 20, 150, proveedores_ids[1]),
        ("BEB002", "Agua Mineral 600ml", "Agua sin gas botella 600ml", "Bebidas", 0.30, 0.80, 15, 30, 200, proveedores_ids[1]),
        ("BEB003", "Jugo Naranja 1L", "Jugo natural de naranja", "Bebidas", 1.50, 3.00, 12, 15, 100, proveedores_ids[1]),
        ("BEB004", "Cerveza Pilsen Lata", "Cerveza 355ml lata", "Bebidas", 0.80, 1.80, 45, 40, 200, proveedores_ids[1]),

        # LÁCTEOS
        ("LAC001", "Leche Gloria 1L", "Leche entera UHT 1 litro", "Lácteos", 1.20, 2.20, 5, 25, 120, proveedores_ids[3]),
        ("LAC002", "Yogurt Frutado", "Yogurt sabores surtidos 1L", "Lácteos", 1.80, 3.50, 8, 15, 80, proveedores_ids[3]),
        ("LAC003", "Queso Fresco 500g", "Queso fresco de vaca", "Lácteos", 3.50, 6.00, 4, 10, 50, proveedores_ids[3]),
        ("LAC004", "Mantequilla 200g", "Mantequilla con sal", "Lácteos", 2.00, 3.80, 18, 12, 60, proveedores_ids[3]),

        # SNACKS Y GOLOSINAS
        ("SNK001", "Papas Lays Clásicas", "Papas fritas 150g", "Snacks", 0.90, 2.00, 6, 20, 150, proveedores_ids[4]),
        ("SNK002", "Galletas Oreo", "Galletas chocolate 432g", "Snacks", 1.50, 3.20, 10, 15, 100, proveedores_ids[4]),
        ("SNK003", "Chocolate Sublime", "Chocolate con leche 30g", "Golosinas", 0.50, 1.00, 3, 30, 200, proveedores_ids[4]),
        ("SNK004", "Chizitos Cheese", "Snack de queso 110g", "Snacks", 0.80, 1.80, 14, 18, 120, proveedores_ids[4]),

        # ALIMENTOS BÁSICOS
        ("ALI001", "Arroz Costeño 1kg", "Arroz superior extra", "Alimentos", 1.20, 2.50, 35, 25, 200, proveedores_ids[0]),
        ("ALI002", "Azúcar Rubia 1kg", "Azúcar rubia de caña", "Alimentos", 0.90, 1.80, 28, 20, 150, proveedores_ids[0]),
        ("ALI003", "Aceite Primor 1L", "Aceite vegetal", "Alimentos", 2.50, 4.50, 20, 15, 100, proveedores_ids[0]),
        ("ALI004", "Fideos Don Vittorio", "Fideos tipo spaguetti 500g", "Alimentos", 0.80, 1.60, 7, 25, 180, proveedores_ids[0]),
        ("ALI005", "Atún Florida Lata", "Atún en aceite 170g", "Conservas", 1.50, 2.80, 22, 20, 120, proveedores_ids[0]),

        # PANADERÍA
        ("PAN001", "Pan Molde Bimbo", "Pan de molde 500g", "Panadería", 1.20, 2.50, 9, 15, 80, proveedores_ids[0]),
        ("PAN002", "Pan Francés Unidad", "Pan francés fresco", "Panadería", 0.15, 0.30, 40, 50, 200, proveedores_ids[0]),

        # LIMPIEZA
        ("LMP001", "Detergente Ariel 1kg", "Detergente en polvo", "Limpieza", 3.00, 5.50, 5, 12, 80, proveedores_ids[2]),
        ("LMP002", "Papel Higiénico Elite", "Papel higiénico 4 rollos", "Limpieza", 1.80, 3.50, 18, 15, 100, proveedores_ids[2]),
        ("LMP003", "Lavavajilla Ayudín 900ml", "Lavavajilla líquido limón", "Limpieza", 1.50, 2.80, 11, 10, 70, proveedores_ids[2]),
        ("LMP004", "Lejía Clorox 1L", "Lejía desinfectante", "Limpieza", 1.20, 2.20, 8, 12, 60, proveedores_ids[2]),
    ]

    productos_creados = 0
    productos_stock_bajo = 0

    for producto in productos:
        try:
            producto_model.crear(*producto)
            productos_creados += 1
            # Verificar si tiene stock bajo
            if producto[6] <= producto[7]:  # stock_actual <= stock_minimo
                productos_stock_bajo += 1
            print(f"  [OK] Producto '{producto[1]}' creado")
        except Exception as e:
            print(f"  [ERROR] Error al crear producto '{producto[1]}': {str(e)}")

    print(f"\n[OK] {productos_creados} productos creados")
    print(f"[ALERTA] {productos_stock_bajo} productos con stock bajo\n")

    print("="*60)
    print("DATOS DE PRUEBA CARGADOS EXITOSAMENTE")
    print("="*60)
    print("\nEstadísticas:")
    print(f"  - Proveedores: {len(proveedores_ids)}")
    print(f"  - Productos: {productos_creados}")
    print(f"  - Productos con stock bajo: {productos_stock_bajo}")
    print("\nYa puedes ejecutar el sistema con:")
    print("  python main.py")
    print("\n")

if __name__ == "__main__":
    try:
        cargar_datos_prueba()
        input("Presiona Enter para continuar...")
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        input("Presiona Enter para salir...")

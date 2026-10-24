"""
Script de migración para añadir campos de fecha_ingreso y fecha_vencimiento
a la tabla de productos
"""
import sqlite3
import os

def migrar_base_datos():
    """Añade los campos fecha_ingreso y fecha_vencimiento a la tabla productos"""
    from config import DATABASE as db_name

    if not os.path.exists(db_name):
        print(f"Error: No se encontró la base de datos {db_name}")
        return False

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Verificar si los campos ya existen
        cursor.execute("PRAGMA table_info(productos)")
        columnas = [col[1] for col in cursor.fetchall()]

        campos_añadidos = []

        # Añadir campo fecha_ingreso si no existe
        if 'fecha_ingreso' not in columnas:
            cursor.execute('''
                ALTER TABLE productos
                ADD COLUMN fecha_ingreso TEXT
            ''')
            campos_añadidos.append('fecha_ingreso')
            print("[OK] Campo 'fecha_ingreso' añadido correctamente")
        else:
            print("[INFO] Campo 'fecha_ingreso' ya existe")

        # Añadir campo fecha_vencimiento si no existe
        if 'fecha_vencimiento' not in columnas:
            cursor.execute('''
                ALTER TABLE productos
                ADD COLUMN fecha_vencimiento TEXT
            ''')
            campos_añadidos.append('fecha_vencimiento')
            print("[OK] Campo 'fecha_vencimiento' añadido correctamente")
        else:
            print("[INFO] Campo 'fecha_vencimiento' ya existe")

        # Añadir campo dias_vida_util si no existe
        if 'dias_vida_util' not in columnas:
            cursor.execute('''
                ALTER TABLE productos
                ADD COLUMN dias_vida_util INTEGER DEFAULT 0
            ''')
            campos_añadidos.append('dias_vida_util')
            print("[OK] Campo 'dias_vida_util' añadido correctamente")
        else:
            print("[INFO] Campo 'dias_vida_util' ya existe")

        conn.commit()
        conn.close()

        if campos_añadidos:
            print(f"\n[EXITO] Migracion completada. Campos añadidos: {', '.join(campos_añadidos)}")
        else:
            print("\n[INFO] No se requirieron cambios. Todos los campos ya existen.")

        return True

    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando migración de base de datos...")
    print("-" * 50)
    migrar_base_datos()
    print("-" * 50)
    print("Migración finalizada")

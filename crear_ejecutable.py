"""
Script para crear ejecutable del Sistema de Inventario
Utiliza PyInstaller para generar un archivo .exe portable
"""

import os
import subprocess
import sys

def verificar_pyinstaller():
    """Verifica si PyInstaller esta instalado"""
    try:
        import PyInstaller
        print("✓ PyInstaller esta instalado")
        return True
    except ImportError:
        print("✗ PyInstaller no esta instalado")
        print("\nInstalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller instalado correctamente")
            return True
        except subprocess.CalledProcessError:
            print("✗ Error al instalar PyInstaller")
            print("Por favor, instala manualmente con: pip install pyinstaller")
            return False

def crear_ejecutable():
    """Crea el ejecutable usando PyInstaller"""
    print("\n" + "="*60)
    print("CREANDO EJECUTABLE DEL SISTEMA DE INVENTARIO")
    print("="*60 + "\n")

    if not verificar_pyinstaller():
        return False

    print("\nCreando ejecutable...")
    print("Este proceso puede tardar varios minutos...\n")

    # Comando de PyInstaller
    comando = [
        "pyinstaller",
        "--name=Inventario",
        "--onedir",  # Crear directorio con todas las dependencias
        "--windowed",  # Sin ventana de consola
        # Los módulos .py se detectan solos por sus imports.
        f"--add-data=docs{os.pathsep}docs",
        f"--add-data=.env.example{os.pathsep}.",
        "main.py"
    ]

    try:
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)

        print("\n" + "="*60)
        print("✓ EJECUTABLE CREADO EXITOSAMENTE")
        print("="*60)
        print("\nUbicacion del ejecutable:")
        print(f"  {os.path.abspath('dist/Inventario/Inventario.exe')}")
        print("\nPara distribuir la aplicacion:")
        print("  1. Copia toda la carpeta 'dist/Inventario'")
        print("  2. Ejecuta 'Inventario.exe' en cualquier PC con Windows")
        print("  3. No requiere Python instalado en el PC destino")
        print("\n¡Listo para usar!")

        return True

    except subprocess.CalledProcessError as e:
        print("\n✗ Error al crear el ejecutable")
        print(f"\nDetalles del error:")
        print(e.stderr if e.stderr else str(e))
        return False
    except Exception as e:
        print(f"\n✗ Error inesperado: {str(e)}")
        return False

def limpiar_archivos():
    """Limpia archivos temporales de PyInstaller"""
    import shutil

    print("\n¿Deseas limpiar los archivos temporales? (s/n): ", end="")
    respuesta = input().lower()

    if respuesta == 's':
        try:
            if os.path.exists('build'):
                shutil.rmtree('build')
                print("✓ Carpeta 'build' eliminada")

            if os.path.exists('Inventario.spec'):
                os.remove('Inventario.spec')
                print("✓ Archivo 'Inventario.spec' eliminado")

            print("\n✓ Limpieza completada")
        except Exception as e:
            print(f"\n✗ Error al limpiar: {str(e)}")

if __name__ == "__main__":
    try:
        exito = crear_ejecutable()

        if exito:
            limpiar_archivos()
            print("\n¡Proceso completado!")
        else:
            print("\nEl proceso fallo. Revisa los errores arriba.")

        input("\nPresiona Enter para salir...")

    except KeyboardInterrupt:
        print("\n\nProceso cancelado por el usuario")
        sys.exit(1)

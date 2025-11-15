"""
Sistema de Integración de Datos
Permite importar/exportar desde múltiples fuentes
"""

import csv
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

class Integrador:
    """Maneja la importación y exportación de datos"""

    def __init__(self, db_path="inventario.db"):
        self.db_path = db_path

    # ==================== IMPORTACIÓN ====================

    def importar_desde_csv(self, archivo_csv: str, tipo: str = "productos") -> Dict[str, Any]:
        """
        Importa datos desde archivo CSV

        Args:
            archivo_csv: Ruta al archivo CSV
            tipo: Tipo de datos (productos, proveedores, movimientos)

        Returns:
            Dict con resultados de la importación
        """
        resultados = {
            'exitosos': 0,
            'fallidos': 0,
            'errores': [],
            'total': 0
        }

        try:
            with open(archivo_csv, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                datos = list(reader)
                resultados['total'] = len(datos)

                if tipo == "productos":
                    resultados = self._importar_productos(datos)
                elif tipo == "proveedores":
                    resultados = self._importar_proveedores(datos)
                elif tipo == "movimientos":
                    resultados = self._importar_movimientos(datos)
                else:
                    resultados['errores'].append(f"Tipo '{tipo}' no soportado")

        except Exception as e:
            resultados['errores'].append(f"Error al leer archivo: {str(e)}")

        return resultados

    def importar_desde_excel(self, archivo_excel: str, tipo: str = "productos", hoja: str = None) -> Dict[str, Any]:
        """
        Importa datos desde archivo Excel

        Args:
            archivo_excel: Ruta al archivo Excel
            tipo: Tipo de datos
            hoja: Nombre de la hoja (opcional)

        Returns:
            Dict con resultados
        """
        try:
            import openpyxl

            workbook = openpyxl.load_workbook(archivo_excel)
            sheet = workbook[hoja] if hoja else workbook.active

            # Convertir a lista de diccionarios
            headers = [cell.value for cell in sheet[1]]
            datos = []

            for row in sheet.iter_rows(min_row=2, values_only=True):
                fila = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
                datos.append(fila)

            # Usar el mismo sistema que CSV
            if tipo == "productos":
                return self._importar_productos(datos)
            elif tipo == "proveedores":
                return self._importar_proveedores(datos)
            elif tipo == "movimientos":
                return self._importar_movimientos(datos)
            else:
                return {
                    'exitosos': 0,
                    'fallidos': 0,
                    'errores': [f"Tipo '{tipo}' no soportado"],
                    'total': 0
                }

        except ImportError:
            return {
                'exitosos': 0,
                'fallidos': 0,
                'errores': ['Instalar openpyxl: pip install openpyxl'],
                'total': 0
            }
        except Exception as e:
            return {
                'exitosos': 0,
                'fallidos': 0,
                'errores': [f"Error al importar: {str(e)}"],
                'total': 0
            }

    def importar_desde_json(self, archivo_json: str, tipo: str = "productos") -> Dict[str, Any]:
        """Importa datos desde archivo JSON"""
        try:
            with open(archivo_json, 'r', encoding='utf-8') as file:
                datos = json.load(file)

            # Si es un objeto con array de datos
            if isinstance(datos, dict) and tipo in datos:
                datos = datos[tipo]

            if tipo == "productos":
                return self._importar_productos(datos)
            elif tipo == "proveedores":
                return self._importar_proveedores(datos)
            elif tipo == "movimientos":
                return self._importar_movimientos(datos)
            else:
                return {
                    'exitosos': 0,
                    'fallidos': 0,
                    'errores': [f"Tipo '{tipo}' no soportado"],
                    'total': 0
                }

        except Exception as e:
            return {
                'exitosos': 0,
                'fallidos': 0,
                'errores': [f"Error al importar: {str(e)}"],
                'total': 0
            }

    def _importar_productos(self, datos: List[Dict]) -> Dict[str, Any]:
        """Importa productos a la base de datos"""
        resultados = {
            'exitosos': 0,
            'fallidos': 0,
            'errores': [],
            'total': len(datos)
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for idx, producto in enumerate(datos, 1):
            try:
                # Mapeo flexible de campos
                codigo = self._obtener_campo(producto, ['codigo', 'code', 'sku', 'id'])
                nombre = self._obtener_campo(producto, ['nombre', 'name', 'producto', 'product'])
                precio_compra = float(self._obtener_campo(producto, ['precio_compra', 'costo', 'cost', 'purchase_price'], 0))
                precio_venta = float(self._obtener_campo(producto, ['precio_venta', 'precio', 'price', 'sale_price'], 0))
                stock_actual = int(self._obtener_campo(producto, ['stock_actual', 'stock', 'cantidad', 'quantity'], 0))
                stock_minimo = int(self._obtener_campo(producto, ['stock_minimo', 'min_stock', 'minimum'], 10))
                stock_maximo = int(self._obtener_campo(producto, ['stock_maximo', 'max_stock', 'maximum'], 100))
                categoria = self._obtener_campo(producto, ['categoria', 'category', 'tipo', 'type'], 'General')
                proveedor_id = self._obtener_campo(producto, ['proveedor_id', 'supplier_id', 'vendor_id'], None)

                # Campos opcionales de fecha
                fecha_ingreso = self._obtener_campo(producto, ['fecha_ingreso', 'date_added', 'created_at'],
                                                   datetime.now().strftime('%Y-%m-%d'))
                fecha_vencimiento = self._obtener_campo(producto, ['fecha_vencimiento', 'expiration_date', 'expire_date'], None)
                dias_vida_util = self._obtener_campo(producto, ['dias_vida_util', 'shelf_life', 'days_valid'], None)

                # Validaciones
                if not codigo or not nombre:
                    resultados['errores'].append(f"Fila {idx}: Código o nombre faltante")
                    resultados['fallidos'] += 1
                    continue

                # Verificar si ya existe
                cursor.execute("SELECT id FROM productos WHERE codigo = ?", (codigo,))
                existe = cursor.fetchone()

                if existe:
                    # Actualizar
                    cursor.execute("""
                        UPDATE productos
                        SET nombre = ?, precio_compra = ?, precio_venta = ?,
                            stock_actual = ?, stock_minimo = ?, stock_maximo = ?,
                            categoria = ?, proveedor_id = ?,
                            fecha_ingreso = ?, fecha_vencimiento = ?, dias_vida_util = ?
                        WHERE codigo = ?
                    """, (nombre, precio_compra, precio_venta, stock_actual, stock_minimo,
                         stock_maximo, categoria, proveedor_id, fecha_ingreso,
                         fecha_vencimiento, dias_vida_util, codigo))
                else:
                    # Insertar
                    cursor.execute("""
                        INSERT INTO productos
                        (codigo, nombre, precio_compra, precio_venta, stock_actual,
                         stock_minimo, stock_maximo, categoria, proveedor_id,
                         fecha_ingreso, fecha_vencimiento, dias_vida_util)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (codigo, nombre, precio_compra, precio_venta, stock_actual,
                         stock_minimo, stock_maximo, categoria, proveedor_id,
                         fecha_ingreso, fecha_vencimiento, dias_vida_util))

                resultados['exitosos'] += 1

            except Exception as e:
                resultados['errores'].append(f"Fila {idx}: {str(e)}")
                resultados['fallidos'] += 1

        conn.commit()
        conn.close()

        return resultados

    def _importar_proveedores(self, datos: List[Dict]) -> Dict[str, Any]:
        """Importa proveedores a la base de datos"""
        resultados = {
            'exitosos': 0,
            'fallidos': 0,
            'errores': [],
            'total': len(datos)
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for idx, proveedor in enumerate(datos, 1):
            try:
                nombre = self._obtener_campo(proveedor, ['nombre', 'name', 'proveedor', 'supplier'])
                contacto = self._obtener_campo(proveedor, ['contacto', 'contact', 'persona'], '')
                telefono = self._obtener_campo(proveedor, ['telefono', 'phone', 'tel'], '')
                email = self._obtener_campo(proveedor, ['email', 'correo', 'mail'], '')
                direccion = self._obtener_campo(proveedor, ['direccion', 'address', 'ubicacion'], '')

                if not nombre:
                    resultados['errores'].append(f"Fila {idx}: Nombre faltante")
                    resultados['fallidos'] += 1
                    continue

                # Verificar si ya existe
                cursor.execute("SELECT id FROM proveedores WHERE nombre = ?", (nombre,))
                existe = cursor.fetchone()

                if existe:
                    cursor.execute("""
                        UPDATE proveedores
                        SET contacto = ?, telefono = ?, email = ?, direccion = ?
                        WHERE nombre = ?
                    """, (contacto, telefono, email, direccion, nombre))
                else:
                    cursor.execute("""
                        INSERT INTO proveedores (nombre, contacto, telefono, email, direccion)
                        VALUES (?, ?, ?, ?, ?)
                    """, (nombre, contacto, telefono, email, direccion))

                resultados['exitosos'] += 1

            except Exception as e:
                resultados['errores'].append(f"Fila {idx}: {str(e)}")
                resultados['fallidos'] += 1

        conn.commit()
        conn.close()

        return resultados

    def _importar_movimientos(self, datos: List[Dict]) -> Dict[str, Any]:
        """Importa movimientos a la base de datos"""
        resultados = {
            'exitosos': 0,
            'fallidos': 0,
            'errores': [],
            'total': len(datos)
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for idx, movimiento in enumerate(datos, 1):
            try:
                producto_codigo = self._obtener_campo(movimiento, ['producto_codigo', 'codigo', 'sku'])
                tipo = self._obtener_campo(movimiento, ['tipo', 'type', 'movimiento'], 'ENTRADA')
                cantidad = int(self._obtener_campo(movimiento, ['cantidad', 'quantity', 'qty'], 0))
                motivo = self._obtener_campo(movimiento, ['motivo', 'reason', 'descripcion'], '')
                fecha = self._obtener_campo(movimiento, ['fecha', 'date', 'created_at'],
                                          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

                # Obtener producto_id desde código
                cursor.execute("SELECT id FROM productos WHERE codigo = ?", (producto_codigo,))
                producto = cursor.fetchone()

                if not producto:
                    resultados['errores'].append(f"Fila {idx}: Producto con código '{producto_codigo}' no encontrado")
                    resultados['fallidos'] += 1
                    continue

                producto_id = producto[0]

                # Insertar movimiento
                cursor.execute("""
                    INSERT INTO movimientos (producto_id, tipo, cantidad, motivo, fecha)
                    VALUES (?, ?, ?, ?, ?)
                """, (producto_id, tipo.upper(), cantidad, motivo, fecha))

                # Actualizar stock del producto
                if tipo.upper() == 'ENTRADA':
                    cursor.execute("UPDATE productos SET stock_actual = stock_actual + ? WHERE id = ?",
                                 (cantidad, producto_id))
                else:
                    cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?",
                                 (cantidad, producto_id))

                resultados['exitosos'] += 1

            except Exception as e:
                resultados['errores'].append(f"Fila {idx}: {str(e)}")
                resultados['fallidos'] += 1

        conn.commit()
        conn.close()

        return resultados

    def _obtener_campo(self, diccionario: Dict, nombres_posibles: List[str], default: Any = None) -> Any:
        """Obtiene un campo del diccionario probando múltiples nombres"""
        for nombre in nombres_posibles:
            if nombre in diccionario and diccionario[nombre] is not None:
                return diccionario[nombre]
        return default

    # ==================== EXPORTACIÓN ====================

    def exportar_a_csv(self, archivo_csv: str, tipo: str = "productos") -> bool:
        """Exporta datos a archivo CSV"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if tipo == "productos":
                cursor.execute("""
                    SELECT p.codigo, p.nombre, p.categoria, p.precio_compra, p.precio_venta,
                           p.stock_actual, p.stock_minimo, p.stock_maximo,
                           p.fecha_ingreso, p.fecha_vencimiento, p.dias_vida_util,
                           pr.nombre as proveedor
                    FROM productos p
                    LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                """)
                headers = ['codigo', 'nombre', 'categoria', 'precio_compra', 'precio_venta',
                          'stock_actual', 'stock_minimo', 'stock_maximo',
                          'fecha_ingreso', 'fecha_vencimiento', 'dias_vida_util', 'proveedor']

            elif tipo == "proveedores":
                cursor.execute("SELECT nombre, contacto, telefono, email, direccion FROM proveedores")
                headers = ['nombre', 'contacto', 'telefono', 'email', 'direccion']

            elif tipo == "movimientos":
                cursor.execute("""
                    SELECT p.codigo as producto_codigo, m.tipo, m.cantidad, m.motivo, m.fecha
                    FROM movimientos m
                    JOIN productos p ON m.producto_id = p.id
                    ORDER BY m.fecha DESC
                """)
                headers = ['producto_codigo', 'tipo', 'cantidad', 'motivo', 'fecha']

            else:
                conn.close()
                return False

            datos = cursor.fetchall()
            conn.close()

            with open(archivo_csv, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(datos)

            return True

        except Exception as e:
            print(f"Error al exportar: {e}")
            return False

    def exportar_a_excel(self, archivo_excel: str, tipo: str = "productos") -> bool:
        """Exporta datos a archivo Excel"""
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            workbook = openpyxl.Workbook()
            sheet = workbook.active

            if tipo == "productos":
                sheet.title = "Productos"
                cursor.execute("""
                    SELECT p.codigo, p.nombre, p.categoria, p.precio_compra, p.precio_venta,
                           p.stock_actual, p.stock_minimo, p.stock_maximo,
                           p.fecha_ingreso, p.fecha_vencimiento, p.dias_vida_util,
                           pr.nombre as proveedor
                    FROM productos p
                    LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                """)
                headers = ['Código', 'Nombre', 'Categoría', 'Precio Compra', 'Precio Venta',
                          'Stock Actual', 'Stock Mínimo', 'Stock Máximo',
                          'Fecha Ingreso', 'Fecha Vencimiento', 'Días Vida Útil', 'Proveedor']

            elif tipo == "proveedores":
                sheet.title = "Proveedores"
                cursor.execute("SELECT nombre, contacto, telefono, email, direccion FROM proveedores")
                headers = ['Nombre', 'Contacto', 'Teléfono', 'Email', 'Dirección']

            elif tipo == "movimientos":
                sheet.title = "Movimientos"
                cursor.execute("""
                    SELECT p.codigo as producto_codigo, m.tipo, m.cantidad, m.motivo, m.fecha
                    FROM movimientos m
                    JOIN productos p ON m.producto_id = p.id
                    ORDER BY m.fecha DESC
                    LIMIT 10000
                """)
                headers = ['Producto Código', 'Tipo', 'Cantidad', 'Motivo', 'Fecha']

            else:
                conn.close()
                return False

            # Escribir headers con estilo
            for col, header in enumerate(headers, 1):
                cell = sheet.cell(row=1, column=col)
                cell.value = header
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

            # Escribir datos
            datos = cursor.fetchall()
            for row_idx, row_data in enumerate(datos, 2):
                for col_idx, value in enumerate(row_data, 1):
                    sheet.cell(row=row_idx, column=col_idx, value=value)

            conn.close()

            # Ajustar ancho de columnas
            for column in sheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                sheet.column_dimensions[column_letter].width = adjusted_width

            workbook.save(archivo_excel)
            return True

        except ImportError:
            print("Instalar openpyxl: pip install openpyxl")
            return False
        except Exception as e:
            print(f"Error al exportar: {e}")
            return False

    def exportar_a_json(self, archivo_json: str, tipo: str = "productos") -> bool:
        """Exporta datos a archivo JSON"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if tipo == "productos":
                cursor.execute("""
                    SELECT p.id, p.codigo, p.nombre, p.categoria, p.precio_compra, p.precio_venta,
                           p.stock_actual, p.stock_minimo, p.stock_maximo,
                           p.fecha_ingreso, p.fecha_vencimiento, p.dias_vida_util,
                           p.proveedor_id, pr.nombre as proveedor_nombre
                    FROM productos p
                    LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                """)
                headers = ['id', 'codigo', 'nombre', 'categoria', 'precio_compra', 'precio_venta',
                          'stock_actual', 'stock_minimo', 'stock_maximo',
                          'fecha_ingreso', 'fecha_vencimiento', 'dias_vida_util',
                          'proveedor_id', 'proveedor_nombre']

            elif tipo == "proveedores":
                cursor.execute("SELECT id, nombre, contacto, telefono, email, direccion FROM proveedores")
                headers = ['id', 'nombre', 'contacto', 'telefono', 'email', 'direccion']

            elif tipo == "movimientos":
                cursor.execute("""
                    SELECT m.id, m.producto_id, p.codigo as producto_codigo, p.nombre as producto_nombre,
                           m.tipo, m.cantidad, m.motivo, m.fecha
                    FROM movimientos m
                    JOIN productos p ON m.producto_id = p.id
                    ORDER BY m.fecha DESC
                """)
                headers = ['id', 'producto_id', 'producto_codigo', 'producto_nombre',
                          'tipo', 'cantidad', 'motivo', 'fecha']

            else:
                conn.close()
                return False

            datos = cursor.fetchall()
            conn.close()

            # Convertir a lista de diccionarios
            resultado = []
            for fila in datos:
                item = {headers[i]: fila[i] for i in range(len(headers))}
                resultado.append(item)

            with open(archivo_json, 'w', encoding='utf-8') as file:
                json.dump({tipo: resultado}, file, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error al exportar: {e}")
            return False

    # ==================== UTILIDADES ====================

    def obtener_plantilla_csv(self, tipo: str = "productos") -> str:
        """Genera un archivo CSV de plantilla para importación"""
        plantillas = {
            'productos': ['codigo', 'nombre', 'categoria', 'precio_compra', 'precio_venta',
                         'stock_actual', 'stock_minimo', 'stock_maximo', 'proveedor_id',
                         'fecha_ingreso', 'fecha_vencimiento', 'dias_vida_util'],
            'proveedores': ['nombre', 'contacto', 'telefono', 'email', 'direccion'],
            'movimientos': ['producto_codigo', 'tipo', 'cantidad', 'motivo', 'fecha']
        }

        if tipo not in plantillas:
            return None

        archivo = f"plantilla_{tipo}.csv"

        try:
            with open(archivo, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(plantillas[tipo])

                # Añadir una fila de ejemplo
                if tipo == 'productos':
                    writer.writerow(['PROD001', 'Producto Ejemplo', 'Categoría', '10.00', '15.00',
                                   '50', '10', '100', '', '2025-01-13', '', ''])
                elif tipo == 'proveedores':
                    writer.writerow(['Proveedor Ejemplo', 'Juan Pérez', '555-1234',
                                   'contacto@ejemplo.com', 'Calle 123'])
                elif tipo == 'movimientos':
                    writer.writerow(['PROD001', 'ENTRADA', '10', 'Compra', '2025-01-13'])

            return archivo

        except Exception as e:
            print(f"Error al crear plantilla: {e}")
            return None

    def validar_datos_importacion(self, archivo: str, tipo: str) -> Dict[str, Any]:
        """Valida datos antes de importar (previsualización)"""
        try:
            # Detectar formato
            ext = os.path.splitext(archivo)[1].lower()

            if ext == '.csv':
                with open(archivo, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file)
                    datos = list(reader)[:10]  # Solo primeras 10 filas
            elif ext in ['.xlsx', '.xls']:
                import openpyxl
                workbook = openpyxl.load_workbook(archivo)
                sheet = workbook.active
                headers = [cell.value for cell in sheet[1]]
                datos = []
                for row in list(sheet.iter_rows(min_row=2, values_only=True))[:10]:
                    fila = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
                    datos.append(fila)
            elif ext == '.json':
                with open(archivo, 'r', encoding='utf-8') as file:
                    contenido = json.load(file)
                    if isinstance(contenido, dict) and tipo in contenido:
                        datos = contenido[tipo][:10]
                    else:
                        datos = contenido[:10]
            else:
                return {'valido': False, 'error': 'Formato no soportado'}

            return {
                'valido': True,
                'total_filas': len(datos),
                'preview': datos,
                'columnas': list(datos[0].keys()) if datos else []
            }

        except Exception as e:
            return {'valido': False, 'error': str(e)}

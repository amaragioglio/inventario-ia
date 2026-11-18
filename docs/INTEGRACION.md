# 🔗 Documentación Completa de Integración
## Sistema de Inventario con IA - Versión 2.1

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Métodos de Integración](#métodos-de-integración)
3. [Importación de Datos](#importación-de-datos)
4. [Exportación de Datos](#exportación-de-datos)
5. [API REST](#api-rest)
6. [Integración con n8n](#integración-con-n8n)
7. [Casos de Uso Reales](#casos-de-uso-reales)
8. [Migración desde Otros Sistemas](#migración-desde-otros-sistemas)

---

## 🚀 Introducción

Este sistema está diseñado para **integrarse fácilmente con cualquier sistema existente**. Ya sea que tengas:
- Un sistema POS (Punto de Venta)
- Un ERP empresarial
- Hojas de cálculo Excel
- Bases de datos SQL
- Sistemas en la nube

**Podrás conectarte en minutos**, no en semanas.

### Factor Diferenciador

Nuestra ventaja competitiva: **IA aplicada a inventarios**
- Análisis predictivo automático
- Sugerencias inteligentes de compra
- Detección de patrones de venta
- Automatizaciones con n8n
- Toma de decisiones basada en datos

---

## 📊 Métodos de Integración

### 1. Importación/Exportación de Archivos
**Ideal para**: Migración inicial, sincronización manual
- Formatos: CSV, Excel (.xlsx, .xls), JSON
- Fácil de usar desde la interfaz gráfica
- Validación previa de datos

### 2. API REST
**Ideal para**: Integración en tiempo real, sistemas automáticos
- Endpoints CRUD completos
- Autenticación por token
- Documentación interactiva
- Compatible con cualquier lenguaje

### 3. Webhooks (n8n)
**Ideal para**: Automatizaciones, notificaciones
- 15 tipos de eventos
- Payloads completos con análisis IA
- Sin programación necesaria

---

## 📥 Importación de Datos

### Desde la Interfaz Gráfica

#### Paso 1: Abrir el Importador
```
1. Menú → Integración → Importar Datos
2. Se abre la ventana de Integrador de Datos
```

#### Paso 2: Seleccionar Tipo de Datos
- **Productos**: Inventario completo
- **Proveedores**: Lista de proveedores
- **Movimientos**: Historial de entradas/salidas

#### Paso 3: Seleccionar Archivo
- Formatos aceptados: CSV, Excel, JSON
- Botón "Examinar" para buscar archivo

#### Paso 4: Previsualizar
- Botón "Previsualizar" para validar datos
- Muestra primeras 10 filas
- Detecta errores antes de importar

#### Paso 5: Importar
- Botón "Importar"
- Muestra progreso en tiempo real
- Reporte final con éxitos y errores

### Formatos de Archivo

#### CSV - Productos
```csv
codigo,nombre,categoria,precio_compra,precio_venta,stock_actual,stock_minimo,stock_maximo
PROD001,Coca Cola 2L,Bebidas,2.50,3.50,100,10,200
PROD002,Arroz San Jorge 1kg,Abarrotes,3.80,5.20,50,15,100
```

#### Excel - Proveedores
| nombre | contacto | telefono | email | direccion |
|--------|----------|----------|-------|-----------|
| Bebidas Universal | Juan Pérez | 555-1234 | juan@bebidas.com | Av. Principal 123 |

#### JSON - Movimientos
```json
{
  "movimientos": [
    {
      "producto_codigo": "PROD001",
      "tipo": "ENTRADA",
      "cantidad": 50,
      "motivo": "Compra a proveedor",
      "fecha": "2025-01-13"
    }
  ]
}
```

### Mapeo Flexible de Campos

El sistema reconoce **múltiples nombres** para el mismo campo:

| Campo Sistema | Nombres Alternativos |
|---------------|----------------------|
| codigo | code, sku, id |
| nombre | name, producto, product |
| precio_compra | costo, cost, purchase_price |
| precio_venta | precio, price, sale_price |
| stock_actual | stock, cantidad, quantity |

### Plantillas Descargables

En la pestaña "Plantillas":
- Descarga CSV de ejemplo
- Incluye fila de muestra
- Edita con Excel o cualquier editor
- Importa con un clic

---

## 📤 Exportación de Datos

### Desde la Interfaz Gráfica

```
1. Menú → Integración → Exportar Datos
2. Seleccionar tipo: Productos/Proveedores/Movimientos
3. Seleccionar formato: CSV/Excel/JSON
4. Clic en "Exportar Ahora"
5. Archivo guardado en carpeta del programa
```

### Casos de Uso

**CSV**: Para importar en Excel, Google Sheets
**Excel**: Para reportes profesionales con formato
**JSON**: Para integración con APIs, sistemas web

### Ejemplo de Exportación Excel

Características:
- Encabezados con estilo (fondo azul, texto blanco)
- Columnas autoajustadas
- Todos los datos actuales
- Listo para compartir

---

## 🌐 API REST

### Instalación

```bash
# Instalar dependencias
pip install flask flask-cors

# Iniciar servidor
python api_rest.py
```

Servidor inicia en: `http://localhost:5000`

### Autenticación

**Token**: el valor de `API_TOKEN` en tu archivo `.env` (si no lo defines, se genera uno aleatorio en cada arranque y se muestra en la consola)

En headers de la petición:
```
Authorization: Bearer TU_API_TOKEN
```

**Nota**: Solo se requiere para POST, PUT, DELETE

### Endpoints Principales

#### Listar Productos
```http
GET /api/productos

Query Params (opcionales):
- categoria: Filtrar por categoría
- stock_bajo: true - Solo con stock bajo
- limit: Número de resultados (default: 100)
- offset: Para paginación

Response:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "codigo": "PROD001",
      "nombre": "Coca Cola 2L",
      "categoria": "Bebidas",
      "precio_compra": 2.50,
      "precio_venta": 3.50,
      "stock_actual": 100,
      "stock_minimo": 10,
      "stock_maximo": 200,
      "proveedor_nombre": "Bebidas Universal"
    }
  ]
}
```

#### Crear Producto
```http
POST /api/productos
Authorization: Bearer TU_API_TOKEN
Content-Type: application/json

Body:
{
  "codigo": "PROD003",
  "nombre": "Leche Gloria 1L",
  "categoria": "Lácteos",
  "precio_compra": 3.20,
  "precio_venta": 4.50,
  "stock_actual": 80,
  "stock_minimo": 20,
  "stock_maximo": 150,
  "proveedor_id": 2
}

Response:
{
  "success": true,
  "data": {"id": 3},
  "message": "Producto creado"
}
```

#### Actualizar Producto
```http
PUT /api/productos/3
Authorization: Bearer TU_API_TOKEN
Content-Type: application/json

Body:
{
  "precio_venta": 4.80,
  "stock_actual": 75
}

Response:
{
  "success": true,
  "data": {"id": 3},
  "message": "Producto actualizado"
}
```

#### Registrar Movimiento
```http
POST /api/movimientos
Authorization: Bearer TU_API_TOKEN
Content-Type: application/json

Body:
{
  "producto_id": 1,
  "tipo": "SALIDA",
  "cantidad": 5,
  "motivo": "Venta"
}

Response:
{
  "success": true,
  "data": {"id": 45},
  "message": "Movimiento registrado"
}
```

#### Obtener Estadísticas
```http
GET /api/estadisticas

Response:
{
  "success": true,
  "data": {
    "total_productos": 150,
    "stock_bajo": 12,
    "agotados": 3,
    "valor_total_inventario": 45678.50,
    "movimientos_hoy": 23
  }
}
```

### Ejemplos de Integración

#### Python
```python
import requests

url = "http://localhost:5000/api/productos"
headers = {"Authorization": "Bearer TU_API_TOKEN"}

# Crear producto
data = {
    "codigo": "PROD004",
    "nombre": "Galletas Oreo",
    "precio_compra": 1.50,
    "precio_venta": 2.00
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

#### JavaScript/Node.js
```javascript
const axios = require('axios');

const url = 'http://localhost:5000/api/productos';
const headers = {
  'Authorization': 'Bearer TU_API_TOKEN'
};

const data = {
  codigo: 'PROD005',
  nombre: 'Detergente Ariel',
  precio_compra: 8.50,
  precio_venta: 12.00
};

axios.post(url, data, { headers })
  .then(response => console.log(response.data))
  .catch(error => console.error(error));
```

#### cURL
```bash
curl -X POST http://localhost:5000/api/productos \
  -H "Authorization: Bearer TU_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "PROD006",
    "nombre": "Shampoo Pantene",
    "precio_compra": 7.00,
    "precio_venta": 10.50
  }'
```

---

## 🔄 Integración con n8n

Ver `DOCUMENTACION_N8N.md` para detalles completos.

### Resumen

1. **Configurar Webhook en n8n**
2. **Configurar en App**: Menú → Configuración → Configurar n8n
3. **Recibir 15 tipos de eventos automáticos**

### Eventos Disponibles:
- `stock_bajo` - Producto necesita reabastecimiento
- `producto_proximo_vencer` - Productos cerca de vencer
- `analisis_diario` - Reporte completo diario
- `sugerencias_promocion` - IA sugiere promociones
- Y 11 eventos más...

---

## 💡 Casos de Uso Reales

### Caso 1: Migración desde Excel

**Situación**: Minimarket con inventario en Excel

**Proceso**:
1. Exportar Excel a CSV
2. Abrir App → Integración → Importar Datos
3. Seleccionar CSV
4. Previsualizar
5. Importar
6. ¡Listo en 2 minutos!

**Resultado**: 500 productos migrados correctamente

---

### Caso 2: Integración con POS Existente

**Situación**: Tiene sistema de caja, quiere IA para gestión

**Solución**:
1. POS tiene base de datos SQL
2. Exportar SQL a CSV mensualmente
3. Importar a nuestro sistema
4. IA analiza patrones
5. Recibir sugerencias inteligentes
6. (Opcional) Integrar con API para tiempo real

**Resultado**: IA optimiza compras basado en ventas reales

---

### Caso 3: Sincronización Bidireccional

**Situación**: Quiere que ambos sistemas estén sincronizados

**Solución con n8n**:
```
Sistema POS → Webhook → n8n → API nuestro sistema
   ↑                                    ↓
   └────────── n8n ← Webhook ←─────────┘
```

1. Cada venta en POS → llama API nuestra
2. IA analiza datos
3. Envía eventos a n8n
4. n8n actualiza POS con sugerencias

**Resultado**: Ambos sistemas sincronizados automáticamente

---

### Caso 4: Dashboard Unificado

**Situación**: Múltiples sucursales, quiere vista consolidada

**Solución**:
1. Cada sucursal exporta datos diarios
2. Sistema central importa automáticamente
3. IA analiza TODAS las sucursales
4. Dashboard muestra comparativas
5. Alertas inteligentes por sucursal

**Resultado**: Visión consolidada con IA para toda la cadena

---

## 🔧 Migración desde Otros Sistemas

### Desde Sistemas POS Populares

#### 1. Desde Loyverse POS
```
1. Loyverse → Reportes → Exportar Productos (CSV)
2. Abrir CSV, verificar columnas
3. Importar a nuestro sistema
4. Mapeo automático de campos
```

#### 2. Desde Square POS
```
1. Square Dashboard → Items → Export
2. Descargar CSV
3. Importar con nuestro sistema
4. Productos listos para IA
```

#### 3. Desde Clover POS
```
1. Clover → Inventory → Export
2. Convertir a formato CSV si es necesario
3. Usar plantilla como guía
4. Importar
```

### Desde Sistemas ERP

#### SAP, Oracle, Microsoft Dynamics
1. Exportar desde ERP a CSV/Excel
2. Usar plantilla como referencia
3. Mapear campos manualmente si necesario
4. Importar por lotes (recomendado 1000 productos a la vez)

### Desde Bases de Datos SQL

#### MySQL, PostgreSQL, SQL Server
```sql
-- Exportar productos
SELECT
    codigo as codigo,
    nombre as nombre,
    categoria,
    precio_compra,
    precio_venta,
    stock_actual,
    stock_minimo,
    stock_maximo
FROM productos
INTO OUTFILE 'productos.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

Luego importar CSV a nuestro sistema.

---

## 📊 Ventajas Competitivas

### ¿Por qué elegir este sistema?

#### 1. IA Integrada
- No solo guardas datos, **obtén inteligencia**
- Predicción de demanda automática
- Sugerencias de compra optimizadas
- Detección de patrones de venta

#### 2. Integración Universal
- Compatible con **cualquier sistema**
- Múltiples formatos de importación
- API REST estándar
- Webhooks para automatización

#### 3. Sin Curva de Aprendizaje
- Interfaz intuitiva
- Asistentes paso a paso
- Plantillas incluidas
- Documentación completa

#### 4. Costo-Beneficio
- Instalación única
- Sin suscripciones mensuales
- Sin dependencias de internet (excepto webhooks)
- Escalable según necesidades

---

## 🎯 Propuesta de Valor para Negocios

### Para el Dueño del Minimarket
- "Sube tu Excel y en 2 minutos tienes IA analizando tu inventario"
- "Nunca más te quedarás sin stock de productos clave"
- "Reduce pérdidas por vencimiento en 85%"

### Para Cadenas de Tiendas
- "Consolida el inventario de todas tus sucursales"
- "Análisis comparativo automático entre tiendas"
- "Optimización de compras centralizada"

### Para Distribuidores
- "Conecta con tus clientes automáticamente"
- "Predice demanda de tus productos"
- "Automatiza pedidos recurrentes"

---

## 🚀 Primeros Pasos

### Instalación Rápida

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar aplicación principal
python main.py

# 3. (Opcional) Iniciar API REST
python api_rest.py
```

### Configuración Inicial

1. **Importar Datos Existentes**
   - Menú → Integración → Importar Datos
   - Descargar plantilla si es necesario
   - Importar archivo

2. **Configurar n8n** (Opcional pero recomendado)
   - Menú → Configuración → Configurar n8n
   - Pegar URL del webhook
   - Probar conexión

3. **Empezar a Usar**
   - Dashboard muestra estadísticas
   - IA analiza automáticamente
   - Recibes alertas inteligentes

---

## 📞 Soporte Técnico

### Documentación Disponible
- `README.md` - Guía general
- `DOCUMENTACION_N8N.md` - Integración n8n
- `DOCUMENTACION_INTEGRACION.md` - Este documento
- `MEJORAS_FINALES.md` - Últimas mejoras

### Ayuda en la Aplicación
- Menú → Ayuda → Documentación n8n
- Menú → Integración → API REST (info)

### Ejemplos Incluidos
- Plantillas CSV descargables
- Ejemplos de código en documentación
- API con endpoint de documentación

---

## 📈 Roadmap Futuro

### Próximas Integraciones
- [ ] Connector para WooCommerce
- [ ] Connector para Shopify
- [ ] Integración directa con QuickBooks
- [ ] Exportación a SAP
- [ ] Webhook bidireccional automático

### Mejoras Planificadas
- [ ] Dashboard web responsive
- [ ] App móvil (iOS/Android)
- [ ] Machine Learning avanzado
- [ ] Reportes personalizables
- [ ] Multi-idioma

---

## ✅ Checklist de Integración

Para garantizar una integración exitosa:

- [ ] Datos respaldados del sistema anterior
- [ ] Formato de archivo validado (CSV/Excel/JSON)
- [ ] Mapeo de campos verificado
- [ ] Previsualización realizada
- [ ] Importación de prueba con 10 productos
- [ ] Importación completa exitosa
- [ ] Verificación de datos en dashboard
- [ ] n8n configurado (si aplica)
- [ ] API REST probada (si aplica)
- [ ] Personal capacitado en uso básico

---

## 🎉 Conclusión

Este sistema no es solo un inventario más. Es una **plataforma de inteligencia empresarial** que:

✅ Se integra con **cualquier sistema existente**
✅ Proporciona **IA aplicada a tu negocio**
✅ Automatiza **decisiones repetitivas**
✅ Ahorra **tiempo y dinero**
✅ Escala **según tus necesidades**

**¿Listo para empezar?**

1. Instala el sistema
2. Importa tus datos
3. Deja que la IA trabaje por ti

---

*Documentación generada: 13 de Enero, 2025*
*Versión del Sistema: 2.1*
*Contacto: Consulta README.md para más información*

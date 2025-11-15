# Sistema de Inventario Inteligente para Minimarket

Sistema completo de gestión de inventario con interfaz moderna (estilo Apple/macOS), detección automática de stock bajo, pedidos automáticos e integración con n8n e IA.

## Características

- **Gestión de Productos**: CRUD completo de productos con control de stock
- **Pedidos Automáticos**: Genera pedidos cuando el stock está bajo (nuevo!)
- **Integración n8n + IA**: Usa IA (OpenAI/ChatGPT) para decidir cantidades óptimas (nuevo!)
- **Notificaciones Inteligentes**: Alertas por WhatsApp, Email, Telegram con n8n (nuevo!)
- **API REST**: Endpoints para integración con sistemas externos (nuevo!)
- **Gestión de Proveedores**: Administra proveedores y conecta productos con sus proveedores
- **Control de Movimientos**: Registra todas las entradas y salidas de stock
- **Dashboard Intuitivo**: Vista general con estadísticas en tiempo real
- **Reportes**: Genera reportes de stock, valor de inventario y movimientos
- **Interfaz Moderna**: Diseño estilo Apple/macOS con efectos hover y animaciones

## Requisitos

- Python 3.7 o superior
- tkinter (incluido con Python)
- SQLite3 (incluido con Python)
- Flask (para API REST)
- flask-cors (para CORS)
- requests (para webhooks)

## Instalación

### Instalar Dependencias

```bash
pip install -r requirements.txt
```

O instalar manualmente:
```bash
pip install Flask flask-cors requests
```

## Inicio Rápido

### Opcion 1: Ejecutar directamente con Python

1. Asegurate de tener Python instalado
2. Navega a la carpeta del proyecto
3. Ejecuta:
```bash
python main.py
```

### Opcion 2: Crear ejecutable (.exe)

1. Instala PyInstaller:
```bash
pip install pyinstaller
```

2. Ejecuta el script de compilacion:
```bash
python crear_ejecutable.py
```

3. El ejecutable estara en la carpeta `dist/SistemaInventario`

## Uso

### Dashboard
- Muestra estadísticas generales del inventario
- Lista de productos con stock bajo
- Valor total del inventario

### Productos
- **Nuevo Producto**: Crea un nuevo producto en el inventario
- **Editar**: Doble clic sobre un producto para editarlo
- **Eliminar**: Desactiva un producto
- **Entrada Stock**: Registra entrada de mercancía
- **Salida Stock**: Registra salida de mercancía
- **Buscar**: Busca productos por código o nombre

### Proveedores
- **Nuevo Proveedor**: Registra un nuevo proveedor
- **Editar**: Actualiza información del proveedor
- **Ver Productos**: Muestra todos los productos de un proveedor
- Conecta productos con sus proveedores para facilitar pedidos

### Pedidos Auto (NUEVO!)
- Ver pedidos automáticos generados por el sistema
- Estados: PENDIENTE → PROCESADO → RECIBIDO → CANCELADO
- **Marcar Recibido**: Actualiza el stock automáticamente
- **Marcar Procesado**: Indica que el pedido fue enviado al proveedor
- **Cancelar**: Cancela un pedido pendiente
- Los pedidos se generan automáticamente cuando stock_actual <= stock_minimo

### Movimientos
- Historial completo de entradas y salidas
- Tracking de quién realizó cada movimiento
- Fecha y hora de cada operación

### Reportes
- **Reporte de Stock**: Estado actual de todos los productos
- **Reporte de Valor**: Valor total del inventario y ganancias potenciales
- **Reporte de Movimientos**: Estadísticas de entradas y salidas

### ⚙️ Configuración (NUEVO!)
- **URL de Webhook de n8n**: Configura la integración con n8n
- **Notificaciones Automáticas**: Activa/desactiva el envío de webhooks
- **Probar Conexión**: Verifica que el webhook funcione correctamente
- **Ver Guía**: Abre el archivo INTEGRACION_N8N.md con instrucciones completas
- **Estado del Sistema**: Muestra si el webhook está configurado y si las notificaciones están activas

### Alertas
- Notificaciones automáticas de stock bajo
- Botón de alertas en la barra superior muestra la cantidad pendiente
- Sistema de verificación cada 5 minutos

## Estructura del Proyecto

```
inventario/
├── main.py                    # Aplicación principal con interfaz Tkinter
├── database.py                # Gestión de base de datos SQLite
├── models.py                  # Modelos de datos (Producto, Proveedor, Pedido, etc.)
├── notifications.py           # Sistema de notificaciones y alertas
├── webhook_client.py          # Cliente para enviar webhooks a n8n (NUEVO!)
├── webhook_server.py          # Servidor API REST para n8n (NUEVO!)
├── cargar_datos_prueba.py     # Script para cargar datos de ejemplo
├── crear_ejecutable.py        # Script para generar ejecutable
├── INTEGRACION_N8N.md         # Guía completa de integración con n8n (NUEVO!)
├── README.md                  # Este archivo
├── requirements.txt           # Dependencias del proyecto
└── inventario.db              # Base de datos (se crea automáticamente)
```

## Base de Datos

El sistema utiliza SQLite y crea automáticamente la base de datos con las siguientes tablas:

- **productos**: Información de productos y stock
- **proveedores**: Datos de proveedores
- **movimientos**: Historial de entradas/salidas
- **alertas**: Notificaciones de stock bajo
- **pedidos_automaticos**: Pedidos generados automáticamente (NUEVO!)
- **configuracion**: Parámetros del sistema (webhook URL, etc.)

## Integración con n8n e IA

### ¿Qué es n8n?
n8n es una herramienta de automatización que te permite conectar diferentes servicios (como tu inventario, OpenAI, WhatsApp, Email, etc.) y crear flujos de trabajo automáticos.

### ¿Qué puede hacer con n8n + IA?
- **Decisiones inteligentes**: La IA analiza patrones de venta y sugiere cantidades óptimas a pedir
- **Notificaciones multicanal**: Recibe alertas por WhatsApp, Email, Telegram, Slack
- **Emails automáticos**: Envía pedidos directamente a tus proveedores
- **Reportes inteligentes**: Genera análisis semanales con IA
- **Detección de anomalías**: Identifica problemas en el inventario

### Configuración Rápida

#### 1. Iniciar el Servidor de API
```bash
python webhook_server.py
```
El servidor estará disponible en `http://localhost:5000`

#### 2. Configurar en la Aplicación
1. Abre la aplicación principal: `python main.py`
2. Ve a la pestaña **⚙️ Configuración**
3. Ingresa tu URL de webhook de n8n
4. Activa las notificaciones automáticas
5. Guarda la configuración
6. Prueba la conexión

#### 3. Crear Flujos en n8n
Consulta el archivo `INTEGRACION_N8N.md` para ver ejemplos completos de flujos, incluyendo:
- Pedido inteligente con IA (OpenAI)
- Notificaciones por WhatsApp/Email/Telegram
- Reportes semanales automáticos

### API REST Endpoints

**Consulta:**
- `GET /api/health` - Verificar que el servidor esté funcionando
- `GET /api/productos/stock-bajo` - Obtener productos con stock bajo
- `GET /api/pedidos/pendientes` - Obtener pedidos pendientes
- `GET /api/alertas` - Obtener alertas no leídas

**Acciones:**
- `POST /api/pedidos/crear` - Crear un pedido
- `POST /api/pedidos/<id>/procesar` - Marcar pedido como procesado
- `POST /api/pedidos/<id>/recibir` - Marcar pedido como recibido (actualiza stock)
- `POST /webhook/stock-bajo` - Recibir decisiones de IA desde n8n

Ver `INTEGRACION_N8N.md` para ejemplos de uso completos con requests/responses.

## Flujo de Trabajo Automático con IA

1. **Stock bajo detectado**: El sistema detecta que `stock_actual <= stock_minimo`
2. **Webhook enviado**: Se envía un webhook a n8n con datos del producto y proveedor
3. **IA analiza**: OpenAI analiza historial de ventas y sugiere cantidad óptima
4. **Pedido creado**: El sistema genera un pedido automático
5. **Notificaciones**: El dueño recibe alertas por WhatsApp/Email/Telegram
6. **Email al proveedor**: n8n envía automáticamente un email con el pedido
7. **Seguimiento**: El pedido se marca como PROCESADO → RECIBIDO
8. **Stock actualizado**: Al marcar como RECIBIDO, el stock se actualiza automáticamente

## Flujo de Trabajo Típico (Manual)

1. **Registrar Proveedores**: Primero registra tus proveedores
2. **Agregar Productos**: Crea productos y asocialos con proveedores
3. **Configurar Stock Minimo**: Define el stock minimo para cada producto
4. **Registrar Movimientos**: Usa Entrada/Salida para actualizar stock
5. **Monitorear Alertas**: Revisa las alertas de stock bajo regularmente
6. **Generar Reportes**: Analiza el estado de tu inventario

## Solución de Problemas

### Error al iniciar la aplicación
- Verifica que tienes Python 3.7+ instalado: `python --version`
- Instala las dependencias: `pip install -r requirements.txt`
- Asegúrate de estar en el directorio correcto

### Error al importar Flask
- Instala Flask: `pip install Flask flask-cors requests`
- Si usas un entorno virtual, actívalo primero

### No se crean pedidos automáticos
- Verifica que el producto tenga un **proveedor asignado**
- Revisa que el `stock_actual <= stock_minimo`
- Comprueba la pestaña "Pedidos Auto" para ver los pedidos creados

### Los webhooks no funcionan
1. Asegúrate de que `webhook_server.py` esté corriendo
2. Ve a **⚙️ Configuración** y verifica la URL del webhook
3. Prueba la conexión con el botón **🧪 Probar Conexión**
4. Verifica que n8n esté accesible desde tu red

### No se envían notificaciones a n8n
- Ve a **⚙️ Configuración**
- Activa el checkbox "Activar notificaciones automáticas"
- Guarda la configuración
- Verifica que la URL del webhook sea correcta
- Revisa que n8n tenga un workflow activo escuchando en esa URL

### Base de datos bloqueada
- Cierra todas las instancias de la aplicación
- Si el problema persiste, cierra cualquier programa que pueda estar accediendo a `inventario.db`

### Alertas no aparecen
- Las alertas se verifican cada 5 minutos automáticamente
- Puedes forzar la verificación actualizando el dashboard
- Verifica que el stock esté realmente por debajo del mínimo

## Tecnologías Utilizadas

- **Python 3**: Lenguaje de programación principal
- **Tkinter**: Interfaz gráfica de usuario (GUI)
- **SQLite**: Base de datos local
- **Flask**: Servidor API REST
- **n8n**: Plataforma de automatización de workflows
- **OpenAI/ChatGPT**: Inteligencia artificial para decisiones inteligentes

## Créditos

Sistema de inventario inteligente desarrollado para minimarkets con automatización avanzada mediante n8n e IA.

**Características destacadas:**
- Interfaz moderna estilo Apple/macOS
- Pedidos automáticos con IA
- Integración completa con n8n
- Notificaciones multicanal

---

**¡Tu minimarket ahora es inteligente! 🤖🏪**

# Inventario IA

Aplicación de escritorio para gestionar el inventario de minimarkets y pequeños comercios. Registra productos, proveedores y movimientos de stock, y ayuda a decidir cuándo reponer mercancía.

El inventario se guarda en SQLite. La integración opcional con n8n permite enviar alertas y conectar el flujo de reposición con un proveedor de IA.

## Qué puedes hacer

- Registrar productos y sus proveedores, con niveles mínimos y máximos de stock.
- Registrar entradas y salidas de mercancía y consultar el historial.
- Detectar stock bajo, revisar pedidos de reposición y actualizar el stock al recibirlos.
- Consultar reportes de existencias, valor del inventario y movimientos.

## Inicio rápido en Windows

Desde PowerShell, con Git y Python 3.11 con Tkinter:

```powershell
git clone https://github.com/amaragioglio/inventario-ia.git
cd inventario-ia
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

En el primer arranque, la aplicación crea `inventario.db` en la carpeta de trabajo. Conserva una copia de ese archivo si vas a migrar tu instalación o actualizar un clon que ya tenía la base versionada.

Para probar la aplicación con datos de ejemplo, usa una copia separada del proyecto y consulta la [guía de datos de prueba](DATOS_PRUEBA_GENERADOS.md). El script `generar_datos_prueba.py` reemplaza los registros de las tablas de inventario.

## Automatización opcional con n8n

Abre **Configuración** en la aplicación para registrar la URL del webhook de n8n, probar la conexión y activar las notificaciones. En n8n puedes configurar avisos por correo, WhatsApp o Telegram y usar un proveedor de IA para sugerir cantidades de reposición.

Para probar el servidor de webhooks en el mismo equipo, genera un token y arranca el servidor desde PowerShell:

```powershell
$env:API_TOKEN = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
.\.venv\Scripts\python.exe -m flask --app webhook_server run --host 127.0.0.1 --port 5000
```

Configura el mismo token en la credencial de n8n que envía `Authorization: Bearer <token>` al servidor. La aplicación de escritorio funciona por separado. Mantén ambos servidores en un entorno de confianza. Consulta la [guía de integración con n8n](INTEGRACION_N8N.md) para ver el flujo y los endpoints. Si activas un webhook, los datos incluidos en sus avisos se comparten con el servicio que configures.

## Estructura

| Archivo | Función |
| --- | --- |
| `main.py` | Interfaz Tkinter |
| `database.py` y `models.py` | Persistencia en SQLite y operaciones de inventario |
| `webhook_client.py` y `webhook_server.py` | Integración con n8n |
| `crear_ejecutable.py` | Empaquetado para Windows con PyInstaller |

## Licencia

[MIT](LICENSE).

# 🤖 Guía de Integración con n8n + IA

## 📋 Tabla de Contenidos
1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura)
3. [Configuración Inicial](#configuración)
4. [API REST](#api-rest)
5. [Webhooks](#webhooks)
6. [Flujos de n8n](#flujos-n8n)
7. [Ejemplos con IA](#ejemplos-ia)

---

## 🎯 Introducción

Este sistema de inventario está diseñado para integrarse con **n8n** y usar **IA** para tomar decisiones inteligentes sobre pedidos automáticos.

### ¿Qué puede hacer n8n + IA?

- ✅ **Analizar patrones de venta** para predecir cuándo se agotará un producto
- ✅ **Decidir cantidades óptimas** a pedir según tendencias
- ✅ **Notificar al dueño** por WhatsApp, Email, Telegram, etc.
- ✅ **Enviar emails automáticos** a proveedores con pedidos
- ✅ **Generar reportes inteligentes** semanales/mensuales
- ✅ **Detectar anomalías** en el inventario

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────┐
│  Sistema Inventario │
│    (Tkinter App)    │
└──────────┬──────────┘
           │
           │ Detecta stock bajo
           │
           ▼
┌─────────────────────┐
│  webhook_client.py  │
│   (Envía eventos)   │
└──────────┬──────────┘
           │
           │ HTTP POST
           │
           ▼
┌─────────────────────┐
│       n8n           │
│  (Workflow Engine)  │
└──────────┬──────────┘
           │
           ├──────► 🤖 OpenAI/ChatGPT (Decide cantidad)
           ├──────► 📧 Email (Notifica dueño)
           ├──────► 📱 WhatsApp (Alerta urgente)
           ├──────► 📊 Google Sheets (Registro)
           │
           ▼
┌─────────────────────┐
│  webhook_server.py  │
│   (API REST 5000)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Base de Datos     │
│    (SQLite)         │
└─────────────────────┘
```

---

## ⚙️ Configuración Inicial

### Paso 1: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 2: Iniciar Servidor de API

```bash
python webhook_server.py
```

El servidor estará disponible en `http://localhost:5000`. Antes de iniciarlo, configura `API_TOKEN` con un token aleatorio de al menos 24 caracteres. Añade `Authorization: Bearer <tu-token>` a las solicitudes de n8n que consulten o modifiquen el inventario.

### Paso 3: Configurar Webhook de n8n

Opción A - **Desde Python:**
```python
from webhook_client import configurar_n8n

# Configurar webhook de n8n
configurar_n8n('https://tu-n8n.com/webhook/inventario')
```

Opción B - **Desde la App:**
Ir a la interfaz de configuración (próximamente) y configurar la URL del webhook.

---

## 🔌 API REST Endpoints

### 1. Consultar Productos con Stock Bajo

**GET** `/api/productos/stock-bajo`

**Respuesta:**
```json
{
  "success": true,
  "count": 5,
  "productos": [
    {
      "id": 1,
      "codigo": "BEB001",
      "nombre": "Coca Cola 2L",
      "categoria": "Bebidas",
      "stock_actual": 3,
      "stock_minimo": 20,
      "stock_maximo": 150,
      "precio_compra": 1.20,
      "precio_venta": 2.50,
      "proveedor": {
        "id": 2,
        "nombre": "Distribuidora Bebidas Premium",
        "contacto": "Laura Sánchez",
        "telefono": "555-1002",
        "email": "pedidos@bebidaspremium.com"
      },
      "necesita": 117
    }
  ]
}
```

### 2. Obtener Pedidos Pendientes

**GET** `/api/pedidos/pendientes`

**Respuesta:**
```json
{
  "success": true,
  "count": 3,
  "pedidos": [
    {
      "id": 1,
      "producto": {
        "id": 1,
        "nombre": "Coca Cola 2L",
        "codigo": "BEB001"
      },
      "proveedor": {
        "id": 2,
        "nombre": "Distribuidora Bebidas Premium"
      },
      "cantidad_solicitada": 117,
      "estado": "PENDIENTE",
      "fecha_pedido": "2025-01-13 10:30:00",
      "notas": "Pedido automático"
    }
  ]
}
```

### 3. Crear Pedido

**POST** `/api/pedidos/crear`

**Body:**
```json
{
  "producto_id": 1,
  "proveedor_id": 2,
  "cantidad": 120,
  "notas": "Pedido creado desde n8n con IA"
}
```

### 4. Marcar Pedido como Recibido

**POST** `/api/pedidos/1/recibir`

**Respuesta:**
```json
{
  "success": true,
  "message": "Pedido 1 recibido y stock actualizado"
}
```

### 5. Obtener Alertas

**GET** `/api/alertas`

---

## 🎣 Webhooks

### Evento: Stock Bajo

Cuando un producto alcanza su stock mínimo, el sistema envía automáticamente un webhook a n8n:

**Payload enviado a n8n:**
```json
{
  "evento": "stock_bajo",
  "producto": {
    "id": 1,
    "codigo": "BEB001",
    "nombre": "Coca Cola 2L",
    "categoria": "Bebidas",
    "stock_actual": 3,
    "stock_minimo": 20,
    "stock_maximo": 150,
    "precio_compra": 1.20,
    "precio_venta": 2.50
  },
  "proveedor": {
    "id": 2,
    "nombre": "Distribuidora Bebidas Premium",
    "contacto": "Laura Sánchez",
    "telefono": "555-1002",
    "email": "pedidos@bebidaspremium.com",
    "direccion": "Av. Industrial 789"
  },
  "cantidad_recomendada": 117
}
```

### Evento: Notificación al Dueño

**Payload:**
```json
{
  "evento": "notificacion_dueno",
  "tipo": "critico",  // "critico", "advertencia", "info"
  "mensaje": "🚨 CRÍTICO: Coca Cola 2L está AGOTADO",
  "detalles": {
    "producto": "Coca Cola 2L",
    "stock_actual": 0,
    "stock_minimo": 20,
    "proveedor": "Distribuidora Bebidas Premium"
  }
}
```

---

## 🔄 Flujos de n8n Recomendados

### Flujo 1: Pedido Inteligente con IA

```
1. [Webhook Trigger] ← Recibe evento "stock_bajo"
2. [OpenAI Node] ← Analiza historial y decide cantidad
3. [HTTP Request] ← Crea pedido vía API
4. [Email] ← Envía email al proveedor
5. [WhatsApp] ← Notifica al dueño
```

**Prompt para OpenAI:**
```
Eres un asistente de gestión de inventario.

Producto: {{ $json.producto.nombre }}
Stock actual: {{ $json.producto.stock_actual }}
Stock mínimo: {{ $json.producto.stock_minimo }}
Stock máximo: {{ $json.producto.stock_maximo }}
Precio compra: ${{ $json.producto.precio_compra }}
Categoría: {{ $json.producto.categoria }}

Historial de ventas (últimos 30 días): [Aquí iría el historial]

¿Cuántas unidades debería pedir considerando:
- Tendencias de venta
- Estacionalidad
- Presupuesto disponible
- Vida útil del producto

Responde SOLO con un número.
```

### Flujo 2: Notificaciones Inteligentes

```
1. [Webhook Trigger] ← Recibe evento "notificacion_dueno"
2. [Switch Node] ← Separa por tipo (crítico/advertencia/info)
3a. [Si es CRÍTICO] → WhatsApp urgente
3b. [Si es ADVERTENCIA] → Email + Telegram
3c. [Si es INFO] → Solo log en Google Sheets
```

### Flujo 3: Reporte Semanal Automático

```
1. [Schedule Trigger] ← Todos los lunes 8am
2. [HTTP Request] ← GET /api/productos/stock-bajo
3. [OpenAI Node] ← Genera análisis inteligente
4. [Email] ← Envía reporte al dueño
5. [Google Sheets] ← Guarda histórico
```

---

## 🤖 Ejemplos con IA

### Ejemplo 1: Predicción de Ventas

```javascript
// Node de código en n8n
const producto = $input.first().json.producto;
const ventas_diarias = 5; // Obtenido de historial

// Calcular días hasta agotarse
const dias_restantes = producto.stock_actual / ventas_diarias;

// Decidir urgencia
if (dias_restantes <= 2) {
  return {
    urgencia: 'CRITICO',
    cantidad_pedir: producto.stock_maximo,
    mensaje: `Solo quedan ${dias_restantes.toFixed(1)} días de stock`
  };
} else if (dias_restantes <= 5) {
  return {
    urgencia: 'ADVERTENCIA',
    cantidad_pedir: Math.floor(producto.stock_maximo * 0.8),
    mensaje: `Quedan ${dias_restantes.toFixed(1)} días de stock`
  };
}
```

### Ejemplo 2: Email Automático al Proveedor

```
Asunto: Pedido Automático - {{ $json.producto.nombre }}

Estimado/a {{ $json.proveedor.contacto }},

Solicitamos cotización y disponibilidad para el siguiente pedido:

Producto: {{ $json.producto.nombre }}
Código: {{ $json.producto.codigo }}
Cantidad: {{ $json.cantidad_decidida }} unidades
Categoría: {{ $json.producto.categoria }}

Datos de contacto:
Minimarket: [Tu Nombre]
Teléfono: [Tu Teléfono]
Email: [Tu Email]

Por favor, confirmar disponibilidad y tiempo de entrega.

Saludos cordiales,
Sistema Automático de Inventario
```

### Ejemplo 3: WhatsApp Urgente

```
🚨 *ALERTA CRÍTICA*

{{ $json.mensaje }}

📦 Producto: {{ $json.detalles.producto }}
📊 Stock: {{ $json.detalles.stock_actual }} unidades
⚠️ Mínimo: {{ $json.detalles.stock_minimo }} unidades
🏢 Proveedor: {{ $json.detalles.proveedor }}

Revisa el sistema para tomar acción inmediata.
```

---

## 🎛️ Configuración Avanzada

### Variables de Entorno

```bash
# .env
N8N_WEBHOOK_URL=https://tu-n8n.com/webhook/inventario
NOTIFICACIONES_ACTIVAS=true
DUENO_EMAIL=tu@email.com
DUENO_WHATSAPP=+51987654321
DUENO_TELEGRAM_ID=123456789
```

### Webhooks de Respuesta

n8n puede enviar de vuelta decisiones al sistema:

**POST** `http://localhost:5000/webhook/stock-bajo`

**Body:**
```json
{
  "accion": "crear_pedido",  // o "notificar", "ignorar"
  "producto_id": 1,
  "cantidad_sugerida": 150
}
```

---

## 📊 Dashboard Sugerido en n8n

1. **Nodo Schedule**: Ejecutar cada hora
2. **HTTP Request**: GET `/api/productos/stock-bajo`
3. **IF**: Si count > 0
4. **Email**: Notificar al dueño con resumen
5. **Google Sheets**: Actualizar dashboard

---

## 🔐 Seguridad

### Recomendaciones:

1. **Autenticación:** Agregar API Key en headers
2. **HTTPS:** Usar certificados SSL en producción
3. **Rate Limiting:** Limitar peticiones por IP
4. **Validación:** Validar todos los inputs
5. **Logs:** Registrar todas las acciones

---

## 📞 Soporte

¿Necesitas ayuda? Contacta al desarrollador o consulta la documentación de n8n:
- [n8n Docs](https://docs.n8n.io/)
- [OpenAI API](https://platform.openai.com/docs)

---

## 🚀 Próximas Funcionalidades

- [ ] Dashboard web en tiempo real
- [ ] Integración con Slack
- [ ] ML para predicción de demanda
- [ ] Alertas por voz con Twilio
- [ ] Integración con ERPs

---

**¡Tu minimarket ahora es inteligente! 🤖🏪**

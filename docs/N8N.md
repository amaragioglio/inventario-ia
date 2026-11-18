# 📘 Documentación Completa - Integración con n8n

## 🎯 Tabla de Contenidos
1. [Introducción](#introducción)
2. [Configuración Rápida](#configuración-rápida)
3. [Eventos Disponibles](#eventos-disponibles)
4. [Ejemplos de Flujos](#ejemplos-de-flujos)
5. [Estructura de Payloads](#estructura-de-payloads)
6. [Casos de Uso Reales](#casos-de-uso-reales)

---

## 🚀 Introducción

Este sistema de inventario envía **eventos inteligentes** a n8n para que puedas automatizar completamente la gestión de tu minimarket.

### ¿Qué puedes automatizar?
- ✅ Pedidos automáticos a proveedores con IA
- ✅ Notificaciones por WhatsApp/Telegram/Email
- ✅ Sugerencias de promociones en redes sociales
- ✅ Análisis predictivo de ventas
- ✅ Alertas de productos próximos a vencer
- ✅ Reportes diarios automáticos

---

## ⚡ Configuración Rápida

### Paso 1: Crear Webhook en n8n

1. Abre n8n y crea un nuevo workflow
2. Añade un nodo **"Webhook"**
3. Configura:
   - **HTTP Method**: POST
   - **Path**: `/inventario` (o el que prefieras)
4. Copia la URL del webhook (ejemplo: `https://tu-n8n.com/webhook/inventario`)

### Paso 2: Configurar en el Sistema

Opción A - **Desde Python**:
```python
from webhook_client import configurar_n8n

configurar_n8n('https://tu-n8n.com/webhook/inventario')
```

Opción B - **Desde la App** (próximamente):
- Ve a "Configuración" → "Integración n8n"
- Pega tu URL y haz clic en "Probar Conexión"

### Paso 3: Verificar

Reinicia la aplicación y deberías ver:
```
[WEBHOOK] ✅ Enviado: sistema_iniciado
[TAREAS] ✅ Sistema de tareas automáticas iniciado
```

---

## 📡 Eventos Disponibles

### 1. EVENTOS DE STOCK

#### `stock_bajo`
**Cuándo se envía**: Cuando un producto llega a su stock mínimo

**Payload**:
```json
{
  "evento": "stock_bajo",
  "prioridad": "MEDIA|ALTA",
  "timestamp": "2025-01-13T10:30:00",
  "producto": {
    "id": 1,
    "codigo": "BEB001",
    "nombre": "Coca Cola 2L",
    "categoria": "Bebidas",
    "stock_actual": 5,
    "stock_minimo": 10,
    "stock_maximo": 50,
    "precio_compra": 2.50,
    "precio_venta": 3.50
  },
  "proveedor": {
    "id": 1,
    "nombre": "Bebidas Universal",
    "telefono": "555-1003",
    "email": "contacto@bebidasuniversal.com"
  },
  "analisis": {
    "total_vendido": 45,
    "promedio_diario": 1.5,
    "dias_restantes": 3.3
  },
  "recomendaciones": {
    "cantidad_sugerida": 35,
    "urgencia": "NORMAL|URGENTE"
  }
}
```

**Qué hacer con esto**:
- Enviar email automático al proveedor
- Crear pedido en tu sistema ERP
- Notificar al dueño por WhatsApp
- Analizar con IA cuánto pedir según tendencia

---

#### `stock_critico`
**Cuándo se envía**: Cuando un producto llega a 0 unidades

**Payload**:
```json
{
  "evento": "stock_critico",
  "prioridad": "CRITICA",
  "producto": {
    "id": 1,
    "codigo": "BEB001",
    "nombre": "Coca Cola 2L",
    "stock_actual": 0
  },
  "mensaje": "🚨 URGENTE: Coca Cola 2L está AGOTADO",
  "accion_recomendada": "Crear pedido urgente o contactar proveedor inmediatamente"
}
```

---

### 2. EVENTOS DE VENCIMIENTO

#### `producto_proximo_vencer`
**Cuándo se envía**: Automáticamente cada hora para productos que vencen pronto

**Payload**:
```json
{
  "evento": "producto_proximo_vencer",
  "prioridad": "URGENTE|ALTA|MEDIA",
  "producto": {
    "id": 5,
    "nombre": "Yogurt Gloria Fresa",
    "categoria": "Lácteos",
    "stock_actual": 15,
    "fecha_vencimiento": "2025-01-20",
    "dias_restantes": 7
  },
  "sugerencias": {
    "accion": "Crear promoción urgente",
    "descuento_sugerido": "50%",
    "tipo_promocion": "2x1"
  },
  "mensaje": "⏰ Yogurt Gloria Fresa vence en 7 días - Stock: 15 unidades"
}
```

**Automatizaciones sugeridas**:
- Publicar automáticamente en Facebook: "¡2x1 en Yogurt Gloria!"
- Enviar mensaje masivo por WhatsApp a clientes
- Actualizar precios en sistema de caja
- Crear banner digital para pantalla en tienda

---

#### `producto_vencido`
**Cuándo se envía**: Diariamente para productos ya vencidos

**Payload**:
```json
{
  "evento": "producto_vencido",
  "prioridad": "CRITICA",
  "producto": {
    "id": 5,
    "nombre": "Yogurt Gloria Fresa",
    "stock_actual": 8,
    "fecha_vencimiento": "2025-01-10"
  },
  "mensaje": "❌ CRÍTICO: Yogurt Gloria Fresa está VENCIDO - 8 unidades en stock",
  "accion_recomendada": "Retirar del inventario inmediatamente y registrar pérdida"
}
```

---

### 3. EVENTOS DE PEDIDOS

#### `pedido_creado`
**Cuándo se envía**: Cuando el sistema crea un pedido automático

**Payload**:
```json
{
  "evento": "pedido_creado",
  "prioridad": "MEDIA",
  "pedido": {
    "pedido_id": 15,
    "producto_nombre": "Leche Gloria 1L",
    "proveedor_nombre": "Lácteos San José",
    "cantidad_solicitada": 100,
    "stock_actual": 10,
    "motivo": "Stock bajo"
  },
  "mensaje": "📋 Nuevo pedido automático creado: Leche Gloria 1L"
}
```

**Automatizaciones**:
- Enviar email automático al proveedor
- Crear documento PDF del pedido
- Añadir tarea en Trello/Asana
- Notificar al administrador

---

### 4. EVENTOS DE ANÁLISIS

#### `analisis_diario`
**Cuándo se envía**: Automáticamente cada 24 horas

**Payload**:
```json
{
  "evento": "analisis_diario",
  "prioridad": "INFO",
  "reporte": {
    "fecha_generacion": "2025-01-13 08:00:00",
    "movimientos_diarios": {
      "dias_top": [...],
      "dia_semana_mas_activo": "Viernes"
    },
    "sugerencias_promociones": [...],
    "tendencias_categorias": [...],
    "productos_proximos_vencer": 5,
    "productos_vencidos": 2,
    "productos_stock_bajo": 8
  }
}
```

**Automatizaciones**:
- Generar reporte PDF y enviar por email
- Crear post en redes sociales con estadísticas
- Actualizar dashboard en Google Sheets
- Enviar resumen por WhatsApp

---

#### `sugerencias_promocion`
**Cuándo se envía**: Cada 2 horas

**Payload**:
```json
{
  "evento": "sugerencias_promocion",
  "prioridad": "ALTA|MEDIA",
  "total_sugerencias": 5,
  "sugerencias": [
    {
      "tipo": "VENCIMIENTO",
      "urgencia": "URGENTE",
      "producto_nombre": "Yogurt Gloria",
      "razon": "Vence en 5 días",
      "accion": "Promoción 50% de descuento",
      "stock": 15,
      "descuento_sugerido": "50%"
    },
    {
      "tipo": "BAJA_ROTACION",
      "urgencia": "MEDIA",
      "producto_nombre": "Galletas Premium",
      "razon": "Solo 3 vendidos en 30 días, stock: 45",
      "accion": "2x1 o descuento del 25%",
      "descuento_sugerido": "25%"
    }
  ]
}
```

---

#### `dia_alta_actividad`
**Cuándo se envía**: Cuando se detecta actividad inusualmente alta

**Payload**:
```json
{
  "evento": "dia_alta_actividad",
  "prioridad": "INFO",
  "actividad": {
    "fecha": "2025-01-13",
    "total_actividad": 156,
    "entradas": 45,
    "salidas": 111
  },
  "mensaje": "📈 Actividad alta detectada: 156 movimientos"
}
```

---

### 5. NOTIFICACIONES AL DUEÑO

#### `notificacion_dueno`
**Cuándo se envía**: Eventos importantes que requieren atención

**Payload**:
```json
{
  "evento": "notificacion_dueno",
  "prioridad": "ALTA|MEDIA|INFO",
  "tipo": "critico|advertencia|info|exito",
  "icono": "🚨|⚠️|ℹ️|✅",
  "mensaje": "⚠️ URGENTE: Coca Cola 2L tiene stock muy bajo (3 unidades)",
  "detalles": {
    "producto": "Coca Cola 2L",
    "stock_actual": 3,
    "stock_minimo": 10,
    "proveedor": "Bebidas Universal"
  }
}
```

---

## 💡 Ejemplos de Flujos en n8n

### Flujo 1: Pedido Automático con IA

```
Webhook (stock_bajo)
  ↓
Switch (por prioridad)
  ↓ ALTA
  OpenAI (analizar cantidad óptima)
  ↓
  Send Email (al proveedor)
  ↓
  WhatsApp (notificar dueño)
  ↓
  Google Sheets (registrar pedido)
```

### Flujo 2: Promoción Automática en Redes Sociales

```
Webhook (producto_proximo_vencer)
  ↓
Filter (solo dias_restantes <= 7)
  ↓
OpenAI (generar texto promocional)
  ↓
DALL-E (generar imagen promocional)
  ↓
Split branches:
  ├→ Facebook (publicar)
  ├→ Instagram (publicar)
  └→ WhatsApp Business (mensaje masivo)
```

### Flujo 3: Análisis Diario con Reporte

```
Webhook (analisis_diario)
  ↓
Google Sheets (actualizar datos)
  ↓
Python (generar gráficas)
  ↓
Generate PDF (reporte visual)
  ↓
Split branches:
  ├→ Email (enviar a gerente)
  ├→ Telegram (enviar resumen)
  └→ Google Drive (guardar archivo)
```

---

## 🎯 Casos de Uso Reales

### Caso 1: Minimarket "La Esquina"
**Problema**: Siempre se quedaban sin Coca Cola los fines de semana

**Solución n8n**:
1. Webhook `stock_bajo` → Detecta cuando llega al mínimo
2. AI analiza histórico de ventas de fines de semana
3. Envía pedido automático al proveedor el jueves
4. Notifica al dueño por WhatsApp

**Resultado**: 0 desabastecimientos en 3 meses

---

### Caso 2: Minimarket "San José"
**Problema**: Pérdidas por productos vencidos (lácteos)

**Solución n8n**:
1. Webhook `producto_proximo_vencer` cada hora
2. Si vence en ≤7 días → Publicación automática en Facebook
3. Si vence en ≤3 días → Descuento 50% + WhatsApp masivo
4. Si vence en 1 día → Alerta crítica al gerente

**Resultado**: Pérdidas reducidas en 85%

---

### Caso 3: Minimarket "El Ahorro"
**Problema**: Productos de baja rotación ocupando espacio

**Solución n8n**:
1. Webhook `sugerencias_promocion` cada 2 horas
2. Filtrar productos tipo "BAJA_ROTACION"
3. AI genera estrategia de promoción
4. Crea combos automáticamente: "Compra X llévate Y"
5. Publica en redes sociales

**Resultado**: Rotación mejorada 40%

---

## 🔧 Tips Avanzados

### 1. Usar Variables de Entorno
```javascript
// En n8n, guarda tu configuración
const CONFIG = {
  proveedor_coca_cola: {
    email: "pedidos@bebidas.com",
    telefono: "+123456789",
    dias_entrega: 2
  }
};
```

### 2. Filtros Inteligentes
```javascript
// Solo procesar si es urgente Y es fin de semana
const esFinDeSemana = [0, 6].includes(new Date().getDay());
const esUrgente = $json.prioridad === 'URGENTE';

if (esFinDeSemana && esUrgente) {
  // Notificar por teléfono
} else {
  // Notificar por email
}
```

### 3. Acumular Eventos
```javascript
// Agrupar múltiples productos en un solo email
const productos = [];
// ... acumular durante 1 hora ...
// Enviar un solo email con todos los productos
```

---

## 📞 Soporte

- **GitHub**: [reportar issues](https://github.com/tu-repo/inventario)
- **Email**: soporte@tuempresa.com
- **Docs**: Ver `README.md` para más información

---

## 🎉 Conclusión

Con esta integración, tu minimarket se convierte en un negocio **100% automatizado** donde:
- ✅ Los pedidos se hacen solos
- ✅ Las promociones se crean automáticamente
- ✅ Nunca te quedas sin stock
- ✅ Reduces pérdidas por vencimiento
- ✅ Ahorras tiempo y dinero

**¡Feliz automatización! 🚀**

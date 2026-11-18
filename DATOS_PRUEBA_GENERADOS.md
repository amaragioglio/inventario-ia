# 🛒 Datos de Prueba Generados - Minimarket Latino

## 📊 Resumen de Datos Generados

Se han creado datos realistas que simulan **3 meses de operación** de un minimarket latino típico con productos, proveedores, movimientos de stock, alertas y pedidos automáticos.

---

## 🏪 Estructura de Datos

### 📦 **6 Proveedores Realistas**

1. **Distribuidora La Bodega**
   - Contacto: Carlos Méndez
   - Teléfono: 555-1001
   - Especialidad: Alimentos básicos y enlatados

2. **Abarrotes El Sabor Latino**
   - Contacto: María González
   - Teléfono: 555-1002
   - Especialidad: Panadería y embutidos

3. **Bebidas Universal**
   - Contacto: José Rodríguez
   - Teléfono: 555-1003
   - Especialidad: Gaseosas, jugos y bebidas

4. **Lácteos San José**
   - Contacto: Laura Sánchez
   - Teléfono: 555-1004
   - Especialidad: Leche, yogurt, quesos

5. **Limpieza Total SAC**
   - Contacto: Roberto Díaz
   - Teléfono: 555-1005
   - Especialidad: Productos de limpieza

6. **Snacks y Golosinas Express**
   - Contacto: Ana Torres
   - Teléfono: 555-1006
   - Especialidad: Papas, galletas, chocolates

---

### 🛍️ **38 Productos Típicos Latinos**

#### 🥤 **BEBIDAS** (7 productos - Alta rotación)
```
BEB001 - Coca Cola 2L          ($2.50/$3.50)   Stock: 45   Rot: 8-15/día
BEB002 - Inca Kola 2L          ($2.30/$3.20)   Stock: 38   Rot: 8-15/día
BEB003 - Pepsi 2L              ($2.40/$3.40)   Stock: 28   Rot: 8-15/día
BEB004 - Sprite 2L             ($2.40/$3.40)   Stock: 22   Rot: 8-15/día
BEB005 - Agua San Luis 2.5L    ($1.20/$2.00)   Stock: 65   Rot: 8-15/día
BEB006 - Jugo Pulp Durazno 1L  ($2.80/$4.00)   Stock: 18   Rot: 8-15/día
BEB007 - Chicha Morada 1L      ($2.50/$3.50)   Stock: 15   Rot: 8-15/día
```

#### 🍚 **ALIMENTOS BÁSICOS** (8 productos - Rotación media-alta)
```
ALI001 - Arroz Superior 5kg    ($12.00/$15.00) Stock: 42   Rot: 5-12/día
ALI002 - Fideos Don Vittorio   ($3.50/$5.00)   Stock: 35   Rot: 5-12/día
ALI003 - Aceite Primor 1L      ($8.50/$11.00)  Stock: 28   Rot: 5-12/día
ALI004 - Azúcar Blanca 1kg     ($2.80/$4.00)   Stock: 55   Rot: 5-12/día
ALI005 - Sal Marina 1kg        ($1.50/$2.50)   Stock: 68   Rot: 5-12/día
ALI006 - Frijol Canario 1kg    ($6.50/$9.00)   Stock: 32   Rot: 5-12/día
ALI007 - Lentejas 1kg          ($5.50/$8.00)   Stock: 25   Rot: 5-12/día
ALI008 - Harina Blanca 1kg     ($3.20/$5.00)   Stock: 38   Rot: 5-12/día
```

#### 🥛 **LÁCTEOS** (4 productos - Alta rotación, perecederos)
```
LAC001 - Leche Gloria 1L       ($3.80/$5.50)   Stock: 52   Rot: 6-14/día
LAC002 - Yogurt Gloria Fresa   ($6.50/$9.00)   Stock: 24   Rot: 6-14/día
LAC003 - Queso Fresco 500g     ($8.00/$12.00)  Stock: 18   Rot: 6-14/día
LAC004 - Mantequilla Gloria    ($4.50/$7.00)   Stock: 32   Rot: 6-14/día
```

#### 🍿 **SNACKS** (5 productos - Rotación media)
```
SNK001 - Papas Lays 180g       ($3.20/$5.00)   Stock: 45   Rot: 4-10/día
SNK002 - Galletas Soda 6un     ($2.50/$4.00)   Stock: 38   Rot: 4-10/día
SNK003 - Chocolate Sublime     ($1.50/$2.50)   Stock: 62   Rot: 4-10/día
SNK004 - Chizitos 140g         ($3.00/$4.50)   Stock: 28   Rot: 4-10/día
SNK005 - Piqueo Snax 180g      ($4.50/$7.00)   Stock: 22   Rot: 4-10/día
```

#### 🧹 **LIMPIEZA** (5 productos - Rotación baja-media)
```
LIM001 - Detergente Ariel 1kg  ($12.00/$18.00) Stock: 35   Rot: 2-6/día
LIM002 - Papel Higiénico 4un   ($5.50/$8.50)   Stock: 48   Rot: 2-6/día
LIM003 - Lejía Clorox 1L       ($3.50/$5.50)   Stock: 42   Rot: 2-6/día
LIM004 - Jabón Líquido 900ml   ($6.00/$9.00)   Stock: 28   Rot: 2-6/día
LIM005 - Lavavajilla 900ml     ($5.50/$8.00)   Stock: 32   Rot: 2-6/día
```

#### 🍞 **PANADERÍA** (3 productos - Muy alta rotación)
```
PAN001 - Pan Francés unidad    ($0.30/$0.60)   Stock: 85   Rot: 15-30/día
PAN002 - Pan Integral unidad   ($0.50/$1.00)   Stock: 42   Rot: 15-30/día
PAN003 - Tostadas Bimbo 250g   ($3.80/$6.00)   Stock: 28   Rot: 15-30/día
```

#### 🥓 **EMBUTIDOS** (3 productos - Rotación media)
```
EMB001 - Jamón Inglés 250g     ($8.50/$13.00)  Stock: 22   Rot: 3-8/día
EMB002 - Salchicha 500g        ($6.50/$10.00)  Stock: 18   Rot: 3-8/día
EMB003 - Mortadela 250g        ($5.50/$8.50)   Stock: 15   Rot: 3-8/día
```

#### 🥫 **ENLATADOS** (3 productos - Rotación baja)
```
ENL001 - Atún Florida 170g     ($4.50/$7.00)   Stock: 38   Rot: 2-5/día
ENL002 - Duraznos 820g         ($6.50/$10.00)  Stock: 25   Rot: 2-5/día
ENL003 - Leche Condensada      ($5.50/$8.50)   Stock: 32   Rot: 2-5/día
```

---

## 📊 **3,073 Movimientos de Stock** (90 días)

### Patrones de Venta Simulados:

#### **Ventas Diarias por Categoría:**
- **Panadería**: 15-30 unidades/día (muy alta rotación)
- **Bebidas**: 8-15 unidades/día (alta rotación)
- **Lácteos**: 6-14 unidades/día (alta rotación)
- **Alimentos**: 5-12 unidades/día (rotación media-alta)
- **Snacks**: 4-10 unidades/día (rotación media)
- **Embutidos**: 3-8 unidades/día (rotación media)
- **Limpieza**: 2-6 unidades/día (rotación baja-media)
- **Enlatados**: 2-5 unidades/día (rotación baja)

#### **Factores de Variación:**
1. **Días de semana**: Ventas normales (100%)
2. **Fines de semana**: Ventas aumentadas (+50%)
3. **Probabilidad de venta**: 80% de días tiene movimientos
4. **Reabastecimiento**: Cada 7-10 días automáticamente

#### **Tipos de Movimientos:**
- **SALIDA**: Ventas diarias (80% de los días)
- **ENTRADA**: Reabastecimiento periódico (cada 7-10 días)

---

## 🔔 **3 Alertas Generadas**

1. **Inca Kola 2L** (BEB002)
   - Tipo: STOCK_BAJO
   - Mensaje: "Stock bajo detectado - Requiere reabastecimiento"

2. **Aceite Primor 1L** (ALI003)
   - Tipo: STOCK_CRITICO
   - Mensaje: "Stock crítico - Pedido urgente recomendado"

3. **Yogurt Gloria Fresa** (LAC002)
   - Tipo: STOCK_BAJO
   - Mensaje: "Stock por debajo del mínimo"

---

## 📋 **3 Pedidos Automáticos Pendientes**

1. **Inca Kola 2L**
   - Proveedor: Bebidas Universal
   - Cantidad: 80 unidades
   - Nota: "Pedido generado por IA - Alta rotación detectada"

2. **Aceite Primor 1L**
   - Proveedor: Distribuidora La Bodega
   - Cantidad: 45 unidades
   - Nota: "Pedido generado por IA - Stock crítico"

3. **Leche Gloria 1L**
   - Proveedor: Lácteos San José
   - Cantidad: 100 unidades
   - Nota: "Pedido generado por IA - Producto de alta demanda"

---

## 🤖 **Proyecciones IA que Verás en el Dashboard**

### ⚠️ **SE AGOTARÁN PRONTO**
Basado en los movimientos de 3 meses, el sistema detectará:
- Productos con menos de 7 días de stock restante
- Cálculo: `días_restantes = stock_actual / ventas_diarias`
- Ejemplo: "Coca Cola 2L: ~2.3 días (7.2 und/día)"

### 💡 **RECOMENDACIONES INTELIGENTES**
Para productos con stock bajo, calculará:
- Cantidad óptima considerando rotación
- Alta rotación: +30% más
- Rotación media: cantidad estándar
- Baja rotación: -30% menos

### 📈 **TENDENCIAS DETECTADAS**
Mostrará las 3 categorías más activas:
- "Bebidas: 156 movimientos registrados"
- "Alimentos: 98 movimientos registrados"
- "Limpieza: 67 movimientos registrados"

---

## 💰 **Valor Total del Inventario**

### Por Categoría (Aproximado):
```
Bebidas:    ~$750  (35% del total)
Alimentos:  ~$620  (29% del total)
Lácteos:    ~$380  (18% del total)
Snacks:     ~$220  (10% del total)
Limpieza:   ~$110  (5% del total)
Otros:      ~$70   (3% del total)

TOTAL:      ~$2,150
```

---

## 📊 **Estadísticas de Operación**

### Movimientos por Mes:
- **Mes 1**: ~1,024 movimientos
- **Mes 2**: ~1,024 movimientos
- **Mes 3**: ~1,025 movimientos
- **Total**: 3,073 movimientos

### Productos por Estado:
- **Stock óptimo**: ~30 productos (79%)
- **Stock bajo**: ~5 productos (13%)
- **Stock crítico**: ~3 productos (8%)

### Velocidad de Rotación:
- **Alta rotación**: 14 productos (Bebidas, Lácteos, Panadería)
- **Rotación media**: 13 productos (Alimentos, Snacks, Embutidos)
- **Rotación baja**: 11 productos (Limpieza, Enlatados)

---

## 🎯 **Qué Verás en el Dashboard**

### **Panel Izquierdo - Gráfica de Categorías:**
```
📊 Distribución de Productos:
- Alimentos: 21.1%
- Bebidas: 18.4%
- Snacks: 13.2%
- Limpieza: 13.2%
- Lácteos: 10.5%
- Panadería: 7.9%
- Embutidos: 7.9%
- Enlatados: 7.9%
```

### **Panel Derecho - Proyecciones IA:**
```
⚠️ SE AGOTARÁN PRONTO
• Lista de productos que se agotarán en menos de 7 días
• Con días restantes y ventas diarias

💡 RECOMENDACIONES INTELIGENTES
• Top 5 productos con stock bajo
• Cantidad sugerida ajustada por rotación

📈 TENDENCIAS DETECTADAS
• Top 3 categorías más activas
• Número de movimientos registrados
```

### **Tabla de Productos Críticos:**
```
⚠️ Productos que requieren atención inmediata
- Con código, nombre, stock actual, mínimo y categoría
```

---

## 🔄 **Cómo Regenerar los Datos**

Si quieres regenerar los datos con nuevos valores aleatorios:

```bash
cd .\inventario-ia
python generar_datos_prueba.py
```

**NOTA**: Esto borrará todos los datos existentes y creará nuevos datos de prueba.

---

## 📱 **Uso del Sistema con Estos Datos**

### **Para Ver Proyecciones IA:**
1. Abre el dashboard
2. Observa el panel "🤖 Proyecciones Inteligentes"
3. Verás productos que se agotarán pronto
4. Recomendaciones de pedido con cantidades

### **Para Analizar un Producto Específico:**
1. Ve a la pestaña "Productos"
2. Selecciona un producto (ej. Coca Cola 2L)
3. Click en "🤖 Análisis IA"
4. Verás análisis completo con:
   - Métricas de venta
   - Días restantes
   - Cantidad sugerida
   - Mensaje para proveedor

### **Para Gestionar Alertas:**
1. Al abrir la app verás ventana de alertas
2. 3 alertas de stock bajo/crítico
3. Puedes marcarlas como leídas
4. O ir directo a editar el producto

### **Para Procesar Pedidos:**
1. Ve a pestaña "Pedidos Automáticos"
2. Verás 3 pedidos pendientes
3. Puedes marcarlos como procesados
4. O cancelarlos si es necesario

---

## ✨ **Características Realistas**

1. **Productos Latinos Reales**: Marcas conocidas en LATAM
2. **Precios Realistas**: Basados en minimarkets reales
3. **Patrones de Venta**: Reflejan comportamiento real
4. **Variación de Fines de Semana**: +50% ventas
5. **Reabastecimiento Periódico**: Cada 7-10 días
6. **Categorías Balanceadas**: Mix realista de productos
7. **Rotaciones Diferenciadas**: Por tipo de producto
8. **Stock Calculado**: Basado en movimientos reales

---

## 🎉 **Resultado Final**

Un sistema completamente poblado que simula 3 meses de operación de un minimarket latino real con:
- ✅ Productos típicos latinos
- ✅ Proveedores especializados
- ✅ 3,073 transacciones reales
- ✅ Patrones de venta realistas
- ✅ Alertas activas
- ✅ Pedidos pendientes
- ✅ Proyecciones IA funcionales
- ✅ Dashboard con datos significativos

**¡Ahora puedes explorar el sistema como si llevara 3 meses en operación! 🚀**

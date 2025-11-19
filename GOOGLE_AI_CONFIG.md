# Configuracion de Google AI (Gemini) para Sistema de Inventario

Esta guia explica como configurar y usar la integracion con Google AI (Gemini) para el analisis inteligente de inventarios.

## Requisitos Previos

1. Python 3.7 o superior
2. Cuenta de Google
3. API Key de Google AI Studio

## Instalacion de Dependencias

```bash
pip install -r requirements.txt
```

O instalar solo la dependencia de Google AI:

```bash
pip install google-generativeai
```

## Obtencion de API Key

### Paso 1: Acceder a Google AI Studio

1. Visite: https://makersuite.google.com/app/apikey
2. Inicie sesion con su cuenta de Google

### Paso 2: Crear API Key

1. Haga clic en "Create API key"
2. Seleccione el proyecto o cree uno nuevo
3. Copie la API key generada

### Paso 3: Configurar en la Aplicacion

#### Opcion A: Desde la Interfaz Grafica

1. Abra la aplicacion principal (`python main.py`)
2. Vaya a la pestana "Google AI"
3. Haga clic en "Configurar"
4. Pegue su API key
5. Seleccione el modelo (recomendado: `gemini-pro`)
6. Guarde la configuracion

#### Opcion B: Usando la API REST

```bash
curl -X POST http://localhost:5000/api/ai/configurar \
  -H "Content-Type: application/json" \
  -d '{"api_key": "SU_API_KEY_AQUI"}'
```

#### Opcion C: Variable de Entorno

Cree un archivo `.env` en el directorio del proyecto:

```
GOOGLE_AI_API_KEY=SU_API_KEY_AQUI
```

## Funcionalidades Disponibles

### 1. Analisis de Inventario

Analiza el estado general del inventario y proporciona:
- Resumen ejecutivo
- Fortalezas y areas de mejora
- Recomendaciones prioritarias
- Alertas importantes

**API:**
```bash
GET /api/ai/analisis/inventario
```

**Python:**
```python
from google_ai import GoogleAIAssistant

asistente = GoogleAIAssistant()
resultado = asistente.analizar_inventario_general()
print(resultado['respuesta'])
```

### 2. Analisis de Producto Individual

Analiza un producto especifico con metricas detalladas.

**API:**
```bash
GET /api/ai/analisis/producto/{id}
```

**Python:**
```python
resultado = asistente.analizar_producto(producto_id=1)
```

### 3. Prediccion de Demanda

Predice la demanda futura basada en datos historicos.

**API:**
```bash
GET /api/ai/prediccion/demanda?dias=30
GET /api/ai/prediccion/producto/{id}?dias=30
```

**Python:**
```python
# Prediccion general
resultado = asistente.predecir_demanda(dias_prediccion=30)

# Prediccion por producto
resultado = asistente.predecir_demanda(producto_id=1, dias_prediccion=30)
```

### 4. Deteccion de Tendencias

Identifica tendencias y patrones en el inventario.

**API:**
```bash
GET /api/ai/analisis/tendencias
```

**Python:**
```python
resultado = asistente.detectar_tendencias()
```

### 5. Recomendaciones de Compra

Genera recomendaciones inteligentes para reabastecimiento.

**API:**
```bash
GET /api/ai/recomendaciones/compra
```

**Python:**
```python
resultado = asistente.obtener_recomendaciones_compra()
```

### 6. Optimizacion de Precios

Analiza margenes y sugiere optimizaciones de precio.

**API:**
```bash
GET /api/ai/recomendaciones/precios
```

**Python:**
```python
resultado = asistente.optimizar_precios()
```

### 7. Reportes Ejecutivos

Genera reportes profesionales con metricas y recomendaciones.

**API:**
```bash
GET /api/ai/reportes/ejecutivo?dias=30
GET /api/ai/reportes/proveedor/{id}
```

**Python:**
```python
resultado = asistente.generar_reporte_ejecutivo(periodo_dias=30)
resultado = asistente.generar_reporte_proveedor(proveedor_id=1)
```

### 8. Consultas Libres

Permite hacer preguntas en lenguaje natural sobre el inventario.

**API:**
```bash
POST /api/ai/consulta
Content-Type: application/json
{
    "pregunta": "Cuales son los productos mas vendidos?"
}
```

**Python:**
```python
resultado = asistente.consulta_libre("Cuales son los productos mas vendidos?")
```

### 9. Generacion de Mensajes para Proveedores

Genera mensajes profesionales para enviar a proveedores.

**API:**
```bash
POST /api/ai/mensaje-proveedor
Content-Type: application/json
{
    "producto_id": 1,
    "cantidad": 50
}
```

**Python:**
```python
resultado = asistente.sugerir_mensaje_proveedor(producto_id=1, cantidad=50)
```

## Estructura de la Base de Datos

La integracion agrega las siguientes tablas:

### predicciones_ia
Almacena predicciones generadas por la IA.

### analisis_ia
Historial de analisis realizados.

### historial_consultas_ia
Registro de todas las consultas a la IA.

### tendencias_ia
Tendencias detectadas en el inventario.

### configuracion_ia
Configuraciones del modulo de IA.

### reportes_ia
Reportes generados por la IA.

### patrones_demanda
Patrones de demanda identificados.

## Configuraciones Disponibles

| Clave | Descripcion | Valor por Defecto |
|-------|-------------|-------------------|
| google_ai_api_key | API Key de Google AI | (vacio) |
| google_ai_modelo | Modelo a usar | gemini-pro |
| analisis_automatico | Habilitar analisis automatico | 1 |
| frecuencia_analisis_horas | Frecuencia de analisis | 24 |
| umbral_confianza_minimo | Umbral minimo de confianza | 0.7 |
| dias_historico_analisis | Dias de historico | 90 |
| max_tokens_respuesta | Max tokens en respuesta | 2048 |
| idioma_respuestas | Idioma de respuestas | es |
| notificar_predicciones | Notificar predicciones | 1 |
| guardar_historial_consultas | Guardar historial | 1 |

## Modelos Disponibles

| Modelo | Descripcion | Uso Recomendado |
|--------|-------------|-----------------|
| gemini-pro | Modelo principal de texto | Analisis, reportes, consultas |
| gemini-pro-vision | Modelo con vision | Analisis de imagenes |
| gemini-1.5-pro | Modelo avanzado | Analisis complejos |

## Costos

Google AI ofrece un nivel gratuito generoso:
- 60 consultas por minuto
- Sin costo para uso personal

Para uso comercial o alto volumen, consulte los precios en:
https://ai.google.dev/pricing

## Ejemplos de Uso

### Ejemplo 1: Script de Analisis Diario

```python
from google_ai import GoogleAIAssistant

def analisis_diario():
    asistente = GoogleAIAssistant()

    if not asistente.esta_configurado():
        print("Error: Google AI no configurado")
        return

    # Analisis general
    print("Analizando inventario...")
    resultado = asistente.analizar_inventario_general()

    if resultado['exito']:
        print("\n" + resultado['respuesta'])
    else:
        print(f"Error: {resultado['error']}")

    # Recomendaciones de compra
    print("\nGenerando recomendaciones...")
    recomendaciones = asistente.obtener_recomendaciones_compra()

    if recomendaciones['exito']:
        print("\n" + recomendaciones['respuesta'])

if __name__ == "__main__":
    analisis_diario()
```

### Ejemplo 2: Integracion con n8n

La API REST puede integrarse con n8n para automatizaciones:

1. Configure un nodo HTTP Request en n8n
2. URL: `http://localhost:5000/api/ai/analisis/inventario`
3. Metodo: GET
4. Configure acciones basadas en la respuesta

### Ejemplo 3: Alertas Automaticas

```python
from google_ai import GoogleAIAssistant
from webhook_client import WebhookClient

def verificar_y_alertar():
    asistente = GoogleAIAssistant()
    webhook = WebhookClient()

    # Obtener tendencias
    tendencias = asistente.detectar_tendencias()

    if tendencias['exito']:
        # Enviar a n8n para procesamiento
        webhook.enviar_evento('analisis_tendencias', {
            'resultado': tendencias['respuesta'],
            'fecha': datetime.now().isoformat()
        })
```

## Solucion de Problemas

### Error: "google-generativeai no instalado"

```bash
pip install google-generativeai
```

### Error: "API Key no valida"

1. Verifique que la API key sea correcta
2. Asegurese de que el proyecto de Google Cloud tenga la API habilitada
3. Verifique los limites de cuota

### Error: "No hay suficientes datos"

El sistema necesita datos historicos para generar analisis precisos:
- Minimo 30 dias de movimientos
- Al menos 10 productos activos

### Respuestas lentas

1. Verifique su conexion a internet
2. Considere usar el modelo `gemini-pro` (mas rapido)
3. Reduzca el valor de `max_tokens_respuesta`

## Seguridad

### Proteccion de API Key

1. Nunca comparta su API key
2. No la incluya en codigo fuente publico
3. Use variables de entorno en produccion

### Datos Sensibles

La IA procesa datos del inventario. Asegurese de:
- No incluir informacion personal
- Revisar los datos antes de enviarlos
- Cumplir con regulaciones de privacidad

## Soporte

Para problemas con:
- **Google AI SDK**: https://github.com/google/generative-ai-python
- **Sistema de Inventario**: Abra un issue en el repositorio

## Changelog

### Version 1.0.0
- Integracion inicial con Google Gemini
- Analisis de inventario
- Predicciones de demanda
- Recomendaciones de compra
- Optimizacion de precios
- Reportes ejecutivos
- Consultas libres
- API REST completa

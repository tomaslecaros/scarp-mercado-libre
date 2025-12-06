# 🏠 Notificador de Propiedades - Portal Inmobiliario

Aplicación optimizada en Python que monitorea Portal Inmobiliario y envía notificaciones por email cuando aparecen nuevas propiedades que cumplen con tus filtros personalizables.

## 📋 Características

- ✅ Monitoreo automático configurable
- ✅ Múltiples filtros personalizables (precio, dormitorios, ubicación, tipo)
- ✅ Notificaciones por email con información detallada
- ✅ Evita notificaciones duplicadas
- ✅ **Optimizado para producción en Northflank/Railway/Docker**
- ✅ Sin base de datos - solo archivo JSON simple
- ✅ Usa Selenium con scroll automático
- ✅ Distingue entre precios en UF y pesos chilenos (CLP)
- ✅ Manejo robusto de errores con reintentos automáticos

## 🚀 Instalación Local

### 1. Requisitos

- Python 3.11 o superior
- Cuenta de Gmail con contraseña de aplicación
- Chrome/Chromium instalado

### 2. Clonar e instalar dependencias

```bash
# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Configuración de Gmail
GMAIL_USER=tu-email@gmail.com
GMAIL_PASSWORD=tu-app-password-de-16-caracteres

# Lista de destinatarios separados por comas
RECIPIENTS=tu-email@gmail.com,amigo1@gmail.com

# Intervalo de monitoreo en minutos (recomendado: 30-60 para producción)
CHECK_INTERVAL_MINUTES=30

# Filtros en formato JSON (opcional, se pueden definir en main.py)
SEARCH_FILTERS_JSON=[{"name":"Casa 4-5 piezas","url":"https://..."}]
```

### 4. Obtener App Password de Gmail

1. Ve a https://myaccount.google.com/
2. **Seguridad** → **Verificación en 2 pasos** (actívala)
3. **Contraseñas de aplicaciones**
4. Genera una nueva para "Correo"
5. Usa la contraseña de 16 caracteres como `GMAIL_PASSWORD`

### 5. Configurar filtros

Edita [main.py](main.py#L25-L43) y define tus filtros en `SEARCH_FILTERS`:

```python
SEARCH_FILTERS = [
    {
        "name": "Casa 4-5 piezas, máximo 2.000.000 CLP",
        "url": "https://www.portalinmobiliario.com/arriendo/casa/..."
    },
    {
        "name": "Departamento 4-5 piezas máximo 1.500.000 CLP",
        "url": "https://www.portalinmobiliario.com/arriendo/departamento/..."
    }
]
```

Para obtener la URL:
1. Ve a [Portal Inmobiliario](https://www.portalinmobiliario.com)
2. Aplica tus filtros de búsqueda
3. Copia la URL completa de la página de resultados

### 6. Ejecutar

```bash
python main.py
```

Para detener: `Ctrl+C`

## 🐳 Despliegue en Northflank (Producción)

### 1. Preparar el proyecto

Asegúrate de tener tu código en un repositorio Git (GitHub, GitLab).

### 2. Crear servicio en Northflank

1. Ve a [Northflank](https://northflank.com) y crea una cuenta
2. Crea un nuevo **Service** desde tu repositorio Git
3. Selecciona **Dockerfile** como build method

### 3. Configurar variables de entorno en Northflank

En el dashboard de Northflank, ve a tu servicio → **Environment Variables** y agrega:

```
GMAIL_USER=tu-email@gmail.com
GMAIL_PASSWORD=tu-app-password
RECIPIENTS=email1@gmail.com,email2@gmail.com
CHECK_INTERVAL_MINUTES=30

# Variables específicas para Docker/Linux
CHROME_BINARY=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

### 4. Configurar el servicio

- **Service Type**: Worker (no Web)
- **Port**: No necesario (es un worker)
- **Health Check**: Deshabilitado
- **Replicas**: 1

### 5. Deploy

Northflank desplegará automáticamente usando el `Dockerfile`. Los logs aparecerán en tiempo real.

## 🚢 Alternativa: Railway

Similar a Northflank:

1. Crea proyecto en [Railway](https://railway.app)
2. Conecta tu repositorio
3. Agrega las mismas variables de entorno
4. Railway detectará el Dockerfile automáticamente

## 📁 Estructura del Proyecto

```
.
├── main.py              # Loop principal y punto de entrada
├── scraper.py           # Scraping optimizado con Selenium
├── email_service.py     # Servicio de envío de emails
├── storage.py           # Gestión de propiedades ya vistas
├── config.py            # Configuración y variables de entorno
├── requirements.txt     # Dependencias Python (optimizado)
├── Dockerfile           # Configuración Docker para producción
├── .dockerignore        # Archivos a ignorar en Docker
├── .env                 # Variables de entorno (local, no subir a Git)
└── data/
    └── properties-seen.json  # Propiedades vistas (generado automáticamente)
```

## 🔧 Mejoras Implementadas

### Versión Optimizada para Producción

- **Scraper simplificado**: Menos scrolls, más eficiente
- **Manejo de errores robusto**: Reintentos automáticos
- **Logging mejorado**: Menos ruido, más información útil
- **Docker optimizado**: Chromium headless nativo
- **Sin webdriver-manager**: Usa el driver del sistema (más confiable)
- **Bloqueo de imágenes**: Carga más rápida
- **Timeout configurado**: Evita cuelgues

### Problemas Resueltos

1. ✅ Error `[WinError 193]` - Ahora usa Chromium del sistema en Docker
2. ✅ Errores de GPU/WebGL - Deshabilitados con flags optimizados
3. ✅ Intervalo muy largo - Configurable vía variable de entorno
4. ✅ Recursos excesivos - Scraping simplificado

## 🐛 Solución de Problemas

### Error: "GMAIL_USER no está configurado"

Verifica tu archivo `.env` o las variables de entorno en Northflank.

### Error: "SMTPAuthenticationError"

- Usa una **App Password** de 16 caracteres
- NO uses tu contraseña normal de Gmail
- Activa la verificación en 2 pasos

### No se encuentran propiedades

- Verifica que la URL de búsqueda sea correcta
- Portal Inmobiliario puede haber cambiado su estructura HTML
- Revisa los selectores CSS en [scraper.py](scraper.py#L200-L205)

### Errores en producción (Northflank/Railway)

Revisa los logs del servicio:
- Verifica que las variables de entorno estén configuradas
- Asegúrate de que `CHROME_BINARY` y `CHROMEDRIVER_PATH` estén definidas
- Los errores de WebGL/GPU son normales en headless (se ignoran)

### Consumo excesivo de recursos

- Aumenta `CHECK_INTERVAL_MINUTES` a 30-60 minutos
- Reduce el número de filtros simultáneos
- En Northflank/Railway, considera un plan con más recursos

## 📝 Configuración Recomendada para Producción

```env
# Intervalo óptimo para no sobrecargar el servidor ni Portal Inmobiliario
CHECK_INTERVAL_MINUTES=30

# Docker/Linux (Northflank/Railway)
CHROME_BINARY=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

## ⚠️ Notas Importantes

- Respeta los términos de uso de Portal Inmobiliario
- Intervalo mínimo recomendado: 30 minutos en producción
- El scraper puede necesitar ajustes si el sitio cambia
- Los logs de GPU/WebGL en headless son normales (no afectan funcionamiento)

## 🤝 Contribuciones

Proyecto personal optimizado para uso en producción. Siéntete libre de modificarlo.

## 📄 Licencia

Código abierto para uso personal.

---

**¡Feliz búsqueda de propiedades! 🏡**

### 📞 Soporte

Si tienes problemas:

1. Revisa los logs del servicio en Northflank/Railway
2. Verifica las variables de entorno
3. Asegúrate de que Chromium esté disponible en Docker
4. Revisa que Portal Inmobiliario no haya cambiado su estructura

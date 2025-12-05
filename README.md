# 🏠 Notificador de Propiedades - Portal Inmobiliario

Aplicación simple en Python que monitorea Portal Inmobiliario cada 5 minutos y envía notificaciones por email cuando aparecen nuevas propiedades (casas/departamentos) que cumplen con tus filtros personalizables.

## 📋 Características

- ✅ Monitoreo automático cada 5 minutos (configurable)
- ✅ Filtros personalizables (precio, dormitorios, ubicación, tipo)
- ✅ Notificaciones por email con información detallada
- ✅ Evita notificaciones duplicadas
- ✅ Listo para desplegar en Railway
- ✅ Sin base de datos - solo archivo JSON simple
- ✅ **Usa Selenium con scroll automático para obtener TODAS las propiedades** (no solo las primeras 10)
- ✅ **Distingue entre precios en UF y pesos chilenos (CLP)**

## 🚀 Instalación Local

### 1. Requisitos

- Python 3.8 o superior
- Cuenta de Gmail con contraseña de aplicación
- **Chrome o Chromium instalado** (Selenium lo usa automáticamente - webdriver-manager lo descarga si es necesario)

### 2. Clonar e instalar dependencias

```bash
# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
# Configuración de Gmail
GMAIL_USER=tu-email@gmail.com
GMAIL_PASSWORD=tu-app-password-de-16-caracteres

# Lista de destinatarios separados por comas
RECIPIENTS=tu-email@gmail.com,amigo1@gmail.com,amigo2@gmail.com

# Intervalo de monitoreo en minutos (por defecto 5)
CHECK_INTERVAL_MINUTES=5

# URL de búsqueda de Portal Inmobiliario con tus filtros aplicados
SEARCH_URL=https://www.portalinmobiliario.com/arriendo/casa/_DisplayType_M_PriceRange_5CLP-2000000CLP_BEDROOMS_4-5_item*location_lat:-33.43758786585081*-33.38908449639877,lon:-70.61507607490566*-70.50898934394863

# Filtros adicionales (opcionales)
PRICE_MIN=
PRICE_MAX=
BEDROOMS_MIN=
PROPERTY_TYPE=
```

### 4. Obtener App Password de Gmail

Para enviar emails desde Gmail, necesitas una "Contraseña de aplicación":

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Ve a **Seguridad** → **Verificación en 2 pasos** (debe estar activada)
3. Ve a **Contraseñas de aplicaciones**
4. Genera una nueva contraseña para "Correo" y "Otro (personalizado)" → "Notificador"
5. Copia la contraseña de 16 caracteres y úsala como `GMAIL_PASSWORD`

### 5. Obtener URL de búsqueda

1. Ve a [Portal Inmobiliario](https://www.portalinmobiliario.com)
2. Aplica tus filtros de búsqueda (precio, ubicación, dormitorios, etc.)
3. Copia la URL completa de la página de resultados
4. Pégala en `SEARCH_URL` en tu archivo `.env`

### 6. Ejecutar

```bash
python main.py
```

El programa comenzará a monitorear inmediatamente y cada 5 minutos verificará nuevas propiedades.

Para detener, presiona `Ctrl+C`.

## 📁 Estructura del Proyecto

```
.
├── main.py              # Loop principal y punto de entrada
├── scraper.py           # Lógica de scraping de Portal Inmobiliario
├── email_service.py     # Servicio de envío de emails
├── storage.py           # Gestión de propiedades ya vistas
├── config.py            # Configuración y carga de variables de entorno
├── requirements.txt     # Dependencias Python
├── Procfile             # Configuración para Railway
├── .env.example         # Template de variables de entorno
├── README.md            # Este archivo
└── data/
    └── properties-seen.json  # Archivo donde se guardan propiedades vistas (se crea automáticamente)
```

## 🚢 Despliegue en Railway

### 1. Preparar el proyecto

Asegúrate de tener todos los archivos en un repositorio Git (GitHub, GitLab, etc.).

### 2. Crear proyecto en Railway

1. Ve a [Railway](https://railway.app) y crea una cuenta
2. Haz clic en **New Project**
3. Selecciona **Deploy from GitHub repo** (o la opción que prefieras)
4. Conecta tu repositorio y selecciona este proyecto

### 3. Configurar variables de entorno

En el dashboard de Railway:

1. Ve a tu proyecto → **Variables**
2. Agrega las siguientes variables de entorno (los mismos valores que en `.env`):

   ```
   GMAIL_USER=tu-email@gmail.com
   GMAIL_PASSWORD=tu-app-password
   RECIPIENTS=tu-email@gmail.com,amigo1@gmail.com
   CHECK_INTERVAL_MINUTES=5
   SEARCH_URL=https://www.portalinmobiliario.com/...
   ```

### 4. Configurar el servicio

Railway detectará automáticamente que es un proyecto Python. El `Procfile` ya está configurado para ejecutar como un worker.

1. Ve a **Settings** → **Service**
2. Asegúrate de que el tipo de servicio sea **Worker** (no Web Service)
3. El comando debería ser: `python main.py`

### 5. Desplegar

Railway desplegará automáticamente cuando hagas push al repositorio. Puedes ver los logs en tiempo real en el dashboard.

## 🔧 Configuración Avanzada

### Cómo Funciona el Scraping

El scraper usa **Selenium** (un navegador real automatizado) para:

1. **Abrir la página** de búsqueda en Portal Inmobiliario
2. **Hacer scroll automático** hasta el final de la página para cargar todas las propiedades (lazy loading)
3. **Esperar** a que se carguen todas las propiedades dinámicamente
4. **Extraer** todas las propiedades visibles (no solo las primeras 10)

Esto asegura que veas **TODAS** las propiedades disponibles, no solo las primeras que aparecen.

### Filtros Adicionales

Puedes agregar filtros adicionales en `config.py` o mediante variables de entorno:

- `PRICE_MIN`: Precio mínimo en CLP
- `PRICE_MAX`: Precio máximo en CLP
- `BEDROOMS_MIN`: Cantidad mínima de dormitorios
- `PROPERTY_TYPE`: Tipo de propiedad ("casa" o "departamento")

### Modificar el Scraper

Si Portal Inmobiliario cambia su estructura HTML, puedes ajustar los selectores CSS en `scraper.py`, específicamente en la función `extract_property_info()`.

**Nota**: Si Selenium te da problemas, el scraper tiene un fallback automático al método antiguo (requests).

## 🐛 Solución de Problemas

### Error: "GMAIL_USER no está configurado"

Asegúrate de tener un archivo `.env` con todas las variables necesarias, o configúralas en Railway.

### Error: "SMTPAuthenticationError"

- Verifica que tu `GMAIL_PASSWORD` sea una "App Password" de 16 caracteres, no tu contraseña normal
- Asegúrate de que la verificación en 2 pasos esté activada en tu cuenta de Google

### No se encuentran propiedades

- Verifica que la URL de búsqueda (`SEARCH_URL`) sea correcta
- Puede que Portal Inmobiliario haya cambiado su estructura HTML - revisa `scraper.py`
- Verifica que los selectores CSS en `extract_property_info()` estén actualizados

### Emails no se envían

- Revisa los logs en Railway o en la consola
- Verifica que los destinatarios estén correctamente configurados
- Asegúrate de que no haya problemas de conectividad

## 📝 Notas Importantes

- ⚠️ Respeta los términos de uso de Portal Inmobiliario
- ⚠️ No hagas requests muy frecuentes para evitar ser bloqueado
- ⚠️ El intervalo por defecto es 5 minutos - es recomendable mantenerlo
- ⚠️ El scraper puede necesitar ajustes si Portal Inmobiliario cambia su estructura

## 🤝 Contribuciones

Este es un proyecto simple y personal. Siéntete libre de modificarlo según tus necesidades.

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso personal.

## 🆘 Soporte

Si tienes problemas:

1. Revisa los logs del programa
2. Verifica la configuración en `.env`
3. Asegúrate de que todas las dependencias estén instaladas
4. Revisa que Portal Inmobiliario no haya cambiado su estructura

---

¡Feliz búsqueda de propiedades! 🏡

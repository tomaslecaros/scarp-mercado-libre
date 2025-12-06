# 🚀 Guía de Deployment en Northflank

Esta guía te ayudará a desplegar tu notificador de propiedades en Northflank paso a paso.

## 📋 Pre-requisitos

1. ✅ Cuenta en [Northflank](https://northflank.com) (tienen plan gratuito)
2. ✅ Repositorio Git con tu código (GitHub, GitLab, Bitbucket)
3. ✅ App Password de Gmail configurada
4. ✅ Filtros de búsqueda definidos en `main.py`

## 🔧 Paso 1: Preparar tu Repositorio

Asegúrate de tener estos archivos en tu repositorio:

```
✅ Dockerfile
✅ requirements.txt
✅ main.py
✅ scraper.py
✅ config.py
✅ email_service.py
✅ storage.py
✅ .dockerignore
```

**IMPORTANTE**: NO subas tu archivo `.env` al repositorio (debe estar en `.gitignore`).

## 🌐 Paso 2: Crear Proyecto en Northflank

1. Inicia sesión en [Northflank](https://app.northflank.com)
2. Haz clic en **"Create New Project"**
3. Dale un nombre: `notificador-propiedades`
4. Haz clic en **"Create Project"**

## ⚙️ Paso 3: Crear Servicio

Dentro de tu proyecto:

1. Haz clic en **"Create Service"**
2. Selecciona **"Combined Service"**
3. Elige tu proveedor Git (GitHub/GitLab/Bitbucket)
4. Autoriza la conexión si es necesario
5. Selecciona tu repositorio
6. Selecciona la rama (normalmente `main` o `master`)

## 🐳 Paso 4: Configurar Build

En la sección de Build:

1. **Build Type**: Selecciona **"Dockerfile"**
2. **Dockerfile Path**: Deja como está (`/Dockerfile`)
3. **Build Context**: `/`
4. **Build Arguments**: Ninguno necesario

## 🔐 Paso 5: Configurar Variables de Entorno

Esta es la parte más importante. Ve a la pestaña **"Environment Variables"** y agrega:

### Variables Obligatorias:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `GMAIL_USER` | `tu-email@gmail.com` | Tu email de Gmail |
| `GMAIL_PASSWORD` | `abcd efgh ijkl mnop` | App Password de 16 caracteres |
| `RECIPIENTS` | `email1@gmail.com,email2@gmail.com` | Destinatarios (separados por comas) |
| `CHECK_INTERVAL_MINUTES` | `30` | Intervalo de verificación en minutos |

### Variables para Docker (Obligatorias en Northflank):

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `CHROME_BINARY` | `/usr/bin/chromium` | Ubicación de Chromium |
| `CHROMEDRIVER_PATH` | `/usr/bin/chromedriver` | Ubicación del driver |

### Cómo agregar las variables:

1. Haz clic en **"Add Variable"**
2. Ingresa el **Name** (nombre de la variable)
3. Ingresa el **Value** (valor)
4. Haz clic en **"Add"**
5. Repite para cada variable

## 🎯 Paso 6: Configurar el Servicio

En la sección **"Service Settings"**:

1. **Service Type**: **Worker** (NO Web Service)
   - Esto es crucial: tu app no es un servidor web
2. **Port**: Déjalo vacío (no necesitas puerto para un worker)
3. **Health Checks**: Deshabilitado
4. **Replicas**: 1
5. **Resources**:
   - CPU: 0.2 vCPU (o más si tienes plan pago)
   - Memory: 512 MB - 1 GB recomendado

## 🚀 Paso 7: Deploy

1. Revisa todas las configuraciones
2. Haz clic en **"Create Service"**
3. Northflank comenzará a:
   - Clonar tu repositorio
   - Construir la imagen Docker
   - Desplegar el contenedor

## 📊 Paso 8: Verificar Deployment

### Ver Logs en Tiempo Real:

1. Ve a tu servicio en Northflank
2. Haz clic en la pestaña **"Logs"**
3. Deberías ver algo como:

```
🏠 Notificador de Propiedades - Portal Inmobiliario
✓ Configuración válida

📋 CONFIGURACIÓN:
   📧 Email de envío: tu-email@gmail.com
   📨 Destinatarios: email1@gmail.com, email2@gmail.com
   ⏰ Intervalo de verificación: 30 minuto(s)
   🔍 Filtros configurados: 4

🚀 Iniciando monitoreo continuo...
```

### Verificar Estado:

- **Status**: Debe estar en **"Running"** (verde)
- Si está en **"Failed"** (rojo), revisa los logs para ver el error

## 🐛 Solución de Problemas Comunes

### Error: "GMAIL_USER no está configurado"

❌ **Problema**: Las variables de entorno no se están leyendo

✅ **Solución**:
- Verifica que agregaste todas las variables en Northflank
- Asegúrate de que no haya espacios extra en los nombres
- Reinicia el servicio después de agregar variables

### Error: "ChromeDriver not found"

❌ **Problema**: Chromium no está disponible

✅ **Solución**:
- Verifica que `CHROME_BINARY=/usr/bin/chromium` esté configurado
- Verifica que `CHROMEDRIVER_PATH=/usr/bin/chromedriver` esté configurado
- El Dockerfile ya instala Chromium automáticamente

### Error: "SMTPAuthenticationError"

❌ **Problema**: Credenciales de Gmail incorrectas

✅ **Solución**:
- Verifica que `GMAIL_PASSWORD` sea una **App Password** de 16 caracteres
- NO uses tu contraseña normal de Gmail
- Activa la verificación en 2 pasos en Gmail
- Genera una nueva App Password: https://myaccount.google.com/apppasswords

### El servicio se reinicia constantemente

❌ **Problema**: Recursos insuficientes o error en el código

✅ **Solución**:
- Revisa los logs para ver el error específico
- Aumenta la memoria asignada (Settings → Resources)
- Verifica que tu código funcione localmente primero

### No se encuentran propiedades

❌ **Problema**: URLs de filtros incorrectas o Portal Inmobiliario cambió

✅ **Solución**:
- Verifica las URLs en `main.py`
- Prueba las URLs en tu navegador
- Revisa los selectores CSS en `scraper.py`

## 🔄 Actualizar el Código

Cuando hagas cambios en tu código:

1. Haz commit y push a tu repositorio Git
2. Northflank detectará el cambio automáticamente
3. Construirá y desplegará la nueva versión
4. Puedes ver el progreso en la pestaña **"Builds"**

### Forzar Re-deploy Manual:

Si necesitas re-desplegar sin cambios:

1. Ve a tu servicio
2. Haz clic en **"Restart"** en la esquina superior derecha

## 📈 Monitoreo

### Ver Estadísticas:

- **Logs**: Pestaña "Logs" para ver output en tiempo real
- **Metrics**: Pestaña "Metrics" para ver uso de CPU/Memoria
- **Events**: Pestaña "Events" para ver historial de deployments

### Configurar Alertas (Plan Pago):

Puedes configurar alertas para:
- Servicio caído
- Alto uso de recursos
- Errores en logs

## 💰 Costos

Northflank tiene un plan gratuito con:
- 2 servicios gratuitos
- Recursos limitados
- Perfecto para este proyecto

Si necesitas más recursos, revisa sus planes en [northflank.com/pricing](https://northflank.com/pricing)

## 🎓 Mejores Prácticas

1. **Intervalo de Verificación**:
   - Producción: 30-60 minutos
   - Evita intervalos muy cortos para no sobrecargar Portal Inmobiliario

2. **Recursos**:
   - Mínimo: 512 MB RAM
   - Recomendado: 1 GB RAM para múltiples filtros

3. **Logs**:
   - Revisa los logs regularmente
   - Los errores de GPU/WebGL son normales en headless

4. **Persistencia de Datos**:
   - El archivo `data/properties-seen.json` se mantiene entre reinicios
   - Pero se pierde si eliminas el servicio
   - Considera usar un volumen persistente si es crítico

## ✅ Checklist Final

Antes de hacer deploy, verifica:

- [ ] Dockerfile está en el repositorio
- [ ] Variables de entorno configuradas en Northflank
- [ ] `GMAIL_PASSWORD` es una App Password (no contraseña normal)
- [ ] Filtros de búsqueda definidos en `main.py`
- [ ] Service Type configurado como **Worker**
- [ ] Recursos asignados (mínimo 512 MB)
- [ ] URLs de filtros son válidas

## 📞 Ayuda Adicional

- **Documentación Northflank**: https://northflank.com/docs
- **Logs del Servicio**: Revisa siempre aquí primero
- **Issues GitHub**: Si encuentras bugs en el código

---

**¡Listo! Tu notificador debería estar funcionando en producción.** 🎉

Si encuentras errores, revisa los logs y compáralos con esta guía.

# 🔍 Configuración de Múltiples Filtros

Esta aplicación soporta múltiples URLs de búsqueda, cada una con su propia descripción. Esto te permite monitorear diferentes criterios de búsqueda simultáneamente.

## 📋 Formato de Configuración

### ⭐ Opción Recomendada: Configurar en `main.py` (Más Simple)

**La forma más fácil es agregar tus filtros directamente en `main.py`**, en las líneas 15-26 aproximadamente:

```python
SEARCH_FILTERS = [
    {
        "name": "4 piezas máximo 1.800.000 CLP",
        "url": "https://www.portalinmobiliario.com/arriendo/casa/_DisplayType_M_PriceRange_5CLP-1800000CLP_BEDROOMS_4_item*..."
    },
    {
        "name": "5 piezas máximo 2.000.000 CLP",
        "url": "https://www.portalinmobiliario.com/arriendo/casa/_DisplayType_M_PriceRange_5CLP-2000000CLP_BEDROOMS_5_item*..."
    },
]
```

Simplemente abre `main.py` y agrega tus filtros en la lista `SEARCH_FILTERS`.

### Opción Alternativa: Variables de Entorno

Si prefieres usar variables de entorno, puedes configurar `SEARCH_FILTERS_JSON` en tu archivo `.env`:

```env
SEARCH_FILTERS_JSON=[{"name": "Descripción del filtro 1", "url": "https://..."}, {"name": "Descripción del filtro 2", "url": "https://..."}]
```

O también puedes usar `SEARCH_URL` para un solo filtro:

```env
SEARCH_URL=https://www.portalinmobiliario.com/arriendo/casa/...
```

## 📝 Ejemplo Completo

### Paso 1: Obtener las URLs

1. Ve a Portal Inmobiliario
2. Aplica tus filtros (precio, dormitorios, ubicación, etc.)
3. Copia la URL completa de la búsqueda
4. Repite para cada combinación de filtros que quieras monitorear

### Paso 2: Configurar en `main.py` (Recomendado)

Abre `main.py` y busca la sección `SEARCH_FILTERS` (alrededor de la línea 15). Agrega tus filtros así:

```python
SEARCH_FILTERS = [
    {
        "name": "4 piezas max 1.800.000",
        "url": "https://www.portalinmobiliario.com/arriendo/casa/_DisplayType_M_PriceRange_5CLP-1800000CLP_BEDROOMS_4_item*..."
    },
    {
        "name": "5 piezas max 2.000.000",
        "url": "https://www.portalinmobiliario.com/arriendo/casa/_DisplayType_M_PriceRange_5CLP-2000000CLP_BEDROOMS_5_item*..."
    },
    {
        "name": "Departamentos 3 piezas Las Condes",
        "url": "https://www.portalinmobiliario.com/arriendo/departamento/..."
    }
]
```

**✅ Ventajas:**
- Más fácil de leer y editar
- No necesitas formatear JSON
- Puedes usar comentarios
- Más simple de versionar en Git

### Paso Alternativo: Configurar en `.env`

Si prefieres usar variables de entorno:

```env
GMAIL_USER=tu-email@gmail.com
GMAIL_PASSWORD=tu-app-password

RECIPIENTS=tu-email@gmail.com,amigo1@gmail.com

CHECK_INTERVAL_MINUTES=5

SEARCH_FILTERS_JSON=[{"name": "4 piezas max 1.800.000", "url": "https://..."}, {"name": "5 piezas max 2.000.000", "url": "https://..."}]
```

**⚠️ IMPORTANTE (solo si usas `.env`):**
- El JSON debe estar en una sola línea
- No uses saltos de línea dentro del JSON
- Usa comillas dobles (`"`) para las claves y valores

## 🎯 Ventajas de Múltiples Filtros

1. **Monitoreo Simultáneo**: Puedes monitorear diferentes criterios a la vez
   - Ejemplo: "4 piezas máximo 1.800.000" y "5 piezas máximo 2.000.000"

2. **Notificaciones Organizadas**: En el email, las propiedades se agrupan por filtro
   - Verás claramente qué propiedad viene de qué filtro

3. **Sin Duplicados**: Si la misma propiedad aparece en múltiples filtros, solo recibirás una notificación

## 📧 Ejemplo de Email

Cuando encuentre propiedades nuevas, el email se verá así:

```
🏠 Nuevas Propiedades Encontradas

🔍 4 piezas max 1.800.000 (2 propiedades)
   - Casa en Las Condes - $1.500.000
   - Casa en Providencia - $1.750.000

🔍 5 piezas max 2.000.000 (1 propiedad)
   - Casa en Lo Barnechea - $1.950.000
```

## 🔄 Migración desde Versión Anterior

Si ya tenías configurado `SEARCH_URL` en variables de entorno, la aplicación seguirá funcionando igual. El sistema automáticamente convierte `SEARCH_URL` a un formato de filtro único.

Para migrar a múltiples filtros en `main.py`:
1. Abre `main.py`
2. Busca la sección `SEARCH_FILTERS` (línea ~15)
3. Agrega tus filtros en la lista
4. ¡Listo! Ya no necesitas `SEARCH_URL` en el `.env`

## ❓ Preguntas Frecuentes

**P: ¿Dónde debo configurar los filtros?**
R: **Recomendado**: Directamente en `main.py` en la sección `SEARCH_FILTERS`. Es más fácil y claro.

**P: ¿Puedo usar variables de entorno en lugar de `main.py`?**
R: Sí, puedes usar `SEARCH_FILTERS_JSON` en `.env`, pero configurar en `main.py` es más simple.

**P: ¿Qué pasa si una propiedad aparece en múltiples filtros?**
R: Solo recibirás una notificación. El sistema evita duplicados usando el ID único de la propiedad.

**P: ¿Cómo veo qué filtro encontró cada propiedad?**
R: En el email, las propiedades están agrupadas por filtro con su descripción.

**P: ¿Puedo cambiar las descripciones de los filtros?**
R: Sí, solo cambia el valor de `"name"` en la lista. La descripción solo se usa para mostrar en logs y emails.

**P: ¿Qué pasa si no configuro filtros en `main.py`?**
R: El sistema intentará usar la configuración de `config.py` o variables de entorno como respaldo.


"""
Ejemplo de cómo configurar múltiples filtros directamente en el código.

Si prefieres no usar variables de entorno JSON, puedes configurar los filtros
directamente aquí y luego importarlos en config.py
"""

# Ejemplo de configuración de múltiples filtros
EJEMPLO_FILTROS = [
    {
        "name": "4 piezas máximo 1.800.000 CLP",
        "url": "https://www.portalinmobiliario.com/arriendo/casa/_DisplayType_M_PriceRange_5CLP-1800000CLP_BEDROOMS_4_item*location_lat:-33.42955368359416*-33.38104582647317,lon:-70.63084336547851*-70.52475663452148?polygon_location=..."
    },
    {
        "name": "5 piezas máximo 2.000.000 CLP",
        "url": "https://www.portalinmobiliario.com/arriendo/casa/_DisplayType_M_PriceRange_5CLP-2000000CLP_BEDROOMS_5_item*location_lat:-33.42955368359416*-33.38104582647317,lon:-70.63084336547851*-70.52475663452148?polygon_location=..."
    },
    {
        "name": "Departamentos 3 piezas Las Condes",
        "url": "https://www.portalinmobiliario.com/arriendo/departamento/..."
    }
]

# Para usar estos filtros:
# 1. Copia las URLs desde Portal Inmobiliario con tus filtros aplicados
# 2. Agrega una descripción clara en "name"
# 3. Si quieres usar esto en config.py, reemplaza la función load_search_filters()
#    para que retorne EJEMPLO_FILTROS directamente


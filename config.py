"""
Configuración del notificador de propiedades.
Puedes modificar los filtros directamente aquí o usar variables de entorno.
"""
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ============ CONFIGURACIÓN DE EMAIL ============
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")  # App password de Gmail
RECIPIENTS = os.getenv("RECIPIENTS", "").split(",") if os.getenv("RECIPIENTS") else []
# Limpiar espacios en blanco de los emails
RECIPIENTS = [email.strip() for email in RECIPIENTS if email.strip()]

# ============ CONFIGURACIÓN DE MONITOREO ============
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "5"))

# URL única (para compatibilidad hacia atrás) - se usa si no hay múltiples filtros
SEARCH_URL = os.getenv(
    "SEARCH_URL",
    "https://www.portalinmobiliario.com/arriendo/casa/_DisplayType_M_PriceRange_5CLP-2000000CLP_BEDROOMS_4-5_item*location_lat:-33.42955368359416*-33.38104582647317,lon:-70.63084336547851*-70.52475663452148?polygon_location=%7C%7DvjEx%7EwmLy%40gB%3F%7D%5BjDwI%7CPuIl%5DmEbO%7BK%60Gyg%40x%40c%7C%40vc%40gQjf%40qGvI%3F%7CGfCpKvI%7CG%7CLpKlb%40bFlEbObyAlLvJfNfBbFrH%7EGlSbFxYx%40%7CLpBnFx%40lT%7DPb%5EkLre%40sSpUwIdB%3FdAqm%40pGy%40bAunAdAmLgBaXgQoTmc%40eW_hAmLe_%40y%40%7BZnCkD%3FiCuAgCuA%3FZjS"
)

# ============ MÚLTIPLES FILTROS ============
# Puedes definir múltiples URLs de búsqueda, cada una con su descripción
# Formato: Lista de diccionarios con 'name' (descripción) y 'url'

def load_search_filters():
    """
    Carga los filtros de búsqueda desde variable de entorno o usa configuración por defecto.
    
    Si existe SEARCH_FILTERS_JSON, lo usa (formato JSON).
    Si no, pero existe SEARCH_URL, usa ese como único filtro.
    Si no existe ninguno, usa el valor por defecto.
    """
    # Intentar cargar desde JSON en variable de entorno
    search_filters_json = os.getenv("SEARCH_FILTERS_JSON", None)
    
    if search_filters_json:
        try:
            filters = json.loads(search_filters_json)
            # Validar formato
            if isinstance(filters, list):
                # Cada filtro debe tener 'name' y 'url'
                validated_filters = []
                for i, filter_item in enumerate(filters):
                    if isinstance(filter_item, dict) and "name" in filter_item and "url" in filter_item:
                        validated_filters.append({
                            "name": filter_item["name"],
                            "url": filter_item["url"]
                        })
                    else:
                        print(f"⚠️ Advertencia: Filtro {i+1} ignorado (falta 'name' o 'url')")
                return validated_filters if validated_filters else None
            elif isinstance(filters, dict):
                # Formato alternativo: dict con claves como nombres
                validated_filters = []
                for name, url in filters.items():
                    validated_filters.append({"name": name, "url": url})
                return validated_filters if validated_filters else None
        except json.JSONDecodeError as e:
            print(f"⚠️ Error al parsear SEARCH_FILTERS_JSON: {e}")
    
    # Si no hay múltiples filtros pero hay SEARCH_URL, convertir a formato de filtro único
    if SEARCH_URL:
        return [{"name": "Filtro único", "url": SEARCH_URL}]
    
    return None

# Cargar filtros de búsqueda (para cuando se usa desde config.py directamente)
SEARCH_FILTERS = load_search_filters()

# Compatibilidad: Si no hay filtros definidos, usar URL única
if not SEARCH_FILTERS:
    SEARCH_FILTERS = [{"name": "Filtro único", "url": SEARCH_URL}]

# Función para cargar filtros desde config (cuando se llama desde main.py)
def load_search_filters_from_config():
    """Carga filtros desde config.py (variables de entorno o valores por defecto)."""
    filters = load_search_filters()
    if not filters:
        filters = [{"name": "Filtro único", "url": SEARCH_URL}]
    return filters

# ============ FILTROS ADICIONALES (opcionales) ============
# Estos filtros se aplican además de los que ya están en la URL
# Si no los necesitas, déjalos en None

FILTERS = {
    "precio_min": os.getenv("PRICE_MIN", None),  # Precio mínimo en CLP (opcional)
    "precio_max": os.getenv("PRICE_MAX", None),  # Precio máximo en CLP (opcional)
    "dormitorios_min": os.getenv("BEDROOMS_MIN", None),  # Cantidad mínima de dormitorios (opcional)
    "tipo": os.getenv("PROPERTY_TYPE", None),  # "casa" o "departamento" (opcional)
}

# Convertir strings a números si están definidos
if FILTERS["precio_min"]:
    FILTERS["precio_min"] = int(FILTERS["precio_min"])
if FILTERS["precio_max"]:
    FILTERS["precio_max"] = int(FILTERS["precio_max"])
if FILTERS["dormitorios_min"]:
    FILTERS["dormitorios_min"] = int(FILTERS["dormitorios_min"])

# ============ VALIDACIÓN ============
def validate_config(search_filters=None):
    """
    Valida que la configuración esté completa.
    
    Args:
        search_filters: Lista de filtros a validar (opcional). Si no se proporciona, usa SEARCH_FILTERS.
    """
    errors = []
    filters_to_validate = search_filters if search_filters is not None else SEARCH_FILTERS
    
    if not GMAIL_USER:
        errors.append("GMAIL_USER no está configurado")
    if not GMAIL_PASSWORD:
        errors.append("GMAIL_PASSWORD no está configurado")
    if not RECIPIENTS:
        errors.append("RECIPIENTS no está configurado (al menos un destinatario)")
    if not filters_to_validate or len(filters_to_validate) == 0:
        errors.append("No hay filtros configurados (necesitas al menos un filtro)")
    else:
        # Validar que cada filtro tenga URL válida
        for i, filter_item in enumerate(filters_to_validate):
            if not filter_item.get("url"):
                errors.append(f"Filtro {i+1} ({filter_item.get('name', 'Sin nombre')}) no tiene URL")
    
    if errors:
        raise ValueError(f"Errores de configuración: {', '.join(errors)}")
    
    return True

if __name__ == "__main__":
    # Validar configuración al ejecutar directamente
    try:
        validate_config()
        print("✓ Configuración válida")
        print(f"  Email: {GMAIL_USER}")
        print(f"  Destinatarios: {', '.join(RECIPIENTS)}")
        print(f"  Intervalo: {CHECK_INTERVAL_MINUTES} minutos")
        print(f"\n  Filtros configurados ({len(SEARCH_FILTERS)}):")
        for i, filter_item in enumerate(SEARCH_FILTERS, 1):
            print(f"    {i}. {filter_item['name']}")
            print(f"       URL: {filter_item['url'][:70]}...")
    except ValueError as e:
        print(f"✗ {e}")


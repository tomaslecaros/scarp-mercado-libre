"""
Scraper simplificado para Portal Inmobiliario.
Versión optimizada para producción con mejor manejo de errores.
"""
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configuración de Selenium optimizada para producción
def get_driver(headless: bool = True):
    """
    Crea y retorna un driver de Selenium configurado para producción.

    Args:
        headless: Si True, ejecuta el navegador sin interfaz gráfica

    Returns:
        WebDriver configurado
    """
    chrome_options = Options()

    # Opciones esenciales para headless y producción
    if headless:
        chrome_options.add_argument('--headless=new')

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--silent')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Deshabilitar imágenes y recursos innecesarios para acelerar carga
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Bloquear imágenes
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Detectar si estamos en producción (Docker/Linux) o desarrollo (Windows)
    chrome_binary = os.getenv('CHROME_BINARY', None)
    chromedriver_path = os.getenv('CHROMEDRIVER_PATH', None)

    # En Docker/Linux, usar chromium instalado por apt
    if chrome_binary:
        chrome_options.binary_location = chrome_binary

    try:
        if chromedriver_path and os.path.exists(chromedriver_path):
            # Usar driver del sistema si está disponible
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            # Intentar sin especificar path (usar el del sistema)
            driver = webdriver.Chrome(options=chrome_options)

        return driver
    except Exception as e:
        print(f"❌ Error al inicializar Chrome: {e}")
        raise

def extract_price(price_text: str) -> tuple:
    """
    Extrae el precio numérico y la unidad de un texto.

    Returns:
        Tuple (precio, unidad) donde precio es int o None, unidad es 'UF', 'CLP', o None
    """
    if not price_text:
        return None, None

    price_text_upper = price_text.upper().strip()
    is_uf = bool(re.search(r'\bUF\b', price_text_upper))

    # Remover todo excepto números
    cleaned = re.sub(r'[^\d.,]', '', price_text)

    if not cleaned:
        return None, None

    # Remover puntos y comas (separadores de miles)
    numbers_only = cleaned.replace('.', '').replace(',', '')

    if not numbers_only:
        return None, None

    try:
        price_value = int(numbers_only)
        unidad = 'UF' if is_uf else 'CLP'
        return price_value, unidad
    except ValueError:
        return None, None

def extract_property_id(url: str) -> Optional[str]:
    """
    Extrae el ID único de una propiedad desde su URL.
    Ejemplo: 'https://...MLC-123456789-...' -> 'MLC-123456789'
    """
    if not url:
        return None

    # Buscar patrón MLC- seguido de números
    match = re.search(r'MLC-?\d+', url, re.IGNORECASE)
    if match:
        return match.group(0).upper()

    # Alternativa: buscar cualquier número largo en la URL
    match = re.search(r'/(\d{8,})', url)
    if match:
        return match.group(1)

    # Última opción: usar el path de la URL como ID
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]
    if path_parts:
        return path_parts[-1]

    return None

def scroll_page_simple(driver, max_scrolls: int = 5, scroll_pause_time: float = 2.0):
    """
    Hace scroll automático simplificado para cargar propiedades.

    Args:
        driver: WebDriver de Selenium
        max_scrolls: Número máximo de scrolls
        scroll_pause_time: Tiempo de espera entre scrolls

    Returns:
        Número de scrolls realizados
    """
    print("📜 Haciendo scroll para cargar propiedades...")

    for _ in range(max_scrolls):
        # Scroll hacia abajo
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

    print(f"✓ Scroll completado: {max_scrolls} scrolls realizados")
    return max_scrolls

def scrape_properties(url: str, headless: bool = True, max_retries: int = 3) -> List[Dict]:
    """
    Scrapea propiedades de Portal Inmobiliario usando Selenium.
    Versión simplificada y robusta para producción.

    Args:
        url: URL a scrapear
        headless: Si True, ejecuta el navegador sin interfaz gráfica
        max_retries: Número máximo de reintentos en caso de error

    Returns:
        Lista de diccionarios con información de cada propiedad
    """
    print(f"🔍 Scrapeando: {url[:80]}...")

    for attempt in range(max_retries):
        driver = None

        try:
            # Usar Selenium para cargar contenido dinámico
            print(f"🌐 Abriendo navegador (intento {attempt + 1}/{max_retries})...")
            driver = get_driver(headless=headless)
            driver.set_page_load_timeout(60)  # Timeout de 60 segundos

            driver.get(url)

            # Esperar a que la página cargue
            print("⏳ Esperando carga inicial...")
            time.sleep(5)

            # Hacer scroll simple
            scroll_page_simple(driver, max_scrolls=5, scroll_pause_time=2.0)

            # Esperar un poco más
            time.sleep(2)

            # Obtener el HTML completo
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')

            properties = []

            # Selector para items de propiedades
            property_items = soup.select('li.ui-search-layout__item, article.ui-search-result, div.ui-search-result')

            if not property_items:
                property_items = soup.select('div[data-item-id], a[href*="portalinmobiliario.com"]')

            print(f"📦 Encontradas {len(property_items)} propiedades potenciales")

            # Extraer propiedades únicas
            seen_ids = set()

            for item in property_items:
                try:
                    prop = extract_property_info(item, url)
                    if prop and prop.get('id'):
                        prop_id = prop['id']
                        if prop_id not in seen_ids:
                            seen_ids.add(prop_id)
                            properties.append(prop)
                except Exception:
                    continue

            print(f"✓ Extraídas {len(properties)} propiedades válidas")

            # Cerrar navegador
            if driver:
                driver.quit()
                print("🔒 Navegador cerrado")

            return properties

        except WebDriverException as e:
            print(f"⚠ Error en intento {attempt + 1}/{max_retries}: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass

            if attempt < max_retries - 1:
                print(f"   Reintentando en 5 segundos...")
                time.sleep(5)
            else:
                print(f"❌ Máximo de reintentos alcanzado")
                return []

        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass

            if attempt < max_retries - 1:
                print(f"   Reintentando en 5 segundos...")
                time.sleep(5)
            else:
                return []

    return []

def extract_property_info(item, base_url: str) -> Optional[Dict]:
    """Extrae información de una propiedad desde un elemento HTML."""

    # Buscar link de la propiedad
    link_elem = item.select_one('a[href*="portalinmobiliario.com"], a.ui-search-link')
    if not link_elem:
        link_elem = item.find('a', href=True)

    if not link_elem or not link_elem.get('href'):
        return None

    link = link_elem['href']
    if link.startswith('/'):
        link = urljoin(base_url, link)

    property_id = extract_property_id(link)
    if not property_id:
        return None

    # Extraer título
    title_elem = item.select_one('h2, .ui-search-item__title, .ui-search-item__group__element')
    title = title_elem.get_text(strip=True) if title_elem else "Propiedad sin título"

    # Extraer precio
    price_elem = item.select_one('.ui-search-price, .price, [data-price], .ui-search-item__price')
    price_text = price_elem.get_text(strip=True) if price_elem else ""
    price, price_unit = extract_price(price_text)

    # Extraer ubicación
    location_elem = item.select_one('.ui-search-item__location, .location, [data-location]')
    location = location_elem.get_text(strip=True) if location_elem else ""

    # Extraer dormitorios
    bedrooms_elem = item.select_one('[data-bedrooms], .bedrooms, .ui-search-item__bedrooms')
    bedrooms = None
    if bedrooms_elem:
        bedrooms_text = bedrooms_elem.get_text(strip=True)
        bedrooms_match = re.search(r'(\d+)', bedrooms_text)
        if bedrooms_match:
            bedrooms = int(bedrooms_match.group(1))

    # Extraer baños
    bathrooms_elem = item.select_one('[data-bathrooms], .bathrooms, .ui-search-item__bathrooms')
    bathrooms = None
    if bathrooms_elem:
        bathrooms_text = bathrooms_elem.get_text(strip=True)
        bathrooms_match = re.search(r'(\d+)', bathrooms_text)
        if bathrooms_match:
            bathrooms = int(bathrooms_match.group(1))

    # Extraer área (m²)
    area_elem = item.select_one('[data-area], .area, .ui-search-item__area')
    area = None
    if area_elem:
        area_text = area_elem.get_text(strip=True)
        area_match = re.search(r'(\d+)', area_text.replace('.', '').replace(',', ''))
        if area_match:
            area = int(area_match.group(1))

    return {
        'id': property_id,
        'title': title,
        'price': price,
        'price_unit': price_unit,
        'location': location,
        'link': link,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'area': area
    }

def filter_properties(properties: List[Dict], filters: Dict) -> List[Dict]:
    """
    Filtra propiedades según criterios adicionales.
    """
    if not filters:
        return properties

    filtered = []

    for prop in properties:
        # Filtro de precio mínimo
        if filters.get('precio_min') and prop.get('price'):
            if prop['price'] < filters['precio_min']:
                continue

        # Filtro de precio máximo
        if filters.get('precio_max') and prop.get('price'):
            if prop['price'] > filters['precio_max']:
                continue

        # Filtro de dormitorios mínimos
        if filters.get('dormitorios_min') and prop.get('bedrooms'):
            if prop['bedrooms'] < filters['dormitorios_min']:
                continue

        filtered.append(prop)

    return filtered

if __name__ == "__main__":
    # Prueba del scraper
    print("Probando scraper...")
    from config import SEARCH_URL
    props = scrape_properties(SEARCH_URL)

    if props:
        print(f"\n✓ Se encontraron {len(props)} propiedades:")
        for i, prop in enumerate(props[:3], 1):
            print(f"\n{i}. {prop.get('title', 'Sin título')}")
            print(f"   Precio: ${prop.get('price', 'N/A'):,}" if prop.get('price') else "   Precio: N/A")
            print(f"   ID: {prop.get('id')}")
    else:
        print("⚠ No se encontraron propiedades")

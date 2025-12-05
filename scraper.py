"""
Scraper para Portal Inmobiliario.
Extrae información de propiedades de la página de búsqueda usando Selenium.
"""
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from config import SEARCH_URL

# Configuración de Selenium
def get_driver(headless: bool = True):
    """
    Crea y retorna un driver de Selenium configurado.
    
    Args:
        headless: Si True, ejecuta el navegador sin interfaz gráfica (para servidores)
    
    Returns:
        WebDriver configurado
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')  # Sin interfaz gráfica
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Intentar usar ChromeDriverManager para descargar automáticamente el driver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        # Si falla, intentar con el driver del sistema
        print(f"⚠ Advertencia: {e}. Intentando con driver del sistema...")
        driver = webdriver.Chrome(options=chrome_options)
    
    return driver

def extract_price(price_text: str) -> tuple:
    """
    Extrae el precio numérico y la unidad de un texto.
    
    Returns:
        Tuple (precio, unidad) donde:
        - precio: int o None
        - unidad: 'UF', 'CLP', o None
    
    Ejemplos:
        '$ 1.500.000' -> (1500000, 'CLP')
        '1.200 UF' -> (1200, 'UF')
        'UF 1.200' -> (1200, 'UF')
    """
    if not price_text:
        return None, None
    
    price_text_upper = price_text.upper().strip()
    
    # Detectar si es UF (buscar UF antes o después del número)
    is_uf = bool(re.search(r'\bUF\b', price_text_upper))
    
    # Remover puntos que son separadores de miles, pero mantener la estructura
    # Primero detectar el formato del número
    # Puede ser: 1.500.000 o 1,500,000 o 1200
    
    # Remover todo excepto números, puntos y comas
    cleaned = re.sub(r'[^\d.,]', '', price_text)
    
    if not cleaned:
        return None, None
    
    # Determinar si usa punto o coma como separador de miles
    # En Chile: punto para miles, coma para decimales (pero en precios generalmente no hay decimales)
    # Portal Inmobiliario generalmente usa puntos para miles
    
    # Remover puntos (separadores de miles) y comas
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
    
    # Buscar patrones comunes de ID en URLs de Portal Inmobiliario
    # Patrón: MLC- seguido de números
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

def scroll_page(driver, max_scrolls: int = 30, scroll_pause_time: float = 3.0):
    """
    Hace scroll automático en la página para cargar todas las propiedades.
    
    Args:
        driver: WebDriver de Selenium
        max_scrolls: Número máximo de scrolls a realizar
        scroll_pause_time: Tiempo de espera entre scrolls (segundos)
    
    Returns:
        Número de scrolls realizados
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    no_change_count = 0  # Contador de veces que no hay cambio
    
    print("📜 Haciendo scroll para cargar todas las propiedades...")
    
    while scrolls < max_scrolls:
        # Scroll hacia abajo suavemente
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Esperar a que cargue nuevo contenido
        time.sleep(scroll_pause_time)
        
        # Calcular nueva altura y comparar
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            no_change_count += 1
            # Si no hay cambio 3 veces seguidas, probablemente no hay más contenido
            if no_change_count >= 3:
                print(f"✓ Fin del scroll después de {scrolls + 1} intentos (sin cambios)")
                break
            # Intentar scroll más pequeño para activar lazy loading
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)
        else:
            no_change_count = 0  # Resetear contador si hay cambio
            print(f"   Scroll #{scrolls + 1}: Nueva altura {new_height}px (cargando más contenido...)")
        
        last_height = new_height
        scrolls += 1
        
        # Mostrar progreso cada 5 scrolls
        if scrolls % 5 == 0:
            print(f"   Progreso: {scrolls} scrolls realizados...")
    
    # Hacer un último scroll lento desde arriba hacia abajo para asegurar que todo se cargue
    print("   Haciendo scroll final para asegurar carga completa...")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    for i in range(1, 6):
        scroll_position = (i * 20) / 100 * driver.execute_script("return document.body.scrollHeight")
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(0.8)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Más tiempo al final
    
    print(f"✓ Scroll completado: {scrolls} scrolls realizados")
    return scrolls

def scrape_properties(url: str = None, use_selenium: bool = True, headless: bool = True) -> List[Dict]:
    """
    Scrapea propiedades de Portal Inmobiliario usando Selenium con scroll automático.
    
    Args:
        url: URL a scrapear (si es None, usa SEARCH_URL)
        use_selenium: Si True, usa Selenium. Si False, usa requests (método antiguo)
        headless: Si True, ejecuta el navegador sin interfaz gráfica
    
    Returns:
        Lista de diccionarios con información de cada propiedad:
        {
            'id': 'MLC-123456789',
            'title': 'Casa en Las Condes',
            'price': 1500000,
            'price_unit': 'CLP',  # 'UF' o 'CLP'
            'location': 'Las Condes',
            'link': 'https://...',
            'bedrooms': 4,
            'bathrooms': 2,
            'area': 120
        }
    """
    if url is None:
        url = SEARCH_URL
    
    print(f"🔍 Scrapeando: {url[:80]}...")
    
    driver = None
    
    try:
        if use_selenium:
            # Usar Selenium para cargar contenido dinámico
            print("🌐 Abriendo navegador con Selenium...")
            driver = get_driver(headless=headless)
            driver.get(url)
            
            # Esperar a que la página cargue
            print("⏳ Esperando a que la página cargue...")
            time.sleep(5)  # Más tiempo para carga inicial
            
            # Hacer scroll para cargar todas las propiedades
            scroll_page(driver, max_scrolls=30, scroll_pause_time=3.0)
            
            # Esperar un poco más para que termine de cargar
            time.sleep(3)
            
            # Obtener el HTML completo después del scroll
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            
        else:
            # Método antiguo con requests (fallback)
            import requests
            HEADERS = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
        
        properties = []
        
        # Portal Inmobiliario usa diferentes estructuras según la página
        # Intentamos múltiples selectores comunes
        
        # Selector 1: Items de propiedades (más común)
        property_items = soup.select('li.ui-search-layout__item, article.ui-search-result, div.ui-search-result')
        
        if not property_items:
            # Selector 2: Cards de propiedades
            property_items = soup.select('div[data-item-id], a[href*="portalinmobiliario.com"]')
        
        print(f"📦 Encontradas {len(property_items)} propiedades potenciales en el HTML")
        
        # Extraer propiedades únicas usando IDs para evitar duplicados
        seen_ids = set()
        
        for item in property_items:
            try:
                prop = extract_property_info(item, url)
                if prop and prop.get('id'):
                    prop_id = prop['id']
                    # Evitar duplicados
                    if prop_id not in seen_ids:
                        seen_ids.add(prop_id)
                        properties.append(prop)
            except Exception as e:
                # Continuar con la siguiente propiedad si hay error
                continue
        
        print(f"✓ Extraídas {len(properties)} propiedades válidas y únicas")
        return properties
        
    except WebDriverException as e:
        print(f"❌ Error con Selenium: {e}")
        print("⚠ Intentando con método alternativo (requests)...")
        # Fallback al método antiguo
        if use_selenium:
            return scrape_properties(url, use_selenium=False)
        return []
    except Exception as e:
        print(f"❌ Error al procesar: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        # Cerrar el navegador si se abrió
        if driver:
            try:
                driver.quit()
                print("🔒 Navegador cerrado")
            except:
                pass

def extract_property_info(item, base_url: str) -> Optional[Dict]:
    """Extrae información de una propiedad desde un elemento HTML."""
    
    # Buscar link de la propiedad
    link_elem = item.select_one('a[href*="portalinmobiliario.com"], a.ui-search-link')
    if not link_elem:
        link_elem = item.find('a', href=True)
    
    if not link_elem or not link_elem.get('href'):
        return None
    
    link = link_elem['href']
    # Convertir a URL absoluta si es relativa
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
    
    # Extraer fecha de publicación (intentar múltiples selectores)
    published_date = None
    date_elem = item.select_one('.ui-search-item__date, .date, [data-date], .published-date, .ui-search-item__subtitle')
    if not date_elem:
        # Buscar texto que contenga fechas
        all_text = item.get_text()
        # Buscar patrones como "Publicado hace X días", "Hace X días", fechas específicas
        date_patterns = [
            r'Publicado\s+hace\s+(\d+)\s+d[íi]as?',
            r'Hace\s+(\d+)\s+d[íi]as?',
            r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})',  # Fechas formato DD/MM/YYYY
        ]
        for pattern in date_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                date_elem_text = match.group(0)
                published_date = date_elem_text.strip()
                break
    
    if date_elem and not published_date:
        published_date = date_elem.get_text(strip=True)
    
    return {
        'id': property_id,
        'title': title,
        'price': price,
        'price_unit': price_unit,  # 'UF' o 'CLP'
        'location': location,
        'link': link,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'area': area,
        'published_date': published_date  # Fecha de publicación si está disponible
    }

def filter_properties(properties: List[Dict], filters: Dict) -> List[Dict]:
    """
    Filtra propiedades según criterios adicionales.
    
    Args:
        properties: Lista de propiedades
        filters: Diccionario con filtros a aplicar
    
    Returns:
        Lista de propiedades que cumplen los filtros
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
        
        # Filtro de tipo (necesitaríamos más información para esto)
        # Por ahora lo dejamos como está ya que la URL ya filtra por tipo
        
        filtered.append(prop)
    
    return filtered

if __name__ == "__main__":
    # Prueba del scraper
    print("Probando scraper...")
    props = scrape_properties()
    
    if props:
        print(f"\n✓ Se encontraron {len(props)} propiedades:")
        for i, prop in enumerate(props[:3], 1):  # Mostrar solo las primeras 3
            print(f"\n{i}. {prop.get('title', 'Sin título')}")
            print(f"   Precio: ${prop.get('price', 'N/A'):,}" if prop.get('price') else "   Precio: N/A")
            print(f"   ID: {prop.get('id')}")
            print(f"   Link: {prop.get('link', 'N/A')[:80]}...")
    else:
        print("⚠ No se encontraron propiedades. Verifica la URL y los selectores CSS.")


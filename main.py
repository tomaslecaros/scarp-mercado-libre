"""
Notificador de Propiedades - Portal Inmobiliario
Loop principal que ejecuta el scraper periódicamente y envía notificaciones.
"""
import time
import sys
from datetime import datetime
from typing import List, Dict

# ============ CONFIGURACIÓN DE FILTROS ============
# 👇 AGREGA TUS FILTROS AQUÍ 👇
# 
# Cada filtro debe tener:
#   - "name": Una descripción clara (ej: "4 piezas máximo 1.800.000")
#   - "url": La URL completa de Portal Inmobiliario con tus filtros aplicados
#
# Para obtener la URL:
#   1. Ve a Portal Inmobiliario
#   2. Aplica tus filtros (precio, dormitorios, ubicación, etc.)
#   3. Copia la URL completa de la búsqueda
#   4. Pégalo aquí en "url"
#
# Puedes agregar tantos filtros como quieras. Cada uno será monitoreado independientemente.

SEARCH_FILTERS = [
        {
        "name": "CASA 4-5 piezas, máximo 2.000.000 CLP",
        "url": "https://www.portalinmobiliario.com/arriendo/casa/_DisplayType_M_PriceRange_5CLP-2000000CLP_BEDROOMS_4-5_item*location_lat:-33.42955368359416*-33.38104582647317,lon:-70.63084336547851*-70.52475663452148?polygon_location=%7C%7DvjEx%7EwmLy%40gB%3F%7D%5BjDwI%7CPuIl%5DmEbO%7BK%60Gyg%40x%40c%7C%40vc%40gQjf%40qGvI%3F%7CGfCpKvI%7CG%7CLpKlb%40bFlEbObyAlLvJfNfBbFrH%7EGlSbFxYx%40%7CLpBnFx%40lT%7DPb%5EkLre%40sSpUwIdB%3FdAqm%40pGy%40bAunAdAmLgBaXgQoTmc%40eW_hAmLe_%40y%40%7BZnCkD%3FiCuAgCuA%3FZjS"
    },
    {
        "name": "DEPARTAMENTO 4-5 piezas máximo 1.500.000 CLP",
        "url": "https://www.portalinmobiliario.com/arriendo/departamento/_DisplayType_M_PriceRange_5CLP-1500000CLP_BEDROOMS_4-5_item*location_lat:-33.42955368359416*-33.38104582647317,lon:-70.63084336547851*-70.52475663452148?polygon_location=%7C%7DvjEx%7EwmLy%40gB%3F%7D%5BjDwI%7CPuIl%5DmEbO%7BK%60Gyg%40x%40c%7C%40vc%40gQjf%40qGvI%3F%7CGfCpKvI%7CG%7CLpKlb%40bFlEbObyAlLvJfNfBbFrH%7EGlSbFxYx%40%7CLpBnFx%40lT%7DPb%5EkLre%40sSpUwIdB%3FdAqm%40pGy%40bAunAdAmLgBaXgQoTmc%40eW_hAmLe_%40y%40%7BZnCkD%3FiCuAgCuA%3FZjS"
    },
       {
        "name": "DEPARTAMENTO 5 piezas máximo 2.000.000 CLP",
        "url": "https://www.portalinmobiliario.com/arriendo/departamento/_DisplayType_M_PriceRange_5CLP-2000000CLP_BEDROOMS_5-5_item*location_lat:-33.42955368359416*-33.38104582647317,lon:-70.63084336547851*-70.52475663452148?polygon_location=%7C%7DvjEx%7EwmLy%40gB%3F%7D%5BjDwI%7CPuIl%5DmEbO%7BK%60Gyg%40x%40c%7C%40vc%40gQjf%40qGvI%3F%7CGfCpKvI%7CG%7CLpKlb%40bFlEbObyAlLvJfNfBbFrH%7EGlSbFxYx%40%7CLpBnFx%40lT%7DPb%5EkLre%40sSpUwIdB%3FdAqm%40pGy%40bAunAdAmLgBaXgQoTmc%40eW_hAmLe_%40y%40%7BZnCkD%3FiCuAgCuA%3FZjS"
    },
    {
        "name": "CASA 5 piezas máximo 2.500.000 CLP",
        "url": "https://www.portalinmobiliario.com/arriendo/casa/_DisplayType_M_PriceRange_5CLP-2500000CLP_BEDROOMS_5-5_item*location_lat:-33.42980439238421*-33.380794976935,lon:-70.63144418029785*-70.52415581970214?polygon_location=%7C%7DvjEx%7EwmLy%40gB%3F%7D%5BjDwI%7CPuIl%5DmEbO%7BK%60Gyg%40x%40c%7C%40vc%40gQjf%40qGvI%3F%7CGfCpKvI%7CG%7CLpKlb%40bFlEbObyAlLvJfNfBbFrH%7EGlSbFxYx%40%7CLpBnFx%40lT%7DPb%5EkLre%40sSpUwIdB%3FdAqm%40pGy%40bAunAdAmLgBaXgQoTmc%40eW_hAmLe_%40y%40%7BZnCkD%3FiCuAgCuA%3FZjS"
    },

]

# Si no defines filtros aquí (lista vacía), el sistema intentará usar la configuración de config.py
# Puedes dejar SEARCH_FILTERS vacío [] para usar variables de entorno o config.py como respaldo

from config import (
    CHECK_INTERVAL_MINUTES,
    FILTERS,
    validate_config,
    load_search_filters_from_config
)
from scraper import scrape_properties, filter_properties
from storage import get_new_properties
from email_service import send_email

# Cargar filtros: primero intenta usar los definidos aquí, si no hay, usa config.py
if not SEARCH_FILTERS:
    SEARCH_FILTERS = load_search_filters_from_config()

def format_property_summary(properties: List[Dict]) -> str:
    """Formatea un resumen de las propiedades para logging."""
    if not properties:
        return "0 propiedades"
    
    summary = f"{len(properties)} propiedad(es): "
    summaries = []
    for prop in properties[:3]:  # Mostrar solo las primeras 3
        title = prop.get('title', 'Sin título')[:40]
        price = prop.get('price')
        price_unit = prop.get('price_unit', 'CLP')
        
        if price:
            if price_unit == 'UF':
                price_str = f"{price:,} UF".replace(",", ".")
            else:
                price_str = f"${price:,}".replace(",", ".")
        else:
            price_str = "N/A"
        
        summaries.append(f"{title} ({price_str})")
    
    summary += ", ".join(summaries)
    if len(properties) > 3:
        summary += f", y {len(properties) - 3} más..."
    
    return summary

def run_check():
    """
    Ejecuta una verificación completa recorriendo todos los filtros configurados:
    1. Para cada filtro: Scrapea propiedades
    2. Aplica filtros adicionales (si los hay)
    3. Identifica propiedades nuevas (agregando información del filtro)
    4. Acumula todas las propiedades nuevas
    5. Envía un solo email con todas las propiedades nuevas agrupadas por filtro
    """
    print("\n" + "="*80)
    print(f"🔍 Verificando propiedades - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*80)

    # Lista para acumular todas las propiedades nuevas de todos los filtros
    all_new_properties = []
    errors_count = 0

    try:
        # Estado inicial del almacenamiento
        from storage import load_properties_data, get_storage_stats
        stats = get_storage_stats()
        print(f"\n📊 Estado del almacenamiento ANTES de la verificación:")
        print(f"   Total de propiedades ya vistas: {stats['total_seen']}")

        # Recorrer cada filtro configurado
        print(f"\n🔍 Filtros configurados: {len(SEARCH_FILTERS)}")
        
        for filter_idx, search_filter in enumerate(SEARCH_FILTERS, 1):
            filter_name = search_filter.get('name', f'Filtro {filter_idx}')
            filter_url = search_filter.get('url', '')
            
            print(f"\n{'='*80}")
            print(f"📋 FILTRO {filter_idx}/{len(SEARCH_FILTERS)}: {filter_name}")
            print(f"{'='*80}")
            
            if not filter_url:
                print(f"⚠ Saltando filtro '{filter_name}': No tiene URL configurada")
                continue

            try:
                # 1. Scrapear propiedades de este filtro
                print(f"\n1️⃣ SCRAPING: Obteniendo propiedades...")
                print(f"   URL: {filter_url[:70]}...")

                all_properties = scrape_properties(filter_url)

                if not all_properties:
                    print(f"⚠ No se encontraron propiedades en este filtro.")
                    continue
            except Exception as e:
                print(f"❌ Error al scrapear filtro '{filter_name}': {e}")
                errors_count += 1
                continue
            
            print(f"✓ Scraping completado: {len(all_properties)} propiedades encontradas")
            
            # 2. Aplicar filtros adicionales (si los hay)
            if any(FILTERS.values()):
                print(f"\n2️⃣ FILTRADO: Aplicando filtros adicionales...")
                filtered_properties = filter_properties(all_properties, FILTERS)
                print(f"✓ Después de aplicar filtros: {len(filtered_properties)} propiedades")
            else:
                filtered_properties = all_properties
            
            # 3. Identificar propiedades nuevas y agregar información del filtro
            print(f"\n3️⃣ COMPARACIÓN: Identificando propiedades nuevas...")
            new_properties = get_new_properties(filtered_properties, property_id_key='id')
            
            # Agregar información del filtro a cada propiedad nueva
            for prop in new_properties:
                prop['filter_name'] = filter_name
                prop['filter_url'] = filter_url
            
            if new_properties:
                print(f"✨ ¡ENCONTRADAS {len(new_properties)} PROPIEDAD(ES) NUEVA(S) en este filtro!")
                all_new_properties.extend(new_properties)
            else:
                print(f"✓ No hay propiedades nuevas en este filtro")
        
        # Resumen de todas las propiedades nuevas encontradas
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN GENERAL")
        print(f"{'='*80}")
        print(f"Total de propiedades nuevas encontradas: {len(all_new_properties)}")
        if errors_count > 0:
            print(f"⚠ Errores durante el scraping: {errors_count} filtro(s) con problemas")
        
        if not all_new_properties:
            print(f"\n✓ Resultado: No hay propiedades nuevas en ninguno de los filtros")
            return
        
        # Agrupar propiedades por filtro para mostrar en logs
        from collections import defaultdict
        properties_by_filter = defaultdict(list)
        for prop in all_new_properties:
            filter_name = prop.get('filter_name', 'Sin filtro')
            properties_by_filter[filter_name].append(prop)
        
        print(f"\n📧 Propiedades nuevas por filtro:")
        for filter_name, props in properties_by_filter.items():
            print(f"   • {filter_name}: {len(props)} propiedad(es)")
            for i, prop in enumerate(props[:2], 1):  # Mostrar solo las primeras 2
                title = prop.get('title', 'Sin título')[:50]
                price = prop.get('price')
                price_unit = prop.get('price_unit', 'CLP')
                if price:
                    if price_unit == 'UF':
                        price_str = f"{price:,} UF".replace(",", ".")
                    else:
                        price_str = f"${price:,}".replace(",", ".")
                else:
                    price_str = "N/A"
                print(f"     {i}. {title} - {price_str}")
            if len(props) > 2:
                print(f"     ... y {len(props) - 2} más")
        
        # 4. Enviar email con todas las propiedades nuevas (agrupadas por filtro)
        print(f"\n4️⃣ EMAIL: Enviando notificación por email...")
        success = send_email(all_new_properties)
        
        if success:
            from config import RECIPIENTS
            print(f"   ✓ Email enviado exitosamente a {len(RECIPIENTS)} destinatario(s)")
        else:
            print(f"   ⚠ Hubo un problema al enviar el email")
        
        # 5. Estado final
        print(f"\n5️⃣ ALMACENAMIENTO: Guardando propiedades nuevas...")
        stats_after = get_storage_stats()
        print(f"   Total de propiedades vistas ahora: {stats_after['total_seen']}")
        print(f"   Propiedades nuevas guardadas: {len(all_new_properties)}")
        
        print(f"\n{'='*80}")
        print(f"✅ Verificación completada exitosamente")
        print(f"{'='*80}")
        
    except KeyboardInterrupt:
        print("\n⚠ Interrupción del usuario. Cerrando...")
        raise
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal con el loop infinito."""
    print("="*80)
    print("🏠 Notificador de Propiedades - Portal Inmobiliario")
    print("="*80)
    
    # Validar configuración (pasar los filtros definidos aquí)
    try:
        validate_config(SEARCH_FILTERS)
        print("✓ Configuración válida")
    except ValueError as e:
        print(f"❌ Error de configuración: {e}")
        print("\nPor favor, configura:")
        print("  1. Las variables de entorno en .env (GMAIL_USER, GMAIL_PASSWORD, RECIPIENTS)")
        print("  2. Los filtros de búsqueda en main.py (línea ~20)")
        sys.exit(1)
    
    from config import GMAIL_USER, RECIPIENTS
    from storage import get_storage_stats
    
    # Mostrar configuración
    print(f"\n📋 CONFIGURACIÓN:")
    print(f"   📧 Email de envío: {GMAIL_USER}")
    print(f"   📨 Destinatarios: {', '.join(RECIPIENTS)}")
    print(f"   ⏰ Intervalo de verificación: {CHECK_INTERVAL_MINUTES} minuto(s)")
    print(f"   🔍 Filtros configurados: {len(SEARCH_FILTERS)}")
    for i, filter_item in enumerate(SEARCH_FILTERS, 1):
        print(f"      {i}. {filter_item['name']}")
    
    # Mostrar estado inicial del almacenamiento
    stats = get_storage_stats()
    print(f"\n📊 ESTADO INICIAL:")
    print(f"   Propiedades ya vistas: {stats['total_seen']}")
    print(f"   Archivo de almacenamiento: {stats['storage_file']}")
    
    print("\n" + "="*80)
    print("🚀 Iniciando monitoreo continuo...")
    print("   Presiona Ctrl+C para detener")
    print("="*80)
    
    # Ejecutar primera verificación inmediatamente
    run_check()
    
    # Loop principal
    try:
        while True:
            # Esperar el intervalo configurado
            wait_seconds = CHECK_INTERVAL_MINUTES * 60
            print(f"\n{'='*80}")
            print(f"⏳ Esperando {CHECK_INTERVAL_MINUTES} minuto(s) hasta la próxima verificación...")
            print(f"{'='*80}")
            
            if CHECK_INTERVAL_MINUTES == 1:
                # Si es 1 minuto, mostrar contador de segundos
                for remaining_seconds in range(60, 0, -10):
                    print(f"   ⏱️  Esperando... {remaining_seconds} segundos restantes", end='\r')
                    time.sleep(10)
                print(f"   ⏱️  Esperando... 0 segundos    ")  # Limpiar línea
            else:
                # Contar hacia atrás cada minuto
                for remaining_minutes in range(CHECK_INTERVAL_MINUTES - 1, 0, -1):
                    time.sleep(60)  # Esperar 1 minuto
                    print(f"   ⏱️  {remaining_minutes} minuto(s) restante(s)...", end='\r')
                # Último minuto
                print(f"   ⏱️  Esperando últimos 60 segundos...", end='\r')
                time.sleep(60)
                print()  # Nueva línea después del último segundo
            
            # Ejecutar nueva verificación
            run_check()
            
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("🛑 Monitoreo detenido por el usuario")
        print("="*60)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


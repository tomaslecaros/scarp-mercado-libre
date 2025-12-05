"""
Script de prueba para verificar la configuración y hacer una prueba rápida del scraper.
"""
import sys

print("="*60)
print("🧪 Prueba de Configuración - Notificador de Propiedades")
print("="*60)

# 1. Verificar configuración
print("\n1️⃣ Verificando configuración...")
try:
    from config import validate_config, SEARCH_URL, GMAIL_USER, RECIPIENTS, CHECK_INTERVAL_MINUTES
    validate_config()
    print("✓ Configuración válida")
    print(f"  📧 Email: {GMAIL_USER}")
    print(f"  📨 Destinatarios: {len(RECIPIENTS)} destinatario(s)")
    print(f"  ⏰ Intervalo: {CHECK_INTERVAL_MINUTES} minutos")
    print(f"  🔗 URL: {SEARCH_URL[:100]}...")
except ValueError as e:
    print(f"❌ Error de configuración: {e}")
    print("\nPor favor, verifica tu archivo .env")
    sys.exit(1)

# 2. Probar scraper (una sola vez, sin loop)
print("\n2️⃣ Probando scraper (esto puede tomar unos segundos)...")
try:
    from scraper import scrape_properties
    
    print(f"🔍 Buscando propiedades en: {SEARCH_URL[:80]}...")
    properties = scrape_properties(SEARCH_URL)
    
    if properties:
        print(f"✓ Se encontraron {len(properties)} propiedades")
        print(f"\n📋 Mostrando todas las propiedades encontradas ({len(properties)} total):")
        print("=" * 80)
        for i, prop in enumerate(properties, 1):  # Mostrar TODAS las propiedades
            print(f"\n{'='*80}")
            print(f"{i}. {prop.get('title', 'Sin título')}")
            print(f"{'-'*80}")
            
            if prop.get('price'):
                price_unit = prop.get('price_unit', 'CLP')
                if price_unit == 'UF':
                    price_str = f"{prop['price']:,} UF".replace(",", ".")
                else:
                    price_str = f"${prop['price']:,}".replace(",", ".")
                print(f"   💰 Precio: {price_str}")
            
            if prop.get('location'):
                print(f"   📍 Ubicación: {prop['location']}")
            
            details = []
            if prop.get('bedrooms'):
                details.append(f"🛏️  {prop['bedrooms']} dormitorios")
            if prop.get('bathrooms'):
                details.append(f"🚿 {prop['bathrooms']} baños")
            if prop.get('area'):
                details.append(f"📐 {prop['area']} m²")
            
            if details:
                print(f"   {' | '.join(details)}")
            
            # Mostrar ID
            print(f"   🆔 ID: {prop.get('id', 'N/A')}")
            
            # Mostrar URL completa
            link = prop.get('link', 'N/A')
            if link and link != 'N/A':
                print(f"   🔗 URL: {link}")
            else:
                print(f"   🔗 URL: No disponible")
            
            # Mostrar fecha de publicación si está disponible
            if prop.get('published_date'):
                print(f"   📅 Publicación: {prop['published_date']}")
            else:
                print(f"   📅 Publicación: No disponible en la lista")
            
            print()
    else:
        print("⚠ No se encontraron propiedades")
        print("\nPosibles razones:")
        print("  - La URL puede estar incorrecta")
        print("  - Portal Inmobiliario puede haber cambiado su estructura")
        print("  - Puede requerir autenticación o tener protección anti-bot")
        
except Exception as e:
    print(f"❌ Error al probar el scraper: {e}")
    import traceback
    traceback.print_exc()

# 3. Verificar sistema de almacenamiento
print("\n3️⃣ Verificando sistema de almacenamiento...")
try:
    from storage import get_storage_stats
    stats = get_storage_stats()
    print(f"✓ Sistema de almacenamiento funcionando")
    print(f"  📊 Propiedades vistas: {stats['total_seen']}")
    print(f"  📁 Archivo: {stats['storage_file']}")
except Exception as e:
    print(f"⚠ Advertencia: {e}")

print("\n" + "="*60)
print("✅ Prueba completada")
print("="*60)
print("\nSi todo está bien, puedes ejecutar:")
print("  python main.py")
print("\nEsto iniciará el monitoreo continuo cada 5 minutos.")


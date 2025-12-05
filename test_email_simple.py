"""
Script de prueba SIMPLE para testear el envío de emails.
Envía TODAS las propiedades encontradas sin filtrar - solo para debug.
"""
import sys

print("="*80)
print("📧 PRUEBA DE ENVÍO DE EMAIL - Debug Simple")
print("="*80)

# 1. Verificar configuración
print("\n1️⃣ Verificando configuración...")
try:
    from config import GMAIL_USER, GMAIL_PASSWORD, RECIPIENTS, SEARCH_URL
    print(f"   📧 Email: {GMAIL_USER}")
    print(f"   🔑 Password: {'*' * len(GMAIL_PASSWORD) if GMAIL_PASSWORD else 'NO CONFIGURADO'}")
    print(f"   📨 Destinatarios: {', '.join(RECIPIENTS)}")
    
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("❌ Faltan credenciales de Gmail")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# 2. Scrapear propiedades (máximo 3 para prueba rápida)
print("\n2️⃣ Scrapeando propiedades (solo para probar email)...")
try:
    from scraper import scrape_properties
    properties = scrape_properties(SEARCH_URL)
    
    if not properties:
        print("⚠ No se encontraron propiedades. Usando datos de prueba...")
        # Crear propiedades de prueba
        properties = [
            {
                'id': 'TEST-001',
                'title': 'Propiedad de Prueba 1',
                'price': 1500000,
                'price_unit': 'CLP',
                'location': 'Las Condes',
                'link': 'https://www.portalinmobiliario.com/test1'
            },
            {
                'id': 'TEST-002',
                'title': 'Propiedad de Prueba 2',
                'price': 1800000,
                'price_unit': 'CLP',
                'location': 'Providencia',
                'link': 'https://www.portalinmobiliario.com/test2'
            }
        ]
    else:
        # Tomar solo las primeras 3 para prueba rápida
        properties = properties[:3]
        print(f"✓ Usando {len(properties)} propiedades para la prueba")
    
except Exception as e:
    print(f"⚠ Error al scrapear: {e}")
    print("Usando datos de prueba...")
    properties = [
        {
            'id': 'TEST-001',
            'title': 'Propiedad de Prueba',
            'price': 1500000,
            'price_unit': 'CLP',
            'location': 'Las Condes',
            'link': 'https://www.portalinmobiliario.com/test'
        }
    ]

# 3. Mostrar lo que se enviará
print(f"\n3️⃣ Resumen - Se enviará email con {len(properties)} propiedad(es):")
for i, prop in enumerate(properties, 1):
    print(f"   {i}. {prop.get('title', 'Sin título')[:50]}")

# 4. Enviar email de prueba
print(f"\n4️⃣ ENVIANDO EMAIL DE PRUEBA...")
print(f"   De: {GMAIL_USER}")
print(f"   Para: {', '.join(RECIPIENTS)}")
print()

try:
    from email_service import send_email
    
    # Enviar con asunto de prueba
    success = send_email(
        properties, 
        subject="🧪 PRUEBA - Notificador Portal Inmobiliario"
    )
    
    if success:
        print(f"\n{'='*80}")
        print("✅ ¡¡¡ EMAIL ENVIADO EXITOSAMENTE !!!")
        print(f"{'='*80}")
        print(f"\nRevisa tu bandeja de entrada en:")
        for recipient in RECIPIENTS:
            print(f"   📧 {recipient}")
        print(f"\nSi no lo ves, revisa la carpeta de SPAM")
    else:
        print(f"\n{'='*80}")
        print("❌ FALLO EL ENVÍO DEL EMAIL")
        print(f"{'='*80}")
        print("\n🔍 Verifica:")
        print("   1. GMAIL_PASSWORD debe ser una 'App Password' de 16 caracteres")
        print("   2. NO uses tu contraseña normal de Gmail")
        print("   3. Para obtener App Password:")
        print("      - Ve a: https://myaccount.google.com/")
        print("      - Seguridad > Verificación en 2 pasos (debe estar activa)")
        print("      - Contraseñas de aplicaciones > Generar nueva")
        print("      - Usa esa contraseña de 16 caracteres en GMAIL_PASSWORD")
        
except Exception as e:
    print(f"\n❌ ERROR al enviar email:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    print(f"\n{'='*80}")
    print("💡 TIPS para solucionar:")
    print("   1. GMAIL_PASSWORD debe ser una App Password (16 caracteres)")
    print("   2. Verifica que la verificación en 2 pasos esté activa")
    print("   3. Asegúrate de que no haya espacios en la contraseña")

print("\n" + "="*80)


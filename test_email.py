"""
Script de prueba para testear el envío de emails.
Envía TODAS las propiedades encontradas sin filtrar por ya vistas.
Solo para debug del sistema de email.
"""
import sys

print("="*80)
print("📧 PRUEBA DE ENVÍO DE EMAIL - Debug")
print("="*80)

# 1. Verificar configuración
print("\n1️⃣ Verificando configuración de email...")
try:
    from config import validate_config, SEARCH_URL, GMAIL_USER, RECIPIENTS
    validate_config()
    print("✓ Configuración válida")
    print(f"   📧 Email de envío: {GMAIL_USER}")
    print(f"   📨 Destinatarios: {', '.join(RECIPIENTS)}")
except ValueError as e:
    print(f"❌ Error de configuración: {e}")
    print("\nPor favor, verifica tu archivo .env")
    sys.exit(1)

# 2. Scrapear propiedades
print("\n2️⃣ Scrapeando propiedades (esto puede tomar unos segundos)...")
try:
    from scraper import scrape_properties
    
    print(f"🔍 Buscando propiedades...")
    properties = scrape_properties(SEARCH_URL)
    
    if not properties:
        print("⚠ No se encontraron propiedades")
        sys.exit(1)
    
    print(f"✓ Se encontraron {len(properties)} propiedades")
    
except Exception as e:
    print(f"❌ Error al scrapear: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Mostrar propiedades que se enviarán
print(f"\n3️⃣ Propiedades que se enviarán por email ({len(properties)} total):")
print("-" * 80)
for i, prop in enumerate(properties, 1):
    print(f"\n{i}. {prop.get('title', 'Sin título')[:60]}")
    if prop.get('price'):
        price_unit = prop.get('price_unit', 'CLP')
        if price_unit == 'UF':
            price_str = f"{prop['price']:,} UF".replace(",", ".")
        else:
            price_str = f"${prop['price']:,}".replace(",", ".")
        print(f"   💰 Precio: {price_str}")
    print(f"   🔗 Link: {prop.get('link', 'N/A')[:70]}...")
    print(f"   🆔 ID: {prop.get('id', 'N/A')}")

# 4. Confirmar antes de enviar
print(f"\n{'='*80}")
print(f"⚠️  ADVERTENCIA: Esto enviará un email con {len(properties)} propiedades")
print(f"   Destinatarios: {', '.join(RECIPIENTS)}")
print(f"{'='*80}")
response = input("\n¿Continuar con el envío? (s/n): ")

if response.lower() != 's':
    print("❌ Envío cancelado por el usuario")
    sys.exit(0)

# 5. Enviar email
print(f"\n4️⃣ Enviando email de prueba...")
try:
    from email_service import send_email
    
    success = send_email(properties, subject="🧪 PRUEBA - Notificador de Propiedades")
    
    if success:
        print(f"\n{'='*80}")
        print("✅ ¡Email enviado exitosamente!")
        print(f"{'='*80}")
        print(f"\nRevisa tu bandeja de entrada en:")
        for recipient in RECIPIENTS:
            print(f"   - {recipient}")
    else:
        print(f"\n{'='*80}")
        print("❌ Error al enviar el email")
        print(f"{'='*80}")
        print("\nPosibles problemas:")
        print("   1. Verifica que GMAIL_PASSWORD sea una App Password (16 caracteres)")
        print("   2. Verifica que la verificación en 2 pasos esté activada en Google")
        print("   3. Revisa los logs de error arriba")
        
except Exception as e:
    print(f"❌ Error al enviar email: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("✅ Prueba completada")
print("="*80)


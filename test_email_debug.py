"""
Script de prueba MUY SIMPLE solo para debug del email.
Prueba la conexión SMTP y muestra errores detallados.
"""
import smtplib
from email.mime.text import MIMEText
import sys

print("="*80)
print("🔍 PRUEBA DE CONEXIÓN EMAIL - Debug Detallado")
print("="*80)

# Cargar configuración
try:
    from config import GMAIL_USER, GMAIL_PASSWORD, RECIPIENTS
except Exception as e:
    print(f"❌ Error al cargar configuración: {e}")
    sys.exit(1)

print(f"\n📋 CONFIGURACIÓN:")
print(f"   Email: {GMAIL_USER}")
print(f"   Password length: {len(GMAIL_PASSWORD) if GMAIL_PASSWORD else 0} caracteres")
print(f"   Password preview: {'*' * min(4, len(GMAIL_PASSWORD)) if GMAIL_PASSWORD else 'VACÍO'}...")
print(f"   Destinatarios: {', '.join(RECIPIENTS)}")

# Verificar que todo esté configurado
if not GMAIL_USER:
    print("\n❌ GMAIL_USER no está configurado")
    sys.exit(1)

if not GMAIL_PASSWORD:
    print("\n❌ GMAIL_PASSWORD no está configurado")
    sys.exit(1)

if not RECIPIENTS:
    print("\n❌ RECIPIENTS no está configurado")
    sys.exit(1)

# Verificar formato de password
if len(GMAIL_PASSWORD) != 16:
    print(f"\n⚠️  ADVERTENCIA: La App Password debe tener 16 caracteres")
    print(f"   Tu password tiene {len(GMAIL_PASSWORD)} caracteres")
    print(f"   Si es diferente, puede que no sea una App Password")
    
    respuesta = input("\n¿Continuar de todas formas? (s/n): ")
    if respuesta.lower() != 's':
        sys.exit(0)

# Crear email de prueba simple
print(f"\n📧 Creando email de prueba...")
msg = MIMEText("Este es un email de prueba del Notificador de Propiedades.\n\nSi recibes esto, el sistema de email funciona correctamente.")
msg['Subject'] = '🧪 PRUEBA - Notificador Portal Inmobiliario'
msg['From'] = GMAIL_USER
msg['To'] = ', '.join(RECIPIENTS)

# Intentar conectar y enviar
print(f"\n🔌 Conectando a Gmail SMTP...")
try:
    print("   Paso 1: Conectando a smtp.gmail.com:587...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    print("   ✓ Conexión establecida")
    
    print("   Paso 2: Iniciando TLS...")
    server.starttls()
    print("   ✓ TLS iniciado")
    
    print(f"   Paso 3: Autenticando con usuario: {GMAIL_USER}...")
    print(f"          (Password: {'*' * len(GMAIL_PASSWORD)})")
    
    # Limpiar password de posibles espacios
    password_clean = GMAIL_PASSWORD.strip()
    if password_clean != GMAIL_PASSWORD:
        print(f"   ⚠️  Advertencia: El password tenía espacios (ya limpiados)")
    
    server.login(GMAIL_USER, password_clean)
    print("   ✓ Autenticación exitosa")
    
    print(f"   Paso 4: Enviando email a {len(RECIPIENTS)} destinatario(s)...")
    server.sendmail(GMAIL_USER, RECIPIENTS, msg.as_string())
    print("   ✓ Email enviado")
    
    print("   Paso 5: Cerrando conexión...")
    server.quit()
    print("   ✓ Conexión cerrada")
    
    print(f"\n{'='*80}")
    print("✅ ¡¡¡ EMAIL ENVIADO EXITOSAMENTE !!!")
    print(f"{'='*80}")
    print(f"\nRevisa tu bandeja de entrada:")
    for recipient in RECIPIENTS:
        print(f"   📧 {recipient}")
    print(f"\nSi no lo ves, revisa la carpeta de SPAM")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ ERROR DE AUTENTICACIÓN:")
    print(f"   Tipo: SMTPAuthenticationError")
    print(f"   Código SMTP: {getattr(e, 'smtp_code', 'N/A')}")
    print(f"   Error SMTP: {getattr(e, 'smtp_error', 'N/A')}")
    print(f"\n💡 SOLUCIÓN:")
    print(f"   1. Asegúrate de usar una 'App Password' de 16 caracteres")
    print(f"   2. NO uses tu contraseña normal de Gmail")
    print(f"   3. Para obtener App Password:")
    print(f"      a) Ve a: https://myaccount.google.com/")
    print(f"      b) Seguridad > Verificación en 2 pasos (DEBE estar activa)")
    print(f"      c) Contraseñas de aplicaciones > Generar nueva")
    print(f"      d) Copia la contraseña de 16 caracteres (ej: abcd efgh ijkl mnop)")
    print(f"      e) Pégalo en tu .env sin espacios: GMAIL_PASSWORD=abcdefghijklmnop")
    print(f"   4. Si ya tienes App Password, verifica que no tenga espacios")
    
except smtplib.SMTPException as e:
    print(f"\n❌ ERROR SMTP:")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Mensaje: {e}")
    
except Exception as e:
    print(f"\n❌ ERROR INESPERADO:")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Mensaje: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)


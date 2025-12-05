"""
Servicio de envío de emails usando Gmail SMTP.
Envía notificaciones cuando se encuentran nuevas propiedades.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from datetime import datetime

from config import GMAIL_USER, GMAIL_PASSWORD, RECIPIENTS

def format_price(price: int, unit: str = None) -> str:
    """
    Formatea un precio con separadores de miles y su unidad.
    
    Args:
        price: Valor numérico del precio
        unit: Unidad ('UF' o 'CLP'). Si es None, asume CLP
    
    Returns:
        String formateado como "$1.500.000" o "1.200 UF"
    """
    if price is None:
        return "No especificado"
    
    # Formatear el número con puntos como separadores de miles
    price_str = f"{price:,}".replace(",", ".")
    
    # Si es UF, mostrar sin el símbolo $ y con "UF" al final
    if unit and unit.upper() == 'UF':
        return f"{price_str} UF"
    
    # Si es CLP o no se especifica, mostrar con $
    return f"${price_str}"

def create_email_body(properties: List[Dict]) -> str:
    """
    Crea el cuerpo del email con la información de las propiedades, agrupadas por filtro.
    
    Args:
        properties: Lista de diccionarios con información de propiedades (debe incluir 'filter_name')
    
    Returns:
        String con el contenido HTML del email
    """
    # Agrupar propiedades por filtro
    from collections import defaultdict
    properties_by_filter = defaultdict(list)
    for prop in properties:
        filter_name = prop.get('filter_name', 'Filtro sin nombre')
        properties_by_filter[filter_name].append(prop)
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; margin-top: 30px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #3498db; }}
            .filter-group {{
                margin: 25px 0;
                padding: 15px;
                background-color: #f5f5f5;
                border-radius: 5px;
            }}
            .property {{ 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                padding: 15px; 
                margin: 15px 0;
                background-color: #ffffff;
            }}
            .property-title {{ 
                font-size: 18px; 
                font-weight: bold; 
                color: #2980b9;
                margin-bottom: 10px;
            }}
            .property-detail {{ 
                margin: 5px 0; 
                color: #555;
            }}
            .property-link {{ 
                display: inline-block; 
                margin-top: 10px; 
                padding: 8px 15px; 
                background-color: #3498db; 
                color: white; 
                text-decoration: none; 
                border-radius: 3px;
            }}
            .property-link:hover {{
                background-color: #2980b9;
            }}
            .price {{ 
                font-size: 20px; 
                color: #27ae60; 
                font-weight: bold;
            }}
            .footer {{ 
                margin-top: 30px; 
                padding-top: 20px; 
                border-top: 1px solid #ddd; 
                color: #888; 
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <h1>🏠 Nuevas Propiedades Encontradas</h1>
        <p>Se encontraron <strong>{len(properties)}</strong> nueva(s) propiedad(es) que cumplen con tus criterios:</p>
    """
    
    # Iterar por cada filtro
    for filter_name, filter_properties in properties_by_filter.items():
        html_body += f"""
        <div class="filter-group">
            <h2>🔍 {filter_name} ({len(filter_properties)} propiedad/es)</h2>
        """
        
        for prop in filter_properties:
            html_body += f"""
            <div class="property">
                <div class="property-title">{prop.get('title', 'Sin título')}</div>
                <div class="property-detail">
                    <span class="price">{format_price(prop.get('price'), prop.get('price_unit'))}</span>
                </div>
            """
            
            if prop.get('location'):
                html_body += f'<div class="property-detail">📍 {prop.get("location")}</div>'
            
            details = []
            if prop.get('bedrooms'):
                details.append(f"🛏️ {prop['bedrooms']} dormitorios")
            if prop.get('bathrooms'):
                details.append(f"🚿 {prop['bathrooms']} baños")
            if prop.get('area'):
                details.append(f"📐 {prop['area']} m²")
            
            if details:
                html_body += f'<div class="property-detail">{" | ".join(details)}</div>'
            
            # Link destacado de la propiedad
            link = prop.get('link', '#')
            html_body += f"""
                <div style="margin-top: 12px;">
                    <a href="{link}" class="property-link" target="_blank">🔗 Ver Propiedad Completa</a>
                </div>
            """
            
            # Mostrar fecha de detección si es nueva
            if prop.get('detected_at'):
                try:
                    detected_date = datetime.fromisoformat(prop['detected_at'])
                    detected_str = detected_date.strftime('%d/%m/%Y %H:%M')
                    html_body += f'<div class="property-detail" style="margin-top: 8px; color: #27ae60; font-size: 12px;">✨ Encontrada el {detected_str}</div>'
                except:
                    pass
            
            html_body += "</div>"
        
        html_body += "</div>"  # Cerrar filter-group
    
    html_body += f"""
        <div class="footer">
            <p>Este es un email automático del Notificador de Propiedades.</p>
            <p>Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    
    return html_body

def create_text_body(properties: List[Dict]) -> str:
    """
    Crea el cuerpo del email en texto plano, agrupado por filtro.
    
    Args:
        properties: Lista de diccionarios con información de propiedades (debe incluir 'filter_name')
    
    Returns:
        String con el contenido en texto plano
    """
    # Agrupar propiedades por filtro
    from collections import defaultdict
    properties_by_filter = defaultdict(list)
    for prop in properties:
        filter_name = prop.get('filter_name', 'Filtro sin nombre')
        properties_by_filter[filter_name].append(prop)
    
    text_body = f"🏠 Nuevas Propiedades Encontradas\n\n"
    text_body += f"Se encontraron {len(properties)} nueva(s) propiedad(es) que cumplen con tus criterios:\n\n"
    text_body += "=" * 70 + "\n\n"
    
    # Iterar por cada filtro
    for filter_name, filter_properties in properties_by_filter.items():
        text_body += f"🔍 {filter_name} ({len(filter_properties)} propiedad/es)\n"
        text_body += "=" * 70 + "\n\n"
        
        for i, prop in enumerate(filter_properties, 1):
            text_body += f"{i}. {prop.get('title', 'Sin título')}\n"
            text_body += f"   Precio: {format_price(prop.get('price'), prop.get('price_unit'))}\n"
            
            if prop.get('location'):
                text_body += f"   Ubicación: {prop.get('location')}\n"
            
            details = []
            if prop.get('bedrooms'):
                details.append(f"{prop['bedrooms']} dormitorios")
            if prop.get('bathrooms'):
                details.append(f"{prop['bathrooms']} baños")
            if prop.get('area'):
                details.append(f"{prop['area']} m²")
            
            if details:
                text_body += f"   {' | '.join(details)}\n"
            
            # Link destacado
            link = prop.get('link', 'N/A')
            text_body += f"   🔗 Link: {link}\n"
            
            # Mostrar fecha de detección si es nueva
            if prop.get('detected_at'):
                try:
                    detected_date = datetime.fromisoformat(prop['detected_at'])
                    detected_str = detected_date.strftime('%d/%m/%Y %H:%M')
                    text_body += f"   ✨ Encontrada el: {detected_str}\n"
                except:
                    pass
            
            text_body += "\n" + "-" * 70 + "\n\n"
    
    text_body += f"\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
    text_body += "Este es un email automático del Notificador de Propiedades.\n"
    
    return text_body

def send_email(properties: List[Dict], subject: str = None) -> bool:
    """
    Envía un email con las nuevas propiedades encontradas.
    
    Args:
        properties: Lista de diccionarios con información de propiedades
        subject: Asunto del email (opcional)
    
    Returns:
        True si se envió correctamente, False en caso contrario
    """
    if not properties:
        print("⚠ No hay propiedades para enviar por email")
        return False
    
    if not RECIPIENTS:
        print("⚠ No hay destinatarios configurados")
        return False
    
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("⚠ Credenciales de Gmail no configuradas")
        return False
    
    if subject is None:
        subject = f"🏠 {len(properties)} Nueva(s) Propiedad(es) Encontrada(s) en Portal Inmobiliario"
    
    try:
        # Crear mensaje multipart (HTML + texto plano)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = GMAIL_USER
        msg['To'] = ', '.join(RECIPIENTS)
        
        # Crear versiones del cuerpo
        text_content = create_text_body(properties)
        html_content = create_email_body(properties)
        
        # Adjuntar ambas versiones
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Conectar al servidor SMTP de Gmail
        print(f"📧 Enviando email a {len(RECIPIENTS)} destinatario(s)...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        
        # Enviar email
        text = msg.as_string()
        server.sendmail(GMAIL_USER, RECIPIENTS, text)
        server.quit()
        
        print(f"✓ Email enviado exitosamente a: {', '.join(RECIPIENTS)}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación SMTP:")
        print(f"   Código de error: {e.smtp_code if hasattr(e, 'smtp_code') else 'N/A'}")
        print(f"   Mensaje: {e.smtp_error.decode() if hasattr(e, 'smtp_error') and e.smtp_error else str(e)}")
        print(f"\n💡 Verifica:")
        print(f"   1. GMAIL_USER: {GMAIL_USER}")
        print(f"   2. GMAIL_PASSWORD debe ser una 'App Password' de 16 caracteres")
        print(f"   3. NO uses tu contraseña normal de Gmail")
        print(f"   4. La verificación en 2 pasos debe estar activada")
        print(f"   5. Para obtener App Password: https://myaccount.google.com/apppasswords")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ Error SMTP al enviar email:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado al enviar email:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Prueba del servicio de email
    test_properties = [
        {
            'id': 'TEST-123',
            'title': 'Casa en Las Condes - Prueba',
            'price': 1500000,
            'location': 'Las Condes, Santiago',
            'link': 'https://www.portalinmobiliario.com/test',
            'bedrooms': 4,
            'bathrooms': 2,
            'area': 120
        }
    ]
    
    print("⚠ Este es un TEST. No se enviará ningún email real.")
    print("Para probar el envío, ejecuta main.py con propiedades reales.")


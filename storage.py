"""
Utilidad para gestionar las propiedades ya vistas.
Guarda los IDs de propiedades en un archivo JSON para evitar notificaciones duplicadas.
También guarda la fecha de detección para saber cuándo se encontró cada propiedad.
"""
import json
import os
from typing import Set, List, Dict
from pathlib import Path
from datetime import datetime

STORAGE_FILE = Path("data/properties-seen.json")

def ensure_data_directory():
    """Asegura que el directorio data existe."""
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_seen_properties() -> Set[str]:
    """Carga los IDs de propiedades ya vistas desde el archivo JSON."""
    ensure_data_directory()
    
    if not STORAGE_FILE.exists():
        return set()
    
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Compatibilidad: puede ser una lista simple o un dict con más info
            if isinstance(data, list):
                return set(data)
            elif isinstance(data, dict):
                return set(data.get("property_ids", []))
            return set()
    except (json.JSONDecodeError, IOError) as e:
        print(f"Advertencia: No se pudo cargar el archivo de propiedades vistas: {e}")
        return set()

def load_properties_data() -> Dict[str, Dict]:
    """Carga datos completos de propiedades (ID, fecha de detección, etc.)"""
    ensure_data_directory()
    
    if not STORAGE_FILE.exists():
        return {}
    
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Formato nuevo: dict con información detallada
            if isinstance(data, dict) and "properties" in data:
                return data.get("properties", {})
            # Formato antiguo: solo lista de IDs
            elif isinstance(data, list):
                return {pid: {"first_seen": None} for pid in data}
            elif isinstance(data, dict) and "property_ids" in data:
                return {pid: {"first_seen": None} for pid in data.get("property_ids", [])}
            return {}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Advertencia: No se pudo cargar el archivo de propiedades vistas: {e}")
        return {}

def save_seen_properties(property_ids: Set[str]):
    """Guarda los IDs de propiedades vistas en el archivo JSON (formato antiguo para compatibilidad)."""
    ensure_data_directory()
    
    try:
        data = {
            "property_ids": list(property_ids),
            "count": len(property_ids)
        }
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error: No se pudo guardar el archivo de propiedades vistas: {e}")

def save_properties_data(properties_data: Dict[str, Dict]):
    """Guarda datos completos de propiedades (con fechas)."""
    ensure_data_directory()
    
    try:
        data = {
            "properties": properties_data,
            "property_ids": list(properties_data.keys()),  # Para compatibilidad
            "count": len(properties_data),
            "last_updated": datetime.now().isoformat()
        }
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error: No se pudo guardar el archivo de propiedades vistas: {e}")

def add_seen_property(property_id: str):
    """Agrega un ID de propiedad a la lista de vistas."""
    seen = load_seen_properties()
    seen.add(property_id)
    save_seen_properties(seen)

def add_seen_properties(property_ids: List[str]):
    """Agrega múltiples IDs de propiedades a la lista de vistas."""
    seen = load_seen_properties()
    seen.update(property_ids)
    save_seen_properties(seen)

def is_property_seen(property_id: str) -> bool:
    """Verifica si una propiedad ya fue vista."""
    seen = load_seen_properties()
    return property_id in seen

def get_new_properties(all_properties: List[Dict], property_id_key: str = "id") -> List[Dict]:
    """
    Filtra las propiedades que no han sido vistas antes.
    Agrega información de cuándo se encontraron (fecha de detección).
    
    Args:
        all_properties: Lista de diccionarios con información de propiedades
        property_id_key: Clave del diccionario que contiene el ID único
    
    Returns:
        Lista de propiedades nuevas (no vistas antes) con fecha de detección
    """
    properties_data = load_properties_data()
    new_properties = []
    already_seen = []
    now = datetime.now().isoformat()
    
    print(f"   Comparando {len(all_properties)} propiedades con {len(properties_data)} ya vistas...")
    
    for prop in all_properties:
        prop_id = str(prop.get(property_id_key, ""))
        if not prop_id:
            continue
            
        if prop_id not in properties_data:
            # Es una propiedad nueva - agregar fecha de detección
            prop['detected_at'] = now
            prop['is_new'] = True
            new_properties.append(prop)
            # Guardar en el almacenamiento con fecha e información del filtro
            properties_data[prop_id] = {
                "first_seen": now,
                "last_seen": now,
                "title": prop.get('title', ''),
                "link": prop.get('link', ''),
                "filter_name": prop.get('filter_name', ''),
                "filter_url": prop.get('filter_url', '')
            }
        else:
            already_seen.append(prop_id)
    
    # Mostrar cuáles ya fueron vistas
    if already_seen:
        print(f"   ✅ {len(already_seen)} propiedad(es) ya vista(s) (no se enviarán):")
        for prop_id in already_seen[:5]:  # Mostrar solo las primeras 5
            prop_info = properties_data.get(prop_id, {})
            title = prop_info.get('title', 'Sin título')[:40]
            first_seen = prop_info.get('first_seen', 'Desconocida')
            print(f"      - {prop_id}: {title} (vista desde {first_seen[:10]})")
        if len(already_seen) > 5:
            print(f"      ... y {len(already_seen) - 5} más")
    
    # Guardar las nuevas propiedades vistas (con fechas)
    if new_properties:
        # Actualizar también las propiedades ya vistas con last_seen
        for prop in all_properties:
            prop_id = str(prop.get(property_id_key, ""))
            if prop_id in properties_data:
                properties_data[prop_id]["last_seen"] = now
        
        save_properties_data(properties_data)
        print(f"   💾 Guardadas {len(new_properties)} propiedades nuevas en almacenamiento")
    
    return new_properties

def get_storage_stats() -> Dict:
    """Obtiene estadísticas del almacenamiento."""
    seen = load_seen_properties()
    return {
        "total_seen": len(seen),
        "storage_file": str(STORAGE_FILE),
        "file_exists": STORAGE_FILE.exists()
    }

if __name__ == "__main__":
    # Prueba básica
    print("Probando sistema de almacenamiento...")
    stats = get_storage_stats()
    print(f"  Propiedades vistas: {stats['total_seen']}")
    print(f"  Archivo: {stats['storage_file']}")


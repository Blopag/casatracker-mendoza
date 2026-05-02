import json
import os
import re

def analyze_matches():
    file_path = os.path.join(os.path.dirname(__file__), 'propiedades_totales.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    match_count = 0
    portal_counts = {}
    
    for prop in data:
        portal = prop.get('portal') or prop.get('origen') or 'Desconocido'
        portal_counts[portal] = portal_counts.get(portal, 0) + 1
        
        titulo = str(prop.get('titulo', '')).lower()
        desc = str(prop.get('descripcion', '')).lower()
        full_text = titulo + " " + desc
        
        has_jardin = 'jardin' in full_text or 'jardín' in full_text or 'patio' in full_text
        
        beds = prop.get('beds') or prop.get('habitaciones')
        try:
            beds = int(beds)
        except:
            beds = 0
            
        baths = prop.get('baths') or prop.get('banos')
        try:
            baths = int(baths)
        except:
            baths = 0
            
        precio = str(prop.get('precio', ''))
        price_num = 0
        price_str = precio.replace('.', '')
        match = re.search(r'(\d+)', price_str)
        if match and ('US$' in precio.upper() or 'USD' in precio.upper()):
            price_num = int(match.group(1))
            
        is_match = (50000 <= price_num <= 90000) and (beds >= 3) and (baths >= 2) and has_jardin
        
        if is_match:
            match_count += 1
            print(f"Match: {portal} - {precio} - {beds} beds - {baths} baths - {titulo}")
            
    print(f"Total properties: {len(data)}")
    print(f"Properties per portal: {portal_counts}")
    print(f"Total matches: {match_count}")

if __name__ == "__main__":
    analyze_matches()

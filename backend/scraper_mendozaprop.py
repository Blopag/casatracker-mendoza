import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_mendozaprop():
    url = "https://www.mendozaprop.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("Iniciando scraper de MendozaProp...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar el script con los datos JSON
        script_tag = soup.find('script', id='__NEXT_DATA__')
        
        if not script_tag:
            print("No se encontró el bloque JSON de datos.")
            return []
            
        json_data = json.loads(script_tag.string)
        
        # Extraer ventas
        sales = json_data.get('props', {}).get('pageProps', {}).get('data', {}).get('latests', {}).get('sales', [])
        
        propiedades = []
        
        for sale in sales:
            moneda = "USD" if sale.get('currency_id') == 1 else ("ARS" if sale.get('currency_id') == 2 else "")
            precio_formateado = f"{moneda} {sale.get('price', '')}".strip()
            
            propiedad = {
                "id": str(sale.get('id', '')),
                "url": f"https://www.mendozaprop.com/propiedades/{sale.get('id', '')}", 
                "titulo": sale.get('title', ''),
                "precio": precio_formateado,
                "ubicacion": sale.get('address', ''),
                "habitaciones": sale.get('bedrooms', 0),
                "banos": sale.get('bathrooms', 0),
                "superficie": f"{sale.get('m2', '')} {sale.get('m2_unit', '')}".strip(),
                "imagen": sale.get('images', [])[0] if sale.get('images') else "",
                "inmobiliaria": sale.get('owner_company', ''),
                "descripcion": sale.get('description', ''),
                "origen": "MendozaProp"
            }
            propiedades.append(propiedad)
            
        # Guardar resultados
        output_path = os.path.join(os.path.dirname(__file__), 'resultados_mendozaprop.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(propiedades, f, ensure_ascii=False, indent=4)
            
        print(f"Scraping completado. {len(propiedades)} propiedades guardadas de MendozaProp.")
        return propiedades

    except Exception as e:
        print(f"Error durante el scraping: {e}")
        return []

if __name__ == "__main__":
    scrape_mendozaprop()

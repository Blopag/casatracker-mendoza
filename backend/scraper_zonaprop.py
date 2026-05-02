import requests
from bs4 import BeautifulSoup
import json
import re
import os

def scrape_zonaprop():
    url = "https://www.zonaprop.com.ar/casas-venta-mendoza-provincia-50000-90000-dolar-orden-publicado-descendente.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Referer': 'https://www.zonaprop.com.ar/'
    }
    
    print("Iniciando scraper de Zonaprop...")
    
    try:
        response = requests.get(url, headers=headers)
        
        # Zonaprop usually has anti-bot measures, but if it responds we can parse it
        # In case the direct request is blocked, we will use the debug file we already have for now,
        # but the logic remains the same for the response text.
        
        if response.status_code == 200:
            html_content = response.text
        else:
            print(f"Error {response.status_code} al acceder a Zonaprop. Intentando leer desde archivo local (debug_zonaprop.html)...")
            file_path = os.path.join(os.path.dirname(__file__), 'debug_zonaprop.html')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            else:
                return []

        soup = BeautifulSoup(html_content, 'html.parser')
        scripts = soup.find_all('script')
        
        propiedades = []
        
        for script in scripts:
            if script.string and 'window.__PRELOADED_STATE__' in script.string:
                content = script.string.strip()
                start_idx = content.find('{')
                if start_idx != -1:
                    json_str = content[start_idx:]
                    parts = re.split(r';\s*window\.', json_str)
                    for part in parts:
                        try:
                            if part.endswith(';'):
                                part = part[:-1]
                            data = json.loads(part)
                            
                            if 'listStore' in data and 'listPostings' in data['listStore']:
                                postings = data['listStore']['listPostings']
                                
                                for p in postings:
                                    try:
                                        # Extraer ID y URL
                                        posting_id = str(p.get('postingId', ''))
                                        url_prop = f"https://www.zonaprop.com.ar{p.get('url', '')}"
                                        
                                        # Extraer Título
                                        titulo = p.get('title', '')
                                        
                                        # Extraer Precio
                                        precio_str = ""
                                        precios_ops = p.get('priceOperationTypes', [])
                                        if precios_ops and len(precios_ops) > 0:
                                            prices = precios_ops[0].get('prices', [])
                                            if prices and len(prices) > 0:
                                                curr = prices[0].get('currency', '')
                                                amt = prices[0].get('formattedAmount', '')
                                                precio_str = f"{curr} {amt}".strip()
                                        
                                        # Extraer Ubicación
                                        ubicacion = ""
                                        loc = p.get('postingLocation', {})
                                        if loc and 'address' in loc:
                                            ubicacion = loc['address'].get('name', '')
                                            if not ubicacion and 'location' in loc:
                                                ubicacion = loc['location'].get('name', '')
                                                
                                        # Extraer Features
                                        main_features = p.get('mainFeatures', {})
                                        
                                        habitaciones = 0
                                        if 'CFT2' in main_features and main_features['CFT2'].get('value'):
                                            try: habitaciones = int(main_features['CFT2']['value'])
                                            except: pass
                                            
                                        banos = 0
                                        if 'CFT3' in main_features and main_features['CFT3'].get('value'):
                                            try: banos = int(main_features['CFT3']['value'])
                                            except: pass
                                            
                                        superficie = ""
                                        if 'CFT100' in main_features and main_features['CFT100'].get('value'):
                                            superficie = f"{main_features['CFT100']['value']} m2"
                                            
                                        # Extraer Imagen
                                        imagen = ""
                                        vis_pics = p.get('visiblePictures', {})
                                        if vis_pics and 'pictures' in vis_pics and len(vis_pics['pictures']) > 0:
                                            imagen = vis_pics['pictures'][0].get('url730x532', '')
                                            if not imagen:
                                                imagen = vis_pics['pictures'][0].get('url360x266', '')
                                                
                                        # Extraer Inmobiliaria
                                        inmobiliaria = ""
                                        pub = p.get('publisher', {})
                                        if pub:
                                            inmobiliaria = pub.get('name', '')
                                            
                                        propiedad = {
                                            "id": posting_id,
                                            "url": url_prop,
                                            "titulo": titulo,
                                            "precio": precio_str,
                                            "ubicacion": ubicacion,
                                            "habitaciones": habitaciones,
                                            "banos": banos,
                                            "superficie": superficie,
                                            "imagen": imagen,
                                            "inmobiliaria": inmobiliaria,
                                            "descripcion": p.get('descriptionNormalized', ''),
                                            "origen": "Zonaprop"
                                        }
                                        propiedades.append(propiedad)
                                    except Exception as e:
                                        print(f"Error procesando publicación individual: {e}")
                            break
                        except Exception as e:
                            pass
        
        # Guardar resultados
        output_path = os.path.join(os.path.dirname(__file__), 'resultados_zonaprop.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(propiedades, f, ensure_ascii=False, indent=4)
            
        print(f"Scraping completado. {len(propiedades)} propiedades guardadas de Zonaprop.")
        return propiedades

    except Exception as e:
        print(f"Error durante el scraping de Zonaprop: {e}")
        return []

if __name__ == "__main__":
    scrape_zonaprop()

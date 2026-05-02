import requests
from bs4 import BeautifulSoup
import json
import os
import re

def scrape_argenprop():
    print("Iniciando busqueda en Argenprop...")
    
    url = "https://www.argenprop.com/casas/venta/mendoza-provincia?moneda=dolares&preciomin=50000&preciomax=90000"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error HTTP {response.status_code} al acceder a Argenprop")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        propiedades = soup.find_all('div', class_='listing__item')
        resultados = []
        
        for prop in propiedades:
            # Precio
            precio_elem = prop.find('p', class_='card__price')
            precio = precio_elem.text.strip() if precio_elem else "Precio Consultar"
            
            # Filtro rapido para USD 50k-90k
            if "USD" in precio:
                try:
                    val = int(re.sub(r'[^\d]', '', precio))
                    # Opcionalmente podemos filtrar aca, pero lo dejamos para el frontend
                except:
                    pass

            # Titulo y Ubicacion
            titulo_elem = prop.find('h2', class_='card__title')
            titulo = titulo_elem.text.strip() if titulo_elem else "Casa en Venta"
            
            ubicacion_elem = prop.find('p', class_='card__address')
            ubicacion = ubicacion_elem.text.strip() if ubicacion_elem else "Mendoza"
            
            # Link
            link_elem = prop.find('a', class_='card')
            link = "https://www.argenprop.com" + link_elem['href'] if link_elem and 'href' in link_elem.attrs else "#"
            
            # Imagen
            img_elem = prop.find('img', class_='card__photo')
            img_url = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"
            if img_elem:
                if img_elem.has_attr('data-src'):
                    img_url = img_elem['data-src']
                elif img_elem.has_attr('src'):
                    img_url = img_elem['src']
            
            # Atributos (habs, banos, etc)
            habs = "0"
            banos = "0"
            area = "N/A"
            
            features = prop.find_all('li', class_='card__main-features-item')
            for f in features:
                text = f.text.strip().lower()
                if "dor" in text or "hab" in text:
                    match = re.search(r'\d+', text)
                    if match: habs = match.group()
                elif "bañ" in text:
                    match = re.search(r'\d+', text)
                    if match: banos = match.group()
                elif "m²" in text:
                    area = text

            descripcion = ""
            desc_elem = prop.find('p', class_='card__info')
            if desc_elem:
                descripcion = desc_elem.text.strip()

            resultados.append({
                "portal": "Argenprop",
                "titulo": f"{titulo} - {ubicacion}",
                "precio": precio,
                "link": link,
                "beds": habs,
                "baths": banos,
                "area": area,
                "image": img_url,
                "descripcion": descripcion
            })
            
        print(f"Se encontraron {len(resultados)} propiedades en Argenprop.")
        output_path = os.path.join(os.path.dirname(__file__), 'resultados_argenprop.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)
            
        print(f"Datos guardados en {output_path}")
        return resultados

    except Exception as e:
        print(f"Error al scrapear Argenprop: {e}")
        return []

if __name__ == "__main__":
    scrape_argenprop()

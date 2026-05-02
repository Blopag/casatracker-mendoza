import json
import re
import os
from bs4 import BeautifulSoup
import cloudscraper

BASE_URL = "https://inmuebles.mercadolibre.com.ar/casas/venta/mendoza/50000-90000-dolares"

def scrape_mercadolibre():
    print("Iniciando busqueda en Mercado Libre con Cloudscraper...")
    
    resultados = []
    
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        print(f"Navegando a: {BASE_URL}")
        response = scraper.get(BASE_URL)
        
        with open("debug_ml.html", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print("Pagina descargada. Analizando contenido...")
        soup = BeautifulSoup(response.text, "html.parser")
        
        propiedades = soup.find_all("li", class_="ui-search-layout__item")
        
        for prop in propiedades:
            titulo_elem = prop.find("h2", class_="poly-box") or prop.find("h2")
            if not titulo_elem:
                continue
            titulo = titulo_elem.text.strip()
            
            ubicacion_elem = prop.find("span", class_="poly-component__location")
            ubicacion = ubicacion_elem.text.strip() if ubicacion_elem else "Mendoza"
            
            precio_elem = prop.find("span", class_="andes-money-amount__fraction")
            moneda_elem = prop.find("span", class_="andes-money-amount__currency-symbol")
            
            precio_val = precio_elem.text.strip() if precio_elem else ""
            moneda = moneda_elem.text.strip() if moneda_elem else "U$S"
            precio = f"{moneda} {precio_val}" if precio_val else "Precio Consultar"
            
            link_elem = prop.find("a", href=True)
            link = link_elem["href"] if link_elem else "#"
            
            img_elem = prop.find("img")
            img_url = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"
            if img_elem:
                if img_elem.has_attr("data-src"):
                    img_url = img_elem["data-src"]
                elif img_elem.has_attr("src"):
                    img_url = img_elem["src"]
                    
            habs = "0"
            banos = "0"
            area = "N/A"
            
            attr_elems = prop.find_all("span", class_="poly-attributes-list__item")
            for attr in attr_elems:
                text = attr.text.lower()
                if "dor" in text or "hab" in text:
                    match = re.search(r'\d+', text)
                    if match: habs = match.group()
                elif "bañ" in text:
                    match = re.search(r'\d+', text)
                    if match: banos = match.group()
                elif "m²" in text:
                    area = text.strip()

            resultados.append({
                "portal": "Mercado Libre",
                "titulo": f"{titulo}",
                "precio": precio,
                "ubicacion": ubicacion,
                "link": link,
                "beds": habs,
                "baths": banos,
                "area": area,
                "image": img_url,
                "descripcion": "" 
            })
            
    except Exception as e:
        print(f"Error al scrapear Mercado Libre: {e}")
        return None

    print(f"Se encontraron {len(resultados)} propiedades en Mercado Libre.")
    output_path = os.path.join(os.path.dirname(__file__), 'resultados_mercadolibre.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
        
    print(f"Datos guardados en {output_path}")
    return resultados

if __name__ == "__main__":
    scrape_mercadolibre()

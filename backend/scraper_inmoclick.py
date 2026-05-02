import requests
from bs4 import BeautifulSoup
import json
import time

# URL de búsqueda de Inmoclick: Casas en Mendoza (vamos a aplicar un rango de precios por defecto)
# Nota: La URL exacta puede variar según los filtros de Inmoclick.
BASE_URL = "https://www.inmoclick.com.ar/inmuebles/venta-en-casas-en-mendoza"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

def scrape_inmoclick():
    print("Iniciando busqueda en Inmoclick...")
    
    # Parámetros simulados para la primera búsqueda
    params = {
        "precio_min": "50000",
        "precio_max": "90000",
        "moneda": "2" # Asumimos 2 = USD en el portal
    }
    
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        print("Página descargada. Buscando propiedades...")
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # En Inmoclick, las tarjetas de propiedades suelen estar en etiquetas article o divs con ciertas clases
        # Vamos a buscar todos los 'article' que usualmente envuelven las publicaciones
        propiedades = soup.find_all("article")
        
        resultados = []
        
        for prop in propiedades:
            # Extraer Título/Ubicación
            address_div = prop.find("div", class_="property-data")
            if address_div:
                # Quitamos saltos de línea y espacios extra
                titulo = " ".join(address_div.text.split())
            else:
                titulo = "Casa en Venta"
                
            # Extraer Precio
            precio_elem = prop.find("p", class_="price")
            precio = precio_elem.text.strip() if precio_elem else "Precio Consultar"
            
            # Extraer Link
            link_elem = prop.find("a", itemprop="url") or prop.find("a", href=True)
            link = "https://www.inmoclick.com.ar" + link_elem["href"] if link_elem and link_elem.has_attr("href") else "#"
            
            # Extraer Foto Real
            img_elem = prop.find("img", itemprop="photo")
            img_url = "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80" # Fallback
            if img_elem:
                if img_elem.has_attr("data-defer-src"):
                    img_url = img_elem["data-defer-src"]
                elif img_elem.has_attr("src"):
                    img_url = img_elem["src"]
            
            # Extraer Habitaciones
            hab_elem = prop.find("div", class_="wi-dormitorio")
            habs = hab_elem.text.strip() if hab_elem else "?"
            
            # Extraer Baños
            ban_elem = prop.find("div", class_="wi-banio")
            banos = ban_elem.text.strip() if ban_elem else "?"
            
            # Extraer Superficie
            sup_elem = prop.find("div", class_="wi-sup-total")
            area = sup_elem.text.strip() if sup_elem else "?"
            
            # Filtrar si no hay link
            if link == "#":
                continue
                
            resultados.append({
                "portal": "Inmoclick",
                "titulo": titulo,
                "precio": precio,
                "link": link,
                "beds": habs,
                "baths": banos,
                "area": area,
                "image": img_url
            })
            
        print(f"Se encontraron {len(resultados)} propiedades preliminares.")
        
        # Guardar en JSON para conectarlo luego con nuestro Dashboard
        with open('resultados_inmoclick.json', 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)
            
        print("Datos guardados en resultados_inmoclick.json")
        return resultados

    except Exception as e:
        print(f"Error al scrapear Inmoclick: {e}")
        return None

if __name__ == "__main__":
    scrape_inmoclick()

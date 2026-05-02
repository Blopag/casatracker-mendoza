import requests
import json
import os
import re

BASE_API = "https://api-ar.redremax.com/remaxweb-ar/api/listings/findAllWithEntrepreneurships"
IMG_BASE = "https://salesforce-res-ar.redremax.com/image/upload/c_fill,g_center,h_480,w_640/v1/"

def scrape_remax():
    print("Iniciando busqueda en Remax Argentina (API)...")
    resultados = []
    
    # type 9 = casa, operation 1 = venta, mendoza
    # Precios en USD: 50000 a 90000
    params = {
        "page": 0,
        "pageSize": 48,
        "sort": "-createdAt",
        "in_polygons": "Mendoza",
        "types": 9,
        "operationId": 1,
        "currencyId": 1,      # USD
        "minPrice": 50000,
        "maxPrice": 90000,
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.remax.com.ar/",
    }
    
    try:
        response = requests.get(BASE_API, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        api_data = response.json()
        
        if api_data.get("code") != 200 or not api_data.get("data"):
            print(f"Respuesta inesperada de Remax API: {api_data.get('message')}")
            return []
        
        listings = api_data["data"].get("data", [])
        print(f"Remax API devolvio {len(listings)} propiedades.")
        
        for listing in listings:
            try:
                # Precio
                precio_val = listing.get("price", 0)
                moneda = listing.get("currency", {}).get("value", "USD")
                precio = f"{moneda} {int(precio_val):,}".replace(",", ".") if precio_val else "Precio Consultar"
                
                # Titulo y ubicacion
                titulo = listing.get("title", "Casa en Venta")
                ubicacion = listing.get("geoLabel", "Mendoza")
                
                # Link
                slug = listing.get("slug", "")
                entity_id = listing.get("entityId", "")
                link = f"https://www.remax.com.ar/listing/{slug}/{entity_id}" if slug else "https://www.remax.com.ar"
                
                # Imagen
                fotos = listing.get("photos", [])
                img_url = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"
                if fotos:
                    raw = fotos[0].get("rawValue", "")
                    if raw:
                        img_url = IMG_BASE + raw
                
                # Atributos
                habs = str(listing.get("bedrooms", 0) or 0)
                banos = str(listing.get("bathrooms", 0) or 0)
                area_total = listing.get("dimensionTotalBuilt", 0) or 0
                area_cubierta = listing.get("dimensionCovered", 0) or 0
                area = f"{int(area_total)} m²" if area_total else (f"{int(area_cubierta)} m²" if area_cubierta else "N/A")
                
                resultados.append({
                    "portal": "Remax",
                    "titulo": titulo,
                    "precio": precio,
                    "ubicacion": ubicacion,
                    "link": link,
                    "beds": habs,
                    "baths": banos,
                    "area": area,
                    "image": img_url,
                    "descripcion": f"{area} totales | {listing.get('totalRooms', 0)} ambientes"
                })
            except Exception as e:
                print(f"  Error procesando propiedad Remax: {e}")
                continue
        
    except Exception as e:
        print(f"Error al conectar con Remax API: {e}")
        return []
    
    print(f"Se encontraron {len(resultados)} propiedades en Remax.")
    output_path = os.path.join(os.path.dirname(__file__), "resultados_remax.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
    print(f"Datos guardados en {output_path}")
    return resultados

if __name__ == "__main__":
    scrape_remax()

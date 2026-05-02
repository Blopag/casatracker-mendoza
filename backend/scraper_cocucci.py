import requests
import json
import os
import re
from bs4 import BeautifulSoup

BASE_URL = "https://www.cocucci.com.ar/Casas"
PROP_BASE = "https://www.cocucci.com.ar"
IMG_BASE = "https://static.tokkobroker.com/pictures/"

def scrape_cocucci():
    print("Iniciando busqueda en Cocucci Inmobiliaria...")
    resultados = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    page = 1
    while True:
        url = BASE_URL if page == 1 else f"{BASE_URL}?page={page}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"  HTTP {response.status_code} en pagina {page}. Fin de paginacion.")
                break
            
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.find_all("li", attrs={"prop-id": True})
            
            if not items:
                print(f"  No hay mas propiedades en pagina {page}.")
                break
            
            print(f"  Pagina {page}: {len(items)} propiedades encontradas.")
            
            for item in items:
                try:
                    # Link y precio
                    link_elem = item.find("a", href=True)
                    link = PROP_BASE + link_elem["href"] if link_elem else "#"
                    
                    precio_div = item.find("div", class_="prop-valor-nro")
                    precio_raw = precio_div.get_text(strip=True) if precio_div else ""
                    # El texto viene todo junto: "USD200.000CHO7991726+/- Favorito"
                    # Extraemos "USD200.000" con regex
                    precio_match = re.search(r"(USD[\d\.]+)", precio_raw)
                    precio = precio_match.group(1) if precio_match else None
                    
                    # Filtro precio: solo USD entre 50k y 90k
                    if precio:
                        precio_limpio = re.sub(r"[^\d]", "", precio)
                        try:
                            precio_num = int(precio_limpio)
                            if precio_num < 50000 or precio_num > 90000:
                                continue  # fuera de rango
                        except:
                            pass
                    else:
                        continue  # no es USD, saltamos

                    
                    # Titulo y ubicacion
                    desc_div = item.find("div", class_="prop-desc-tipo-ub")
                    titulo = desc_div.get_text(strip=True) if desc_div else "Casa en Venta"
                    
                    dir_div = item.find("div", class_="prop-desc-dir")
                    ubicacion = dir_div.get_text(strip=True) if dir_div else "Mendoza"
                    
                    # Imagen
                    img_elem = item.find("img", class_="dest-img")
                    img_url = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"
                    if img_elem:
                        img_url = img_elem.get("src", img_url)
                    
                    # Datos extras (area en prop-data, dormitorios en prop-data2)
                    area = "N/A"
                    habs = "0"
                    
                    data1 = item.find("div", class_="prop-data")
                    if data1:
                        area_text = data1.find("div")
                        if area_text:
                            area = area_text.get_text(strip=True)
                    
                    data2 = item.find("div", class_="prop-data2")
                    if data2:
                        habs_text = data2.find("div")
                        if habs_text:
                            habs = habs_text.get_text(strip=True)
                    
                    resultados.append({
                        "portal": "Cocucci",
                        "titulo": f"{titulo} - {ubicacion}",
                        "precio": precio,
                        "ubicacion": ubicacion,
                        "link": link,
                        "beds": habs,
                        "baths": "N/A",
                        "area": area,
                        "image": img_url,
                        "descripcion": f"{titulo} en {ubicacion}"
                    })
                except Exception as e:
                    print(f"  Error procesando propiedad Cocucci: {e}")
                    continue
            
            # Verificar si hay siguiente pagina
            siguiente = soup.find("a", string=lambda t: t and "siguiente" in t.lower())
            if not siguiente:
                break
            page += 1
            
        except Exception as e:
            print(f"Error al conectar con Cocucci (pagina {page}): {e}")
            break
    
    print(f"Se encontraron {len(resultados)} propiedades en Cocucci (filtradas por precio USD 50k-90k).")
    output_path = os.path.join(os.path.dirname(__file__), "resultados_cocucci.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
    print(f"Datos guardados en {output_path}")
    return resultados

if __name__ == "__main__":
    scrape_cocucci()

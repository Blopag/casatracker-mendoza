import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

def check_mendozaprop():
    print("Conectando con MendozaProp...")
    try:
        # Vamos a intentar buscar "casas en venta" o la pagina principal
        url = "https://www.mendozaprop.com/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        with open("debug_mendozaprop.html", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print(f"Status Code: {response.status_code}")
        print("Guardado en debug_mendozaprop.html para analizar los selectores.")
    except Exception as e:
        print(f"Error: {e}")

def check_zonaprop():
    print("\nConectando con Zonaprop...")
    try:
        url = "https://www.zonaprop.com.ar/casas-venta-mendoza-provincia.html"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        with open("debug_zonaprop.html", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print(f"Status Code: {response.status_code}")
        print("Guardado en debug_zonaprop.html para analizar los selectores.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mendozaprop()
    check_zonaprop()

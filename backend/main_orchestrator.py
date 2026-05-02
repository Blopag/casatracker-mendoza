import json
import os
import re
import subprocess

# Tasa de cambio ARS -> USD (dolar MEP referencia).
# Actualizar manualmente si es necesario.
MEP_RATE = 1400  # ARS por 1 USD

PRECIO_MIN_USD = 50_000
PRECIO_MAX_USD = 90_000

def run_scraper(script_name):
    print(f"Ejecutando {script_name}...")
    try:
        subprocess.run(['python', script_name], check=True, cwd=os.path.dirname(__file__))
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando {script_name}: {e}")

def parse_precio_usd(precio_str):
    """
    Convierte un string de precio a un valor numérico en USD.
    Formatos soportados:
      - 'US$ 232.000'  -> 232000 USD
      - 'USD 165000'   -> 165000 USD
      - 'USD60.000'    -> 60000  USD
      - 'USD 75.000'   -> 75000  USD
      - 'ARS 7000000'  -> 7000000 / MEP_RATE USD
      - '20000'        -> asumido USD si < 1.000.000, sino ARS
      - 'Consultar'    -> None (no filtrar, dejar pasar)
    """
    if not precio_str:
        return None

    s = precio_str.strip().upper()

    # Si no tiene moneda ni número reconocible, no filtrar
    if re.search(r'[A-Z]{2,3}SULTAR|CONSULTE|PRECIO CONSUL', s):
        return None  # dejar pasar propiedades sin precio publicado

    # Detectar moneda
    is_usd = bool(re.search(r'USD|US\$|U\$D|U\$S', s))
    is_ars = bool(re.search(r'ARS|\$(?!D)', s)) and not is_usd

    # Extraer solo dígitos y puntos/comas
    numeros = re.sub(r'[^\d.,]', '', s)

    if not numeros:
        return None

    # En Argentina usan punto como separador de miles y coma como decimal
    # Ejemplos: "232.000" = 232000,  "232,000" = 232000
    # Si hay coma Y punto: "1.232,50" → float (pero no es nuestro caso)
    # Si solo hay puntos: "232.000" → reemplazar puntos → 232000
    # Si solo hay comas: "232,000" → reemplazar comas → 232000
    if ',' in numeros and '.' in numeros:
        # formato europeo: 1.232,50 → quitar puntos, cambiar coma por punto
        numeros = numeros.replace('.', '').replace(',', '.')
    elif '.' in numeros:
        # puede ser separador de miles (232.000) o decimal (232.5)
        partes = numeros.split('.')
        if len(partes[-1]) == 3:  # último grupo de 3 dígitos → miles
            numeros = numeros.replace('.', '')
        # si no, ya es decimal, lo dejamos
    elif ',' in numeros:
        numeros = numeros.replace(',', '')

    try:
        valor = float(numeros)
    except ValueError:
        return None

    if is_ars:
        return valor / MEP_RATE
    elif is_usd:
        return valor
    else:
        # Sin moneda explícita: si es < 1.000.000 asumimos USD, sino ARS
        if valor < 1_000_000:
            return valor
        else:
            return valor / MEP_RATE

def en_rango_precio(prop):
    """Retorna True si la propiedad está dentro del rango 50k-90k USD."""
    precio_str = prop.get('precio', '')
    valor_usd = parse_precio_usd(precio_str)

    if valor_usd is None:
        return True  # precio no publicado: incluir (el usuario lo ve en el dashboard)

    return PRECIO_MIN_USD <= valor_usd <= PRECIO_MAX_USD

def consolidate_data():
    base_dir = os.path.dirname(__file__)
    files = [
        'resultados_inmoclick.json',
        'resultados_mendozaprop.json',
        'resultados_zonaprop.json',
        'resultados_cocucci.json',
    ]

    all_properties = []

    for filename in files:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        antes = len(data)
                        filtradas = [p for p in data if en_rango_precio(p)]
                        all_properties.extend(filtradas)
                        descartadas = antes - len(filtradas)
                        print(f"  {filename}: {len(filtradas)} dentro del rango ({descartadas} descartadas por precio)")
            except Exception as e:
                print(f"Error procesando {filename}: {e}")

    output_path = os.path.join(base_dir, 'propiedades_totales.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_properties, f, ensure_ascii=False, indent=4)

    print(f"\nConsolidación completada. Total propiedades en rango (USD {PRECIO_MIN_USD:,}–{PRECIO_MAX_USD:,}): {len(all_properties)}")
    print(f"Guardado en: {output_path}")

def main():
    print("--- INICIANDO CASATRACKER ORCHESTRATOR ---")
    run_scraper('scraper_inmoclick.py')
    run_scraper('scraper_mendozaprop.py')
    run_scraper('scraper_zonaprop.py')
    run_scraper('scraper_cocucci.py')
    print("------------------------------------------")
    consolidate_data()

if __name__ == "__main__":
    main()

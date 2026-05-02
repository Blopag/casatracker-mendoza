import json
import os
import shutil
import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

BASE_DIR = os.path.dirname(__file__)
ACTUALES_PATH = os.path.join(BASE_DIR, "propiedades_totales.json")
ANTERIORES_PATH = os.path.join(BASE_DIR, "propiedades_anteriores.json")


def cargar_propiedades(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def enviar_telegram(texto):
    if not TOKEN or not CHAT_ID:
        print("⚠️  Sin credenciales Telegram (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID).")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    res = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    })
    if res.ok:
        print("✅ Alerta enviada a Telegram.")
    else:
        print(f"❌ Error al enviar Telegram: {res.text}")


def detectar_novedades():
    actuales = cargar_propiedades(ACTUALES_PATH)
    anteriores = cargar_propiedades(ANTERIORES_PATH)

    links_anteriores = {p.get("link") for p in anteriores}
    novedades = [p for p in actuales if p.get("link") not in links_anteriores]

    if not novedades:
        print("Sin propiedades nuevas hoy.")
    else:
        print(f"🏡 {len(novedades)} propiedades nuevas detectadas.")
        texto = f"🏡 *CasaTracker Mendoza* — {len(novedades)} propiedades nuevas!\n\n"
        for p in novedades[:5]:
            texto += f"📍 *{p.get('titulo', 'Sin título')}*\n"
            texto += f"💰 {p.get('precio', 'Consultar')}\n"
            texto += f"🛏 {p.get('beds', '?')} hab  🛁 {p.get('baths', '?')} baños\n"
            texto += f"🔗 {p.get('link', '#')}\n\n"
        if len(novedades) > 5:
            texto += f"_...y {len(novedades) - 5} más._"
        enviar_telegram(texto)

    # Guardar estado actual para la próxima ejecución
    shutil.copy(ACTUALES_PATH, ANTERIORES_PATH)
    print("Estado actualizado en propiedades_anteriores.json")


if __name__ == "__main__":
    detectar_novedades()

import os
import time
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SUBITO_URL = os.environ.get("SUBITO_URL")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

def check_subito():
    seen_ids = set()
    print("Iniciando monitor...")
    send_telegram_message("🤖 <b>Bot activado:</b> Monitoreando alquileres en Bolonia...")

    while True:
        try:
            response = requests.get(SUBITO_URL, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                articles = soup.find_all("div", class_=lambda c: c and ("SmallCard" in c or "ItemCard" in c))
                
                for article in articles:
                    link_tag = article.find("a", href=True)
                    if not link_tag:
                        continue
                    
                    link = link_tag["href"]
                    ad_id = link.split("-")[-1].replace(".htm", "")
                    
                    title_tag = article.find("h2")
                    title = title_tag.get_text(strip=True) if title_tag else "Anuncio sin título"
                    
                    price_tag = article.find("p", class_=lambda c: c and "price" in c.lower())
                    price = price_tag.get_text(strip=True) if price_tag else "Precio no especificado"

                    if ad_id not in seen_ids:
                        seen_ids.add(ad_id)
                        if len(seen_ids) > 15: 
                            msg = f"🚨 <b>¡NUEVO ALQUILER EN BOLONIA!</b>\n\n<b>{title}</b>\n💰 {price}\n\n🔗 <a href='{link}'>Ver anuncio en Subito</a>"
                            send_telegram_message(msg)
            else:
                print(f"Error HTTP {response.status_code}")

        except Exception as e:
            print(f"Error en bucle: {e}")

        time.sleep(60)

if __name__ == "__main__":
    check_subito()

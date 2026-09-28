import os
import time
import requests
from bs4 import BeautifulSoup
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# 1. Mini servidor web para Render (mantiene el servicio Web Service activo en el plan gratuito $0)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot de Subito activo")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# 2. Configuración de credenciales desde variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SUBITO_URL = os.environ.get("SUBITO_URL")

def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Falta TELEGRAM_TOKEN o CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")

def check_subito():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    seen_ids = set()
    
    send_telegram_message("🤖 <b>Bot activado:</b> Monitoreando alquileres en Bolonia...")
    
    # Bucle principal de monitoreo continuo
    while True:
        try:
            if not SUBITO_URL:
                print("Esperando SUBITO_URL...")
                time.sleep(60)
                continue

            response = requests.get(SUBITO_URL, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                items = soup.find_all("div", class_=lambda c: c and "items__item" in c)
                
                for item in items:
                    link_elem = item.find("a", href=True)
                    if not link_elem:
                        continue
                    
                    link = link_elem["href"]
                    title_elem = item.find("h2") or item.find("h3")
                    title = title_elem.text.strip() if title_elem else "Nuevo anuncio"
                    
                    price_elem = item.find("p", class_=lambda c: c and "price" in c)
                    price = price_elem.text.strip() if price_elem else "Consultar precio"
                    
                    if link not in seen_ids:
                        seen_ids.add(link)
                        # Solo notificar en ciclos posteriores para no saturar al arrancar
                        if len(seen_ids) > len(items):
                            msg = f"🏠 <b>¡Nuevo anuncio en Subito!</b>\n\n📌 <b>{title}</b>\n💰 {price}\n\n🔗 <a href='{link}'>Ver anuncio</a>"
                            send_telegram_message(msg)
            else:
                print(f"Respuesta de Subito: {response.status_code}")
                
        except Exception as e:
            print(f"Error durante el escaneo: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    check_subito()


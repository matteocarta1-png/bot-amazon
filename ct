import requests
import time
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE ---
DISCORD_WEBHOOK_URL = "INSERISCI_QUI_IL_TUO_WEBHOOK"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
}

# --- LISTA COMPLETA 50 PRODOTTI ---
PRODOTTI = [
    {"nome": "PS5 Slim Digital", "asins": {"IT": ("amazon.it", "B0CY5JFL4L"), "DE": ("amazon.de", "B0CLTF9723"), "ES": ("amazon.es", "B0CY5JFL4L"), "FR": ("amazon.fr", "B0CY5JFL4L"), "UK": ("amazon.co.uk", "B0CY5JFL4L")}},
    {"nome": "PS5 Slim Standard", "asins": {"IT": ("amazon.it", "B0C9R4K6LN"), "DE": ("amazon.de", "B0C9R4K6LN"), "ES": ("amazon.es", "B0C9R4K6LN"), "FR": ("amazon.fr", "B0C9R4K6LN"), "UK": ("amazon.co.uk", "B0C9R4K6LN")}},
    {"nome": "DualSense Controller PS5", "asins": {"IT": ("amazon.it", "B08H99BPJN"), "DE": ("amazon.de", "B08H99BPJN"), "ES": ("amazon.es", "B08H99BPJN"), "FR": ("amazon.fr", "B08H99BPJN"), "UK": ("amazon.co.uk", "B08H99BPJN")}},
    {"nome": "Nintendo Switch OLED", "asins": {"IT": ("amazon.it", "B07VGRJ29K"), "DE": ("amazon.de", "B07VGRJ29K"), "ES": ("amazon.es", "B07VGRJ29K"), "FR": ("amazon.fr", "B07VGRJ29K"), "UK": ("amazon.co.uk", "B07VGRJ29K")}},
    {"nome": "Xbox Series X 1TB", "asins": {"IT": ("amazon.it", "B09B29LL14"), "DE": ("amazon.de", "B09B29LL14"), "ES": ("amazon.es", "B09B29LL14"), "FR": ("amazon.fr", "B09B29LL14"), "UK": ("amazon.co.uk", "B09B29LL14")}},
    {"nome": "Xbox Series S 512GB", "asins": {"IT": ("amazon.it", "B087VM5XC6"), "DE": ("amazon.de", "B087VM5XC6"), "ES": ("amazon.es", "B087VM5XC6"), "FR": ("amazon.fr", "B087VM5XC6"), "UK": ("amazon.co.uk", "B087VM5XC6")}},
    {"nome": "Meta Quest 3 128GB", "asins": {"IT": ("amazon.it", "B0B8C3X7S4"), "DE": ("amazon.de", "B0B8C3X7S4"), "ES": ("amazon.es", "B0B8C3X7S4"), "FR": ("amazon.fr", "B0B8C3X7S4"), "UK": ("amazon.co.uk", "B0B8C3X7S4")}},
    {"nome": "ASUS ROG Ally Z1 Extreme", "asins": {"IT": ("amazon.it", "B0CFRYRN1N"), "DE": ("amazon.de", "B0CFRYRN1N"), "ES": ("amazon.es", "B0CFRYRN1N"), "FR": ("amazon.fr", "B0CFRYRN1N"), "UK": ("amazon.co.uk", "B0CFRYRN1N")}},
    {"nome": "AirPods Pro (2ª Gen)", "asins": {"IT": ("amazon.it", "B09G9F5C1R"), "DE": ("amazon.de", "B09G9F5C1R"), "ES": ("amazon.es", "B09G9F5C1R"), "FR": ("amazon.fr", "B09G9F5C1R"), "UK": ("amazon.co.uk", "B09G9F5C1R")}},
    {"nome": "AirPods 3ª Generazione", "asins": {"IT": ("amazon.it", "B0CHWXZB18"), "DE": ("amazon.de", "B0CHWXZB18"), "ES": ("amazon.es", "B0CHWXZB18"), "FR": ("amazon.fr", "B0CHWXZB18"), "UK": ("amazon.co.uk", "B0CHWXZB18")}},
    {"nome": "iPhone 15 128GB", "asins": {"IT": ("amazon.it", "B0CHWZCY47"), "DE": ("amazon.de", "B0CHWZCY47"), "ES": ("amazon.es", "B0CHWZCY47"), "FR": ("amazon.fr", "B0CHWZCY47"), "UK": ("amazon.co.uk", "B0CHWZCY47")}},
    {"nome": "iPhone 15 Pro Max 256GB", "asins": {"IT": ("amazon.it", "B0CHX281Y3"), "DE": ("amazon.de", "B0CHX281Y3"), "ES": ("amazon.es", "B0CHX281Y3"), "FR": ("amazon.fr", "B0CHX281Y3"), "UK": ("amazon.co.uk", "B0CHX281Y3")}},
    {"nome": "Galaxy S24 Ultra", "asins": {"IT": ("amazon.it", "B0CTM2S44C"), "DE": ("amazon.de", "B0CTM2S44C"), "ES": ("amazon.es", "B0CTM2S44C"), "FR": ("amazon.fr", "B0CTM2S44C"), "UK": ("amazon.co.uk", "B0CTM2S44C")}},
    {"nome": "Galaxy A55 5G", "asins": {"IT": ("amazon.it", "B0CV4GMB3H"), "DE": ("amazon.de", "B0C43D5Q4S"), "ES": ("amazon.es", "B0C43D5Q4S"), "FR": ("amazon.fr", "B0C43D5Q4S"), "UK": ("amazon.co.uk", "B0C43D5Q4S")}},
    {"nome": "Redmi Note 13 5G", "asins": {"IT": ("amazon.it", "B0CQMH5DMB"), "DE": ("amazon.de", "B0B8R4J985"), "ES": ("amazon.es", "B0B8R4J985"), "FR": ("amazon.fr", "B0B8R4J985"), "UK": ("amazon.co.uk", "B0B8R4J985")}},
    {"nome": "Sony WH-1000XM5", "asins": {"IT": ("amazon.it", "B09Y2MYL5C"), "DE": ("amazon.de", "B09JR837S7"), "ES": ("amazon.es", "B09JR837S7"), "FR": ("amazon.fr", "B09JR837S7"), "UK": ("amazon.co.uk", "B09JR837S7")}},
    {"nome": "JBL Flip 6", "asins": {"IT": ("amazon.it", "B09G98CH98"), "DE": ("amazon.de", "B09G98CH98"), "ES": ("amazon.es", "B09G98CH98"), "FR": ("amazon.fr", "B09G98CH98"), "UK": ("amazon.co.uk", "B09G98CH98")}},
    {"nome": "MacBook Air M1", "asins": {"IT": ("amazon.it", "B08N5N6RSS"), "DE": ("amazon.de", "B08N5N6RSS"), "ES": ("amazon.es", "B08N5N6RSS"), "FR": ("amazon.fr", "B08N5N6RSS")}},
    {"nome": "MacBook Air M3", "asins": {"IT": ("amazon.it", "B0CX2542LN"), "DE": ("amazon.de", "B0CX2542LN"), "ES": ("amazon.es", "B0CX2542LN"), "FR": ("amazon.fr", "B0CX2542LN")}},
    {"nome": "iPad 10.9 (10ª Gen)", "asins": {"IT": ("amazon.it", "B09G936L71"), "DE": ("amazon.de", "B09G936L71"), "ES": ("amazon.es", "B09G936L71"), "FR": ("amazon.fr", "B09G936L71"), "UK": ("amazon.co.uk", "B09G936L71")}},
    {"nome": "iPad Pro 11", "asins": {"IT": ("amazon.it", "B09G3HQ181"), "DE": ("amazon.de", "B09G3HQ181"), "ES": ("amazon.es", "B09G3HQ181"), "FR": ("amazon.fr", "B09G3HQ181"), "UK": ("amazon.co.uk", "B09G3HQ181")}},
    {"nome": "Galaxy Tab A9+", "asins": {"IT": ("amazon.it", "B0CX23H2T9"), "DE": ("amazon.de", "B0CX23H2T9"), "ES": ("amazon.es", "B0CX23H2T9"), "FR": ("amazon.fr", "B0CX23H2T9"), "UK": ("amazon.co.uk", "B0CX23H2T9")}},
    {"nome": "HP Laptop 15s", "asins": {"IT": ("amazon.it", "B0B13CK1R9"), "DE": ("amazon.de", "B0B13CK1R9"), "ES": ("amazon.es", "B0B13CK1R9"), "FR": ("amazon.fr", "B0B13CK1R9")}},
    {"nome": "Lenovo IdeaPad Slim 3", "asins": {"IT": ("amazon.it", "B09H2281S6"), "DE": ("amazon.de", "B09H2281S6"), "ES": ("amazon.es", "B09H2281S6"), "FR": ("amazon.fr", "B09H2281S6")}},
    {"nome": "Monitor Gaming Odyssey G3", "asins": {"IT": ("amazon.it", "B088T25M5U"), "DE": ("amazon.de", "B088T25M5U"), "ES": ("amazon.es", "B088T25M5U"), "FR": ("amazon.fr", "B088T25M5U"), "UK": ("amazon.co.uk", "B088T25M5U")}},
    {"nome": "Logitech MX Master 3S", "asins": {"IT": ("amazon.it", "B093TK9WMB"), "DE": ("amazon.de", "B093TK9WMB"), "ES": ("amazon.es", "B093TK9WMB"), "FR": ("amazon.fr", "B093TK9WMB"), "UK": ("amazon.co.uk", "B093TK9WMB")}},
    {"nome": "Samsung 980 Pro 1TB", "asins": {"IT": ("amazon.it", "B07XH33M6C"), "DE": ("amazon.de", "B07XH33M6C"), "ES": ("amazon.es", "B07XH33M6C"), "FR": ("amazon.fr", "B07XH33M6C"), "UK": ("amazon.co.uk", "B07XH33M6C")}},
    {"nome": "Apple Watch Series 9", "asins": {"IT": ("amazon.it", "B0CHX6Y141"), "DE": ("amazon.de", "B0CHX6Y141"), "ES": ("amazon.es", "B0CHX6Y141"), "FR": ("amazon.fr", "B0CHX6Y141"), "UK": ("amazon.co.uk", "B0CHX6Y141")}},
    {"nome": "Galaxy Watch 6", "asins": {"IT": ("amazon.it", "B0C7LDKT13"), "DE": ("amazon.de", "B0C7LDKT13"), "ES": ("amazon.es", "B0C7LDKT13"), "FR": ("amazon.fr", "B0C7LDKT13"), "UK": ("amazon.co.uk", "B0C7LDKT13")}},
    {"nome": "Garmin Forerunner 55", "asins": {"IT": ("amazon.it", "B09G9F64P6"), "DE": ("amazon.de", "B09G9F64P6"), "ES": ("amazon.es", "B09G9F64P6"), "FR": ("amazon.fr", "B09G9F64P6"), "UK": ("amazon.co.uk", "B09G9F64P6")}},
    {"nome": "Xiaomi Band 8", "asins": {"IT": ("amazon.it", "B0C9RMZ3K2"), "DE": ("amazon.de", "B0C9RMZ3K2"), "ES": ("amazon.es", "B0C9RMZ3K2"), "FR": ("amazon.fr", "B0C9RMZ3K2"), "UK": ("amazon.co.uk", "B0C9RMZ3K2")}},
    {"nome": "Dyson V15 Detect", "asins": {"IT": ("amazon.it", "B0BDK6Z6X8"), "DE": ("amazon.de", "B0BDK6Z6X8"), "ES": ("amazon.es", "B0BDK6Z6X8"), "FR": ("amazon.fr", "B0BDK6Z6X8")}},
    {"nome": "Cecotec Airfryer 5.5L", "asins": {"IT": ("amazon.it", "B08K3H6D8M"), "DE": ("amazon.de", "B08K3H6D8M"), "ES": ("amazon.es", "B08K3H6D8M"), "FR": ("amazon.fr", "B08K3H6D8M")}},
    {"nome": "Philips Airfryer XXL", "asins": {"IT": ("amazon.it", "B01D9DGA56"), "DE": ("amazon.de", "B01D9DGA56"), "ES": ("amazon.es", "B01D9DGA56"), "FR": ("amazon.fr", "B01D9DGA56")}},
    {"nome": "Roomba 692", "asins": {"IT": ("amazon.it", "B094R3NMS3"), "DE": ("amazon.de", "B094R3NMS3"), "ES": ("amazon.es", "B094R3NMS3"), "FR": ("amazon.fr", "B094R3NMS3")}},
    {"nome": "Dreame L10s Ultra", "asins": {"IT": ("amazon.it", "B09JS3G8W1"), "DE": ("amazon.de", "B09JS3G8W1"), "ES": ("amazon.es", "B09JS3G8W1"), "FR": ("amazon.fr", "B09JS3G8W1")}},
    {"nome": "De'Longhi Magnifica S", "asins": {"IT": ("amazon.it", "B084G2938Y"), "DE": ("amazon.de", "B084G2938Y"), "ES": ("amazon.es", "B084G2938Y"), "FR": ("amazon.fr", "B084G2938Y")}},
    {"nome": "Fire TV Stick 4K Max", "asins": {"IT": ("amazon.it", "B09339C9Z4"), "DE": ("amazon.de", "B09339C9Z4"), "ES": ("amazon.es", "B09339C9Z4"), "FR": ("amazon.fr", "B09339C9Z4"), "UK": ("amazon.co.uk", "B09339C9Z4")}},
    {"nome": "Echo Dot 5ª Gen", "asins": {"IT": ("amazon.it", "B09B2C4Z6N"), "DE": ("amazon.de", "B09B2C4Z6N"), "ES": ("amazon.es", "B09B2C4Z6N"), "FR": ("amazon.fr", "B09B2C4Z6N"), "UK": ("amazon.co.uk", "B09B2C4Z6N")}},
    {"nome": "Echo Show 8", "asins": {"IT": ("amazon.it", "B09B2X23Y2"), "DE": ("amazon.de", "B09B2X23Y2"), "ES": ("amazon.es", "B09B2X23Y2"), "FR": ("amazon.fr", "B09B2X23Y2"), "UK": ("amazon.co.uk", "B09B2X23Y2")}},
    {"nome": "LG OLED TV 55", "asins": {"IT": ("amazon.it", "B0C39R5Y32"), "DE": ("amazon.de", "B0C39R5Y32"), "ES": ("amazon.es", "B0C39R5Y32"), "FR": ("amazon.fr", "B0C39R5Y32")}},
    {"nome": "Samsung TV 55 Crystal", "asins": {"IT": ("amazon.it", "B0C34B8K3M"), "DE": ("amazon.de", "B0C34B8K3M"), "ES": ("amazon.es", "B0C34B8K3M"), "FR": ("amazon.fr", "B0C34B8K3M")}},
    {"nome": "Bose Soundbar 600", "asins": {"IT": ("amazon.it", "B0942N6N1F"), "DE": ("amazon.de", "B0942N6N1F"), "ES": ("amazon.es", "B0942N6N1F"), "FR": ("amazon.fr", "B0942N6N1F"), "UK": ("amazon.co.uk", "B0942N6N1F")}},
    {"nome": "Casio Vintage", "asins": {"IT": ("amazon.it", "B002K88062"), "DE": ("amazon.de", "B002K88062"), "ES": ("amazon.es", "B002K88062"), "FR": ("amazon.fr", "B002K88062"), "UK": ("amazon.co.uk", "B002K88062")}},
    {"nome": "Tommy Hilfiger Crono", "asins": {"IT": ("amazon.it", "B0833Z412B"), "DE": ("amazon.de", "B0833Z412B"), "ES": ("amazon.es", "B0833Z412B"), "FR": ("amazon.fr", "B0833Z412B"), "UK": ("amazon.co.uk", "B0833Z412B")}},
    {"nome": "Avviatore Auto", "asins": {"IT": ("amazon.it", "B07P88H32P"), "DE": ("amazon.de", "B07P88H32P"), "ES": ("amazon.es", "B07P88H32P"), "FR": ("amazon.fr", "B07P88H32P")}},
    {"nome": "Compressore Portatile", "asins": {"IT": ("amazon.it", "B07S7XJ9F2"), "DE": ("amazon.de", "B07S7XJ9F2"), "ES": ("amazon.es", "B07S7XJ9F2"), "FR": ("amazon.fr", "B07S7XJ9F2"), "UK": ("amazon.co.uk", "B07S7XJ9F2")}},
    {"nome": "Kindle Paperwhite", "asins": {"IT": ("amazon.it", "B09SWTG963"), "DE": ("amazon.de", "B09SWTG963"), "ES": ("amazon.es", "B09SWTG963"), "FR": ("amazon.fr", "B09SWTG963"), "UK": ("amazon.co.uk", "B09SWTG963")}},
    {"nome": "Kindle Scribe", "asins": {"IT": ("amazon.it", "B0B2JV723R"), "DE": ("amazon.de", "B0B2JV723R"), "ES": ("amazon.es", "B0B2JV723R"), "FR": ("amazon.fr", "B0B2JV723R"), "UK": ("amazon.co.uk", "B0B2JV723R")}},
    {"nome": "Fire TV Stick 4K", "asins": {"IT": ("amazon.it", "B08C1LR9QH"), "DE": ("amazon.de", "B08C1LR9QH"), "ES": ("amazon.es", "B08C1LR9QH"), "FR": ("amazon.fr", "B08C1LR9QH"), "UK": ("amazon.co.uk", "B08C1LR9QH")}}
]

# --- FUNZIONI ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot attivo!")

def start_health_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

def monitor():
    while True:
        for p in PRODOTTI:
            for paese, (domain, asin) in p["asins"].items():
                url = f"https://www.{domain}/dp/{asin}"
                try:
                    r = requests.get(url, headers=HEADERS, timeout=10)
                    if r.status_code == 200:
                        soup = BeautifulSoup(r.content, "html.parser")
                        prezzo = soup.select_one("span.a-price span.a-offscreen")
                        if prezzo:
                            print(f"[{paese}] {p['nome']}: {prezzo.text}")
                    time.sleep(3) # Pausa tra ogni richiesta
                except Exception:
                    pass
        time.sleep(600) # Pausa tra cicli completi

if __name__ == "__main__":
    threading.Thread(target=start_health_server, daemon=True).start()
    monitor()

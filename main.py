import requests
import time
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE BOT ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1538678502440706178/xRaJv_l3RhOirbbZ_AvDr1aFaV-bJeSKcWbnk3EiqHnwdqATTDAeKCs6LsPCdALnHkjG"

# LISTA PRODOTTI MONITORATI
PRODOTTI = [
    # --- PLAYSTATION & GAMING ---
    {"asin": "B08N5WRWNW", "nome": "PlayStation 5 Console Standard"},
    {"asin": "B0CLTF9723", "nome": "PlayStation 5 Digital Edition (Slim)"},
    {"asin": "B080000000", "nome": "DualSense Controller PS5 Wireless"},
    
    # --- TELEFONIA & AUDIO ---
    {"asin": "B09G9F5C1R", "nome": "Apple AirPods Pro (2ª Gen)"},
    {"asin": "B08H93ZRK9", "nome": "Apple iPhone 13 / 14 / 15"},
    {"asin": "B0B7BPB3S9", "nome": "Samsung Galaxy S23 / S24 Ultra"},
    {"asin": "B0C9R8X4M1", "nome": "Xiaomi Redmi Note Series"},
    
    # --- COMPUTER & INFORMATICA ---
    {"asin": "B08N5N6RSS", "nome": "Apple MacBook Air M1 / M2"},
    {"asin": "B0B13CK1R9", "nome": "HP Laptop 15s (Intel Core i5 / i7)"},
    {"asin": "B09H2281S6", "nome": "Lenovo IdeaPad Slim 3"},
    {"asin": "B088T25M5U", "nome": "Samsung Monitor Gaming Odyssey"},

    # --- ARTICOLI SPORTIVI & WEARABLE ---
    {"asin": "B09G9F64P6", "nome": "Garmin Forerunner Smartwatch Sportivo"},
    {"asin": "B09HS7Y5XN", "nome": "Fitbit Charge Smartband Fitness"},
    {"asin": "B08XWN7N8Q", "nome": "Panca Piana Palestra Regolabile"},
    {"asin": "B07V2C4K21", "nome": "Tapis Roulant Elettrico Pieghevole"},

    # --- GIOIELLI & OROLOGI ---
    {"asin": "B002K88062", "nome": "Orologio Casio Vintage Digital Unisex"},
    {"asin": "B01E2T3YPO", "nome": "Bracciale Pandora Moments in Argento"},
    {"asin": "B0833Z412B", "nome": "Orologio Tommy Hilfiger Cronografo"},

    # --- ARTICOLI PER BAMBINI & NEONATI ---
    {"asin": "B071XB2M2B", "nome": "Seggiolino Auto Foppapedretti Isodyna"},
    {"asin": "B00N3V1J1K", "nome": "Passeggino Leggero Chicco London"},
    {"asin": "B08KSF4986", "nome": "Pampers Baby-Dry Pacco Scorta"},

    # --- ACCESSORI AUTO & MOTO ---
    {"asin": "B07P88H32P", "nome": "Avviatore di Emergenza / Powerbank Auto"},
    {"asin": "B079133MNT", "nome": "Dash Cam Auto Full HD 1080P"},
    {"asin": "B07S7XJ9F2", "nome": "Compressore Portatile Elettrico Auto/Moto"}
]

PERCENTUALE_MINIMA_SCONTO = 80.0  # Notifica solo con sconti >= 80%

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# Mini Server Web per soddisfare Render
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Amazon attivo e funzionante!")

def start_health_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

def invia_notifica_discord(nome, prezzo_attuale, prezzo_listino, percentuale_sconto, url, asin):
    payload = {
        "content": f"@everyone 🚨 *SUPER ERRORE DI PREZZO (-{percentuale_sconto:.0f}%)!* 🚨",
        "embeds": [
            {
                "title": f"📦 {nome}",
                "description": f"Il prezzo è crollato del *{percentuale_sconto:.1f}%*!",
                "url": url,
                "color": 15158332,
                "fields": [
                    {"name": "🔥 Prezzo Scontato", "value": f"*{prezzo_attuale:.2f} €*", "inline": True},
                    {"name": "❌ Prezzo di Listino", "value": f"~{prezzo_listino:.2f} €~", "inline": True},
                    {"name": "📉 Sconto Rilevato", "value": f"*-{percentuale_sconto:.0f}%*", "inline": True},
                    {"name": "🛒 Link Acquisto Direct", "value": f"[Apri subito su Amazon]({url})", "inline": False}
                ],
                "footer": {"text": "Amazon Price Tracker Bot • Alert 80%+ Sconto"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        ]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        print(f"✅ Notifica inviata con successo per {nome}")
    except Exception as e:
        print(f"❌ Errore invio Discord: {e}")

def estrai_dati_prezzo(soup):
    try:
        # Cerca la percentuale di sconto indicata da Amazon
        badge_sconto = soup.select_one("span.savingsPercentage")
        if badge_sconto:
            match_sconto = re.search(r'([0-9]+)', badge_sconto.get_text())
            if match_sconto:
                sconto_percentuale = float(match_sconto.group(1))
                elem_prezzo = soup.select_one("span.a-price span.a-offscreen")
                if elem_prezzo:
                    match_p = re.search(r'([0-9]+[\.,][0-9]+)', elem_prezzo.get_text().strip())
                    if match_p:
                        prezzo_attuale = float(match_p.group(1).replace('.', '').replace(',', '.'))
                        prezzo_listino = prezzo_attuale / (1 - (sconto_percentuale / 100))
                        return prezzo_attuale, prezzo_listino, sconto_percentuale

        # Calcola la differenza dal prezzo barrato
        elem_listino = soup.select_one("span.a-price[data-a-strike='true'] span.a-offscreen, .basisPrice span.a-offscreen")
        elem_attuale = soup.select_one("span.a-price span.a-offscreen")
        
        if elem_listino and elem_attuale:
            match_l = re.search(r'([0-9]+[\.,][0-9]+)', elem_listino.get_text().strip())
            match_a = re.search(r'([0-9]+[\.,][0-9]+)', elem_attuale.get_text().strip())
            
            if match_l and match_a:
                prezzo_listino = float(match_l.group(1).replace('.', '').replace(',', '.'))
                prezzo_attuale = float(match_a.group(1).replace('.', '').replace(',', '.'))
                
                if prezzo_listino > prezzo_attuale:
                    sconto_percentuale = ((prezzo_listino - prezzo_attuale) / prezzo_listino) * 100
                    return prezzo_attuale, prezzo_listino, sconto_percentuale

    except Exception as e:
        print(f"   ⚠️ Errore calcolo prezzi: {e}")
        
    return None, None, 0.0

def controlla_prezzi():
    while True:
        print(f"\n--- Inizio ciclo di controllo ({time.strftime('%H:%M:%S')}) ---")
        for prod in PRODOTTI:
            url = f"https://www.amazon.it/dp/{prod['asin']}"
            print(f"🔍 Controllo: {prod['nome']} ({prod['asin']})...")
            
            try:
                response = requests.get(url, headers=HEADERS, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    prezzo_attuale, prezzo_listino, sconto_percentuale = estrai_dati_prezzo(soup)
                    
                    if prezzo_attuale:
                        print(f"   Prezzo: {prezzo_attuale:.2f} € | Sconto: {sconto_percentuale:.1f}%")
                        if sconto_percentuale >= PERCENTUALE_MINIMA_SCONTO:
                            print(f"   🚨 ALLARME! Sconto del {sconto_percentuale:.1f}% rilevato!")
                            invia_notifica_discord(prod['nome'], prezzo_attuale, prezzo_listino, sconto_percentuale, url, prod['asin'])
                    else:
                        print("   ℹ️ Nessun prezzo/sconto rilevato.")
                else:
                    print(f"   ⚠️ Risposta Amazon: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Errore durante il controllo: {e}")
                
            time.sleep(5)  # Pausa tra i prodotti
            
        print("\n😴 Attesa di 10 minuti prima della prossima scansione...")
        time.sleep(600)

if __name__ == "__main__":
    print("🚀 Bot Amazon Tracker Sconti 80%+ Avviato!")
    threading.Thread(target=start_health_server, daemon=True).start()
    controlla_prezzi()

import requests
import time
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE BOT ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1538678502440706178/xRaJv_l3RhOirbbZ_AvDr1aFaV-bJeSKcWbnk3EiqHnwdqATTDAeKCs6LsPCdALnHkjG"

PRODOTTI = [
    {"asin": "B08N5WRWNW", "nome": "PlayStation 5 Console", "soglia_errore": 350.0},
    {"asin": "B09G9F5C1R", "nome": "Apple AirPods Pro", "soglia_errore": 120.0},
    {"asin": "B08H93ZRK9", "nome": "Apple iPhone 13 / 14 / 15", "soglia_errore": 450.0},
    {"asin": "B0B7BPB3S9", "nome": "Samsung Galaxy S23 / S24 Ultra", "soglia_errore": 500.0},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# Mini Server Web per soddisfare Render Web Service
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Amazon attivo e funzionante!")

def start_health_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

def invia_notifica_discord(nome, prezzo, url, asin):
    payload = {
        "content": "@everyone 🚨 *POSSIBILE ERRORE DI PREZZO RILEVATO!* 🚨",
        "embeds": [
            {
                "title": f"📦 {nome}",
                "description": "È stato rilevato un prezzo insolitamente basso su Amazon!",
                "url": url,
                "color": 15158332,
                "fields": [
                    {"name": "💶 Prezzo Rilevato", "value": f"*{prezzo:.2f} €*", "inline": True},
                    {"name": "🆔 Codice ASIN", "value": f"{asin}", "inline": True},
                    {"name": "🛒 Link Acquisto Direct", "value": f"[Clicca qui per aprire su Amazon]({url})", "inline": False}
                ],
                "footer": {"text": "Amazon Price Tracker Bot • Notifica Automatica"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        ]
    }
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if res.status_code in [200, 204]:
            print(f"✅ Notifica inviata con successo su Discord per: {nome}")
        else:
            print(f"⚠️ Errore invio Discord ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"❌ Errore durante l'invio del webhook: {e}")

def estrai_prezzo(soup):
    selettori = [
        "span.a-price span.a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#corePrice_feature_div span.a-offscreen",
        ".apexPriceToPay span.a-offscreen"
    ]
    for selettore in selettori:
        elem = soup.select_one(selettore)
        if elem:
            testo = elem.get_text().strip()
            match = re.search(r'([0-9]+[\.,][0-9]+)', testo)
            if match:
                valore_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    return float(valore_str)
                except ValueError:
                    continue
    return None

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
                    prezzo = estrai_prezzo(soup)
                    
                    if prezzo:
                        print(f"   Prezzo trovato: {prezzo:.2f} € (Soglia allarme: {prod['soglia_errore']} €)")
                        if prezzo <= prod['soglia_errore']:
                            print("   🚨 ALLARME! Prezzo inferiore alla soglia!")
                            invia_notifica_discord(prod['nome'], prezzo, url, prod['asin'])
                    else:
                        print("   ℹ️ Impossibile leggere il prezzo.")
                else:
                    print(f"   ⚠️ Codice risposta Amazon: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Errore: {e}")
                
            time.sleep(5)
            
        print("\n😴 Attesa di 10 minuti...")
        time.sleep(600)

if __name__ == "__main__":
    print("🚀 Bot Amazon Price Tracker avviato!")
    
    # Invia messaggio di test all'avvio
    invia_notifica_discord("TEST - Bot Avviato con Successo", 0.00, "https://www.amazon.it", "TEST_ASIN")
    
    # Avvia il server web in background per Render
    threading.Thread(target=start_health_server, daemon=True).start()
    
    # Avvia il ciclo del bot
    controlla_prezzi()

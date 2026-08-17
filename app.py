import requests
import time
import re
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE BOT ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1538678502440706178/xRaJv_l3RhOirbbZ_AvDr1aFaV-bJeSKcWbnk3EiqHnwdqATTDAeKCs6LsPCdALnHkjG"

# API Key di ScraperAPI presa dal tuo pannello
SCRAPER_API_KEY = "83ce5ffe4fafd171995864cb1d058938"

# Sconto minimo per inviare la notifica su Discord (es. 1.0 = 1%)
PERCENTUALE_MINIMA_SCONTO = 1.0

# LISTA PRODOTTI TOP MAPPATI PER OGNI PAESE
PRODOTTI = [
    # --- CONSOLE & GAMING ---
    {
        "nome": "PlayStation 5 Slim Digital",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0CY5JFL4L"), "Germania 🇩🇪": ("amazon.de", "B0CLTF9723"), "Spagna 🇪🇸": ("amazon.es", "B0CY5JFL4L"), "Francia 🇫🇷": ("amazon.fr", "B0CY5JFL4L"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0CY5JFL4L")}
    },
    {
        "nome": "PlayStation 5 Slim Standard",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0C9R4K6LN"), "Germania 🇩🇪": ("amazon.de", "B0C9R4K6LN"), "Spagna 🇪🇸": ("amazon.es", "B0C9R4K6LN"), "Francia 🇫🇷": ("amazon.fr", "B0C9R4K6LN"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0C9R4K6LN")}
    },
    {
        "nome": "DualSense Controller PS5 White",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B08H99BPJN"), "Germania 🇩🇪": ("amazon.de", "B08H99BPJN"), "Spagna 🇪🇸": ("amazon.es", "B08H99BPJN"), "Francia 🇫🇷": ("amazon.fr", "B08H99BPJN"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B08H99BPJN")}
    },
    {
        "nome": "Nintendo Switch OLED",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B07VGRJ29K"), "Germania 🇩🇪": ("amazon.de", "B07VGRJ29K"), "Spagna 🇪🇸": ("amazon.es", "B07VGRJ29K"), "Francia 🇫🇷": ("amazon.fr", "B07VGRJ29K"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B07VGRJ29K")}
    },
    {
        "nome": "Xbox Series X 1TB",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09B29LL14"), "Germania 🇩🇪": ("amazon.de", "B09B29LL14"), "Spagna 🇪🇸": ("amazon.es", "B09B29LL14"), "Francia 🇫🇷": ("amazon.fr", "B09B29LL14"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B09B29LL14")}
    },
    {
        "nome": "Xbox Series S 512GB",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B087VM5XC6"), "Germania 🇩🇪": ("amazon.de", "B087VM5XC6"), "Spagna 🇪🇸": ("amazon.es", "B087VM5XC6"), "Francia 🇫🇷": ("amazon.fr", "B087VM5XC6"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B087VM5XC6")}
    },
    {
        "nome": "Meta Quest 3 128GB",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0B8C3X7S4"), "Germania 🇩🇪": ("amazon.de", "B0B8C3X7S4"), "Spagna 🇪🇸": ("amazon.es", "B0B8C3X7S4"), "Francia 🇫🇷": ("amazon.fr", "B0B8C3X7S4"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0B8C3X7S4")}
    },
    {
        "nome": "ASUS ROG Ally Z1 Extreme",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0CFRYRN1N"), "Germania 🇩🇪": ("amazon.de", "B0CFRYRN1N"), "Spagna 🇪🇸": ("amazon.es", "B0CFRYRN1N"), "Francia 🇫🇷": ("amazon.fr", "B0CFRYRN1N"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0CFRYRN1N")}
    },

    # --- TELEFONIA & AUDIO ---
    {
        "nome": "Apple AirPods Pro (2ª Gen)",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09G9F5C1R"), "Germania 🇩🇪": ("amazon.de", "B09G9F5C1R"), "Spagna 🇪🇸": ("amazon.es", "B09G9F5C1R"), "Francia 🇫🇷": ("amazon.fr", "B09G9F5C1R"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B09G9F5C1R")}
    },
    {
        "nome": "Apple AirPods 3ª Generazione",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0CHWXZB18"), "Germania 🇩🇪": ("amazon.de", "B0CHWXZB18"), "Spagna 🇪🇸": ("amazon.es", "B0CHWXZB18"), "Francia 🇫🇷": ("amazon.fr", "B0CHWXZB18"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0CHWXZB18")}
    },
    {
        "nome": "Apple iPhone 15 128GB",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0CHWZCY47"), "Germania 🇩🇪": ("amazon.de", "B0CHWZCY47"), "Spagna 🇪🇸": ("amazon.es", "B0CHWZCY47"), "Francia 🇫🇷": ("amazon.fr", "B0CHWZCY47"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0CHWZCY47")}
    },
    {
        "nome": "Apple iPhone 15 Pro Max 256GB",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0CHX281Y3"), "Germania 🇩🇪": ("amazon.de", "B0CHX281Y3"), "Spagna 🇪🇸": ("amazon.es", "B0CHX281Y3"), "Francia 🇫🇷": ("amazon.fr", "B0CHX281Y3"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0CHX281Y3")}
    },
    {
        "nome": "Samsung Galaxy S24 Ultra",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0CTM2S44C"), "Germania 🇩🇪": ("amazon.de", "B0CTM2S44C"), "Spagna 🇪🇸": ("amazon.es", "B0CTM2S44C"), "Francia 🇫🇷": ("amazon.fr", "B0CTM2S44C"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0CTM2S44C")}
    },
    {
        "nome": "Samsung Galaxy A55 5G",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0C43D5Q4S"), "Germania 🇩🇪": ("amazon.de", "B0C43D5Q4S"), "Spagna 🇪🇸": ("amazon.es", "B0C43D5Q4S"), "Francia 🇫🇷": ("amazon.fr", "B0C43D5Q4S"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0C43D5Q4S")}
    },
    {
        "nome": "Xiaomi Redmi Note 13 5G",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0B8R4J985"), "Germania 🇩🇪": ("amazon.de", "B0B8R4J985"), "Spagna 🇪🇸": ("amazon.es", "B0B8R4J985"), "Francia 🇫🇷": ("amazon.fr", "B0B8R4J985"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0B8R4J985")}
    },
    {
        "nome": "Sony WH-1000XM5 Cuffie BT",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09JR837S7"), "Germania 🇩🇪": ("amazon.de", "B09JR837S7"), "Spagna 🇪🇸": ("amazon.es", "B09JR837S7"), "Francia 🇫🇷": ("amazon.fr", "B09JR837S7"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B09JR837S7")}
    },
    {
        "nome": "JBL Flip 6 Cassa Bluetooth",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09G98CH98"), "Germania 🇩🇪": ("amazon.de", "B09G98CH98"), "Spagna 🇪🇸": ("amazon.es", "B09G98CH98"), "Francia 🇫🇷": ("amazon.fr", "B09G98CH98"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B09G98CH98")}
    },

    # --- INFORMATICA & TABLET ---
    {
        "nome": "Apple MacBook Air M1",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B08N5N6RSS"), "Germania 🇩🇪": ("amazon.de", "B08N5N6RSS"), "Spagna 🇪🇸": ("amazon.es", "B08N5N6RSS"), "Francia 🇫🇷": ("amazon.fr", "B08N5N6RSS")}
    },
    {
        "nome": "Apple MacBook Air M3",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0CX2542LN"), "Germania 🇩🇪": ("amazon.de", "B0CX2542LN"), "Spagna 🇪🇸": ("amazon.es", "B0CX2542LN"), "Francia 🇫🇷": ("amazon.fr", "B0CX2542LN")}
    },
    {
        "nome": "Apple iPad 10.9 (10ª Gen)",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09G936L71"), "Germania 🇩🇪": ("amazon.de", "B09G936L71"), "Spagna 🇪🇸": ("amazon.es", "B09G936L71"), "Francia 🇫🇷": ("amazon.fr", "B09G936L71"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B09G936L71")}
    },
    {
        "nome": "Apple iPad Pro 11",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09G3HQ181"), "Germania 🇩🇪": ("amazon.de", "B09G3HQ181"), "Spagna 🇪🇸": ("amazon.es", "B09G3HQ181"), "Francia 🇫🇷": ("amazon.fr", "B09G3HQ181"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B09G3HQ181")}
    },
    {
        "nome": "Samsung Galaxy Tab A9+",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0CX23H2T9"), "Germania 🇩🇪": ("amazon.de", "B0CX23H2T9"), "Spagna 🇪🇸": ("amazon.es", "B0CX23H2T9"), "Francia 🇫🇷": ("amazon.fr", "B0CX23H2T9"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0CX23H2T9")}
    },
    {
        "nome": "HP Laptop 15s Intel i5",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0B13CK1R9"), "Germania 🇩🇪": ("amazon.de", "B0B13CK1R9"), "Spagna 🇪🇸": ("amazon.es", "B0B13CK1R9"), "Francia 🇫🇷": ("amazon.fr", "B0B13CK1R9")}
    },
    {
        "nome": "Lenovo IdeaPad Slim 3",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09H2281S6"), "Germania 🇩🇪": ("amazon.de", "B09H2281S6"), "Spagna 🇪🇸": ("amazon.es", "B09H2281S6"), "Francia 🇫🇷": ("amazon.fr", "B09H2281S6")}
    },
    {
        "nome": "Samsung Monitor Gaming Odyssey G3",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B088T25M5U"), "Germania 🇩🇪": ("amazon.de", "B088T25M5U"), "Spagna 🇪🇸": ("amazon.es", "B088T25M5U"), "Francia 🇫🇷": ("amazon.fr", "B088T25M5U"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B088T25M5U")}
    },
    {
        "nome": "Logitech MX Master 3S Mouse",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B093TK9WMB"), "Germania 🇩🇪": ("amazon.de", "B093TK9WMB"), "Spagna 🇪🇸": ("amazon.es", "B093TK9WMB"), "Francia 🇫🇷": ("amazon.fr", "B093TK9WMB"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B093TK9WMB")}
    },
    {
        "nome": "SSD Interno Samsung 980 Pro 1TB",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B07XH33M6C"), "Germania 🇩🇪": ("amazon.de", "B07XH33M6C"), "Spagna 🇪🇸": ("amazon.es", "B07XH33M6C"), "Francia 🇫🇷": ("amazon.fr", "B07XH33M6C"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B07XH33M6C")}
    },

    # --- SMARTWATCH & WEARABLE ---
    {
        "nome": "Apple Watch Series 9 GPS 41mm",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0CHX6Y141"), "Germania 🇩🇪": ("amazon.de", "B0CHX6Y141"), "Spagna 🇪🇸": ("amazon.es", "B0CHX6Y141"), "Francia 🇫🇷": ("amazon.fr", "B0CHX6Y141"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0CHX6Y141")}
    },
    {
        "nome": "Samsung Galaxy Watch 6",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0C7LDKT13"), "Germania 🇩🇪": ("amazon.de", "B0C7LDKT13"), "Spagna 🇪🇸": ("amazon.es", "B0C7LDKT13"), "Francia 🇫🇷": ("amazon.fr", "B0C7LDKT13"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0C7LDKT13")}
    },
    {
        "nome": "Garmin Forerunner 55",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09G9F64P6"), "Germania 🇩🇪": ("amazon.de", "B09G9F64P6"), "Spagna 🇪🇸": ("amazon.es", "B09G9F64P6"), "Francia 🇫🇷": ("amazon.fr", "B09G9F64P6"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B09G9F64P6")}
    },
    {
        "nome": "Xiaomi Smart Band 8",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0C9RMZ3K2"), "Germania 🇩🇪": ("amazon.de", "B0C9RMZ3K2"), "Spagna 🇪🇸": ("amazon.es", "B0C9RMZ3K2"), "Francia 🇫🇷": ("amazon.fr", "B0C9RMZ3K2"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0C9RMZ3K2")}
    },

    # --- ELETTRODOMESTICI & CASA ---
    {
        "nome": "Dyson V15 Detect Extra",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0BDK6Z6X8"), "Germania 🇩🇪": ("amazon.de", "B0BDK6Z6X8"), "Spagna 🇪🇸": ("amazon.es", "B0BDK6Z6X8"), "Francia 🇫🇷": ("amazon.fr", "B0BDK6Z6X8")}
    },
    {
        "nome": "Cecotec Friggitrice ad Aria 5.5L",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B08K3H6D8M"), "Germania 🇩🇪": ("amazon.de", "B08K3H6D8M"), "Spagna 🇪🇸": ("amazon.es", "B08K3H6D8M"), "Francia 🇫🇷": ("amazon.fr", "B08K3H6D8M")}
    },
    {
        "nome": "Philips Airfryer XXL",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B01D9DGA56"), "Germania 🇩🇪": ("amazon.de", "B01D9DGA56"), "Spagna 🇪🇸": ("amazon.es", "B01D9DGA56"), "Francia 🇫🇷": ("amazon.fr", "B01D9DGA56")}
    },
    {
        "nome": "iRobot Roomba 692",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B094R3NMS3"), "Germania 🇩🇪": ("amazon.de", "B094R3NMS3"), "Spagna 🇪🇸": ("amazon.es", "B094R3NMS3"), "Francia 🇫🇷": ("amazon.fr", "B094R3NMS3")}
    },
    {
        "nome": "Dreame L10s Ultra Robot",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09JS3G8W1"), "Germania 🇩🇪": ("amazon.de", "B09JS3G8W1"), "Spagna 🇪🇸": ("amazon.es", "B09JS3G8W1"), "Francia 🇫🇷": ("amazon.fr", "B09JS3G8W1")}
    },
    {
        "nome": "De'Longhi Magnifica S Macchina Caffe",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B084G2938Y"), "Germania 🇩🇪": ("amazon.de", "B084G2938Y"), "Spagna 🇪🇸": ("amazon.es", "B084G2938Y"), "Francia 🇫🇷": ("amazon.fr", "B084G2938Y")}
    },

    # --- TV & SOUNDBAR & DOMOTICA ---
    {
        "nome": "Fire TV Stick 4K Max",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09339C9Z4"), "Germania 🇩🇪": ("amazon.de", "B09339C9Z4"), "Spagna 🇪🇸": ("amazon.es", "B09339C9Z4"), "Francia 🇫🇷": ("amazon.fr", "B09339C9Z4"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B09339C9Z4")}
    },
    {
        "nome": "Echo Dot 5ª Generazione",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09B2C4Z6N"), "Germania 🇩🇪": ("amazon.de", "B09B2C4Z6N"), "Spagna 🇪🇸": ("amazon.es", "B09B2C4Z6N"), "Francia 🇫🇷": ("amazon.fr", "B09B2C4Z6N"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B09B2C4Z6N")}
    },
    {
        "nome": "Echo Show 8 Smart Display",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B09B2X23Y2"), "Germania 🇩🇪": ("amazon.de", "B09B2X23Y2"), "Spagna 🇪🇸": ("amazon.es", "B09B2X23Y2"), "Francia 🇫🇷": ("amazon.fr", "B09B2X23Y2"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B09B2X23Y2")}
    },
    {
        "nome": "LG OLED TV 55 C3/C4",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0C39R5Y32"), "Germania 🇩🇪": ("amazon.de", "B0C39R5Y32"), "Spagna 🇪🇸": ("amazon.es", "B0C39R5Y32"), "Francia 🇫🇷": ("amazon.fr", "B0C39R5Y32")}
    },
    {
        "nome": "Samsung TV 55 Crystal UHD",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0C34B8K3M"), "Germania 🇩🇪": ("amazon.de", "B0C34B8K3M"), "Spagna 🇪🇸": ("amazon.es", "B0C34B8K3M"), "Francia 🇫🇷": ("amazon.fr", "B0C34B8K3M")}
    },
    {
        "nome": "Bose Smart Soundbar 600",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0942N6N1F"), "Germania 🇩🇪": ("amazon.de", "B0942N6N1F"), "Spagna 🇪🇸": ("amazon.es", "B0942N6N1F"), "Francia 🇫🇷": ("amazon.fr", "B0942N6N1F"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0942N6N1F")}
    },

    # --- ACCESSORI & SPORT ---
    {
        "nome": "Orologio Casio Vintage Digital",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B002K88062"), "Germania 🇩🇪": ("amazon.de", "B002K88062"), "Spagna 🇪🇸": ("amazon.es", "B002K88062"), "Francia 🇫🇷": ("amazon.fr", "B002K88062"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B002K88062")}
    },
    {
        "nome": "Orologio Tommy Hilfiger Cronografo",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B0833Z412B"), "Germania 🇩🇪": ("amazon.de", "B0833Z412B"), "Spagna 🇪🇸": ("amazon.es", "B0833Z412B"), "Francia 🇫🇷": ("amazon.fr", "B0833Z412B"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B0833Z412B")}
    },
    {
        "nome": "Avviatore Emergenza Auto Powerbank",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B07P88H32P"), "Germania 🇩🇪": ("amazon.de", "B07P88H32P"), "Spagna 🇪🇸": ("amazon.es", "B07P88H32P"), "Francia 🇫🇷": ("amazon.fr", "B07P88H32P")}
    },
    {
        "nome": "Compressore Portatile Elettrico",
        "asins": {"Italia 🇮🇹": ("amazon.it", "B07S7XJ9F2"), "Germania 🇩🇪": ("amazon.de", "B07S7XJ9F2"), "Spagna 🇪🇸": ("amazon.es", "B07S7XJ9F2"), "Francia 🇫🇷": ("amazon.fr", "B07S7XJ9F2"), "Regno Unito 🇬🇧": ("amazon.co.uk", "B07S7XJ9F2")}
    }
]

# Web Server interno per Keep-Alive su Render
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot Amazon Europe 45 Top Products Attivo!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()

def start_health_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

def invia_notifica_discord(nome, paese, prezzo_attuale, prezzo_listino, percentuale_sconto, url):
    simbolo_valuta = "£" if "UK" in paese or "Regno Unito" in paese else "€"
    payload = {
        "content": f"@everyone 🚨 OFFERTA RILEVATA su {paese} (-{percentuale_sconto:.0f}%)! 🚨",
        "embeds": [
            {
                "title": f"📦 {nome} ({paese})",
                "description": f"Il prezzo è sceso del {percentuale_sconto:.1f}% su Amazon!",
                "url": url,
                "color": 3066993,
                "fields": [
                    {"name": "🌍 Store", "value": f"{paese}", "inline": True},
                    {"name": "🔥 Prezzo Scontato", "value": f"{prezzo_attuale:.2f} {simbolo_valuta}", "inline": True},
                    {"name": "❌ Prezzo Listino", "value": f"{prezzo_listino:.2f} {simbolo_valuta}", "inline": True},
                    {"name": "📉 Sconto Rilevato", "value": f"-{percentuale_sconto:.0f}%", "inline": True},
                    {"name": "🛒 Link Acquisto", "value": f"[Apri prodotto su {paese}]({url})", "inline": False}
                ],
                "footer": {"text": "Amazon Europe Price Tracker Bot"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        ]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        print(f"✅ Notifica inviata su Discord per {nome} ({paese})", flush=True)
    except Exception as e:
        print(f"❌ Errore invio Discord: {e}", flush=True)

def estrai_dati_prezzo(soup):
    try:
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

        elem_solo_prezzo = soup.select_one("span.a-price span.a-offscreen")
        if elem_solo_prezzo:
            match_sp = re.search(r'([0-9]+[\.,][0-9]+)', elem_solo_prezzo.get_text().strip())
            if match_sp:
                prezzo_attuale = float(match_sp.group(1).replace('.', '').replace(',', '.'))
                return prezzo_attuale, prezzo_attuale, 0.0

    except Exception:
        pass
        
    return None, None, 0.0

def controlla_prezzi():
    while True:
        print(f"\n--- Inizio ciclo di controllo ({time.strftime('%H:%M:%S')}) ---", flush=True)
        for prod in PRODOTTI:
            for paese, (domain, asin) in prod["asins"].items():
                url = f"https://www.{domain}/dp/{asin}"
                
                # Utilizzo di ScraperAPI per aggirare i blocchi e i captcha di Amazon
                scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"

                try:
                    r = requests.get(scraper_url, timeout=30)
                    
                    if r.status_code == 404:
                        print(f"⚠️ [{paese}] Risposta: 404 (ASIN {asin} non trovato)", flush=True)
                        continue
                    elif r.status_code != 200:
                        print(f"🚫 [{paese}] Errore HTTP {r.status_code} da ScraperAPI", flush=True)
                        continue

                    soup = BeautifulSoup(r.content, "html.parser")
                    p_attuale, p_listino, sconto = estrai_dati_prezzo(soup)

                    if p_attuale:
                        if sconto >= PERCENTUALE_MINIMA_SCONTO:
                            print(f"🔥 [{paese}] {prod['nome']} -> Prezzo: {p_attuale:.2f}€ | Listino: {p_listino:.2f}€ | SCONTO: {sconto:.1f}%", flush=True)
                            invia_notifica_discord(prod['nome'], paese, p_attuale, p_listino, sconto, url)
                        else:
                            print(f"ℹ️ [{paese}] {prod['nome']} -> Prezzo: {p_attuale:.2f}€ (Nessuno sconto o inferiore a {PERCENTUALE_MINIMA_SCONTO}%)", flush=True)
                    else:
                        print(f"❌ [{paese}] {prod['nome']} -> Impossibile leggere il prezzo (Tag non presente)", flush=True)

                except Exception as e:
                    print(f"❌ [{paese}] Errore durante il controllo di {prod['nome']}: {e}", flush=True)

                time.sleep(random.uniform(2, 4))

        print(f"\n--- Scansione completata! Attesa di 3 minuti prima del prossimo ciclo... ---", flush=True)
        time.sleep(180)

if __name__ == "__main__":
    threading.Thread(target=start_health_server, daemon=True).start()
    controlla_prezzi()

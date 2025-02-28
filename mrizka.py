import random
import json
from flask import Flask, jsonify, render_template, request, Response
import requests
from bs4 import BeautifulSoup
import re
import logging
from urllib.parse import quote

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename="app_errors.log", level=logging.ERROR)

# Načtení slov ze souboru JSON
with open('slova.json', 'r', encoding='utf-8') as f:
    slova = json.load(f)

# Česká abeceda s diakritikou
ceska_abeceda = "aábcčdďeéěfghiíjklmnňoópqrřsštťuúůvwxyýzž"

# Cache for word meanings
meaning_cache = {}

def vytvor_mrizku(velikost, pocet_slov):
    # Omezení délky slov pro malou mřížku 10x10
    if velikost == 10:
        slova_filtr = [slovo for slovo in slova if 2 <= len(slovo) <= 5]  # Slova 2–5 písmen
    else:
        slova_filtr = slova  # Pro větší mřížky žádné omezení

    vybrana_slova = random.sample(slova_filtr, min(pocet_slov, len(slova_filtr)))
    mrizka = [[' ' for _ in range(velikost)] for _ in range(velikost)]
    smer = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    pozice_slov = {}

    def lze_umistit(slovo, radek, sloupec, smer_r, smer_s):
        delka = len(slovo)
        for i in range(delka):
            novy_radek = radek + i * smer_r
            novy_sloupec = sloupec + i * smer_s
            if (novy_radek < 0 or novy_radek >= velikost or 
                novy_sloupec < 0 or novy_sloupec >= velikost or 
                (mrizka[novy_radek][novy_sloupec] != ' ' and mrizka[novy_radek][novy_sloupec] != slovo[i])):
                return False
        return True
    
    def umisti_slovo(slovo, radek, sloupec, smer_r, smer_s):
        pozice = []
        for i in range(len(slovo)):
            novy_radek = radek + i * smer_r
            novy_sloupec = sloupec + i * smer_s
            mrizka[novy_radek][novy_sloupec] = slovo[i]
            pozice.append([novy_radek, novy_sloupec])
        pozice_slov[slovo] = pozice
    
    for slovo in vybrana_slova:
        umisteno = False
        pokusy = 0
        while not umisteno and pokusy < 100:
            smer_r, smer_s = random.choice(smer)
            radek = random.randint(0, velikost - 1)
            sloupec = random.randint(0, velikost - 1)
            if lze_umistit(slovo, radek, sloupec, smer_r, smer_s):
                umisti_slovo(slovo, radek, sloupec, smer_r, smer_s)
                umisteno = True
            pokusy += 1
    
    for i in range(velikost):
        for j in range(velikost):
            if mrizka[i][j] == ' ':
                mrizka[i][j] = random.choice(ceska_abeceda)
    
    return {"mrizka": mrizka, "slova": vybrana_slova, "pozice": pozice_slov}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mrizka')
def get_mrizka():
    velikosti = [10, 15, 20, 25, 30, 40, 50]
    game_mode = request.args.get('mode', 'normal')
    
    if game_mode == 'speed':
        pocet_slov_range = range(5, 31)  # Allow up to 30 words for speed mode
    else:
        pocet_slov_range = range(5, 16)  # Original range for normal mode
        
    velikost = int(request.args.get('velikost', 10))
    pocet_slov = int(request.args.get('pocet_slov', 5))
    velikost = min(max(velikost, min(velikosti)), max(velikosti))
    pocet_slov = min(max(pocet_slov, min(pocet_slov_range)), max(pocet_slov_range))
    data = vytvor_mrizku(velikost, pocet_slov)
    return jsonify(data)

def fetch_meaning_sync(word):
    """Synchronous function to fetch the meaning of a word using regular requests"""
    try:
        logging.info(f"Attempting to fetch meaning for word: {word}")
        encoded_word = quote(word)
        url = f"https://www.nechybujte.cz/slovnik-soucasne-cestiny/{encoded_word}"
        
        # Use regular requests library instead of asyncio
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            logging.info("Content retrieved successfully")
            soup = BeautifulSoup(response.text, 'html.parser')
            meaning_span = soup.select_one('span.ssc_desc1.w')
            
            if meaning_span:
                meaning_text = meaning_span.get_text(separator=" ", strip=True)
                meaning_text = re.sub(r'\s+', ' ', meaning_text).strip()
                logging.info(f"Meaning found for {word}: {meaning_text}")
                return meaning_text
            else:
                logging.warning(f"No meaning span found for {word}")
                return "Význam nenalezen"
        else:
            logging.warning(f"Failed to fetch URL: {response.status_code}")
            return "Failed to fetch meaning"
    except Exception as e:
        logging.error(f"Error fetching meaning for {word}: {e}")
        return f"Error: {e}"

@app.route('/meaning')
def get_meaning():
    word = request.args.get('word', '')
    if not word:
        return "Word not provided", 400
    
    # Check if meaning is already in cache
    if word in meaning_cache:
        return Response(meaning_cache[word], mimetype='text/plain')
    
    try:
        # Use synchronous function instead of asyncio
        meaning = fetch_meaning_sync(word)
        
        # Store result in cache
        meaning_cache[word] = meaning
        
        return Response(meaning, mimetype='text/plain')
    except Exception as e:
        logging.error(f"Error in get_meaning for {word}: {e}")
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
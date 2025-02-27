import random
import json
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Načtení slov ze souboru JSON
with open('slova.json', 'r', encoding='utf-8') as f:
    slova = json.load(f)

# Česká abeceda s diakritikou
ceska_abeceda = "aábcčdďeéěfghiíjklmnňoópqrřsštťuúůvwxyýzž"

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
    pocet_slov_range = range(5, 16)
    velikost = int(request.args.get('velikost', 10))
    pocet_slov = int(request.args.get('pocet_slov', 5))
    velikost = min(max(velikost, min(velikosti)), max(velikosti))
    pocet_slov = min(max(pocet_slov, min(pocet_slov_range)), max(pocet_slov_range))
    data = vytvor_mrizku(velikost, pocet_slov)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
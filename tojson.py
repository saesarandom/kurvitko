
import json

# Načtení slov z CSV souboru (první sloupec = slovo, ignorujeme frekvenci)
slova = []
with open('slova.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():  # Přeskočí prázdné řádky
            slovo = line.split()[0].strip()  # Vezme první slovo na řádku (ignoruje frekvenci, pokud je)
            if slovo and slovo.isalpha():  # Filtrujeme pouze písmena (žádné čísla, speciální znaky)
                slova.append(slovo)

# Omezíme na unikátní slova a odstraníme duplikáty
slova = list(dict.fromkeys(slova))  # Zachová pořadí, odstraní duplikáty

# Uložení do JSON
with open('slova.json', 'w', encoding='utf-8') as f:
    json.dump(slova, f, ensure_ascii=False, indent=2)

print(f"Převedeno {len(slova)} unikátních slov do slova.json")
from crawl4ai import Crawler
import json

# Initialize the crawler
crawler = Crawler()

# Crawl a dictionary page for a word (e.g., "příjezdový")
result = crawler.crawl("https://www.nechybujte.cz/slovnik-soucasne-cestiny/nápor")

# Extract the meaning using a CSS selector (adjust based on the website’s structure)
meaning = result.extract_text(".definition")

print(f"Meaning of 'příjezdový': {meaning}")

# Cache meaning
cache = {}
with open("word_meanings.json", "r", encoding="utf-8") as f:
    cache = json.load(f) if f.readable() else {}

cache["příjezdový"] = meaning

# Save to file
with open("word_meanings.json", "w", encoding="utf-8") as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)
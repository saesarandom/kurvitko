import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        try:
            result = await crawler.arun(
                url="https://www.nechybujte.cz/slovnik-soucasne-cestiny/nápor",
            )
            # Use extract_text with a CSS selector to get the content
            meaning = result.extract_text("span.ssc_desc1.w")  # Target the span with the meaning
            if meaning:
                # Split the text into words (assuming <w> tags are rendered as space-separated text)
                words = [word.strip() for word in meaning.split() if word.strip()]
                # Join words, preserving commas and cleaning up
                meaning_text = " ".join(words).replace(" ,", ",").replace("  ", " ").strip()
                print(meaning_text)
            else:
                print("Meaning not found. Check the CSS selector or URL.")
        except Exception as e:
            print(f"Error crawling: {e}")

if __name__ == "__main__":
    asyncio.run(main())
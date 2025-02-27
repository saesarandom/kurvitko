import asyncio
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import re

async def main():
    async with AsyncWebCrawler() as crawler:
        try:
            # Crawl the URL
            result = await crawler.arun(
                url="https://www.nechybujte.cz/slovnik-soucasne-cestiny/upír",
            )
            # Try to access HTML content (fallback to markdown if html isn’t available)
            content = getattr(result, 'html', result.markdown)
            if content:
                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                # Find the span with class "ssc_desc1 w"
                meaning_span = soup.select_one('span.ssc_desc1.w')
                if meaning_span:
                    # Get all text content within the span, preserving commas and spaces
                    # Use get_text() with separator to maintain structure
                    meaning_text = meaning_span.get_text(separator=" ", strip=True)
                    # Clean up extra spaces but preserve commas
                    meaning_text = re.sub(r'\s+', ' ', meaning_text).strip()
                    print(meaning_text)
                else:
                    print("Meaning span not found. Check the CSS selector or HTML structure.")
            else:
                print("No content returned. Check the URL or crawler setup.")
        except Exception as e:
            print(f"Error crawling: {e}")

if __name__ == "__main__":
    asyncio.run(main())
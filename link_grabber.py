import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_product_links(url: str) -> list:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to URL
        await page.goto(url, wait_until="domcontentloaded")
        print(f"Final URL: {page.url}")

        # Wait for initial content
        await page.wait_for_selector('.product-tile', timeout=15000)

        # Scroll incrementally to avoid footer
        scroll_count = 0
        max_scrolls = 100
        last_count = 0
        same_count = 0
        scroll_step = 800  # Pixels to scroll each time
        
        while scroll_count < max_scrolls:
            # Get current product count before scrolling
            current_products = await page.query_selector_all('.product-tile')
            current_count = len(current_products)
            
            # Scroll incrementally (not to the very bottom)
            await page.evaluate(f"window.scrollBy(0, {scroll_step})")
            await asyncio.sleep(2.5)  # Increased wait time for loading
            
            # Check if new products loaded
            new_products = await page.query_selector_all('.product-tile')
            new_count = len(new_products)
            
            # Break conditions
            if new_count == current_count:
                same_count += 1
                if same_count >= 4:  # Break if no new products after 4 scrolls
                    print("No new products detected. Stopping scroll.")
                    break
            else:
                same_count = 0
                print(f"Scroll {scroll_count+1}: Products increased from {current_count} to {new_count}")
            
            # Check if we've reached the footer
            is_at_bottom = await page.evaluate("""() => {
                return window.innerHeight + window.scrollY >= document.body.scrollHeight - 100
            }""")
            
            if is_at_bottom:
                print("Reached bottom of page. Stopping scroll.")
                break
                
            scroll_count += 1

        # Final product count
        final_products = await page.query_selector_all('.product-tile')
        print(f"\nTotal products loaded: {len(final_products)}")

        # Get HTML and parse
        content = await page.content()
        await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        product_links = []
        
        for link in soup.select('a[href^="/products/"]'):
            href = link["href"]
            # Skip non-product links
            if "/products/" not in href or "/products/c" in href:
                continue
                
            full_url = f"https://www.coach.com{href}"
            if full_url not in product_links:
                product_links.append(full_url)
                
        return product_links

# if __name__ == "__main__":
#     target_url = "https://www.coach.com/shop/women/view-all"
#     links = asyncio.run(scrape_product_links(target_url))
    
#     print(f"\nFound {len(links)} unique product links:")
#     for link in links:
#         print(link)
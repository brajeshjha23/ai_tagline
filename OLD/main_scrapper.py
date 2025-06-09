import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import pandas as pd
from typing import List, Dict
import uuid
import os
from link_grabber import scrape_product_links

async def scrape_and_extract_details(url: str, output_dir: str) -> Dict:
    """
    Launches a headless browser, navigates to the given URL, waits for 5 seconds,
    saves the HTML content to a file, and extracts product details, images, and reviews using BeautifulSoup.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(url)

            # Wait for the page to fully load
            await asyncio.sleep(9)

            # Get the HTML content
            content = await page.content()

            # Generate unique filename for HTML
            html_filename = f"scraped_page_{uuid.uuid4().hex}.html"
            html_filepath = os.path.join(output_dir, html_filename)
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Save to file
            with open(html_filepath, "w", encoding="utf-8") as f:
                f.write(content)

            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")

            await browser.close()

            details_container = soup.find('div', id='description2')
            product_details = {"url": url}

            product_name_tag = soup.find('h3', {'data-qa': 'pdp_txt_pdt_title'})
            if product_name_tag:
                product_details['product_name'] = product_name_tag.get_text(strip=True)
            else:
                product_details['product_name'] = None  # or use "N/A"

            # Extract product price
            price_tag = soup.find('span', {'data-qa': 'cm_txt_pdt_price'})
            if price_tag:
                product_details['price'] = price_tag.get_text(strip=True)
            else:
                product_details['price'] = None  # or use "N/A"

            if not details_container:
                print(f"Product details section not found for {url}")
                return product_details

            # Extract detail sections (e.g., Size, Materials)
            for section in details_container.find_all('div', class_='product-props__details'):
                header_tag = section.find('h2')
                if not header_tag:
                    continue
                header = header_tag.get_text(strip=True)
                items = [li.get_text(strip=True) for li in section.find_all('li')]
                product_details[header] = items

            # Extract Editor's Notes
            editor_section = details_container.find_next_sibling('div', class_='css-xc41pm')
            if editor_section:
                notes_div = editor_section.find('div', class_='css-1r44snt')
                if notes_div:
                    notes = notes_div.get_text(strip=True)
                    product_details["Editor's Notes"] = notes

            # Extract image URLs from splide container
            splide_container = soup.find('div', class_='css-8h57m5')
            if splide_container:
                img_tags = splide_container.find_all('img', class_='chakra-image css-boil6')
                image_urls = list(set(img.get('src') for img in img_tags if img.get('src')))
                product_details["Images"] = image_urls
            else:
                print(f"Splide image container not found for {url}")
                product_details["Images"] = []

            # Extract overall reviews
            overall_reviews_div = soup.find('div', class_='css-1vjihxg')
            if overall_reviews_div:
                rating_div = overall_reviews_div.find('div', class_='css-vnjdh5')
                overall_rating = rating_div.get_text(strip=True).split()[0] if rating_div else None

                reviews_count_div = overall_reviews_div.find('div', class_='css-1tx6eu7')
                number_of_reviews = reviews_count_div.get_text(strip=True).split()[0] if reviews_count_div else None
            else:
                overall_rating = None
                number_of_reviews = None

            # Extract individual reviews
            review_items = soup.find_all('div', class_='review-list-item css-cxd8co')
            individual_reviews = []

            for review_item in review_items:
                # Extract reviewer's name and date
                user_info_div = review_item.find('div', class_='review-list-item-user-info css-aqx73m')
                if user_info_div:
                    user_info_text = user_info_div.get_text(strip=True)
                    try:
                        name, date = user_info_text.split(', ', 1)
                    except ValueError:
                        name = user_info_text
                        date = None
                else:
                    name = None
                    date = None

                # Extract rating from stars
                stars_div = review_item.find('div', class_='chakra-stack css-16yi24e')
                if stars_div:
                    full_stars = stars_div.find_all('svg', {'data-qa': 'cm_icon_pt_rs_filled'})
                    half_stars = stars_div.find_all('svg', {'data-qa': 'cm_icon_pt_rs_half'})
                    rating = len(full_stars) + 0.5 * len(half_stars)
                else:
                    rating = None

                # Extract review title
                title_h5 = review_item.find('h5', class_='review-response-details-title css-1hbkifp')
                title = title_h5.get_text(strip=True) if title_h5 else None

                # Extract review description
                desc_div = review_item.find('div', class_='review-response-details-description show-less css-1a6nsdk')
                description = desc_div.get_text(strip=True) if desc_div else None

                # Extract recommendation
                recommend_div = review_item.find('div', class_='css-1ptaiic')
                if recommend_div:
                    recommend_text = recommend_div.get_text(strip=True)
                    try:
                        recommend = recommend_text.split(': ')[1]
                    except IndexError:
                        recommend = None
                else:
                    recommend = None

                # Extract helpfulness counts
                thumbs_up_span = review_item.find('span', {'data-qa': 'rnr_txt_likerevcount'})
                thumbs_up = int(thumbs_up_span.get_text(strip=True)) if thumbs_up_span else 0

                thumbs_down_span = review_item.find('span', {'data-qa': 'rnr_txt_dislikerevcount'})
                thumbs_down = int(thumbs_down_span.get_text(strip=True)) if thumbs_down_span else 0

                # Compile individual review
                review = {
                    "reviewer": name,
                    "date": date,
                    "rating": rating,
                    "title": title,
                    "description": description,
                    "recommend": recommend,
                    "thumbs_up": thumbs_up,
                    "thumbs_down": thumbs_down
                }
                individual_reviews.append(review)

            # Add reviews to product details
            product_details["Reviews"] = {
                "overall_rating": overall_rating,
                "number_of_reviews": number_of_reviews,
                "individual_reviews": individual_reviews
            }

            return product_details
    except Exception as e:
        print(f"Error Processing {url}: ",e)
        return {}
    
async def scrape_multiple_urls(urls: List[str], output_dir: str) -> List[Dict]:
    """
    Scrapes multiple URLs and returns a list of extracted product details.
    If scrape_and_extract_details returns an empty dict ({}), that result is skipped.
    """
    results = []
    for url in urls:
        print(f"Scraping {url}...")
        result = await scrape_and_extract_details(url, output_dir)
        # Only add to results if not an empty dict
        if result:
            results.append(result)
        else:
            print(f"Skipped {url} because scrape returned empty result.")
    return results


def save_to_excel(results: List[Dict], output_file: str):
    """
    Saves the scraped data to an Excel file, flattening nested structures
    and storing all individual reviews in one column (one row per product).
    """
    excel_data = []
    for result in results:
        # Base fields for this product
        row = {
            "URL": result.get("url", ""),
            "Editor's Notes": result.get("Editor's Notes", ""),
            "Images": ", ".join(result.get("Images", [])),
            "Overall Rating": result.get("Reviews", {}).get("overall_rating", ""),
            "Number of Reviews": result.get("Reviews", {}).get("number_of_reviews", "")
        }

        # Add other product-specific keys (e.g., Size, Materials, etc.)
        for key, value in result.items():
            if key not in ["url", "Editor's Notes", "Images", "Reviews"]:
                row[key] = ", ".join(value) if isinstance(value, list) else value

        # Aggregate all individual reviews into one string
        individual_reviews = result.get("Reviews", {}).get("individual_reviews", [])
        review_strings = []
        for review in individual_reviews:
            # Customize this formatting as needed
            reviewer = review.get("reviewer", "")
            date = review.get("date", "")
            rating = review.get("rating", "")
            title = review.get("title", "")
            description = review.get("description", "")
            recommend = review.get("recommend", "")
            thumbs_up = review.get("thumbs_up", 0)
            thumbs_down = review.get("thumbs_down", 0)

            # Example: combine fields into a single-line summary for each review
            single_review = (
                f"{reviewer} ({date}) rated {rating}:\n"
                f"Title: {title}\n"
                f"Description: {description}\n"
                f"Recommend: {recommend}, Thumbs Up: {thumbs_up}, Thumbs Down: {thumbs_down}"
            )
            review_strings.append(single_review)

        # Join all review summaries with a blank line between them
        row["All Reviews"] = "\n\n".join(review_strings)

        excel_data.append(row)

    # Create DataFrame and save to Excel
    df = pd.DataFrame(excel_data)
    df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")

def save_to_json(results: List[Dict], output_file: str):
    """
    Saves the scraped data to a JSON file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    # List of URLs to scrape
    target_urls = [
        "https://www.coach.com/products/tabby-shoulder-bag-20/CW917-LHCHK.html?rrec=true",
        "https://www.coach.com/products/tabby-shoulder-bag-20/CY201-B4%2FHA.html?rrec=true",
        "https://www.coach.com/products/soft-empire-carryall-bag-48/CW617-B4MER.html?rrec=true"
    ]

    # target_url = "https://www.coach.com/shop/women/view-all"
    # target_urls = asyncio.run(scrape_product_links(target_url))
    
    print(f"\nFound {len(target_urls)} unique product links:")
    target_urls = target_urls[:10]
    
    output_dir = "scraped_data"
    excel_output = "product_details.xlsx"
    json_output = "product_details.json"

    # Run the scraper
    extracted_data = asyncio.run(scrape_multiple_urls(target_urls, output_dir))

    # Save to Excel and JSON
    save_to_excel(extracted_data, excel_output)
    save_to_json(extracted_data, json_output)

    print("Extraction and saving complete.")
from image_details_extractor import generate_product_description
from tagline_generator import generate_luxury_tagline_from_json
import json
from typing import List, Dict
import pandas as pd


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
            "Number of Reviews": result.get("Reviews", {}).get("number_of_reviews", ""),
            # Newly added fields
            "Product Description": result.get("Product Description", ""),
            "Luxury Tagline": result.get("Luxury Tagline", "")
        }

        # Add other product-specific keys (e.g., Style Number, Measurements, Materials, etc.)
        for key, value in result.items():
            if key not in ["url", "Editor's Notes", "Images", "Reviews", "Product Description", "Luxury Tagline"]:
                if isinstance(value, list):
                    row[key] = ", ".join(value)
                elif isinstance(value, dict):
                    # Skip nested dicts (e.g., Reviews) since handled above
                    continue
                else:
                    row[key] = value

        # Aggregate all individual reviews into one string
        individual_reviews = result.get("Reviews", {}).get("individual_reviews", [])
        review_strings = []
        for review in individual_reviews:
            reviewer = review.get("reviewer", "")
            date = review.get("date", "")
            rating = review.get("rating", "")
            title = review.get("title", "")
            description = review.get("description", "")
            recommend = review.get("recommend", "")
            thumbs_up = review.get("thumbs_up", 0)
            thumbs_down = review.get("thumbs_down", 0)

            single_review = (
                f"{reviewer} ({date}) rated {rating}:\n"
                f"Title: {title}\n"
                f"Description: {description}\n"
                f"Recommend: {recommend}, Thumbs Up: {thumbs_up}, Thumbs Down: {thumbs_down}"
            )
            review_strings.append(single_review)

        row["All Reviews"] = "\n\n".join(review_strings)
        excel_data.append(row)

    df = pd.DataFrame(excel_data)
    df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")

def main():
    # 1. Load JSON file
    input_json_path = "Outputs\product_details_women_105.json"
    output_json_path = "Final_Output\output_105_women.json"
    output_excel_path = "Final_Output\output_105_women.xlsx"

    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. Iterate over each product in the JSON list
    for item in data:
        print(f"Processing: {item['url']}")
        images = item.get("Images", [])
        # Generate product description from images
        if images != []:
            product_description = generate_product_description(images)
        else:
            product_description = {}


        # Generate luxury tagline using the description and the full JSON object
        luxury_tagline = generate_luxury_tagline_from_json(product_description, item)
        item["Product Description"] = product_description
        item["Luxury Tagline"] = luxury_tagline
        print(f"Completed: {item['url']}")

    # 3. Save the updated JSON back to disk
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Updated JSON saved to {output_json_path}")

    # 4. Save the results (including Product Description and Luxury Tagline) to Excel
    save_to_excel(data, output_excel_path)

if __name__ == "__main__":
    main()



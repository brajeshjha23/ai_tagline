from openai import OpenAI
import os
from pathlib import Path
import json
import base64
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def generate_product_description(image_file_paths):
    """
    Given a list of image file paths or URLs, send multiple images to Mistral Pixtral-12B
    for a detailed product description in JSON format.
    """
    # Ensure input is a non-empty list
    assert isinstance(image_file_paths, list) and image_file_paths, "Provide a non-empty list of image paths or URLs"

    # Build the multimodal message content
    message_content = []
    for idx, image_path in enumerate(image_file_paths, start=1):
        # Detect if the path is a URL (starts with http:// or https://)
        if image_path.startswith("http://") or image_path.startswith("https://"):
            # Directly append the ImageURLChunk for remote URLs
            message_content.append({"type": "text", "text": f"Image {idx} (URL):"})
            message_content.append({"type": "image_url", "image_url": {"url": image_path}})
        else:
            # Treat as local file path: validate and Base64-encode
            image_file = Path(image_path)
            assert image_file.is_file(), f"Invalid image path: {image_path}"

            # Encode the image to Base64
            encoded_bytes = base64.b64encode(image_file.read_bytes())
            encoded_str = encoded_bytes.decode()
            base64_data_url = f"data:image/jpeg;base64,{encoded_str}"

            # Append labeled Base64-encoded image
            message_content.append({"type": "text", "text": f"Image {idx} (Local):"})
            message_content.append({"type": "image_url", "image_url": {"url": base64_data_url}})

    # Append a final TextChunk with instructions for description
    instruction_text = (
        "You are a luxury fashion product analyst. Based on the above images, "
        "provide a detailed JSON output that includes:\n"
        "1. Product name (if identifiable) or suggested generic name.\n"
        "2. Materials and fabrics with texture details.\n"
        "3. Aesthetic style, unique elements (e.g., modern minimalist, classic vintage).\n"
        "4. Color palette and design motifs.\n"
        "5. Possible brand heritage or historical influences if recognizable.\n"
        "6. Suggested use-case or styling recommendations.\n"
        "7. Any notable craftsmanship techniques visible.\n"
        "Format the output strictly as JSON with keys matching the above points and no extra commentary."
        "**Do not use the word 'logo','casual','handbag','modern'**"
    )
    message_content.append({"type": "text", "text": instruction_text})

    # Call to the Mistral Pixtral model
    try:
        chat_response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
    except Exception as e:
        print(f"⚠️ Skipped image due to error: {e}")
        return {}

    # Parse and save the JSON response
    response_dict = json.loads(chat_response.choices[0].message.content)

    # Persist the result to a file
    output_path = Path("image_analysis_output")
    output_path.mkdir(exist_ok=True)
    output_file = output_path / "product_description.json"
    with open(output_file, "w") as json_file:
        json.dump(response_dict, json_file, indent=4)

    return response_dict

# Example usage:
# if __name__ == "__main__":
#     images = [
#         "https://coach.scene7.com/is/image/Coach/cy201_b4bk_a0?$mobileProductV3$",
#         "https://coach.scene7.com/is/image/Coach/cy201_b4bk_a3?$mobileProductV3$",
#         "https://coach.scene7.com/is/image/Coach/en_US-ToroImg_FY25Tabby20Family_a101?$mobileProductV3$",
#         "https://coach.scene7.com/is/image/Coach/cy201_b4bk_a61?$mobileProductV3$",
#         "https://coach.scene7.com/is/image/Coach/cy201_b4bk_a8?$mobileProductV3$",
#         "https://coach.scene7.com/is/image/Coach/cy201_b4bk_a99?$mobileProductV3$",
#         "https://coach.scene7.com/is/image/Coach/cy201_b4bk_a5?$mobileProductV3$",
#     ]
#     description = generate_product_description(images)
#     print(json.dumps(description, indent=4))

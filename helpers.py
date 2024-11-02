import io
import base64
from typing import List
from PIL import Image
import re
from typing import List

## HELPERS
# Function to encode the image
# Function to encode image as base64 and resize to fit within 1024x1024
def encode_image_resized(file, max_size=(750, 750), colors=64):
    # Open the image and convert to RGB (or use original mode if necessary)
    image = Image.open(file).convert("RGB")
    # Resize the image to fit within max_size, preserving aspect ratio
    image.thumbnail(max_size, Image.ANTIALIAS)
    # Optionally reduce colors to save on data size
    image = image.convert("P", palette=Image.ADAPTIVE, colors=colors)
    # Save to a bytes buffer and encode as base64
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")



def process_files_with_descriptions(images_b64: List[str], instructions: List[str]):
    assert len(images_b64) == len(instructions), "Number of files and descriptions must match."
    
    # Build the list of JSON objects with 'description' and 'image' fields
    result = []
    for idx, description in enumerate(instructions):
        image_b64 = images_b64[idx]
        result.append({
            "description": description,
            "image": f"data:image/jpeg;base64,{image_b64}"
        })
    
    return result

def extract_images_from_markdown(content):
    """Extract base64 images from markdown content."""
    # Pattern to match full markdown image syntax with base64 data
    image_pattern = r'!\[(.*?)\]\((data:image\/[^;]+;base64,[^)]+)\)'
    matches = re.findall(image_pattern, content)
    
    if not matches:
        return []
        
    # Get the full markdown image syntax
    full_matches = []
    for match in re.finditer(image_pattern, content):
        full_matches.append(match.group(0))  # This gets the entire match
    
    return full_matches

def create_chat_messages(content, improve_text, base64_images):
    """Create the messages array for the OpenAI chat completion."""
    base_prompt = f"""Please improve the following markdown content according to this request: "{improve_text}"

Original Content:
{content}

Please maintain the markdown formatting and structure while making improvements. Consider:
1. Clarity and readability
2. Technical accuracy
3. Proper markdown syntax
4. Logical flow and organization
5. Integration with the provided images

Provide only the improved markdown content without any explanations or meta-commentary."""
    

    
    message_content =[

            {
                "role": "user",
                "content": [
                    {"type": "text", "text": base_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"{base64_images}" },
                    },
                ],
            }]

    
    return message_content
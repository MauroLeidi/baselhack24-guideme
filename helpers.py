import io
import base64
from typing import List
from PIL import Image

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
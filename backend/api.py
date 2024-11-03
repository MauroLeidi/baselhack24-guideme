import base64
import os
import shutil
import tempfile
from typing import List, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel

from bing import bing_search
from helpers import create_chat_messages, generateteVideofromimagesandaudio, process_files_with_descriptions, clean_descriptions
from openai_prompt import example
from schemas import ImproveTextRequest, Instruction, Instructions, SearchQuery, VideoRequest, VideoResponse
from PIL import Image
import io

# FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()


@app.get("/")
async def read_root():
    return {"message": "Welcome to the API"}


@app.post("/search")
async def search(query: SearchQuery):
    result = bing_search(query.query)
    return {"context": result}


@app.post("/improveText")
async def improve_text(request: ImproveTextRequest):
    description = request.description
    improve_text = request.improveText
    image = request.image

    if not description or not improve_text:
        raise HTTPException(status_code=400, detail="Missing content or improvement instructions")

    # Create messages for the API call
    messages = create_chat_messages(description, improve_text, image)
    

    client = OpenAI(
)
    # Call OpenAI API
    response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=messages,
    response_format=Instruction)

    json_str = response.choices[0].message.parsed
    print(json_str)
    # Access the list of instructions
    if json_str is None:
        raise HTTPException(status_code=400, detail="Failed to parse instructions from the response.")

    # Extract the improved content
    improved_content = json_str.page_instruction
    return {
        'improved_content': improved_content
    }


@app.post("/uploadfiles/")
async def uploadfiles(files: List[UploadFile] = File(...),additional_prompt: Optional[str] = Form(None)):
    """
    Upload multiple files and return their filenames and descriptions.

    Args:
        files (List[UploadFile]): List of files to be uploaded.
        additional_prompt (Optional[str]): Additional context to be included in the prompt.

    Returns:
        dict: A dictionary containing the filenames of the uploaded files and descriptions.
    """
    filenames = [file.filename for file in files]
    
    # Process uploaded files and convert them to base64
    images_b64 = []
    for file in files:
        content = await file.read()
        images_b64.append(base64.b64encode(content).decode("utf-8"))
    
    # Create a prompt for OpenAI using the filenames
    prompt =f"""I uploaded {len(filenames)} images. These images provide visual instructions for assembling an object. Please analyze each image carefully and generate a clear, concise set of assembly instructions. 
    For each image, provide the following description: Create a detailed instruction in Markdown format that describes what the user should do based on the visual information presented in the corresponding image. 
    Output Format: The response should be structured as a list, where each element is a string that contains the Markdown-formatted instruction for that particular image. IMPORTANT: 1 exact description per image. So the list should be of length {len(filenames)}. 
    
    An example is provided below:
    
    Input: 2 images of a paper airplane construction.
    Output: list of lenght = 2 containing the description of each step. eg: {example}


    Additional context that may be helpful: {additional_prompt}
    """

    print(prompt)

    
    client = OpenAI(
    )
    # Make a call to OpenAI's API to get a description
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png; base64,{images_b64}" },
                    },
                ],
            }
        
        ],
        response_format=Instructions,
    )

    json_str = response.choices[0].message.parsed

    # Access the list of instructions
    if json_str is None:
        raise HTTPException(status_code=400, detail="Failed to parse instructions from the response.")
    instructions = json_str.pages_instructions
    print(instructions)
    imgsWithDescr = process_files_with_descriptions(images_b64,instructions)
    return  imgsWithDescr


@app.post("/generate-video/")
async def generate_video(request: VideoRequest):
    """Generate a video and return it as base64 data URL."""

    
    output_dir = "./output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    temp_dir = os.path.join(output_dir, f"temp_{os.getpid()}")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    saved_files = []

    ## First, we enhance the descriptions using OpenAI
    cleaned_descriptions = clean_descriptions(request.descriptions)
    
    try:
        # Process and save each base64 image
        for idx, base64_str in enumerate(request.images):
            try:
                if ',' in base64_str:
                    base64_str = base64_str.split(',')[1]
                
                image_data = base64.b64decode(base64_str)
                image = Image.open(io.BytesIO(image_data))
                file_path = os.path.join(temp_dir, f"image_{idx}.png")
                image.save(file_path, 'PNG')
                saved_files.append(file_path)
                
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid base64 image at index {idx}: {str(e)}"
                )

        # Generate the video
        output_path = generateteVideofromimagesandaudio(
            pngs=saved_files,
            descriptions=cleaned_descriptions
        )

        # Convert video to base64
        if os.path.exists(output_path):
            with open(output_path, "rb") as video_file:
                video_base64 = base64.b64encode(video_file.read()).decode('utf-8')
                video_data_url = f"data:video/mp4;base64,{video_base64}"
                
            return VideoResponse(video=video_data_url)
        else:
            raise HTTPException(
                status_code=500,
                detail="Video generation failed - output file not found"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating video: {str(e)}"
        )
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(output_path):
            os.remove(output_path)

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
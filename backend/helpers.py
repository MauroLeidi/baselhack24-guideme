import io
import base64
from typing import List
from PIL import Image
import re
from typing import List

import os
from gtts import gTTS
from moviepy.editor import *
import tempfile
import cv2
from pydub import AudioSegment
import subprocess

## HELPERS
# Function to encode the image
# Function to encode image as base64 and resize to fit within max_sizexmax_size
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


# Reformat llm output for frontend
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

# Extract b64 images from string
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

# Some prompt engineering for content improvement requested by the user in the frontend
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


### VIDEO GENERATION

def create_video_from_images(images, durations, output_video_path):
    """Create a video from a list of images with corresponding display durations.

    Args:
        images (list of str): List of file paths to images.
        durations (list of float): List of durations (in seconds) for each image.
        output_video_path (str): The file path where the output video will be saved.
    
    Returns:
        None
    """
    # Check if the lengths of the images and durations lists are the same
    if len(images) != len(durations):
        print("Error: The number of images must match the number of durations.")
        return

    # Read the first image to get dimensions
    first_image_path = images[0]
    frame = cv2.imread(first_image_path)
    if frame is None:
        print(f"Error: Unable to read image {first_image_path}.")
        return

    height, width, layers = frame.shape

    # Create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4
    video = cv2.VideoWriter(output_video_path, fourcc, 30.0, (width, height))

    # Loop through images and durations to create the video
    for img_path, duration in zip(images, durations):
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"Error: Unable to read image {img_path}. Skipping.")
            continue

        # Calculate the number of frames for the given duration
        frame_count = int(duration * 30)  # Assuming 30 FPS

        # Write the same frame multiple times based on duration
        for _ in range(frame_count):
            video.write(frame)

    # Release the VideoWriter object
    video.release()
    print(f"Video saved at {output_video_path}")

def merge_mp3s(mp3_files, output_path):
    """Merge multiple MP3 files into a single MP3 file.

    Args:
        mp3_files (list of str): List of file paths to the MP3 files to be merged.
        output_path (str): The file path where the merged MP3 will be saved.

    Returns:
        None
    """
    # Start with an empty AudioSegment
    combined = AudioSegment.empty()

    # Loop through each file, read it, and append to combined
    for mp3_file in mp3_files:
        try:
            audio = AudioSegment.from_file(mp3_file)
            combined += audio  # Concatenate the audio segments
        except Exception as e:
            print(f"Error reading {mp3_file}: {e}")

    # Export the combined audio to a single MP3 file
    combined.export(output_path, format='mp3')
    
    # Delete the small mp3 files
    for mp3_file in mp3_files:
        os.remove(mp3_file)
        
    print(f"Merged audio saved at {output_path}")

def combine_video_and_audio(video_path, audio_path, output_path):
    """Combine a video file with an audio file, creating a new video file with audio.

    Args:
        video_path (str): The file path of the video to be combined.
        audio_path (str): The file path of the audio to be combined with the video.
        output_path (str): The file path where the output video with audio will be saved.

    Returns:
        None
    """
    # Load the video to get its duration
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = frame_count / fps
    video.release()

    # Load the audio to get its duration
    audio = AudioSegment.from_file(audio_path)
    audio_duration = len(audio) / 1000  # Convert ms to seconds

    # Calculate the minimum duration
    min_duration = min(video_duration, audio_duration)

    # Trim audio to the minimum duration
    trimmed_audio = audio[:int(min_duration * 1000)]  # Convert seconds to ms
    trimmed_audio.export("trimmed_audio.mp3", format='mp3')

    # Use ffmpeg to combine video and the trimmed audio
    command = [
        'ffmpeg', '-y','-i', video_path, '-i', 'trimmed_audio.mp3', 
        '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', 
        '-shortest', output_path
    ]

    # Run the command
    subprocess.run(command)

    # Clean up temporary audio file
    os.remove("trimmed_audio.mp3")
    os.remove(video_path)
    os.remove(audio_path)
    print(f"Combined video saved at {output_path}")

def get_files(directory, extension):
    """Retrieve all files with a specific extension from a directory.

    Args:
        directory (str): The directory to search for files.
        extension (str): The file extension to filter by (e.g., '.png').

    Returns:
        list of str: A list of file paths that match the extension.
    """
    # List to hold paths of files with the specified extension
    png_files = []
    
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(extension):
            # Get the full path of the file
            full_path = os.path.join(directory, filename)
            png_files.append(full_path)
    
    return png_files

def generate_audio_clips(descriptions, basepath, language="en"):
    """Generate audio clips for each description, return their file paths and durations.

    Args:
        descriptions (list of str): List of text descriptions to convert to audio.
        basepath (str): The base path where audio files will be saved.
        language (str): The language code for text-to-speech (default is "en").

    Returns:
        list of tuples: A list containing tuples of (audio_path, duration).
    """
    audio_info = []  # List to hold tuples of (audio_path, duration)
    for idx, text in enumerate(descriptions):
        # Generate audio file
        tts = gTTS(text=text, lang=language)
        temp_audio_path = f"{basepath}audio_{idx}.mp3"
        tts.save(temp_audio_path)

        # Load the audio file to get its duration
        audio = AudioSegment.from_file(temp_audio_path)
        duration = len(audio)  # Duration in milliseconds

        # Append the path and duration as a tuple
        audio_info.append((temp_audio_path, duration))

    return audio_info

def generateteVideofromimagesandaudio(pngs, descriptions):
    """Generate a video from images and audio descriptions.

    Args:
        pngs (list of str): List of file paths to PNG images.
        descriptions (list of str): List of descriptions for the images to be converted to audio.

    Returns:
        None
    """
    basepath = '/tmp'
    # Generate mp3s from each text description, and record the durations
    audiopaths, durations = zip(*generate_audio_clips(descriptions, basepath=basepath, language="en"))
    audiopaths = list(audiopaths)
    durations = list(durations)

    # Combine the audios into a single audio file
    merge_mp3s(audiopaths, basepath + '/totalaudio.mp3')

    # Convert durations from milliseconds to seconds
    durations = [d / 1000 for d in durations]
    
    # Log durations and images being processed
    print(durations)
    print(pngs)

    # Generate a single video from the images using the durations
    create_video_from_images(pngs, durations, '/tmp/totalvideo.mp4')

    # Generate a single video with the combined audio and the generated video
    combine_video_and_audio('/tmp/totalvideo.mp4', '/tmp/totalaudio.mp3', '/tmp/video_with_audio.mp4')


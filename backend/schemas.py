from pydantic import BaseModel
from typing import List

class Page(BaseModel):
    id: int
    content: str

class Instructions(BaseModel):
    pages_instructions: list[str]

class Instruction(BaseModel):
    page_instruction: str

class CleanedText(BaseModel):
    cleaned_text: str
class ImproveTextRequest(BaseModel):
    description: str
    improveText: str
    image: str

class SearchQuery(BaseModel):
    query: str

class VideoRequest(BaseModel):
    images: List[str]  # List of base64 encoded images
    descriptions: List[str] 

class VideoResponse(BaseModel):
    video: str  # base64 encoded video with data URL prefix
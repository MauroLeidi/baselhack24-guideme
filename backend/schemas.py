from pydantic import BaseModel

class Page(BaseModel):
    id: int
    content: str

class Instructions(BaseModel):
    pages_instructions: list[str]

class Instruction(BaseModel):
    page_instruction: str
class ImproveTextRequest(BaseModel):
    description: str
    improveText: str
    image: str

class SearchQuery(BaseModel):
    query: str
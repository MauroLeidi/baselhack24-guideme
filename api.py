from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from typing import List

import requests
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional
import json
from fastapi import FastAPI, UploadFile, Form
from pydantic import BaseModel
from typing import List
import json


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

class Page(BaseModel):
    id: int
    content: str

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API"}

@app.post("/api/generate")
async def generate_pages(
    file: UploadFile = File(...),  # Changed to File(...)
    description: Optional[str] = Form(None)  # Made description optional
):
    try:
        # Log received data for debugging
        print(f"Received file: {file.filename}")
        print(f"Description: {description}")

        # Mock pages data
        pages = [
            {
                "id": 1,
                 "content": f"""# Introduction
This is an automatically generated document based on your input: {description}

## Overview
Here's what we found in your file: {file.filename}

- Point 1: Key findings
- Point 2: Important metrics
- Point 3: Recommendations"""
            },
            {
                "id": 2,
                "content": """# Detailed Analysis

## Key Metrics
- Metric 1: Value
- Metric 2: Value
- Metric 3: Value

## Insights
Here are some interesting patterns we found..."""
            },
        ]
        
        return {
            "status": "success",
            "pages": pages
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
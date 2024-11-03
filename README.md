# Endress & Hauser GuideMe - AI-Powered Documentation Generator

A web application that generates detailed documentation from a sequence of images using AI. The application processes uploaded images, generates descriptive content, and provides an interactive markdown editor for customization.

## TEST IT YOURSELF AT https://frontend-guideme.azurewebsites.net/


## Features

- **Image Upload**: Support for multiple image uploads (the images are considered as a temporal sequence)
- **AI-Powered Content Generation**: Automatically generates descriptions for each image
- **Web Search Integration**: Optional web search feature to enhance content generation with relevant context
- **Interactive Editor**:
  - Split-view markdown editor with live preview
  - Support for images and rich text formatting
  - Content improvement suggestions using AI
  - Page navigation system
  - Export to PDF functionality

## Tech Stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- html2canvas (for PDF export)
- jsPDF (for PDF generation)

### Backend
- FastAPI
- Python
- OpenAI API integration
- Bing Search API integration
- Jiina READER API (for html parsing of search results)

## Project Structure

```
└── ./
    ├── backend/
    │   ├── api.py        # Main FastAPI application
    │   ├── bing.py       # Bing search integration
    │   └── helpers.py    # Utility functions
    └── frontend/
        └── pages/
            ├── editor.tsx # Markdown editor page
            └── index.tsx  # Home/upload page
```

## API Endpoints

- `POST /search`: Perform web search using Bing API
- `POST /improveText`: Improve content using AI
- `POST /uploadfiles/`: Process and analyze uploaded images

## Setup Requirements

1. Environment Variables:
   - OpenAI API key
   - Bing API key

## Getting Started

1. Clone the repository

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

4. Set up environment variables:
```env
OPENAI_API_KEY=your_openai_key
BING_API_KEY=your_bing_key
```

5. Start the backend server:
```bash
cd backend
uvicorn api:app --reload
```

6. Start the frontend development server:
```bash
cd frontend
npm run dev
```

## Usage

1. Access the application through your web browser
2. Upload a sequence of images
3. (Optional) Add a description and enable web search
4. Click "Generate" to process the images
5. Use the editor to customize the generated content
6. Optionally ask for redefined AI generated content
7. Export to PDF or continue editing as needed




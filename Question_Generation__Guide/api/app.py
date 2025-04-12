from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
import json
import datetime

# Add parent directory to path to import from agents folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.Questionmaker import generate_question_paper


# Define request models
class QuestionGenerationRequest(BaseModel):
    exam_type: str
    subject: str
    chapters: List[str]
    num_questions: Optional[int] = 10


# Initialize FastAPI app
app = FastAPI(
    title="Question Generation API",
    # Add explicit root_path to handle potential proxy issues
    root_path="",
)

# Enable CORS with more specific configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicitly allow POST
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"],  # Expose all headers
)

# Ensure temp directory exists
os.makedirs("../temp", exist_ok=True)

# Mount static files directory
app.mount("/temp", StaticFiles(directory="../temp"), name="temp")
app.mount("/static", StaticFiles(directory="../agents"), name="static")


@app.get("/")
async def index():
    """Serve the index.html file"""
    return FileResponse("../agents/index.html")


# Add an OPTIONS handler explicitly for the generate_questions endpoint
@app.options("/api/generate_questions")
async def options_generate_questions():
    """Handle OPTIONS requests for the generate_questions endpoint"""
    return {"allow": "POST, OPTIONS"}


@app.post("/api/generate_questions")
async def api_generate_questions(request: QuestionGenerationRequest):
    """Generate questions based on user selection"""
    try:
        # Extract parameters
        exam_type = request.exam_type
        subject = request.subject
        chapters = request.chapters
        num_questions = request.num_questions

        print(f"Request received: {exam_type}, {subject}, {chapters}, {num_questions}")

        # Generate the questions using our QuestionMaker
        output_path = generate_question_paper(
            exam_type, subject, chapters, num_questions
        )

        print(f"Output generated at: {output_path}")

        # Read the generated markdown file
        with open(output_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Create relative path for frontend to access
        relative_path = output_path.replace("..", "")

        return {
            "success": True,
            "markdown": markdown_content,
            "file_path": relative_path,
        }

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"Error generating questions: {str(e)}")
        print(f"Traceback: {error_details}")
        raise HTTPException(
            status_code=500, detail=f"Error generating questions: {str(e)}"
        )


@app.get("/api/recent_questions")
async def api_recent_questions():
    """Get list of recently generated question papers"""
    try:
        # Path to temp directory
        temp_dir = "../temp"

        # List all files in temp directory
        files = os.listdir(temp_dir)

        # Filter for metadata files
        metadata_files = [f for f in files if f.endswith("_metadata.json")]

        # Read metadata from each file and sort by timestamp
        question_papers = []
        for metadata_file in metadata_files:
            file_path = os.path.join(temp_dir, metadata_file)
            with open(file_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # Add file paths to metadata
            content_file = metadata_file.replace("_metadata.json", "_content.md")
            metadata["metadata_file"] = metadata_file
            metadata["content_file"] = content_file

            question_papers.append(metadata)

        # Sort by timestamp (newest first)
        question_papers.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return {"success": True, "question_papers": question_papers}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving recent questions: {str(e)}"
        )


# If running directly
if __name__ == "__main__":
    import uvicorn

    # Create the temp directory if it doesn't exist
    os.makedirs("../temp", exist_ok=True)

    # Run the FastAPI app with Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)

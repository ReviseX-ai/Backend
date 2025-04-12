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

# Enable CORS with more specific configuration - add PUT and DELETE methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Add more methods
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
    return JSONResponse(
        content={"allow": "POST, OPTIONS"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept"
        }
    )


# Add a test endpoint to verify API is working
@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API functionality"""
    return {"status": "ok", "message": "API is working correctly"}


@app.post("/api/generate_questions")
async def api_generate_questions(request: QuestionGenerationRequest):
    """Generate questions based on user selection"""
    try:
        # Log request for debugging
        print(f"API Request received: {request}")
        
        # Extract parameters
        exam_type = request.exam_type
        subject = request.subject
        chapters = request.chapters
        num_questions = request.num_questions

        print(f"Processing request: {exam_type}, {subject}, {chapters}, {num_questions}")

        # Validate input data
        if not exam_type or not subject or not chapters or len(chapters) == 0:
            raise ValueError("Missing required parameters: exam_type, subject, and chapters are required")
            
        if num_questions <= 0 or num_questions > 20:
            num_questions = 10  # Reset to default if invalid

        # Generate the questions using our QuestionMaker
        print(f"Calling generate_question_paper with params: {exam_type}, {subject}, {chapters}, {num_questions}")
        output_path = generate_question_paper(
            exam_type, subject, chapters, num_questions
        )

        print(f"Output generated at: {output_path}")

        # Check if the file exists
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file was not created: {output_path}")

        # Read the generated markdown file
        with open(output_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
            
        # Verify content is not empty
        if not markdown_content.strip():
            raise ValueError("Generated content is empty")

        # Create relative path for frontend to access
        relative_path = output_path.replace("..", "")

        # Return success response
        print("Returning successful response")
        return JSONResponse(
            content={
                "success": True,
                "markdown": markdown_content,
                "file_path": relative_path,
            }
        )

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"Error generating questions: {str(e)}")
        print(f"Traceback: {error_details}")
        
        # Return a proper error response with correct JSON formatting
        return JSONResponse(
            status_code=200,  # Use 200 instead of 500 to avoid CORS issues
            content={
                "success": False,
                "error": str(e),
                "details": error_details
            }
        )


# Modify the /api/recent_questions endpoint to return JSON response
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

        return JSONResponse(
            content={"success": True, "question_papers": question_papers}
        )

    except Exception as e:
        return JSONResponse(
            status_code=200,  # Use 200 for consistent error handling
            content={
                "success": False,
                "error": f"Error retrieving recent questions: {str(e)}"
            }
        )


@app.get("/results.html")
async def results_page():
    """Serve the results.html file"""
    return FileResponse("../agents/results.html")


# If running directly
if __name__ == "__main__":
    import uvicorn

    # Create the temp directory if it doesn't exist
    os.makedirs("../temp", exist_ok=True)

    # Run the FastAPI app with Uvicorn
    # Use 127.0.0.1 instead of 0.0.0.0 for direct browser access
    port = 5001
    print(f"Starting server. Access the application at: http://127.0.0.1:{port}")
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=True)

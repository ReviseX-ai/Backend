from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import sys
import os
from fastapi.middleware.cors import CORSMiddleware
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

# Import the run_educational_workflow function from the workflow.py file
from workflow import run_educational_workflow

app = FastAPI(
    title="Educational Workflow API",
    description="API for personalized educational assessments and recommendations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

class StudentRequest(BaseModel):
    user_id: str
    psychometric_data: Dict[str, Any]
    progress_data: Dict[str, Any]

class WorkflowResponse(BaseModel):
    user_id: str
    psychometric_insights: str
    progress_insights: str
    mistake_insights: str
    syllabus_recommendations: str
    question_recommendations: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Educational Workflow API"}

@app.post("/analyze", response_model=WorkflowResponse)
async def analyze_student(request: StudentRequest):
    try:
        result = run_educational_workflow(
            request.user_id,
            request.psychometric_data,
            request.progress_data
        )
        
        return WorkflowResponse(
            user_id=request.user_id,
            psychometric_insights=result["psychometric_insights"],
            progress_insights=result["progress_insights"],
            mistake_insights=result["mistake_insights"],
            syllabus_recommendations=result["syllabus_recommendations"],
            question_recommendations=result["question_recommendations"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
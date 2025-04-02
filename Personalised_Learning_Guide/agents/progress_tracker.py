from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
from typing import Dict, Any, Optional

class StudentProgressAnalyzer:
    """
    A class to analyze student progress data and provide personalized insights.
    """
    
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        """
        Initialize the StudentProgressAnalyzer with the specified model.
        
        Args:
            model_id: The ID of the Gemini model to use
            enable_markdown: Whether to enable markdown output
        """
        load_dotenv()
        self.agent = Agent(
            model=Gemini(id=model_id),
            markdown=enable_markdown,
        )
    
    def analyze_progress(self, student_data: str) -> str:
        """
        Analyze student progress data and return insights.
        
        Args:
            student_data: JSON string containing student performance data
        
        Returns:
            A string containing the analysis and recommendations
        """
        prompt = self._create_analysis_prompt(student_data)
        response = self.agent.run(prompt)
        return response.content
    
    def _create_analysis_prompt(self, student_data: str) -> str:
        """
        Create a prompt for the agent to analyze student data.
        
        Args:
            student_data: JSON string containing student performance data
        
        Returns:
            A prompt string for the agent
        """
        return f"""
        You are an educational progress insight provider agent. Analyze this student's progress data and provide:
        1. A summary of their overall performance
        2. Subject-wise analysis highlighting strengths and weaknesses
        3. A brief study guide tailored to the student's needs
        
        Here's the student data:
        {student_data}
        """
    
    def extract_student_info(self, student_data: str) -> Dict[str, Any]:
        """
        Extract basic student information from the data.
        
        Args:
            student_data: JSON string containing student performance data
        
        Returns:
            A dictionary with basic student information
        """
        try:
            data = json.loads(student_data)
            return data.get("student_details", {})
        except json.JSONDecodeError:
            return {}
    
    def get_weak_chapters(self, student_data: str) -> Dict[str, list]:
        """
        Extract weak chapters by subject from student data.
        
        Args:
            student_data: JSON string containing student performance data
        
        Returns:
            A dictionary with subjects as keys and lists of weak chapters as values
        """
        try:
            data = json.loads(student_data)
            analysis = data.get("progress_report", {}).get("subject_wise_analysis", {})
            
            weak_chapters = {}
            for subject, info in analysis.items():
                weak_chapters[subject] = info.get("weak_chapters", [])
            
            return weak_chapters
        except json.JSONDecodeError:
            return {}
    

if __name__ == "__main__":
    analyzer = StudentProgressAnalyzer()
    
    sample_data = """
    {
      "student_details": {
        "name": "Rahul Sharma",
        "student_id": "JEE2025_12345",
        "grade": "12th",
        "target_exam": "JEE Advanced 2025"
      },
      "progress_report": {
        "last_10_days": [
          {
            "date": "2025-03-23",
            "questions_attempted": 50,
            "correct": 40,
            "wrong": 10,
            "subject_wise": {
              "Physics": {
                "questions_attempted": 20,
                "correct": 15,
                "wrong": 5,
                "weak_chapters": ["Modern Physics", "Optics"]
              },
              "Chemistry": {
                "questions_attempted": 15,
                "correct": 12,
                "wrong": 3,
                "weak_chapters": ["Chemical Equilibrium"]
              },
              "Mathematics": {
                "questions_attempted": 15,
                "correct": 13,
                "wrong": 2,
                "weak_chapters": ["Probability"]
              }
            }
          },
          {
            "date": "2025-03-24",
            "questions_attempted": 45,
            "correct": 35,
            "wrong": 10,
            "subject_wise": {
              "Physics": {
                "questions_attempted": 18,
                "correct": 14,
                "wrong": 4,
                "weak_chapters": ["Electrostatics"]
              },
              "Chemistry": {
                "questions_attempted": 12,
                "correct": 9,
                "wrong": 3,
                "weak_chapters": ["Organic Chemistry - Reactions"]
              },
              "Mathematics": {
                "questions_attempted": 15,
                "correct": 12,
                "wrong": 3,
                "weak_chapters": ["Integration"]
              }
            }
          }
        ],
        "total_questions_attempted": 527,
        "total_correct": 428,
        "total_wrong": 99,
        "accuracy": 81.2,
        "subject_wise_analysis": {
          "Physics": {
            "total_attempted": 200,
            "total_correct": 160,
            "total_wrong": 40,
            "weak_chapters": ["Modern Physics", "Optics", "Electrostatics"]
          },
          "Chemistry": {
            "total_attempted": 160,
            "total_correct": 130,
            "total_wrong": 30,
            "weak_chapters": ["Chemical Equilibrium", "Organic Chemistry - Reactions"]
          },
          "Mathematics": {
            "total_attempted": 167,
            "total_correct": 138,
            "total_wrong": 29,
            "weak_chapters": ["Probability", "Integration"]
          }
        }
      }
    }
    """
    
    analysis = analyzer.analyze_progress(sample_data)
    print("STUDENT PROGRESS ANALYSIS:")
    print(analysis)
    print("\n" + "-"*50 + "\n")
    

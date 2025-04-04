from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
from typing import Dict, Any, List




class PsychometricAnalyzer:
    """
    A class to analyze student psychometric data and provide personalized learning insights.
    """

    def __init__(
        self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True
    ):
        """
        Initialize the PsychometricAnalyzer with the specified model.

        Args:
            model_id: The ID of the Gemini model to use
            enable_markdown: Whether to enable markdown output
        """
        load_dotenv()
        self.agent = Agent(
            model=Gemini(id=model_id),
            markdown=enable_markdown,
        )

    def analyze_psychometric_data(self, psychometric_data: str) -> str:
        """
        Analyze psychometric assessment data and return personalized insights.

        Args:
            psychometric_data: JSON string containing psychometric assessment data

        Returns:
            A string containing the analysis and recommendations
        """
        prompt = self._create_analysis_prompt(psychometric_data)
        response = self.agent.run(prompt)
        return response.content

    def _create_analysis_prompt(self, psychometric_data: str) -> str:
        """
        Create a prompt for the agent to analyze psychometric data.

        Args:
            psychometric_data: JSON string containing psychometric assessment data

        Returns:
            A prompt string for the agent
        """
        return f"""
        You are a psychometric analysis agent specializing in educational psychology. 
        Analyze this student's psychometric assessment responses and provide:
        
        1. A summary of their learning style, personality traits, and cognitive strengths
        2. How these psychological factors affect their learning in Physics, Chemistry, Mathematics, and Biology
        3. Personalized strategies for optimal study based on their psychometric profile
        4. Recommendations for managing exam stress and improving focus based on their profile
        5. Guidance on how to leverage their psychological strengths for competitive exam preparation
        6. Provide the analysis within 150 words, but must include top most important points.
        
        Format your response in clear sections with concise, actionable insights.
        
        Here's the student's psychometric assessment data:
        {psychometric_data}
        """

    def extract_learning_style(self, psychometric_data: str) -> str:
        """
        Extract the dominant learning style from psychometric data.

        Args:
            psychometric_data: JSON string containing psychometric assessment data

        Returns:
            A string indicating the dominant learning style
        """
        try:
            data = json.loads(psychometric_data)
            return (
                data.get("analysis", {})
                .get("learning_style", {})
                .get("dominant", "Unknown")
            )
        except json.JSONDecodeError:
            return "Unknown"

    def get_stress_management_tips(self, psychometric_data: str) -> List[str]:
        """
        Extract stress management recommendations based on personality type.

        Args:
            psychometric_data: JSON string containing psychometric assessment data

        Returns:
            A list of stress management recommendations
        """
        try:
            data = json.loads(psychometric_data)
            personality_type = (
                data.get("analysis", {}).get("personality", {}).get("type", "")
            )
            stress_tips = data.get("recommendations", {}).get("stress_management", [])
            return stress_tips
        except json.JSONDecodeError:
            return []

    def generate_subject_specific_advice(
        self, psychometric_data: str, subject: str
    ) -> str:
        """
        Generate subject-specific learning advice based on psychometric profile.

        Args:
            psychometric_data: JSON string containing psychometric assessment data
            subject: The subject for which to generate advice (Physics/Chemistry/Mathematics/Biology)

        Returns:
            Subject-specific learning advice
        """
        prompt = f"""
        Based on this student's psychometric profile, provide specific learning strategies for {subject}.
        Focus on how their learning style, cognitive strengths, and personality traits can be leveraged
        for effective learning in {subject}.
        
        Student's psychometric data:
        {psychometric_data}
        """
        response = self.agent.run(prompt)
        return response.content


if __name__ == "__main__":
    analyzer = PsychometricAnalyzer()

    # Sample psychometric assessment data
    sample_data = """
    {
      "student_details": {
        "name": "Rohit Verma",
        "student_id": "JEE2025_78901",
        "grade": "12th",
        "target_exam": "JEE Advanced 2025"
      },
      "assessment": {
        "learning_style_questions": [
          {
            "question": "When learning something new, I prefer to:",
            "answer": "See visual representations like diagrams and charts",
            "score": "visual"
          },
          {
            "question": "When studying complex concepts, I understand better when I:",
            "answer": "Work through practice problems on my own",
            "score": "kinesthetic"
          },
          {
            "question": "During lectures, I retain information best when I:",
            "answer": "Take detailed notes and organize them visually",
            "score": "visual"
          },
          {
            "question": "When preparing for exams, I prefer to:",
            "answer": "Create mind maps and visual connections between concepts",
            "score": "visual"
          },
          {
            "question": "I find it easiest to remember information when:",
            "answer": "I can visualize it in my mind",
            "score": "visual"
          }
        ],
        "personality_questions": [
          {
            "question": "When facing a difficult problem, I typically:",
            "answer": "Analyze it methodically until I find a logical solution",
            "trait": "analytical"
          },
          {
            "question": "When working on group projects, I usually:",
            "answer": "Prefer working independently on my assigned tasks",
            "trait": "introversion"
          },
          {
            "question": "When under pressure before exams, I:",
            "answer": "Feel anxious but use it to motivate intense study sessions",
            "trait": "anxiety-prone"
          },
          {
            "question": "When receiving feedback on my work, I:",
            "answer": "Take it seriously and meticulously address all points of improvement",
            "trait": "conscientiousness"
          },
          {
            "question": "When planning my study schedule, I prefer to:",
            "answer": "Create a detailed plan with specific goals for each session",
            "trait": "organized"
          }
        ],
        "cognitive_questions": [
          {
            "question": "When solving math problems, I tend to:",
            "answer": "Visualize the problem spatially before calculating",
            "cognitive_area": "spatial reasoning"
          },
          {
            "question": "When memorizing information, I am best at:",
            "answer": "Remembering visual patterns and diagrams",
            "cognitive_area": "visual memory"
          },
          {
            "question": "When working on complex problems, I excel at:",
            "answer": "Breaking them down into logical steps",
            "cognitive_area": "logical reasoning"
          },
          {
            "question": "I find it easiest to focus when:",
            "answer": "I'm in a quiet environment with minimal distractions",
            "cognitive_area": "attention"
          },
          {
            "question": "When learning new equations or formulas, I:",
            "answer": "Try to understand the underlying principles rather than memorizing",
            "cognitive_area": "conceptual thinking"
          }
        ]
      },
      "analysis": {
        "learning_style": {
          "dominant": "Visual",
          "secondary": "Kinesthetic",
          "least_preferred": "Auditory"
        },
        "personality": {
          "type": "Analytical Introvert",
          "strengths": ["Detail-oriented", "Methodical", "Focused"],
          "challenges": ["Test anxiety", "Perfectionism", "Working in groups"]
        },
        "cognitive_profile": {
          "strengths": ["Spatial reasoning", "Visual memory", "Logical thinking"],
          "areas_for_improvement": ["Verbal reasoning", "Working memory under pressure"]
        }
      },
      "recommendations": {
        "study_techniques": [
          "Use mind maps and diagrams to visualize concepts",
          "Create color-coded notes and visual summaries",
          "Solve problems using step-by-step visual approaches",
          "Use flowcharts to connect related concepts",
          "Convert text-heavy content into visual formats"
        ],
        "stress_management": [
          "Practice timed mock tests to build pressure tolerance",
          "Use guided visualization techniques before exams",
          "Implement the Pomodoro technique with 5-minute visual breaks",
          "Create visual relaxation cues for high-stress moments",
          "Develop a pre-exam routine with visualization exercises"
        ]
      }
    }
    """

    analysis = analyzer.analyze_psychometric_data(sample_data)
    print("STUDENT PSYCHOMETRIC ANALYSIS:")
    print(analysis)
    print("\n" + "-" * 50 + "\n")

    # # Example of getting subject-specific advice
    # physics_advice = analyzer.generate_subject_specific_advice(sample_data, "Physics")
    # print("PHYSICS-SPECIFIC LEARNING STRATEGIES:")
    # print(physics_advice)
    # print("\n" + "-" * 50 + "\n")

    # Extract specific insights
    learning_style = analyzer.extract_learning_style(sample_data)
    print(f"Dominant Learning Style: {learning_style}")

    # stress_tips = analyzer.get_stress_management_tips(sample_data)
    # print("Stress Management Recommendations:")
    # for tip in stress_tips:
    #     print(f"- {tip}")

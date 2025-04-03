from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
from typing import Dict, Any, List


class MistakeFinder:
    """
    An enhanced class to analyze student answers, identify mistakes, and provide detailed feedback
    with JEE/NEET specific recommendations.
    """

    def __init__(
        self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True
    ):
        """
        Initialize the MistakeFinder with the specified model.

        Args:
            model_id: The ID of the Gemini model to use
            enable_markdown: Whether to enable markdown output
        """
        load_dotenv()
        self.agent = Agent(
            model=Gemini(id=model_id),
            markdown=enable_markdown,
        )

    def analyze_mistakes(self, student_response: str) -> str:
        """
        Analyze student's answer with enhanced error analysis and JEE/NEET context.

        Args:
            student_response: JSON string containing student's answer and related metadata

        Returns:
            A string containing comprehensive analysis and detailed feedback
        """
        prompt = self._create_analysis_prompt(student_response)
        response = self.agent.run(prompt)
        return response.content

    def _create_analysis_prompt(self, student_response: str) -> str:
        """
        Create an enhanced prompt for comprehensive mistake analysis.

        Args:
            student_response: JSON string containing student's answer and related metadata

        Returns:
            A detailed prompt string for the agent
        """
        return f"""
        You are an expert JEE/NEET mentor specializing in identifying and analyzing student mistakes. 
        Provide a comprehensive analysis of the student's response with the following structure:

        1. ERROR IDENTIFICATION AND ANALYSIS
           - Primary Error Type: (Conceptual/Calculation/Application/Logical)
           - Secondary Error Types (if any)
           - Detailed description of each error identified
           - Step-by-step breakdown of where the solution went wrong

        2. CONCEPTUAL UNDERSTANDING
           - Core concepts involved in the question
           - Specific conceptual gaps identified
           - Related concepts that might need reinforcement
           - Common misconceptions in this topic

        3. ROOT CAUSE ANALYSIS
           - Probable reasons for each error
           - Pattern recognition (if similar errors are common)
           - Prerequisites that might need strengthening
           - Learning style considerations

        4. JEE/NEET RELEVANCE
           - Importance rating (0-10) for JEE/NEET
           - Frequency of concept appearance in past papers
           - Related topics in the syllabus
           - Types of variations asked in exams

        5. CORRECTION STRATEGY
           - Detailed step-by-step correct solution
           - Alternative approaches to solve the same problem
           - Key points to remember
           - Common traps to avoid

        6. SIMILAR QUESTIONS
           - 5 carefully selected questions of similar type that often cause the same error
           - Each question should include:
             * Question text
             * Difficulty level
             * Key concepts tested
             * Common pitfalls to watch for
           - Questions should gradually increase in complexity

        7. PREVENTION STRATEGY
           - Specific study techniques for this topic
           - Practice recommendations
           - Self-assessment checkpoints
           - Topic prerequisites to review

        Format your response clearly with headings and bullet points.
        Limit the entire analysis to 500 words while maintaining comprehensiveness.
        
        Here's the student's response data:
        {student_response}
        """

    def extract_error_types(self, student_response: str) -> Dict[str, Any]:
        """
        Extract detailed error analysis including primary and secondary error types.

        Args:
            student_response: JSON string containing student's answer data

        Returns:
            A dictionary containing error types and their details
        """
        try:
            data = json.loads(student_response)
            analysis = data.get("analysis", {})
            return {
                "primary_error": analysis.get("primary_error_type", "Unknown"),
                "secondary_errors": analysis.get("secondary_error_types", []),
                "error_details": analysis.get("error_details", {}),
                "severity": analysis.get("severity", "unknown")
            }
        except json.JSONDecodeError:
            return {}

    def get_improvement_strategies(self, student_response: str) -> Dict[str, List[str]]:
        """
        Extract comprehensive improvement strategies with categorization.

        Args:
            student_response: JSON string containing student's answer data

        Returns:
            A dictionary of categorized improvement strategies
        """
        try:
            data = json.loads(student_response)
            recommendations = data.get("recommendations", {})
            return {
                "conceptual_improvements": recommendations.get("conceptual_strategies", []),
                "calculation_improvements": recommendations.get("calculation_strategies", []),
                "practice_suggestions": recommendations.get("practice_problems", []),
                "prerequisite_topics": recommendations.get("prerequisites_to_review", [])
            }
        except json.JSONDecodeError:
            return {}

    def generate_topic_specific_feedback(
        self, student_response: str, topic: str, exam_type: str = "JEE"
    ) -> str:
        """
        Generate comprehensive topic-specific feedback with exam focus.

        Args:
            student_response: JSON string containing student's answer data
            topic: The specific topic/concept to focus feedback on
            exam_type: The target exam (JEE/NEET)

        Returns:
            Comprehensive topic-specific feedback and improvement suggestions
        """
        prompt = f"""
        Provide detailed {exam_type}-focused feedback for the topic: {topic}

        Analysis Structure:
        1. TOPIC IMPORTANCE
           - {exam_type} relevance score (0-10)
           - Past year appearance frequency
           - Connected topics in syllabus
           - Weightage in different exam patterns

        2. CONCEPTUAL FRAMEWORK
           - Core concepts within this topic
           - Common misconceptions
           - Critical prerequisites
           - Advanced applications

        3. ERROR ANALYSIS
           - Typical student errors in this topic
           - Pattern recognition
           - Impact on related topics
           - Prevention strategies

        4. PRACTICE STRATEGY
           - Types of questions to practice
           - Difficulty progression path
           - Time management tips
           - Self-assessment criteria

        5. SIMILAR QUESTIONS
           - 5 questions that test the same concept
           - Progressive difficulty levels
           - Various application contexts
           - Common pitfall warnings

        Student's response data:
        {student_response}
        """
        response = self.agent.run(prompt)
        return response.content


if __name__ == "__main__":
    finder = MistakeFinder()

    # Sample student response data with enhanced structure
    sample_data = """
    {
      "student_details": {
        "name": "Rohit Verma",
        "student_id": "JEE2025_78901",
        "subject": "Physics",
        "topic": "Kinematics",
        "exam_type": "JEE Advanced"
      },
      "question_details": {
        "question_id": "PHY_KIN_001",
        "type": "numerical",
        "difficulty": "medium",
        "max_marks": 4,
        "topic_importance": {
          "jee_score": 9,
          "frequency": "Very High",
          "connected_topics": ["Dynamics", "Work-Energy", "Projectile Motion"]
        }
      },
      "student_response": {
        "answer_text": "A particle is thrown vertically upward with initial velocity 20 m/s. Time to reach maximum height = 20/10 = 2s, Maximum height = (20^2)/(2*10) = 20m",
        "work_shown": [
          "Using v = u + at",
          "0 = 20 - 10t",
          "t = 20/10 = 2s",
          "Using h = ut + (1/2)at^2",
          "h = 20 * 2 - (1/2) * 10 * 4",
          "h = 40 - 20 = 20m"
        ],
        "final_answer": "20 meters"
      },
      "analysis": {
        "primary_error_type": "Conceptual",
        "secondary_error_types": ["Calculation", "Application"],
        "error_details": {
          "time_calculation": {
            "error": "Used final equation without considering maximum height condition",
            "correction": "At maximum height, v = 0; t = u/g = 20/10 = 2s is correct",
            "misconception": "Confusion between time to maximum height and total time of flight"
          },
          "height_calculation": {
            "error": "Incorrect application of displacement formula",
            "correction": "Should use h = ut - (1/2)gt^2 with t = 1s",
            "misconception": "Sign convention confusion in vertical motion"
          }
        },
        "severity": "moderate"
      },
      "recommendations": {
        "conceptual_strategies": [
          "Review sign conventions in vertical motion",
          "Study the relationship between displacement, velocity, and acceleration"
        ],
        "calculation_strategies": [
          "Practice step-by-step problem solving",
          "Focus on units and dimensional analysis"
        ],
        "practice_problems": [
          "Similar problems with different initial velocities",
          "Problems combining vertical and horizontal motion"
        ],
        "prerequisites_to_review": [
          "Basic equations of motion",
          "Graphical analysis of motion"
        ]
      }
    }
    """

    analysis = finder.analyze_mistakes(sample_data)
    print("COMPREHENSIVE MISTAKE ANALYSIS:")
    print(analysis)
    print("\n" + "-" * 50 + "\n")

    error_analysis = finder.extract_error_types(sample_data)
    print("Detailed Error Analysis:")
    print(json.dumps(error_analysis, indent=2))

    strategies = finder.get_improvement_strategies(sample_data)
    print("\nComprehensive Improvement Strategies:")
    print(json.dumps(strategies, indent=2))


if __name__ == "__main__":
    finder = MistakeFinder()

    # Sample student response data
    sample_data = """
    {
      "student_details": {
        "name": "Rohit Verma",
        "student_id": "JEE2025_78901",
        "subject": "Physics",
        "topic": "Kinematics"
      },
      "question_details": {
        "question_id": "PHY_KIN_001",
        "type": "numerical",
        "difficulty": "medium",
        "max_marks": 4
      },
      "student_response": {
        "answer_text": "A particle is thrown vertically upward with initial velocity 20 m/s. 
                       Time to reach maximum height = 20/10 = 2s
                       Maximum height = (20^2)/(2*10) = 20m",
        "work_shown": [
          "Using v = u + at",
          "0 = 20 - 10t",
          "t = 20/10 = 2s",
          "Using h = ut + (1/2)at^2",
          "h = 20 * 2 - (1/2) * 10 * 4",
          "h = 40 - 20 = 20m"
        ],
        "final_answer": "20 meters"
      },
      "analysis": {
        "error_types": [
          "Calculation Error",
          "Conceptual Misunderstanding"
        ],
        "mistake_details": {
          "time_calculation": {
            "error": "Used final equation without considering maximum height condition",
            "correction": "At maximum height, v = 0; t = u/g = 20/10 = 2s is correct"
          },
          "height_calculation": {
            "error": "Incorrect application of displacement formula",
            "correction": "Should use h = ut - (1/2)gt^2 with t = 1s"
          }
        },
        "severity": "moderate"
      },
      "recommendations": {
        "improvement_strategies": [
          "Review sign conventions in vertical motion",
          "Practice problems with multiple stages of motion",
          "Focus on physical meaning of equations",
          "Work through step-by-step solutions",
          "Create visual representations of motion"
        ],
        "practice_problems": [
          "PHY_KIN_023",
          "PHY_KIN_045",
          "PHY_KIN_067"
        ]
      }
    }
    """

    analysis = finder.analyze_mistakes(sample_data)
    print("STUDENT MISTAKE ANALYSIS:")
    print(analysis)
    print("\n" + "-" * 50 + "\n")

    error_types = finder.extract_error_types(sample_data)
    print("Identified Error Types:")
    for error in error_types:
        print(f"- {error}")

    strategies = finder.get_improvement_strategies(sample_data)
    print("\nImprovement Strategies:")
    for strategy in strategies:
        print(f"- {strategy}")
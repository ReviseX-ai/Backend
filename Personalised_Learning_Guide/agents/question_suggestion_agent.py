from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
from typing import Dict, Any, List


class TopicQuestionRecommender:
    """
    An agent that recommends specific topics and question types for students to focus on.
    """

    def __init__(
        self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True
    ):
        """
        Initialize the TopicQuestionRecommender with the specified model.

        Args:
            model_id: The ID of the Gemini model to use
            enable_markdown: Whether to enable markdown output
        """
        load_dotenv()
        self.agent = Agent(
            model=Gemini(id=model_id),
            markdown=enable_markdown,
        )

    def recommend_practice_focus(self, performance_data: str) -> str:
        """
        Analyze performance data and recommend specific topics and question types to focus on.

        Args:
            performance_data: JSON string containing performance data

        Returns:
            A string containing topic and question type recommendations
        """
        prompt = self._create_recommendation_prompt(performance_data)
        response = self.agent.run(prompt)
        return response.content

    def _create_recommendation_prompt(self, performance_data: str) -> str:
        """
        Create a prompt for the agent to recommend topics and question types.

        Args:
            performance_data: JSON string containing performance data

        Returns:
            A prompt string for the agent
        """
        return f"""
        You are a specialized exam preparation advisor. Based on this student's performance data:
        
        1. Identify the TOP 3 WEAKEST TOPICS the student should focus on improving immediately
        2. For EACH of these weak topics, recommend:
           - 3 SPECIFIC QUESTION TYPES they should practice
           - The DIFFICULTY LEVEL they should start with (easy/medium/hard)
           - The NUMBER OF QUESTIONS they should solve daily
        3. Suggest a PRIORITY ORDER for tackling these topics
        4. Recommend any SPECIFIC QUESTION PATTERNS that would help strengthen foundational concepts
        
        Keep your recommendations direct, specific, and actionable.
        
        Here's the student's performance data:
        {performance_data}
        """

    def get_weak_topics_with_question_types(self, performance_data: str) -> List[Dict[str, Any]]:
        """
        Extract weak topics and corresponding question types from performance data.

        Args:
            performance_data: JSON string containing performance data

        Returns:
            A list of dictionaries with subject, topic, accuracy percentage, and question types
        """
        try:
            data = json.loads(performance_data)
            weak_topics = []
            
            for subject, topics in data.get("topic_performance", {}).items():
                for topic, stats in topics.items():
                    accuracy = stats.get("accuracy_percentage", 0)
                    if accuracy < 60:  # Consider topics with less than 60% accuracy as weak
                        # Get question types for this topic if available
                        question_types = stats.get("question_types", {})
                        
                        weak_topics.append({
                            "subject": subject,
                            "topic": topic,
                            "accuracy": accuracy,
                            "question_types": question_types
                        })
            
            # Sort by accuracy (ascending)
            weak_topics.sort(key=lambda x: x["accuracy"])
            return weak_topics
        except (json.JSONDecodeError, KeyError):
            return []

    def generate_daily_question_set(self, performance_data: str, topic: str) -> str:
        """
        Generate a recommended set of daily practice questions for a specific weak topic.

        Args:
            performance_data: JSON string containing performance data
            topic: The specific topic to generate questions for

        Returns:
            A string containing recommended daily practice questions
        """
        prompt = f"""
        Create a specific set of daily practice questions for the topic "{topic}" based on the student's performance data.
        
        Include:
        1. The exact types of questions to practice (be specific about question patterns)
        2. A recommended sequence (from foundational to advanced)
        3. The number of questions to attempt daily
        4. How to know when to move to more difficult questions
        
        Be specific and practical in your recommendations.
        
        Student's performance data:
        {performance_data}
        """
        
        response = self.agent.run(prompt)
        return response.content
    
    def recommend_question_bank(self, performance_data: str) -> str:
        """
        Recommend specific question banks or sources based on weak topics.

        Args:
            performance_data: JSON string containing performance data

        Returns:
            A string containing recommended question sources
        """
        weak_topics = self.get_weak_topics_with_question_types(performance_data)
        topics_str = ", ".join([f"{t['topic']} ({t['subject']})" for t in weak_topics[:3]])
        
        prompt = f"""
        Based on the student's weak topics ({topics_str}), recommend:
        
        1. Specific question banks or resources that target these weak areas
        2. For each resource, indicate which specific question types or sections to focus on
        3. A suggested order for working through these resources
        
        Be specific with exact chapter/section names and question numbers where possible.
        Focus on high-quality, targeted practice rather than quantity.
        """
        
        response = self.agent.run(prompt)
        return response.content


if __name__ == "__main__":
    recommender = TopicQuestionRecommender()

    sample_data = """
    {
      "student_details": {
        "name": "Rohit Verma",
        "student_id": "JEE2025_78901",
        "grade": "12th",
        "target_exam": "JEE Advanced 2025"
      },
      "overall_performance": {
        "physics": 65.3,
        "chemistry": 72.8,
        "mathematics": 58.2
      },
      "topic_performance": {
        "physics": {
          "mechanics": {
            "accuracy_percentage": 74.5,
            "questions_attempted": 47,
            "questions_correct": 35,
            "question_types": {
              "conceptual": {"accuracy": 82.0, "count": 22},
              "numerical": {"accuracy": 70.6, "count": 17},
              "graphical": {"accuracy": 62.5, "count": 8}
            }
          },
          "electromagnetism": {
            "accuracy_percentage": 52.1,
            "questions_attempted": 38,
            "questions_correct": 20,
            "question_types": {
              "conceptual": {"accuracy": 58.8, "count": 17},
              "numerical": {"accuracy": 46.7, "count": 15},
              "derivation-based": {"accuracy": 50.0, "count": 6}
            }
          },
          "modern physics": {
            "accuracy_percentage": 55.6,
            "questions_attempted": 27,
            "questions_correct": 15,
            "question_types": {
              "conceptual": {"accuracy": 63.6, "count": 11},
              "numerical": {"accuracy": 50.0, "count": 12},
              "application": {"accuracy": 50.0, "count": 4}
            }
          }
        },
        "chemistry": {
          "physical chemistry": {
            "accuracy_percentage": 58.6,
            "questions_attempted": 29,
            "questions_correct": 17,
            "question_types": {
              "numerical": {"accuracy": 53.8, "count": 13},
              "conceptual": {"accuracy": 66.7, "count": 9},
              "graph-based": {"accuracy": 57.1, "count": 7}
            }
          }
        },
        "mathematics": {
          "vectors": {
            "accuracy_percentage": 42.1,
            "questions_attempted": 38,
            "questions_correct": 16,
            "question_types": {
              "3D geometry": {"accuracy": 35.7, "count": 14},
              "vector algebra": {"accuracy": 53.3, "count": 15},
              "application": {"accuracy": 33.3, "count": 9}
            }
          },
          "probability": {
            "accuracy_percentage": 48.4,
            "questions_attempted": 31,
            "questions_correct": 15,
            "question_types": {
              "basic probability": {"accuracy": 60.0, "count": 10},
              "conditional probability": {"accuracy": 41.7, "count": 12},
              "distributions": {"accuracy": 44.4, "count": 9}
            }
          }
        }
      },
      "recent_tests": [
        {
          "test_id": "PHY-22",
          "date": "2023-08-15",
          "subject": "Physics",
          "score_percentage": 62.0,
          "topics_covered": ["mechanics", "electromagnetism"]
        },
        {
          "test_id": "CHEM-18",
          "date": "2023-08-12",
          "subject": "Chemistry",
          "score_percentage": 74.0,
          "topics_covered": ["organic chemistry", "physical chemistry"]
        },
        {
          "test_id": "MATH-20",
          "date": "2023-08-10",
          "subject": "Mathematics",
          "score_percentage": 56.0,
          "topics_covered": ["vectors", "probability", "calculus"]
        }
      ]
    }
    """

    recommendations = recommender.recommend_practice_focus(sample_data)
    print("TOPIC AND QUESTION TYPE RECOMMENDATIONS:")
    print(recommendations)
    print("\n" + "-" * 50 + "\n")

    weak_topics = recommender.get_weak_topics_with_question_types(sample_data)
    print("WEAK TOPICS WITH QUESTION TYPE DETAILS:")
    for topic in weak_topics:
        print(f"- {topic['subject'].title()}: {topic['topic'].title()} ({topic['accuracy']}% accuracy)")
        if topic['question_types']:
            print("  Question Types:")
            for q_type, stats in topic['question_types'].items():
                print(f"    * {q_type}: {stats['accuracy']}% accuracy ({stats['count']} questions)")
    print("\n" + "-" * 50 + "\n")

    
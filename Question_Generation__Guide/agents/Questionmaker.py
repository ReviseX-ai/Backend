from agno.agent import Agent
from agno.tools.googlesearch import GoogleSearchTools
from agno.models.google import Gemini
import os
import json
import datetime


class QuestionMaker:
    def __init__(self):
        # API key for Gemini model
        self.api_key = "AIzaSyAmO9Jo12hF2XQZ9nlVDA7rL_Y-Fikypz0"

        # Initialize both agents
        self.jee_agent = self._create_jee_agent()
        self.neet_agent = self._create_neet_agent()

        # Create temp directory if it doesn't exist
        os.makedirs("../temp", exist_ok=True)

    def _create_jee_agent(self):
        """Create JEE specific agent"""
        return Agent(
            model=Gemini(id="gemini-2.0-flash-exp", api_key=self.api_key),
            tools=[GoogleSearchTools()],
            description="You are an educational agent that creates challenging MCQ questions from recent JEE Mains papers for advanced preparation.",
            instructions=[
                "Search specifically for recent JEE Mains question papers from the last 2 years.",
                "Provide {num_questions} high-difficulty MCQ questions with 4 options each and mark the correct answer.",
                "Focus on complex {topics} problems and challenging concepts that require deeper understanding.",
                "Include questions from the selected chapters: {chapters}.",
                "For each question, include a detailed explanation of the correct answer and the key concepts tested.",
                "Format questions in the exact style of official JEE Mains papers, with clear numbering and option labeling.",
                "Prioritize questions that test multiple concepts or require multi-step solutions.",
                "Return the output in markdown format.",
            ],
            show_tool_calls=True,
            debug_mode=False,
        )

    def _create_neet_agent(self):
        """Create NEET specific agent"""
        return Agent(
            model=Gemini(id="gemini-2.0-flash-exp", api_key=self.api_key),
            tools=[GoogleSearchTools()],
            description="You are an educational agent that creates challenging MCQ questions from recent NEET papers for medical entrance preparation.",
            instructions=[
                "Search specifically for recent NEET question papers from the last 2 years.",
                "Provide {num_questions} high-difficulty MCQ questions with 4 options each and mark the correct answer.",
                "Focus on complex {topics} problems and challenging concepts that require deeper understanding.",
                "Include questions from the selected chapters: {chapters}.",
                "For each question, include a detailed explanation of the correct answer and the key concepts tested.",
                "Format questions in the exact style of official NEET papers, with clear numbering and option labeling.",
                "Prioritize questions that test multiple concepts or require multi-step solutions.",
                "Return the output in markdown format.",
            ],
            show_tool_calls=True,
            debug_mode=False,
        )

    def generate_questions(self, exam_type, subject, chapters, num_questions=10):
        """
        Generate questions based on exam type, subject and selected chapters

        Args:
            exam_type (str): 'jee' or 'neet'
            subject (str): The subject selected (e.g., 'physics', 'chemistry', etc.)
            chapters (list): List of selected chapters
            num_questions (int): Number of questions to generate

        Returns:
            str: Generated questions in markdown format
        """
        # Prepare the prompt with details
        chapters_str = ", ".join(chapters)
        prompt = f"Generate {num_questions} challenging {exam_type.upper()} {subject} MCQ questions on the following chapters: {chapters_str}"

        # Select the appropriate agent based on exam type
        if exam_type.lower() == "jee":
            agent = self.jee_agent
            topics = subject
        else:  # NEET
            agent = self.neet_agent
            topics = subject

        # Generate response
        response = agent.run(
            prompt,
            format_args={
                "topics": topics,
                "chapters": chapters_str,
                "num_questions": num_questions,
            },
        )

        # Extract content from response object
        if hasattr(response, "content"):
            content = response.content
        else:
            content = str(response)

        # Save to file in temp directory
        filename = f"../temp/{exam_type}_{subject}_questions.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        return content

    def save_question_paper(self, exam_type, subject, chapters, markdown_content):
        """
        Save the generated question paper metadata and content

        Args:
            exam_type (str): 'jee' or 'neet'
            subject (str): The subject selected
            chapters (list): List of selected chapters
            markdown_content (str): The generated markdown content
        """
        metadata = {
            "exam_type": exam_type,
            "subject": subject,
            "chapters": chapters,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        # Create a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../temp/{exam_type}_{subject}_{timestamp}"

        # Save metadata
        with open(f"{filename}_metadata.json", "w") as f:
            json.dump(metadata, f)

        # Save content
        with open(f"{filename}_content.md", "w", encoding="utf-8") as f:
            f.write(markdown_content)

        return f"{filename}_content.md"


# Function to be called from API
def generate_question_paper(exam_type, subject, chapters, num_questions=10):
    """
    Generate a question paper based on the exam type, subject and selected chapters

    Args:
        exam_type (str): 'jee' or 'neet'
        subject (str): The subject selected
        chapters (list): List of selected chapters
        num_questions (int): Number of questions to generate (default: 10)

    Returns:
        str: Path to the generated markdown file
    """
    maker = QuestionMaker()
    content = maker.generate_questions(exam_type, subject, chapters, num_questions)
    return maker.save_question_paper(exam_type, subject, chapters, content)

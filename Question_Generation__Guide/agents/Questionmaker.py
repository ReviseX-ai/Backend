from agno.agent import Agent
from agno.tools.googlesearch import GoogleSearchTools
from agno.models.google import Gemini
import os
import json
import datetime
import re


class QuestionMaker:
    def __init__(self):
        # API key for Gemini model
        self.api_key = "AIzaSyBtsYZXU_L8-dfmq3aFmO-24tPBGQdhIbI"

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
                "Return the output in strict Markdown format with the following structure:",
                "# JEE {topics} Questions",
                "## Question [number]",
                "[question text]",
                "**Options:**",
                "1. [option 1]",
                "2. [option 2]",
                "3. [option 3]",
                "4. [option 4]",
                "",
                "**Correct Answer:** [option number]",
                "",
                "**Explanation:**",
                "[detailed explanation]",
                "",
                "Do not include any non-Markdown formatting or introductory text.",
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
                "Return the output in strict Markdown format with the following structure:",
                "# NEET {topics} Questions",
                "## Question [number]",
                "[question text]",
                "**Options:**",
                "1. [option 1]",
                "2. [option 2]",
                "3. [option 3]",
                "4. [option 4]",
                "",
                "**Correct Answer:** [option number]",
                "",
                "**Explanation:**",
                "[detailed explanation]",
                "",
                "Do not include any non-Markdown formatting or introductory text.",
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
            
        # Print for debugging
        print(f"Generating questions for {exam_type} {subject} on topics: {chapters_str}")
        
        try:
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

            # Validate and fix Markdown content
            content = self._ensure_markdown_format(content, exam_type, subject)

            # Save to file in temp directory
            filename = f"../temp/{exam_type}_{subject}_questions.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Successfully generated content with {len(content)} characters")
            return content
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            raise
            
    def _ensure_markdown_format(self, content, exam_type, subject):
        """
        Ensures the content is properly formatted in Markdown
        
        Args:
            content (str): The content to validate
            exam_type (str): The exam type (jee/neet)
            subject (str): The subject
            
        Returns:
            str: Properly formatted Markdown content
        """
        # Remove any non-Markdown introductory text
        content = re.sub(r'^.*?(?=# |## |\*\*Question)', '', content, flags=re.DOTALL)
        
        # If content doesn't start with a heading, add one
        if not content.strip().startswith('#'):
            content = f"# {exam_type.upper()} {subject.capitalize()} Questions\n\n" + content
            
        # Ensure questions are properly formatted
        content = re.sub(r'Question (\d+):', r'## Question \1', content)
        
        # Ensure options are properly formatted
        content = re.sub(r'\((\d+)\)', r'\1.', content)
        
        # Ensure proper spacing between sections
        content = re.sub(r'(\*\*Correct Answer:\*\*.*?)(\*\*Explanation:\*\*)', r'\1\n\n\2', content)
        content = re.sub(r'(\*\*Explanation:\*\*.*?)(?=## |$)', r'\1\n\n', content, flags=re.DOTALL)
        
        # Fix LaTeX expressions that might be malformed
        # Ensure inline math expressions have proper spacing
        content = re.sub(r'(?<!\$)\$(?!\$)([^$]+?)(?<!\$)\$(?!\$)', r' $\1$ ', content)
        
        # Ensure display math expressions are on their own lines with proper spacing
        content = re.sub(r'(?<!\n)\$\$', r'\n\n$$', content)
        content = re.sub(r'\$\$(?!\n)', r'$$\n\n', content)
        
        # Fix common LaTeX formatting issues
        content = re.sub(r'\\frac\s*{([^{}]+)}\s*{([^{}]+)}', r'\\frac{\1}{\2}', content)
        content = re.sub(r'\\sin\s+', r'\\sin ', content)
        content = re.sub(r'\\cos\s+', r'\\cos ', content)
        content = re.sub(r'\\tan\s+', r'\\tan ', content)
        
        # Ensure LaTeX subscripts and superscripts are properly formatted
        content = re.sub(r'_(\w+)(?!\})', r'_{\\text{\1}}', content)
        
        return content.strip()

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


# Test function to verify QuestionMaker functionality
if __name__ == "__main__":
    print("Running QuestionMaker test...")
    
    # Test parameters
    exam_type = "jee"
    subject = "physics"
    chapters = ["Mechanics", "Electrostatics"]
    num_questions = 2  # Keep small for quick testing
    
    try:
        print(f"Generating {num_questions} questions for {exam_type} {subject} on {', '.join(chapters)}")
        # Create QuestionMaker instance
        maker = QuestionMaker()
        
        # Generate content
        content = maker.generate_questions(exam_type, subject, chapters, num_questions)
        
        # Save content
        output_path = maker.save_question_paper(exam_type, subject, chapters, content)
        
        print(f"Questions generated successfully and saved to: {output_path}")
        print(f"Content preview: {content[:200]}...")
        
    except Exception as e:
        print(f"Error occurred during testing: {str(e)}")
        import traceback
        traceback.print_exc()

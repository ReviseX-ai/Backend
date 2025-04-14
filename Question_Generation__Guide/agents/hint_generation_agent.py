from agno.agent import Agent
from agno.models.google import Gemini

from dotenv import load_dotenv
import os
import logging
from typing import Optional

class HintGenerator:
    """A class for generating helpful hints for any type of question."""
    
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_reasoning: bool = True):
        """
        Initialize the HintGenerator.
        
        Args:
            model_id: The ID of the Gemini model to use
            enable_reasoning: Whether to enable reasoning for the model
        """
        load_dotenv()
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)
        
        self.agent = Agent(
            model=Gemini(id=model_id),
            reasoning=enable_reasoning,
            instructions="""
            You are an expert tutor with years of experience helping students across various subjects.
            Your task is to provide ONE clear, targeted hint for any question a student might ask.
            
            For each question:
            1. Carefully analyze the question to identify the core concept or knowledge required
            2. Create a single hint that guides the student toward figuring out the solution themselves
            3. Ensure your hint is specific enough to be helpful but vague enough to make the student think
            4. Focus on highlighting the key principles or approaches needed for that particular question
            5. Where appropriate, suggest a starting point or approach without giving away the answer
            
            Your hint should be 2-3 sentences at most, clear and concise.
            Avoid giving away the solution directly, but ensure the hint is substantial enough
            to help a struggling student make progress on their own.
            
            You will only be given the question, not the answer, so ensure your hint
            is based on guiding the student's problem-solving process rather than
            working backward from a solution.
            """
        )
    
    def generate_hint(self, question: str) -> str:
        """
        Generate a single focused hint for any type of question.
        
        Args:
            question: The question text
            
        Returns:
            A single hint string
        """
        self.logger.info(f"Generating hint for: {question[:50]}...")
        
        prompt_template = f"""
        Generate a single, focused hint for the following question.
        The hint should guide the student in the right direction without giving away too much.
        
        QUESTION: {question}
        
        Provide just ONE clear, concise hint (2-3 sentences) that will help the student
        understand the conceptual approach needed to solve this problem.
        Don't provide any other text or explanation, just the hint.
        """
        
        try:
            response = self.agent.run(prompt_template).content
            
            hint = self._clean_hint(response)
            self.logger.info(f"Successfully generated hint")
            return hint
                
        except Exception as e:
            self.logger.error(f"Error generating hint: {e}")
            return f"Unable to generate hint due to an error: {str(e)}"
    
    def _clean_hint(self, response: str) -> str:
        """
        Clean and format the hint from the raw response.
        
        Args:
            response: The raw response from the agent
            
        Returns:
            A cleaned hint string
        """
        import re
        
        cleaned = re.sub(r'^(hint:|\s*here\'?s\s+a\s+hint:|\s*hint\s+\d+:)', '', response, flags=re.IGNORECASE)
        
        cleaned = re.sub(r'[*_`#]', '', cleaned)
        
        cleaned = cleaned.strip()
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
            
        return cleaned

if __name__ == "__main__":
    hint_generator = HintGenerator()
    
    questions = [
        "Find the derivative of f(x) = x^3 * sin(x).",
        "What are the main causes of the French Revolution?",
        "How does photosynthesis work?",
        "Solve for x: 3x + 7 = 22",
        "What is the significance of the green light in The Great Gatsby?"
    ]
    
    for question in questions:
        hint = hint_generator.generate_hint(question=question)
        
        print("\nQuestion:", question)
        print("Hint:", hint)
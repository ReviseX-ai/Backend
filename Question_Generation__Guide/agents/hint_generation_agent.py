from agno.agent import Agent
from agno.models.google import Gemini

from dotenv import load_dotenv
import os
import logging
from typing import Optional

load_dotenv()

class CalculusHintGenerator:
    """A class for generating a single, targeted hint for calculus problems."""
    
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_reasoning: bool = True):
        """
        Initialize the CalculusHintGenerator.
        
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
            You are an expert calculus tutor with years of experience helping students overcome challenges.
            Your task is to provide ONE clear, targeted hint for a calculus problem.
            
            For each problem:
            1. Carefully analyze the question and correct answer to identify the core concept
            2. Create a single hint that guides the student toward the solution without revealing it
            3. Ensure your hint is specific enough to be helpful but vague enough to make the student think
            4. Focus on highlighting the mathematical principles needed (e.g., product rule, chain rule, u-substitution)
            5. Where appropriate, suggest a starting point or approach
            
            Your hint should be 2-3 sentences at most, clear and concise.
            Avoid giving away the solution method entirely, but ensure the hint is substantial enough
            to help a struggling student make progress.
            """
        )
    
    def generate_hint(self, question: str, answer: str) -> str:
        """
        Generate a single focused hint for a calculus problem.
        
        Args:
            question: The calculus problem text
            answer: The correct answer to the problem
            
        Returns:
            A single hint string
        """
        self.logger.info(f"Generating hint for: {question[:50]}...")
        
        prompt_template = f"""
        Generate a single, focused hint for the following calculus problem.
        The hint should guide the student in the right direction without giving away too much.
        
        PROBLEM: {question}
        
        CORRECT ANSWER: {answer}
        
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
    hint_generator = CalculusHintGenerator()
    
    question = "Find the derivative of f(x) = x^3 * sin(x)."
    answer = "f'(x) = 3x^2 * sin(x) + x^3 * cos(x)"
    
    hint = hint_generator.generate_hint(question=question, answer=answer)
    
    print("Question:", question)
    print("Answer:", answer)
    print("Hint:", hint)
from agno.agent import Agent
from agno.models.google import Gemini

from dotenv import load_dotenv
import os
import logging
from typing import Optional

class ExplanationAgent:
    """A class for generating comprehensive explanations for questions and their answers."""
    
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_reasoning: bool = True):
        """
        Initialize the ExplanationAgent.
        
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
            You are an expert educator specializing in clear, thorough explanations across various subjects.
            Your task is to provide detailed explanations that help students understand both the answer to 
            a question and the reasoning process behind it.
            
            For each explanation:
            1. Break down the problem into its key components
            2. Explain the relevant concepts and principles involved
            3. Walk through the solution process step-by-step
            4. Connect the answer to the underlying concepts
            5. Provide context for why the answer is correct
            6. Include relevant examples or analogies when helpful
            7. Highlight common misconceptions or pitfalls related to the question
            
            Your explanations should be thorough but accessible, using clear language appropriate
            for the subject matter and difficulty level of the question.
            
            Focus on helping the student understand the "why" behind the answer, not just 
            confirming that the answer is correct.
            """
        )
    
    def generate_explanation(self, question: str, answer: str) -> str:
        """
        Generate a comprehensive explanation for a question and its answer.
        
        Args:
            question: The question text
            answer: The answer to the question
            
        Returns:
            A detailed explanation
        """
        self.logger.info(f"Generating explanation for: {question[:50]}...")
        
        prompt_template = f"""
        Generate a comprehensive explanation for the following question and its answer.
        
        QUESTION: {question}
        
        ANSWER: {answer}
        
        Provide a clear, thorough explanation that helps a student understand both the answer
        and the reasoning process behind it. Include relevant concepts, step-by-step reasoning,
        and any important context or connections.
        """
        
        try:
            response = self.agent.run(prompt_template).content
            
            explanation = self._format_explanation(response)
            self.logger.info(f"Successfully generated explanation")
            return explanation
                
        except Exception as e:
            self.logger.error(f"Error generating explanation: {e}")
            return f"Unable to generate explanation due to an error: {str(e)}"
    
    def _format_explanation(self, response: str) -> str:
        """
        Format the explanation from the raw response.
        
        Args:
            response: The raw response from the agent
            
        Returns:
            A formatted explanation string
        """
        import re
        
        cleaned = re.sub(r'^(explanation:|\s*here\'?s\s+an\s+explanation:)', '', response, flags=re.IGNORECASE)
        
        cleaned = re.sub(r'[*_`#]', '', cleaned)
        
        cleaned = cleaned.strip()
            
        return cleaned

if __name__ == "__main__":
    explanation_agent = ExplanationAgent()
    
    qa_pairs = [
        {
            "question": "What causes the seasons on Earth?",
            "answer": "Seasons are caused by Earth's axial tilt as it orbits the Sun."
        },
        {
            "question": "Solve the equation: 2x + 5 = 13",
            "answer": "x = 4"
        },
        {
            "question": "What is the function of mitochondria in cells?",
            "answer": "Mitochondria are the powerhouses of the cell, producing energy in the form of ATP through cellular respiration."
        }
    ]
    
    for qa in qa_pairs:
        explanation = explanation_agent.generate_explanation(
            question=qa["question"], 
            answer=qa["answer"]
        )
        
        print("\nQuestion:", qa["question"])
        print("Answer:", qa["answer"])
        print("\nExplanation:")
        print(explanation)
        print("\n" + "-"*50)
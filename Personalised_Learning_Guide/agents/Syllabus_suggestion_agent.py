from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import chardet
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyllabusSuggestionAgent:
    def __init__(self):
        """
        Initializes the agent, loads environment variables, and sets up the AI model.
        """
        try:
            load_dotenv()
            self.agent = Agent(
                model=Gemini(id="gemini-2.0-flash-exp"),
                reasoning=True,
                markdown=True
            )
            logger.info("SyllabusSuggestionAgent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SyllabusSuggestionAgent: {str(e)}")
            raise

    def get_syllabus_suggestion(self, progress_tracker_response, psychometric_agent_response):
        """
        Generates syllabus suggestions based on progress and psychometric data.
        """
        try:
            prompt = self.generate_prompt(progress_tracker_response, psychometric_agent_response)
            logger.info("Generated prompt for syllabus suggestion")
            response = self.agent.run(prompt)
            logger.info("Received response from Gemini model")
            return response.content
        except Exception as e:
            logger.error(f"Error generating syllabus suggestion: {str(e)}")
            raise

    def generate_prompt(self, progress_tracker_response, psychometric_agent_response):
        """
        Constructs the prompt for the AI agent.
        """
        return f"""
        📚 **Ultimate Syllabus Mastery Plan** 📚

        Hey, Genius AI! 🚀 I need a rock-solid, ultra-efficient plan to complete my syllabus like a pro. Here's what you need to know:

        📌 **Current Progress & Strengths:**
        {progress_tracker_response}

        🧠 **Learning Style & Weaknesses:**
        {psychometric_agent_response}

        🔮 **Your Mission:**
        1️⃣ Prioritize topics based on difficulty, importance, and my strengths.
        2️⃣ Suggest an optimal learning sequence (which topics first and why).
        3️⃣ Recommend a revision strategy that locks in knowledge effectively.
        4️⃣ Include smart hacks for faster and deeper understanding.

        ⚡ **Format:**
        - 📆 **Study Plan:** (Week-wise or Day-wise breakdown, mostly related to which chapters to cover)
        - 🚀 **High-Yield Topics First:** (What to tackle ASAP)
        - 🔁 **Revision Blueprint:** (Best recall techniques + schedule)
        - 🎯 **Pro Tips:** (Any cool memory hacks, active recall tricks, etc.)

        Make it concise, actionable, and engaging. Let's crush this syllabus! 🔥
        """

    def get_syllabus_suggestion(self, progress_tracker_response, psychometric_agent_response):
        """
        Fetches the progress tracker and psychometric analysis, generates a prompt,
        and retrieves the AI-generated syllabus suggestion.
        :return: AI-generated syllabus completion plan as a string.
        """
        prompt = self.generate_prompt(progress_tracker_response, psychometric_agent_response)
        response = self.agent.run(prompt)
        return response.content

if __name__ == "__main__":
    agent = SyllabusSuggestionAgent()
    progress_tracker_response = read_file("progress_tracker.txt")
    psychometric_agent_response = read_file("psychometric_analysis.txt")
    syllabus_suggestion = agent.get_syllabus_suggestion(progress_tracker_response = progress_tracker_response, psychometric_agent_response=psychometric_agent_response)
    print(syllabus_suggestion)

from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import chardet
import os

temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "temp"))

def detect_encoding(file_path):
    """
        Detects the encoding of a given text file to ensure proper reading.
        :param file_path: Path to the file whose encoding needs to be detected.
        :return: Detected encoding type as a string.
    """
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
    return result["encoding"]

def read_file(file_name):
    """
        Reads the contents of a text file after detecting its encoding.
        :param file_name: Name of the file to read.
        :return: String content of the file.
    """
    file_path = os.path.join(temp_dir, file_name)
    encoding = detect_encoding(file_path)
    with open(file_path, "r", encoding=encoding) as file:
        return file.read()

class SyllabusSuggestionAgent:
    """
    A class-based implementation of an AI-powered syllabus suggestion agent.
    This agent reads progress tracking data and psychometric analysis,
    processes them, and generates an optimal study plan using the Gemini model.
    """

    def __init__(self):
        """
        Initializes the agent, loads environment variables, and sets up the AI model.
        """
        load_dotenv()
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash-exp"),
            reasoning=True,
            markdown=True
        )
        


    def generate_prompt(self, progress_tracker_response, psychometric_agent_response):
        """
        Constructs a well-structured and engaging prompt for the AI agent based on user data.
        :param progress_tracker_response: The progress tracker data.
        :param psychometric_agent_response: The psychometric analysis data.
        :return: A formatted prompt string.
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

        Make it concise, actionable, and engaging. Let’s crush this syllabus! 🔥
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

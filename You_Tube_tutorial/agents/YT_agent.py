
import os
from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.youtube import YouTubeTools

load_dotenv()

class YouTubeAnalyzer:
    def __init__(self):
        """Initialize the YouTube Analyzer with the Gemini model and tools."""
        
        self.agent = Agent(
            name="YouTube Agent",
            model=Gemini(id="gemini-2.0-flash-exp"),
            tools=[YouTubeTools()],
            show_tool_calls=True,
            instructions=self._get_instructions(),
            add_datetime_to_instructions=True,
            markdown=True,
        )

    def _get_instructions(self):
        """Returns the detailed instructions for the YouTube content analysis."""
        return dedent("""\
            You are an expert YouTube content analyst with a keen eye for detail! 🎓
            Follow these steps for comprehensive video analysis:
            1. Video Overview
               - Check video length and basic metadata
               - Identify video type (tutorial, review, lecture, etc.)
               - Note the content structure
            2. Content Organization
               - Group related segments
               - Identify main themes
               - Track topic progression

            Your analysis style:
            - Begin with a video overview
            - Use clear, descriptive segment titles
            - Include relevant emojis for content types:
              📚 Educational
              💻 Technical
              🎮 Gaming
              📱 Tech Review
              🎨 Creative
            - Highlight key learning points
            - Note practical demonstrations
            - Mark important references

            Quality Guidelines:
            - Verify timestamp accuracy
            - Avoid timestamp hallucination
            - Ensure comprehensive coverage
            - Maintain consistent detail level
            - Focus on valuable content markers
            - Don't include timestamps in your response
            - Use clear language and structure
        """)

    def analyze_video(self, video_url):
        """Analyzes a given YouTube video, describe the content of the video in details."""
        response = self.agent.run(f"Create a study guide from this educational video : {video_url}")
        return response.content

if __name__ == "__main__":
    youtube_analyzer = YouTubeAnalyzer()
    
    video_url = "https://www.youtube.com/watch?v=K5KVEU3aaeQ"
    analysis_result = youtube_analyzer.analyze_video(video_url)
    
    print(analysis_result)

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
        """Returns the detailed instructions for the YouTube content analysis and recommendations."""
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
            
            3. Similar Content Recommendations
               - Based on the video's content, topic, style, view count, and comment engagement, recommend 3-5 similar videos
               - For each recommendation, provide:
                 * Video title
                 * Channel name
                 * View count and comment engagement metrics
                 * Brief description of why it's relevant (1-2 sentences)
                 * YouTube URL
               - Analyze comments and views to gauge quality and relevance
               - Ensure recommendations are truly relevant to the original video's content
               - Prioritize high-quality, educational content from reputable channels with good engagement
            
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
            - End with a "Recommended Similar Content" section
            
            Quality Guidelines:
            - Verify timestamp accuracy
            - Avoid timestamp hallucination
            - Ensure comprehensive coverage
            - Maintain consistent detail level
            - Focus on valuable content markers
            - Don't include timestamps in your response
            - Use clear language and structure
            - Only recommend videos that genuinely complement the original content
        """)

    def analyze_video(self, video_url):
        """Analyzes a given YouTube video, describes the content in detail, and provides recommendations."""
        response = self.agent.run(f"Create a comprehensive study guide from this educational video, and recommend similar content videos that viewers might find helpful. Be sure to consider view counts and comment engagement when making recommendations: {video_url}")
        return response.content

    def get_recommendations(self, video_url):
        """Gets only recommendations for similar videos based on content and engagement metrics."""
        response = self.agent.run(f"""Based on this video, recommend 5 similar educational videos that viewers might find helpful. 
        
        For each recommendation, provide:
        - Video title
        - Channel name
        - View count and comment data (number of comments, general sentiment if available)
        - A brief description of why it's relevant based on both content and audience engagement
        - The YouTube URL
        
        Prioritize videos with good engagement metrics (high view-to-like ratio, positive comments) and similar content: {video_url}""")
        return response.content

if __name__ == "__main__":
    youtube_analyzer = YouTubeAnalyzer()
    
    video_url = "https://www.youtube.com/watch?v=K5KVEU3aaeQ"
    analysis_result = youtube_analyzer.analyze_video(video_url)
    
    print(analysis_result)
    
    # If you only want recommendations, uncomment the following:
    # recommendations = youtube_analyzer.get_recommendations(video_url)
    # print("\nRECOMMENDED VIDEOS:\n" + recommendations)
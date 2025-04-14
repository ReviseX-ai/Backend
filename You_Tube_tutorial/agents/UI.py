import streamlit as st
import re
from PIL import Image
import requests
from io import BytesIO
import time
from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.youtube import YouTubeTools
from YT_agent import YouTubeAnalyzer

load_dotenv()


st.set_page_config(
    page_title="YouTube Study Guide Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Primary color theme */
    :root {
        --primary-color: #1565c0;
        --secondary-color: #1976d2;
        --background-color: #f5f9ff;
        --text-color: #333333;
    }
    
    /* Main container styling */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #0d47a1;
    }
    
    /* Card container for inputs */
    .stApp {
        background-color: var(--background-color);
    }
    
    .css-1d391kg, .css-12oz5g7 {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #1565c0;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        border: none;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #0d47a1;
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    
    .badge-education {
        background-color: #e3f2fd;
        color: #0d47a1;
    }
    
    .badge-tech {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    
    .badge-gaming {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
    
    .badge-review {
        background-color: #fff3e0;
        color: #e65100;
    }
    
    .badge-creative {
        background-color: #e8eaf6;
        color: #3f51b5;
    }
    
    /* Video info styling */
    .video-info {
        display: flex;
        align-items: flex-start;
        margin: 20px 0;
        padding: 15px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    .video-details {
        margin-left: 20px;
    }
    
    /* Study guide styling */
    .study-guide {
        background-color: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        margin-top: 20px;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def extract_youtube_id(url):
    """Extract the YouTube video ID from a URL."""
    youtube_regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(youtube_regex, url)
    return match.group(1) if match else None

def get_youtube_thumbnail(video_id):
    """Get the YouTube video thumbnail URL."""
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

def main():
    st.markdown("<h1 style='text-align: center; color: #1565c0;'>YouTube Study Guide Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Transform any educational YouTube video into a comprehensive study guide</p>", unsafe_allow_html=True)
    
    with st.container():
        st.subheader("Enter YouTube Video URL")
        default_url = "https://www.youtube.com/watch?v=K5KVEU3aaeQ"
        video_url = st.text_input("", value=default_url, placeholder="https://www.youtube.com/watch?v=...")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            analyze_button = st.button("Generate Study Guide")
    
    if 'analysis_completed' not in st.session_state:
        st.session_state.analysis_completed = False
    
    if analyze_button:
        video_id = extract_youtube_id(video_url)
        
        if video_id:
            with st.spinner("Analyzing video content... This might take a minute."):
                youtube_analyzer = YouTubeAnalyzer()
                
                try:
                    analysis_result = youtube_analyzer.analyze_video(video_url)
                    st.session_state.analysis_result = analysis_result
                    st.session_state.video_id = video_id
                    st.session_state.analysis_completed = True
                    st.experimental_rerun()
                except Exception as e:
                    print("check")
                    # st.error(f"Error analyzing video: {str(e)}")
        else:
            st.error("Invalid YouTube URL. Please enter a valid YouTube video link.")
    
    if st.session_state.get('analysis_completed', False):
        video_id = st.session_state.video_id
        analysis_result = st.session_state.analysis_result        
        thumbnail_url = get_youtube_thumbnail(video_id)
        st.markdown("<h2 style='color: #1565c0;'>Your Study Guide</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://via.placeholder.com/320x180", width=300)
        
        with col2:
            content_types = []
            if "educational" in analysis_result.lower() or "learning" in analysis_result.lower():
                content_types.append("education")
            if "technical" in analysis_result.lower() or "code" in analysis_result.lower():
                content_types.append("tech")
            if "game" in analysis_result.lower() or "gaming" in analysis_result.lower():
                content_types.append("gaming")
            if "review" in analysis_result.lower():
                content_types.append("review")
            if "creative" in analysis_result.lower() or "art" in analysis_result.lower():
                content_types.append("creative")
            
            if not content_types:
                content_types.append("education")
            
            badges_html = ""
            for content_type in content_types:
                if content_type == "education":
                    badges_html += '<span class="badge badge-education">📚 Educational</span>'
                elif content_type == "tech":
                    badges_html += '<span class="badge badge-tech">💻 Technical</span>'
                elif content_type == "gaming":
                    badges_html += '<span class="badge badge-gaming">🎮 Gaming</span>'
                elif content_type == "review":
                    badges_html += '<span class="badge badge-review">📱 Review</span>'
                elif content_type == "creative":
                    badges_html += '<span class="badge badge-creative">🎨 Creative</span>'
            
            video_title = "Educational Content" # In a real implementation, you'd extract this
            st.markdown(f"<h3>{video_title}</h3>", unsafe_allow_html=True)
            st.markdown(badges_html, unsafe_allow_html=True)
        
        st.markdown(analysis_result)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.download_button(
            label="Download Study Guide",
            data=analysis_result,
            file_name="youtube_study_guide.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()
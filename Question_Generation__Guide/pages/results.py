import streamlit as st
import base64
import json
import os
import io
import glob
from pathlib import Path
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import pdfkit
from PIL import Image

def render_latex(content):
    """Prepare content for better LaTeX rendering in Streamlit"""
    # This function doesn't modify the content but is kept for possible future enhancements
    return content

def create_download_link(content, filename, text="Download PDF"):
    """Create a download link for content"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href

def get_latest_questions_file():
    """Get the most recent questions file from the temp directory"""
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
    content_files = glob.glob(os.path.join(temp_dir, "*_content.md"))
    
    if not content_files:
        return None
        
    # Get the most recent file based on modification time
    latest_file = max(content_files, key=os.path.getmtime)
    
    # Check if file has content
    if os.path.getsize(latest_file) > 0:
        return latest_file
    return None

def load_questions_from_file(file_path):
    """Load questions from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for metadata file
        metadata_file = file_path.replace('_content.md', '_metadata.json')
        metadata = {}
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
        return content, metadata
    except Exception as e:
        st.error(f"Error loading questions: {str(e)}")
        return None, None

def generate_pdf(markdown_content, metadata):
    """Generate PDF from markdown content"""
    try:
        # Use pdfkit to convert markdown to PDF
        pdf_options = {
            'page-size': 'A4',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in',
            'encoding': 'UTF-8',
        }
        
        # Convert markdown to HTML with styling
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; text-align: center; }}
                h2 {{ color: #3498db; margin-top: 20px; }}
                .metadata {{ text-align: center; color: #7f8c8d; margin-bottom: 20px; }}
                .question {{ margin-bottom: 30px; }}
                .options {{ margin-left: 20px; }}
                .explanation {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; }}
            </style>
            <script type="text/x-mathjax-config">
                MathJax.Hub.Config({{
                    tex2jax: {{inlineMath: [['$','$'], ['\\\\(','\\\\)']]}}
                }});
            </script>
            <script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"></script>
        </head>
        <body>
            <div class="metadata">
                <strong>{metadata.get('exam', '').upper()}</strong> | 
                <strong>{metadata.get('subject', '').capitalize()}</strong> | 
                {metadata.get('numQuestions', 0)} questions<br>
                <small>Topics: {', '.join(metadata.get('topics', []))}</small>
            </div>
            {markdown_content}
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        pdf_content = pdfkit.from_string(html_content, False, options=pdf_options)
        return pdf_content
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

def display_math_content(content):
    """Display content with proper math rendering using custom components"""
    # Using streamlit components to render math with MathJax
    math_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"></script>
        <script type="text/x-mathjax-config">
            MathJax.Hub.Config({{
                tex2jax: {{inlineMath: [['$','$'], ['\\\\(','\\\\)']], displayMath: [['$$','$$'], ['\\\\[','\\\\]']]}},
                messageStyle: "none",
                displayAlign: "left",
                "HTML-CSS": {{ linebreaks: {{ automatic: true }}, scale: 100, styles: {{".MathJax_Display": {{ margin: "0.5em 0" }}}} }}
            }});
        </script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: white;
                background-color: #000000;
                padding: 20px;
                max-width: 100%;
                overflow-x: auto;
            }}
            h1, h2, h3, h4, h5, h6, strong {{
                color: white;
            }}
            p {{
                margin-bottom: 1em;
            }}
            .MathJax {{
                color: white !important;
            }}
        </style>
    </head>
    <body>
        <div id="content">
            {content}
        </div>
        <script>
            // Trigger MathJax to reprocess the content
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, "content"]);
        </script>
    </body>
    </html>
    """
    
    # Display using components
    components.html(math_html, height=800, scrolling=True)

def main():
    st.set_page_config(
        page_title="Generated Questions - BharatGen",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # Title
    st.markdown("# Generated Questions")
    
    # Check if we have generated questions in session state
    if not st.session_state.get('generated_questions'):
        # Try to load from latest file
        latest_file = get_latest_questions_file()
        if latest_file:
            content, metadata = load_questions_from_file(latest_file)
            if content:
                st.session_state.generated_questions = content
                if metadata:
                    st.session_state.question_metadata = {
                        "exam": metadata.get("exam_type", ""),
                        "subject": metadata.get("subject", ""),
                        "topics": metadata.get("chapters", []),
                        "numQuestions": len(content.split("## Question")) - 1  # Count questions
                    }
                else:
                    # Create basic metadata
                    st.session_state.question_metadata = {
                        "exam": "exam",
                        "subject": "subject",
                        "topics": [],
                        "numQuestions": len(content.split("## Question")) - 1
                    }
        else:
            st.warning("No generated questions found. Please go back and generate new questions.")
            if st.button("← Back to Question Generator"):
                st.switch_page("streamlit_app.py")
            return
    
    # Get content and metadata from session state
    markdown_content = st.session_state.generated_questions
    metadata = st.session_state.question_metadata
    
    # Debug info
    st.write(f"Content length: {len(markdown_content)} characters")
    st.write(f"Questions detected: {markdown_content.count('## Question')}")
    
    # Display metadata
    if metadata:
        try:
            exam_type = metadata.get('exam', '').upper()
            subject = metadata.get('subject', '').capitalize()
            num_questions = metadata.get('numQuestions', 0)
            topics = metadata.get('topics', [])
            
            st.markdown(
                f"<div style='text-align: center; color: #7f8c8d;'>"
                f"<strong>{exam_type}</strong> | <strong>{subject}</strong> | {num_questions} questions<br>"
                f"<small>Topics: {', '.join(topics)}</small>"
                f"</div>",
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error displaying metadata: {str(e)}")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Generator", use_container_width=True):
            st.switch_page("streamlit_app.py")
    
    # Add print and download buttons
    with col2:
        if st.button("Print Questions", use_container_width=True):
            st.markdown(
                """
                <script>
                function printContent() {
                    window.print();
                }
                </script>
                <button onclick="printContent()">Print</button>
                """,
                unsafe_allow_html=True
            )
            st.info("Use your browser's print function (Ctrl+P or Cmd+P) to print the questions.")
    
    with col3:
        if st.button("Download PDF", use_container_width=True):
            try:
                # Generate PDF
                pdf_content = generate_pdf(markdown_content, metadata)
                
                if pdf_content:
                    # Create download button for PDF
                    filename = f"{metadata.get('exam', 'exam').upper()}_{metadata.get('subject', 'subject')}_questions.pdf"
                    
                    # Create a download button
                    st.download_button(
                        label="Download PDF File",
                        data=pdf_content,
                        file_name=filename,
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error preparing PDF: {str(e)}")
    
    # Display questions with LaTeX rendering
    st.markdown("---")
    
    # Custom styling for the markdown content
    st.markdown("""
    <style>
    .questions-container {
        background-color: #000000;
        color: white;
        padding: 20px;
        border-radius: 5px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Ensure LaTeX is properly rendered
    processed_content = render_latex(markdown_content)
    
    # Display content in a container with black background
    st.markdown('<div class="questions-container">', unsafe_allow_html=True)
    display_math_content(processed_content)
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
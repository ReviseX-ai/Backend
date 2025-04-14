import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import os
import base64
import glob
import re
from pathlib import Path
import time
import markdown
import sys

# Define the API URL
API_URL = "http://127.0.0.1:5001/api"

# Add parent directory to path to import the hint generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.hint_generation_agent import HintGenerator

TOPICS = {
    "physics": {
        "jee": [
            'Mechanics', 'Kinematics', 'Laws of Motion', 'Work, Energy and Power', 
            'Rotational Motion', 'Gravitation', 'Properties of Solids and Liquids', 
            'Thermodynamics', 'Kinetic Theory of Gases', 'Oscillations and Waves', 
            'Electrostatics', 'Current Electricity', 'Magnetic Effects of Current', 
            'Electromagnetic Induction', 'Alternating Current', 'Electromagnetic Waves', 
            'Optics', 'Dual Nature of Matter and Radiation', 'Atoms and Nuclei', 
            'Electronic Devices', 'Communication Systems'
        ],
        "neet": [
            'Physical World and Measurement', 'Kinematics', 'Laws of Motion', 
            'Work, Energy and Power', 'Rotational Motion', 'Gravitation', 
            'Properties of Solids and Liquids', 'Thermodynamics', 'Kinetic Theory of Gases', 
            'Oscillations and Waves', 'Electrostatics', 'Current Electricity', 
            'Magnetic Effects of Current', 'Electromagnetic Induction', 'Alternating Current', 
            'Electromagnetic Waves', 'Optics', 'Dual Nature of Matter and Radiation', 
            'Atoms and Nuclei', 'Electronic Devices'
        ]
    },
    "chemistry": {
        "jee": [
            'Some Basic Concepts of Chemistry', 'Structure of Atom', 'Classification of Elements', 
            'Chemical Bonding and Molecular Structure', 'States of Matter', 'Thermodynamics', 
            'Equilibrium', 'Redox Reactions', 'Hydrogen', 's-Block Elements', 'p-Block Elements', 
            'Organic Chemistry - Basic Principles', 'Hydrocarbons', 'Environmental Chemistry', 
            'Solid State', 'Solutions', 'Electrochemistry', 'Chemical Kinetics', 
            'Surface Chemistry', 'd and f Block Elements', 'Coordination Compounds', 
            'Haloalkanes and Haloarenes', 'Alcohols, Phenols and Ethers', 
            'Aldehydes, Ketones and Carboxylic Acids', 'Amines', 'Biomolecules', 
            'Polymers', 'Chemistry in Everyday Life'
        ],
        "neet": [
            'Some Basic Concepts of Chemistry', 'Structure of Atom', 'Classification of Elements', 
            'Chemical Bonding and Molecular Structure', 'States of Matter', 'Thermodynamics', 
            'Equilibrium', 'Redox Reactions', 'Hydrogen', 's-Block Elements', 'p-Block Elements', 
            'Organic Chemistry - Basic Principles', 'Hydrocarbons', 'Environmental Chemistry', 
            'Solid State', 'Solutions', 'Electrochemistry', 'Chemical Kinetics', 
            'Surface Chemistry', 'd and f Block Elements', 'Coordination Compounds', 
            'Haloalkanes and Haloarenes', 'Alcohols, Phenols and Ethers', 
            'Aldehydes, Ketones and Carboxylic Acids', 'Amines', 'Biomolecules', 
            'Polymers', 'Chemistry in Everyday Life'
        ]
    },
    "mathematics": {
        "jee": [
            'Sets, Relations and Functions', 'Complex Numbers and Quadratic Equations', 
            'Matrices and Determinants', 'Permutations and Combinations', 'Mathematical Induction', 
            'Binomial Theorem', 'Sequences and Series', 'Limit, Continuity and Differentiability', 
            'Integral Calculus', 'Differential Equations', 'Coordinate Geometry', 
            'Three Dimensional Geometry', 'Vector Algebra', 'Statistics and Probability', 
            'Trigonometry', 'Mathematical Reasoning'
        ]
    },
    "biology": {
        "neet": [
            'Diversity in Living World', 'Structural Organisation in Animals and Plants', 
            'Cell Structure and Function', 'Plant Physiology', 'Human Physiology', 
            'Reproduction', 'Genetics and Evolution', 'Biology and Human Welfare', 
            'Biotechnology and its Applications', 'Ecology and Environment'
        ]
    }
}

@st.cache_resource
def get_hint_generator():
    return HintGenerator()

def extract_questions_from_markdown(markdown_content):
    """
    Extract questions, options, and correct answers from markdown content
    
    Returns:
        List of dictionaries with question details
    """
    questions = []
    
    question_blocks = re.split(r'## Question \d+', markdown_content)
    
    if question_blocks and not question_blocks[0].strip().startswith('**Options:**'):
        question_blocks = question_blocks[1:]
    
    for i, block in enumerate(question_blocks):
        if not block.strip():
            continue
            
        # Extract question text - everything before "**Options:**"
        question_match = re.search(r'(.*?)(?=\*\*Options:\*\*)', block, re.DOTALL)
        if not question_match:
            continue
            
        question_text = question_match.group(1).strip()
        
        # Extract options
        options_match = re.search(r'\*\*Options:\*\*(.*?)(?=\*\*Correct Answer:\*\*)', block, re.DOTALL)
        if not options_match:
            continue
            
        options_text = options_match.group(1).strip()
        options = []
        
        # Parse options (1. Option text)
        for opt_match in re.finditer(r'(\d+)\.\s+(.*?)(?=\n\d+\.|\n\n|\Z)', options_text, re.DOTALL):
            opt_num = opt_match.group(1)
            opt_text = opt_match.group(2).strip()
            options.append((opt_num, opt_text))
        
        # Extract correct answer
        correct_match = re.search(r'\*\*Correct Answer:\*\*\s*(\d+)', block)
        correct_answer = correct_match.group(1) if correct_match else ""
        
        # Extract explanation
        explanation_match = re.search(r'\*\*Explanation:\*\*(.*?)(?=## Question \d+|\Z)', block, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else ""
        
        questions.append({
            'question_number': i + 1,
            'question_text': question_text,
            'options': options,
            'correct_answer': correct_answer,
            'explanation': explanation
        })
    
    return questions

def improve_latex_rendering(text):
    """
    Improve the rendering of LaTeX expressions to make them more readable
    
    Args:
        text: The text containing LaTeX expressions
        
    Returns:
        Text with improved LaTeX expressions
    """
    if not text:
        return text
        
    # Fix common LaTeX notation issues
    # Replace \text{} with regular text
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    
    # Add proper spacing around operators in math mode
    text = re.sub(r'([0-9])([a-zA-Z])', r'\1 \2', text)  # Add space between number and variable
    
    # Make sure there are spaces around inline math delimiters for better rendering
    text = re.sub(r'(?<!\s)\$(?!\$)', r' $', text)  # Add space before $
    text = re.sub(r'(?<!\$)\$(?!\s)', r'$ ', text)  # Add space after $
    
    # Improve display math readability
    text = re.sub(r'\$\$(.*?)\$\$', r'\n\n$$\1$$\n\n', text, flags=re.DOTALL)
    
    # Fix vector notation to be more readable
    text = re.sub(r'\\vec\{([^}]+)\}', r'\\vec{\1}', text)
    text = re.sub(r'\\hat\{([^}]+)\}', r'\\hat{\1}', text)
    
    # Fix subscripts and superscripts
    text = re.sub(r'\_\{([^}]+)\}', r'_{\\text{\1}}', text)
    text = re.sub(r'\^\{([^}]+)\}', r'^{\\text{\1}}', text)
    
    # Ensure fractions are properly formatted
    text = re.sub(r'\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'\\frac{\1}{\2}', text)
    
    return text

def parse_latex_in_text(text):
    """Make LaTeX expressions properly renderable by Streamlit markdown"""
    if not text:
        return text
        
    # Improve LaTeX rendering
    text = improve_latex_rendering(text)
    
    return text

def display_math_with_mathjax(text_content):
    """
    Display text with mathematical expressions using MathJax
    
    Args:
        text_content: The text with LaTeX expressions
    
    Returns:
        HTML component with properly rendered math
    """
    # Process text to improve LaTeX rendering
    processed_text = improve_latex_rendering(text_content)
    
    # Break the string into multiple parts to avoid f-string nesting issues
    base_html = f"""
    <div style="background-color: white; padding: 15px; border-radius: 8px; font-family: Arial, sans-serif;">
        <div id="math-content" style="font-size: 1.1rem; line-height: 1.6; color: #333;">
            {processed_text}
        </div>
    </div>
    """
    
    # MathJax script source
    mathjax_src = """
    <script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"></script>
    """
    
    # MathJax configuration - separate from f-string to avoid nesting issues
    mathjax_config = """
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
            tex2jax: {
                inlineMath: [['$','$'], ['\\\\(','\\\\)']],
                displayMath: [['$$','$$'], ['\\\\[','\\\\]']],
                processEscapes: true,
                processEnvironments: true
            },
            TeX: { 
                equationNumbers: { autoNumber: "AMS" },
                extensions: ["AMSmath.js", "AMSsymbols.js"]
            },
            "HTML-CSS": { 
                availableFonts: ["TeX"],
                scale: 110,
                linebreaks: { automatic: true },
                styles: {
                    ".MathJax": {
                        "font-size": "110%",
                        "color": "#333"
                    },
                    ".MathJax_Display": {
                        margin: "0.8em 0"
                    }
                }
            },
            SVG: { linebreaks: { automatic: true } },
            messageStyle: "none"
        });
        MathJax.Hub.Queue(["Typeset", MathJax.Hub, "math-content"]);
    </script>
    """
    
    # Combine all parts
    mathjax_html = base_html + mathjax_src + mathjax_config
    
    # Calculate appropriate height based on content length
    line_count = len(text_content.split('\n'))
    height = 150 + (line_count * 25)  # Base height + additional height per line
    
    # Render the HTML with MathJax
    components.html(mathjax_html, height=height, scrolling=True)

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

# Add JSON storage functionality and UI improvements
def save_responses_to_json(user_answers, questions, metadata):
    """Save user responses to a JSON file"""
    
    # Create a directory to store response data if it doesn't exist
    responses_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "responses")
    os.makedirs(responses_dir, exist_ok=True)
    
    # Format timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Create response data
    response_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": metadata,
        "questions": []
    }
    
    # Add each question with user response
    for q in questions:
        q_num = q['question_number']
        response_data["questions"].append({
            "question_number": q_num,
            "question_text": q['question_text'],
            "options": q['options'],
            "correct_answer": q['correct_answer'],
            "user_answer": user_answers.get(q_num),
            "is_correct": user_answers.get(q_num) == q['correct_answer']
        })
    
    # Save to file
    filename = f"{metadata.get('exam', 'quiz')}_{metadata.get('subject', 'general')}_{timestamp}.json"
    file_path = os.path.join(responses_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(response_data, f, indent=2, ensure_ascii=False)
    
    return file_path

def main():
    st.set_page_config(
        page_title="BharatGen Question Generator",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # Add custom styling with improved white and blue color scheme
    st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        padding: 2rem;
        background-color: #ffffff;
        color: #333;
    }
    
    /* Button Styling - All buttons blue */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        padding: 0.7rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        background-color: #1976D2 !important;
        color: white !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        background-color: #1565C0 !important;
    }
    
    /* Primary and secondary button distinction through opacity */
    button[kind="secondary"] {
        background-color: #1976D2 !important;
        opacity: 0.8;
    }
    
    /* Big buttons for JEE/NEET */
    .big-button button {
        height: 80px !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #1565C0;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    h1 {
        font-size: 2.2rem;
        border-bottom: 2px solid #E3F2FD;
        padding-bottom: 0.5rem;
    }
    
    h2 {
        font-size: 1.7rem;
        margin-top: 1.5rem;
    }
    
    h3 {
        font-size: 1.3rem;
    }
    
    /* Card elements */
    .card {
        padding: 1.5rem;
        border-radius: 12px;
        background-color: #f9fbff;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border: 1px solid #e3f2fd;
    }
    
    /* Question Cards - Blue theme & fix for white boxes */
    .question-card {
        background-color: #f9fbff;
        color: #333;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #1976D2;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .question-text {
        font-size: 1.1rem;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    /* Radio button options - Fix for white boxes */
    div.row-widget.stRadio > div {
        background-color: transparent !important;
    }
    
    div.row-widget.stRadio > div > label {
        background-color: #f9fbff !important;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.8rem;
        transition: all 0.2s ease;
    }
    
    div.row-widget.stRadio > div > label:hover {
        border-color: #1976D2;
        box-shadow: 0 2px 8px rgba(25, 118, 210, 0.1);
        transform: translateY(-2px);
    }
    
    /* Ensure no white boxes appear in radio options */
    div.row-widget.stRadio > div > div {
        background-color: transparent !important;
    }
    
    .option-text {
        margin-left: 10px;
    }
    
    /* Explanation Box - Blue theme */
    .explanation-box {
        background-color: #e3f2fd;
        padding: 1.2rem;
        border-radius: 8px;
        margin-top: 1rem;
        border-left: 4px solid #1976D2;
        color: #333;
    }
    
    /* Hint Box - Blue theme */
    .hint-box {
        background-color: #e1f5fe;
        color: #0277bd;
        padding: 1.2rem;
        border-radius: 8px;
        margin-top: 1rem;
        border-left: 4px solid #0277bd;
    }
    
    /* Answer styling */
    .correct-answer {
        color: #2E7D32;
        font-weight: bold;
        padding: 0.5rem;
        background-color: #E8F5E9;
        border-radius: 4px;
        display: inline-block;
    }
    
    .incorrect-answer {
        color: #C62828;
        font-weight: bold;
        padding: 0.5rem;
        background-color: #FFEBEE;
        border-radius: 4px;
        display: inline-block;
    }
    
    /* Score Display - Blue theme */
    .score-display {
        font-size: 1.2rem;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        text-align: center;
        font-weight: 600;
    }
    
    /* Multiselect - Blue theme */
    div.stMultiSelect > div[data-baseweb="select"] {
        background-color: #f9fbff;
        border-radius: 8px;
    }
    
    div.stMultiSelect div[role="listbox"] {
        background-color: #f9fbff;
    }
    
    div.stMultiSelect span[role="option"]:hover {
        background-color: #e3f2fd;
    }
    
    div.stMultiSelect div[data-baseweb="tag"] {
        background-color: #1976D2 !important;
    }
    
    div.stMultiSelect div[data-baseweb="tag"] span {
        color: white !important;
    }
    
    /* Slider - Blue theme */
    div.stSlider > div > div {
        background-color: #bbdefb !important;
    }
    
    div.stSlider > div > div > div {
        background-color: #1976D2 !important;
    }
    
    /* Fixing the blue box issue and white boxes after options */
    #math-content {
        background-color: transparent !important;
        padding: 0 !important;
        border-radius: 0 !important;
        margin: 0 !important;
    }
    
    /* Make math rendering stand out less */
    .stComponentMixins {
        background-color: transparent !important;
    }
    
    /* Clean up spacing */
    .element-container {
        margin-bottom: 1rem !important;
    }
    
    /* Remove default white backgrounds in components */
    .stRadio > div, .stCheckbox > div, .stMultiSelect > div {
        background-color: transparent !important;
    }
    
    /* Fix white boxes above questions */
    .stMarkdown {
        background-color: transparent !important;
    }
    
    /* Success message styling */
    .success-box {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #2e7d32;
        font-weight: 500;
    }
    
    /* Error message styling */
    .error-box {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #c62828;
        font-weight: 500;
    }
    
    /* Fix white background for all divs */
    div[data-testid="stVerticalBlock"] {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for storing selections and hints
    if 'exam_selected' not in st.session_state:
        st.session_state.exam_selected = False
        st.session_state.exam_type = None
        
    if 'subject_selected' not in st.session_state:
        st.session_state.subject_selected = False
        st.session_state.subject = None
    
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = None
        st.session_state.question_metadata = None
        st.session_state.parsed_questions = None
        st.session_state.user_answers = {}
        st.session_state.show_results = False
        st.session_state.submitted = False
        st.session_state.hints = {}  # Store hints for questions
        st.session_state.responses_saved = False  # Track if responses were saved
    
    # Check if there's a recently generated question file
    latest_file = get_latest_questions_file()
    if latest_file and not st.session_state.generated_questions:
        content, metadata = load_questions_from_file(latest_file)
        if content and metadata:
            st.session_state.generated_questions = content
            st.session_state.question_metadata = {
                "exam": metadata.get("exam_type", ""),
                "subject": metadata.get("subject", ""),
                "topics": metadata.get("chapters", []),
                "numQuestions": len(content.split("## Question")) - 1  # Count questions
            }
            # Parse questions
            st.session_state.parsed_questions = extract_questions_from_markdown(content)
            # Initialize answers dict
            st.session_state.user_answers = {q['question_number']: None for q in st.session_state.parsed_questions}
            # Initialize hints dict
            st.session_state.hints = {q['question_number']: None for q in st.session_state.parsed_questions}
    
    # App title and description
    st.markdown("# BharatGen Question Generator")
    st.markdown("Generate personalized practice questions for JEE and NEET preparation")
    
    # If questions already generated, show them
    if st.session_state.generated_questions and st.session_state.parsed_questions:
        st.markdown("## Answer Generated Questions")
        
        # Display metadata
        if st.session_state.question_metadata:
            exam_type = st.session_state.question_metadata.get('exam', '').upper()
            subject = st.session_state.question_metadata.get('subject', '').capitalize()
            topics = st.session_state.question_metadata.get('topics', [])
            
            st.markdown(
                f"<div style='text-align: center; margin-bottom: 1.5rem; padding: 1rem; background-color: #e3f2fd; border-radius: 10px;'>"
                f"<strong>{exam_type}</strong> | <strong>{subject}</strong> | "
                f"{len(st.session_state.parsed_questions)} questions<br>"
                f"<small>Topics: {', '.join(topics)}</small>"
                f"</div>",
                unsafe_allow_html=True
            )
        
        # Add buttons to start new generation or show results
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate New Questions", type="secondary", use_container_width=True):
                # Reset state for new questions
                st.session_state.generated_questions = None
                st.session_state.question_metadata = None
                st.session_state.parsed_questions = None
                st.session_state.user_answers = {}
                st.session_state.hints = {}
                st.session_state.show_results = False
                st.session_state.submitted = False
                st.session_state.responses_saved = False
                st.rerun()
        
        with col2:
            if not st.session_state.submitted:
                submit_button = st.button("Submit Answers", type="primary", use_container_width=True)
                if submit_button:
                    st.session_state.submitted = True
                    st.session_state.show_results = True
                    
                    # Save responses to JSON
                    saved_path = save_responses_to_json(
                        st.session_state.user_answers, 
                        st.session_state.parsed_questions, 
                        st.session_state.question_metadata
                    )
                    st.session_state.responses_saved = saved_path
                    
                    st.rerun()
            else:
                retry_button = st.button("Try Again", type="primary", use_container_width=True)
                if retry_button:
                    st.session_state.submitted = False
                    st.session_state.show_results = False
                    st.session_state.user_answers = {q['question_number']: None for q in st.session_state.parsed_questions}
                    st.rerun()
        
        # If responses were saved, show success message
        if st.session_state.responses_saved and st.session_state.submitted:
            st.markdown(
                f"<div class='success-box'>"
                f"✓ Your responses have been saved successfully!"
                f"</div>",
                unsafe_allow_html=True
            )
        
        # Show score if results should be displayed
        if st.session_state.show_results:
            correct_count = 0
            total_questions = len(st.session_state.parsed_questions)
            
            for q in st.session_state.parsed_questions:
                if st.session_state.user_answers.get(q['question_number']) == q['correct_answer']:
                    correct_count += 1
            
            score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            
            # Determine score color based on performance
            if score_percentage >= 80:
                score_color = "#4CAF50"  # Green
            elif score_percentage >= 60:
                score_color = "#FB8C00"  # Orange
            else:
                score_color = "#F44336"  # Red
                
            st.markdown(
                f"<div class='score-display' style='background-color: {score_color}; color: white;'>"
                f"Your Score: {correct_count}/{total_questions} ({score_percentage:.1f}%)"
                f"</div>",
                unsafe_allow_html=True
            )
        
        # Display each question with better styling
        for q in st.session_state.parsed_questions:
            q_num = q['question_number']
            
            # Use clean divs to avoid white boxes
            st.markdown(
                f"""
                <div class='question-card'>
                    <h3>Question {q_num}</h3>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Use MathJax for better rendering of the question text
            display_math_with_mathjax(q['question_text'])
            
            # Options with radio buttons - no wrapper divs to avoid white boxes
            selected_option = st.radio(
                "",  # Empty label to reduce spacing
                [f"{opt[0]}. {parse_latex_in_text(opt[1])}" for opt in q['options']],
                index=None,
                key=f"q_{q_num}",
                disabled=st.session_state.submitted,
                label_visibility="collapsed"  # Hide the label completely
            )
            
            # Store selected answer
            if selected_option:
                # Extract the option number (the part before the first dot)
                st.session_state.user_answers[q_num] = selected_option.split('.')[0]
            
            # Add hint button if not submitted
            if not st.session_state.submitted:
                hint_col1, hint_col2 = st.columns([3, 1])
                
                with hint_col2:
                    if st.button(f"Get Hint", key=f"hint_btn_{q_num}", use_container_width=True):
                        # Generate hint if not already generated
                        if not st.session_state.hints.get(q_num):
                            hint_generator = get_hint_generator()
                            hint = hint_generator.generate_hint(q['question_text'])
                            st.session_state.hints[q_num] = hint
                
                # Display hint if available
                if st.session_state.hints.get(q_num):
                    st.markdown(f"<div class='hint-box'><strong>💡 Hint:</strong> {st.session_state.hints[q_num]}</div>", unsafe_allow_html=True)
            
            # Show correct answer and explanation if submitted
            if st.session_state.show_results:
                user_answer = st.session_state.user_answers.get(q_num)
                correct_answer = q['correct_answer']
                
                if user_answer == correct_answer:
                    st.markdown(f"<p class='correct-answer'>✓ Correct! You selected option {user_answer}.</p>", unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<p class='incorrect-answer'>✗ Incorrect. "
                        f"You selected option {user_answer or 'None'}, but the correct answer is option {correct_answer}.</p>", 
                        unsafe_allow_html=True
                    )
                
                # Show explanation using MathJax for better rendering
                st.markdown("<div class='explanation-box'><strong>Explanation:</strong></div>", unsafe_allow_html=True)
                
                # Use the same MathJax rendering for the explanation as for the question
                display_math_with_mathjax(q['explanation'])
            
            # No need to close the div as we're using new ones for each element
            st.markdown("<hr style='margin: 2rem 0; border-color: #e3f2fd;'>", unsafe_allow_html=True)
            
        # Show submission button again at the bottom if not submitted
        if not st.session_state.submitted:
            if st.button("Submit Answers ", type="primary", use_container_width=True):
                st.session_state.submitted = True
                st.session_state.show_results = True
                
                # Save responses to JSON
                saved_path = save_responses_to_json(
                    st.session_state.user_answers, 
                    st.session_state.parsed_questions, 
                    st.session_state.question_metadata
                )
                st.session_state.responses_saved = saved_path
                
                st.rerun()
    
    # If no questions yet generated, show the generator interface
    else:
        # Step 1: Choose Exam - BIGGER BUTTONS
        st.markdown("## Step 1: Choose Exam")
        
        # Add space before buttons
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Add class for bigger buttons
            st.markdown("<div class='big-button'>", unsafe_allow_html=True)
            if st.button("JEE", key="jee_btn", 
                      help="Joint Entrance Examination for engineering programs", 
                      use_container_width=True):
                st.session_state.exam_selected = True
                st.session_state.exam_type = "jee"
                st.session_state.subject_selected = False  # Reset subject if exam changes
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # Add class for bigger buttons
            st.markdown("<div class='big-button'>", unsafe_allow_html=True)
            if st.button("NEET", key="neet_btn", 
                      help="National Eligibility cum Entrance Test for medical programs",
                      use_container_width=True):
                st.session_state.exam_selected = True
                st.session_state.exam_type = "neet"
                st.session_state.subject_selected = False  # Reset subject if exam changes
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Add space after buttons
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # Step 2: Choose Subject (if exam is selected)
        if st.session_state.exam_selected:
            st.markdown(f"## Step 2: Choose Subject")
            
            # Add space before subject buttons
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
            if st.session_state.exam_type == "jee":
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Physics", key="jee_physics_btn", use_container_width=True):
                        st.session_state.subject_selected = True
                        st.session_state.subject = "physics"
                        st.rerun()
                
                with col2:
                    if st.button("Chemistry", key="jee_chemistry_btn", use_container_width=True):
                        st.session_state.subject_selected = True
                        st.session_state.subject = "chemistry"
                        st.rerun()
                
                with col3:
                    if st.button("Mathematics", key="jee_mathematics_btn", use_container_width=True):
                        st.session_state.subject_selected = True
                        st.session_state.subject = "mathematics"
                        st.rerun()
            
            else:  # NEET
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Physics", key="neet_physics_btn", use_container_width=True):
                        st.session_state.subject_selected = True
                        st.session_state.subject = "physics"
                        st.rerun()
                
                with col2:
                    if st.button("Chemistry", key="neet_chemistry_btn", use_container_width=True):
                        st.session_state.subject_selected = True
                        st.session_state.subject = "chemistry"
                        st.rerun()
                
                with col3:
                    if st.button("Biology", key="neet_biology_btn", use_container_width=True):
                        st.session_state.subject_selected = True
                        st.session_state.subject = "biology"
                        st.rerun()
            
            # Add space after subject buttons
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # Step 3: Select Topics/Chapters (if subject is selected)
        if st.session_state.subject_selected:
            st.markdown(f"## Step 3: Select Topics/Chapters")
            
            # Add space before topics section
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
            # Get available topics based on exam and subject
            available_topics = TOPICS.get(st.session_state.subject, {}).get(st.session_state.exam_type, [])
            
            # Use a clean card for topic selection instead of separate div
            st.markdown(
                """
                <div style="background-color: #f9fbff; padding: 20px; border-radius: 12px; 
                box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 1.5rem; border: 1px solid #e3f2fd;">
                <p style="color: #1565C0; font-weight: 500; margin-bottom: 1rem;">Select topics for your question paper:</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Multi-select for topics
            selected_topics = st.multiselect(
                "Choose one or more topics (hold Ctrl/Cmd to select multiple):",
                options=available_topics,
                default=available_topics[:2]  # Default select first two topics
            )
            
            # Number of questions slider
            num_questions = st.slider("Number of Questions:", min_value=1, max_value=20, value=10)
            
            # Add space before generate button
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            
            # Generate button
            generate_button = st.button("Generate Questions", type="primary", use_container_width=True)
            
            if generate_button:
                if not selected_topics:
                    st.markdown(
                        "<div class='error-box'>Please select at least one topic</div>", 
                        unsafe_allow_html=True
                    )
                else:
                    with st.spinner("Generating questions... This may take a minute or two."):
                        # Prepare request data
                        request_data = {
                            "exam_type": st.session_state.exam_type,
                            "subject": st.session_state.subject,
                            "chapters": selected_topics,
                            "num_questions": num_questions
                        }
                        
                        try:
                            # Call API to generate questions
                            response = requests.post(
                                f"{API_URL}/generate_questions", 
                                json=request_data,
                                timeout=180  # Increase timeout to 3 minutes
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data.get("success", False):
                                    # Store questions and metadata in session state
                                    markdown_content = data.get("markdown", "")
                                    
                                    # Fix LaTeX expressions in the markdown content
                                    markdown_content = improve_latex_rendering(markdown_content)
                                    
                                    st.session_state.generated_questions = markdown_content
                                    st.session_state.question_metadata = {
                                        "exam": st.session_state.exam_type,
                                        "subject": st.session_state.subject,
                                        "topics": selected_topics,
                                        "numQuestions": num_questions
                                    }
                                    
                                    # Parse questions
                                    parsed_questions = extract_questions_from_markdown(markdown_content)
                                    st.session_state.parsed_questions = parsed_questions
                                    
                                    # Initialize answers dictionary
                                    st.session_state.user_answers = {q['question_number']: None for q in parsed_questions}
                                    st.session_state.hints = {q['question_number']: None for q in parsed_questions}
                                    
                                    # Reset results flags
                                    st.session_state.show_results = False
                                    st.session_state.submitted = False
                                    st.session_state.responses_saved = False
                                    
                                    # Rerun to show the questions
                                    st.markdown(
                                        "<div class='success-box'>✓ Questions generated successfully!</div>", 
                                        unsafe_allow_html=True
                                    )
                                    st.rerun()
                                else:
                                    st.markdown(
                                        f"<div class='error-box'>Error: {data.get('error', 'Unknown error')}</div>", 
                                        unsafe_allow_html=True
                                    )
                                    if "details" in data:
                                        st.markdown(
                                            f"<div class='error-box'>Details: {data.get('details')}</div>", 
                                            unsafe_allow_html=True
                                        )
                            else:
                                st.markdown(
                                    f"<div class='error-box'>API Error: {response.status_code}</div>", 
                                    unsafe_allow_html=True
                                )
                                try:
                                    st.markdown(
                                        f"<div class='error-box'>Response: {response.text}</div>", 
                                        unsafe_allow_html=True
                                    )
                                except:
                                    pass
                        except Exception as e:
                            st.markdown(
                                f"<div class='error-box'>Error: {str(e)}</div>", 
                                unsafe_allow_html=True
                            )
                            
if __name__ == "__main__":
    main()
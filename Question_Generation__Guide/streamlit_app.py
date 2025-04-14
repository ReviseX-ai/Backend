import streamlit as st
import requests
import json
import os
import base64
import glob
import re
from pathlib import Path
import time
import markdown

# Define the API URL
API_URL = "http://127.0.0.1:5001/api"

# Define the topic mappings (same as in original HTML)
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

def extract_questions_from_markdown(markdown_content):
    """
    Extract questions, options, and correct answers from markdown content
    
    Returns:
        List of dictionaries with question details
    """
    questions = []
    
    # Split by question headers
    question_blocks = re.split(r'## Question \d+', markdown_content)
    
    # Skip the first part (likely the main title)
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

def parse_latex_in_text(text):
    """Make LaTeX expressions properly renderable by Streamlit markdown"""
    # This is needed because Streamlit markdown doesn't handle LaTeX the same way as HTML
    # Ensure we have spaces around inline math
    text = re.sub(r'(?<!\s)\$(?!\$)', ' $', text)
    text = re.sub(r'(?<!\$)\$(?!\s)', '$ ', text)
    return text

def render_markdown_safely(markdown_text):
    """Render markdown content safely for Streamlit"""
    # Process any LaTeX expressions to ensure they render correctly
    markdown_text = parse_latex_in_text(markdown_text)
    return markdown_text

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

def main():
    st.set_page_config(
        page_title="BharatGen Question Generator",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # Add custom styling
    st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    .stButton button {
        width: 100%;
        border-radius: 5px;
        padding: 0.5rem;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .exam-btn {
        height: 60px;
        margin-bottom: 10px;
    }
    .subject-btn {
        height: 50px;
    }
    .card {
        padding: a.75rem;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .question-card {
        background-color: #000000;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .question-text {
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    .option-text {
        margin-left: 10px;
    }
    .explanation-box {
        background-color: #1a1a1a;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .correct-answer {
        color: #4CAF50;
        font-weight: bold;
    }
    .incorrect-answer {
        color: #F44336;
        font-weight: bold;
    }
    .score-display {
        font-size: 1.2rem;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for storing selections
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
                f"<div style='text-align: center; margin-bottom: 1.5rem;'>"
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
                st.session_state.show_results = False
                st.session_state.submitted = False
                st.rerun()
        
        with col2:
            if not st.session_state.submitted:
                submit_button = st.button("Submit Answers", type="primary", use_container_width=True)
                if submit_button:
                    st.session_state.submitted = True
                    st.session_state.show_results = True
                    st.rerun()
            else:
                retry_button = st.button("Try Again", type="primary", use_container_width=True)
                if retry_button:
                    st.session_state.submitted = False
                    st.session_state.show_results = False
                    st.session_state.user_answers = {q['question_number']: None for q in st.session_state.parsed_questions}
                    st.rerun()
        
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
        
        # Display each question
        for q in st.session_state.parsed_questions:
            q_num = q['question_number']
            
            st.markdown(f"<div class='question-card'>", unsafe_allow_html=True)
            
            # Question number and text
            st.markdown(f"<h3>Question {q_num}</h3>", unsafe_allow_html=True)
            st.markdown(f"<div class='question-text'>{render_markdown_safely(q['question_text'])}</div>", unsafe_allow_html=True)
            
            # Options with radio buttons
            selected_option = st.radio(
                f"Select your answer for Question {q_num}:",
                [f"{opt[0]}. {opt[1]}" for opt in q['options']],
                index=None,
                key=f"q_{q_num}",
                disabled=st.session_state.submitted
            )
            
            # Store selected answer
            if selected_option:
                # Extract the option number (the part before the first dot)
                st.session_state.user_answers[q_num] = selected_option.split('.')[0]
            
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
                
                # Show explanation
                st.markdown(f"<div class='explanation-box'><strong>Explanation:</strong><br>{render_markdown_safely(q['explanation'])}</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Show submission button again at the bottom if not submitted
        if not st.session_state.submitted:
            if st.button("Submit Answers (Bottom)", type="primary", use_container_width=True):
                st.session_state.submitted = True
                st.session_state.show_results = True
                st.rerun()
    
    # If no questions yet generated, show the generator interface
    else:
        # Step 1: Choose Exam
        st.markdown("## Step 1: Choose Exam")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("JEE", key="jee_btn", 
                      help="Joint Entrance Examination for engineering programs", 
                      use_container_width=True):
                st.session_state.exam_selected = True
                st.session_state.exam_type = "jee"
                st.session_state.subject_selected = False  # Reset subject if exam changes
                st.rerun()
        
        with col2:
            if st.button("NEET", key="neet_btn", 
                      help="National Eligibility cum Entrance Test for medical programs",
                      use_container_width=True):
                st.session_state.exam_selected = True
                st.session_state.exam_type = "neet"
                st.session_state.subject_selected = False  # Reset subject if exam changes
                st.rerun()
        
        # Step 2: Choose Subject (if exam is selected)
        if st.session_state.exam_selected:
            st.markdown(f"## Step 2: Choose Subject")
            
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
        
        # Step 3: Select Topics/Chapters (if subject is selected)
        if st.session_state.subject_selected:
            st.markdown(f"## Step 3: Select Topics/Chapters")
            
            # Get available topics based on exam and subject
            available_topics = TOPICS.get(st.session_state.subject, {}).get(st.session_state.exam_type, [])
            
            # Multi-select for topics
            selected_topics = st.multiselect(
                "Choose one or more topics (hold Ctrl/Cmd to select multiple):",
                options=available_topics,
                default=available_topics[:2]  # Default select first two topics
            )
            
            # Number of questions slider
            num_questions = st.slider("Number of Questions:", min_value=1, max_value=20, value=10)
            
            # Generate button
            generate_button = st.button("Generate Questions", type="primary", use_container_width=True)
            
            if generate_button:
                if not selected_topics:
                    st.error("Please select at least one topic")
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
                            
                            st.write(f"API Status Code: {response.status_code}")
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data.get("success", False):
                                    # Store questions and metadata in session state
                                    markdown_content = data.get("markdown", "")
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
                                    
                                    # Reset results flags
                                    st.session_state.show_results = False
                                    st.session_state.submitted = False
                                    
                                    # Rerun to show the questions
                                    st.success("Questions generated successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {data.get('error', 'Unknown error')}")
                                    if "details" in data:
                                        st.error(f"Details: {data.get('details')}")
                            else:
                                st.error(f"API Error: {response.status_code}")
                                try:
                                    st.error(f"Response: {response.text}")
                                except:
                                    pass
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
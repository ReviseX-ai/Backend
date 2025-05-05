import streamlit as st
import json
from datetime import datetime
import pandas as pd
import requests
import time
import random
import base64

# Set page config
st.set_page_config(
    page_title="Student Psychometric Profile",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Questions data
questions = [
    {
        "question": "How do you prefer to learn new topics?",
        "options": [
            "A. Watching videos or diagrams",
            "B. Listening to explanations",
            "C. Reading books or articles",
            "D. Doing hands-on activities or experiments"
        ]
    },
    {
        "question": "How do you usually approach a difficult problem?",
        "options": [
            "A. Break it into smaller parts and analyze",
            "B. Ask someone for help or guidance",
            "C. Look for examples or tutorials online",
            "D. Try solving it repeatedly until you succeed"
        ]
    },
    {
        "question": "How do you feel when working in a group project?",
        "options": [
            "A. I enjoy it and usually take the lead",
            "B. I like it if I get to choose my role",
            "C. I prefer working alone",
            "D. I adapt to the group but don't speak much"
        ]
    },
    {
        "question": "What motivates you the most to study?",
        "options": [
            "A. Achieving high marks or rewards",
            "B. Gaining knowledge and understanding",
            "C. Parental or teacher expectations",
            "D. Curiosity and interest in the subject"
        ]
    },
    {
        "question": "When do you feel most focused while studying?",
        "options": [
            "A. Early morning",
            "B. Late at night",
            "C. After physical activity",
            "D. Doesn't matter – I can focus anytime"
        ]
    },
    {
        "question": "What best describes your reaction to failure?",
        "options": [
            "A. I try harder next time",
            "B. I feel disappointed but move on",
            "C. I get discouraged",
            "D. I analyze what went wrong and learn from it"
        ]
    },
    {
        "question": "Which subject do you find most enjoyable?",
        "options": [
            "A. Math or Science",
            "B. Literature or History",
            "C. Arts or Music",
            "D. Sports or Physical Education"
        ]
    },
    {
        "question": "How do you manage time when you have multiple tasks?",
        "options": [
            "A. I make a schedule and stick to it",
            "B. I prioritize the easiest tasks first",
            "C. I do things randomly",
            "D. I often procrastinate but finish just in time"
        ]
    },
    {
        "question": "How do you react to unfamiliar topics?",
        "options": [
            "A. I feel excited to explore them",
            "B. I get nervous but try to understand",
            "C. I avoid them unless necessary",
            "D. I ask others to explain it"
        ]
    },
    {
        "question": "Which of these best describes your personality?",
        "options": [
            "A. Logical and Analytical",
            "B. Creative and Expressive",
            "C. Calm and Observant",
            "D. Energetic and Outgoing"
        ]
    }
]

def apply_custom_css():
    """Apply custom CSS styling for the dashboard"""
    st.markdown("""
    <style>
        /* Global Styles */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Poppins', sans-serif;
    color: #333333;
}

/* Main area styling */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    background-color: #ffffff;
}

/* Headers styling */
h1 {
    color: #1e88e5;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e3f2fd;
    margin-bottom: 2rem;
}
h2 {
    color: #1976d2;
    margin-top: 1.5rem;
}
h3 {
    color: #0d47a1;
    margin-top: 1rem;
}

/* Progress Bar */
.stProgress > div > div {
    background-color: #42a5f5;
    border-radius: 10px;
}

.stProgress {
    height: 15px;
}

/* Buttons */
.stButton button {
    background-color: #ffffff;
    color: #1e88e5;
    border: 2px solid #1e88e5;
    border-radius: 30px;
    padding: 0.6rem 2.5rem;
    box-shadow: 0 4px 15px rgba(30, 136, 229, 0.1);
    transition: all 0.3s ease;
    font-weight: 600;
    width: 100%;
}

.stButton button:hover {
    transform: translateY(-3px);
    background-color: #e3f2fd;
    box-shadow: 0 6px 20px rgba(30, 136, 229, 0.2);
}

.stButton button:active {
    transform: translateY(1px);
}

.stButton button:disabled {
    background-color: #E0E0E0;
    box-shadow: none;
    color: #888;
}

/* Question Container */
.question-container {
    background: #ffffff;
    padding: 2.5rem;
    border-radius: 20px;
    box-shadow: 0 15px 35px rgba(30, 136, 229, 0.1);
    margin: 1rem 0;
    border-left: 5px solid #1e88e5;
    transition: all 0.3s ease;
}

.question-container:hover {
    box-shadow: 0 20px 40px rgba(30, 136, 229, 0.15);
    transform: translateY(-5px);
}

/* Metadata Section */
.metadata {
    background: #f5f9ff;
    color: #333333;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(30, 136, 229, 0.1);
    border: 1px solid #bbdefb;
}

/* Success Messages */
.success-message {
    background: #e3f2fd;
    color: #0d47a1;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin: 2rem 0;
    box-shadow: 0 10px 30px rgba(30, 136, 229, 0.1);
    border: 1px solid #bbdefb;
}

.saving-indicator {
    display: flex;
    align-items: center;
    background-color: #e3f2fd;
    border-radius: 50px;
    padding: 0.5rem 1rem;
    color: #0d47a1;
    font-size: 0.9rem;
    margin-top: 1rem;
}

.saving-indicator.saved {
    background-color: #e8f5e9;
    color: #2e7d32;
    border: 1px solid #c8e6c9;
}

.pulsing-dot {
    height: 10px;
    width: 10px;
    background-color: #2196f3;
    border-radius: 50%;
    margin-right: 8px;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(0.95);
        opacity: 0.7;
    }
    50% {
        transform: scale(1.05);
        opacity: 1;
    }
    100% {
        transform: scale(0.95);
        opacity: 0.7;
    }
}

.saving-indicator.saved .pulsing-dot {
    background-color: #4caf50;
    animation: none;
}

/* Radio Buttons */
div.row-widget.stRadio > div {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

div.row-widget.stRadio > div[role="radiogroup"] > label {
    background-color: #ffffff;
    border: 1px solid #bbdefb;
    border-radius: 10px;
    padding: 1rem;
    transition: all 0.2s ease;
    box-shadow: 0 2px 5px rgba(30, 136, 229, 0.05);
}

div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
    border-color: #2196f3;
    box-shadow: 0 5px 15px rgba(30, 136, 229, 0.1);
    transform: translateY(-2px);
}

/* Results Section */
.results-container {
    background: #ffffff;
    padding: 2.5rem;
    border-radius: 20px;
    box-shadow: 0 15px 35px rgba(30, 136, 229, 0.1);
    margin: 2rem 0;
}

.results-header {
    background: #e3f2fd;
    color: #0d47a1;
    padding: 1.5rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
    border: 1px solid #bbdefb;
}

/* Username input */
div.stTextInput > div > div > input {
    border-radius: 10px;
    border: 2px solid #bbdefb;
    padding: 1rem;
    font-size: 1rem;
    transition: all 0.3s;
    color: #333333;
    background-color: #ffffff;
}

div.stTextInput > div > div > input:focus {
    border-color: #2196f3;
    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

/* Dataframe styling */
.dataframe-container {
    margin-top: 2rem;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #bbdefb;
    background-color: #ffffff;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
}
.stTabs [data-baseweb="tab"] {
    height: 3rem;
    white-space: nowrap;
    border-radius: 0.375rem 0.375rem 0 0;
    padding: 0.5rem 1rem;
    font-weight: 500;
    color: #1976d2;
    background-color: #ffffff;
}
.stTabs [aria-selected="true"] {
    background-color: #e3f2fd !important;
    color: #0d47a1 !important;
}

/* Card-like containers */
.css-1r6slb0 {
    background-color: #ffffff;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(30, 136, 229, 0.1), 0 2px 4px -1px rgba(30, 136, 229, 0.06);
}

/* Sidebar styling */
.css-1d391kg {
    background-color: #f5f9ff;
}

/* Metrics styling */
.css-1xarl3l {
    background-color: #ffffff;
    border-radius: 0.5rem;
    padding: 1rem;
    box-shadow: 0 1px 3px 0 rgba(30, 136, 229, 0.1), 0 1px 2px 0 rgba(30, 136, 229, 0.06);
    color: #333333;
}

/* Brain Wave Animation */
.brain-wave {
    height: 60px;
    width: 100%;
    position: relative;
    margin: 20px 0;
    overflow: hidden;
}

.wave {
    background: linear-gradient(90deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.5) 50%, rgba(33, 150, 243, 0.1) 100%);
    height: 30px;
    width: 200%;
    position: absolute;
    top: 15px;
    left: -50%;
    border-radius: 50%;
    animation: wave 3s infinite ease-in-out;
}

@keyframes wave {
    0% {
        transform: translateX(-30%) scaleY(0.5);
    }
    50% {
        transform: translateX(-20%) scaleY(1.2);
    }
    100% {
        transform: translateX(-10%) scaleY(0.5);
    }
}

/* Animated Header */
.animated-header {
    text-align: center;
    animation: fadeIn 1s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Download button styling */
.download-button {
    background-color: #4caf50 !important;
    color: white !important;
    border: none !important;
    margin-top: 20px;
}

.download-button:hover {
    background-color: #45a049 !important;
    color: white !important;
}
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'start_time' not in st.session_state:
        st.session_state.start_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    if 'test_completed' not in st.session_state:
        st.session_state.test_completed = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{random.randint(1000, 9999)}"
    if 'last_saved' not in st.session_state:
        st.session_state.last_saved = None
    if 'save_status' not in st.session_state:
        st.session_state.save_status = "idle"  # idle, saving, saved
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""
    if 'class_name' not in st.session_state:
        st.session_state.class_name = ""
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'contact' not in st.session_state:
        st.session_state.contact = ""
    if 'registration_time' not in st.session_state:
        st.session_state.registration_time = ""

def get_profile_info():
    # Analyze responses to generate profile
    profile_categories = {
        "Learning Style": "",
        "Problem-Solving Approach": "",
        "Social Dynamics": "",
        "Motivation Factor": "",
        "Cognitive Strength": ""
    }
    
    if len(st.session_state.responses) < len(questions):
        return profile_categories
    
    # Learning style
    q1_response = st.session_state.responses["Q1"]
    if "A" in q1_response:
        profile_categories["Learning Style"] = "Visual"
    elif "B" in q1_response:
        profile_categories["Learning Style"] = "Auditory"
    elif "C" in q1_response:
        profile_categories["Learning Style"] = "Reading/Writing"
    else:
        profile_categories["Learning Style"] = "Kinesthetic"
    
    # Problem-solving
    q2_response = st.session_state.responses["Q2"]
    if "A" in q2_response:
        profile_categories["Problem-Solving Approach"] = "Analytical"
    elif "B" in q2_response:
        profile_categories["Problem-Solving Approach"] = "Collaborative"
    elif "C" in q2_response:
        profile_categories["Problem-Solving Approach"] = "Research-Oriented"
    else:
        profile_categories["Problem-Solving Approach"] = "Persistent"
    
    # Social Dynamics
    q3_response = st.session_state.responses["Q3"]
    if "A" in q3_response:
        profile_categories["Social Dynamics"] = "Leader"
    elif "B" in q3_response:
        profile_categories["Social Dynamics"] = "Selective Collaborator"
    elif "C" in q3_response:
        profile_categories["Social Dynamics"] = "Independent"
    else:
        profile_categories["Social Dynamics"] = "Adaptable Observer"
    
    # Motivation
    q4_response = st.session_state.responses["Q4"]
    if "A" in q4_response:
        profile_categories["Motivation Factor"] = "Achievement-Driven"
    elif "B" in q4_response:
        profile_categories["Motivation Factor"] = "Knowledge-Driven"
    elif "C" in q4_response:
        profile_categories["Motivation Factor"] = "Externally Motivated"
    else:
        profile_categories["Motivation Factor"] = "Intrinsically Curious"
    
    # Cognitive Strength based on subject preference
    q7_response = st.session_state.responses["Q7"]
    if "A" in q7_response:
        profile_categories["Cognitive Strength"] = "Logical-Mathematical"
    elif "B" in q7_response:
        profile_categories["Cognitive Strength"] = "Verbal-Linguistic"
    elif "C" in q7_response:
        profile_categories["Cognitive Strength"] = "Musical-Artistic"
    else:
        profile_categories["Cognitive Strength"] = "Bodily-Kinesthetic"
    
    return profile_categories

def prepare_data_for_download():
    """Prepare the JSON data that will be downloaded by the user"""
    # Get detailed question info with responses
    question_details = []
    for i, q in enumerate(questions):
        q_num = f"Q{i+1}"
        response = st.session_state.responses.get(q_num, "Not answered")
        question_details.append({
            "question_number": q_num,
            "question_text": q["question"],
            "options": q["options"],
            "selected_answer": response
        })
    
    # Create the complete data object
    download_data = {
        "student_info": {
            "name": st.session_state.student_name,
            "class": st.session_state.class_name,
            "email": st.session_state.email,
            "contact": st.session_state.contact,
            "user_id": st.session_state.user_id,
            "registration_time": st.session_state.registration_time
        },
        "test_info": {
            "start_time": st.session_state.start_time,
            "completion_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "completion_status": "Complete" if st.session_state.test_completed else "Incomplete"
        },
        "questions_and_responses": question_details,
        "psychometric_profile": get_profile_info()
    }
    
    return download_data

def download_json_button(data, filename="psychometric_profile.json"):
    """Create a download button for the JSON data"""
    json_str = json.dumps(data, indent=4)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'data:file/json;base64,{b64}'
    
    # Custom styling for download button
    button_style = """
    <style>
    .download-button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 12px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition: background-color 0.3s;
    }
    .download-button:hover {
        background-color: #45a049;
    }
    </style>
    """
    
    st.markdown(button_style, unsafe_allow_html=True)
    
    # Custom download button with icon
    download_button_str = f"""
    <a href="{href}" download="{filename}" class="download-button">
        💾 Download Results (JSON)
    </a>
    """
    st.markdown(download_button_str, unsafe_allow_html=True)

def save_responses_to_server():
    """Simulate saving responses to a server."""
    st.session_state.save_status = "saving"
    
    # Prepare data
    final_data = {
        "user_id": st.session_state.user_id,
        "username": st.session_state.username,
        "student_name": st.session_state.student_name,
        "class_name": st.session_state.class_name,
        "email": st.session_state.email,
        "contact": st.session_state.contact,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "responses": st.session_state.responses,
        "completion_status": {
            "total_questions": len(questions),
            "answered_questions": len(st.session_state.responses),
            "current_question": st.session_state.current_question + 1,
            "is_complete": len(st.session_state.responses) == len(questions)
        },
        "profile": get_profile_info() if st.session_state.test_completed else {}
    }
    
    # Simulate server delay
    time.sleep(1)
    
    # In a real app, you would send the data to your server:
    # try:
    #     response = requests.post(
    #         "https://your-server.com/api/save-psychometric",
    #         json=final_data,
    #         headers={"Content-Type": "application/json"}
    #     )
    #     if response.status_code == 200:
    #         st.session_state.last_saved = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    #         st.session_state.save_status = "saved"
    #     else:
    #         st.session_state.save_status = "error"
    # except Exception as e:
    #     st.session_state.save_status = "error"
    
    # For demo purposes:
    st.session_state.last_saved = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.save_status = "saved"
    
    # Return the data that would be sent to the server
    return final_data

def render_save_indicator():
    if st.session_state.save_status == "saving":
        st.markdown("""
        <div class="saving-indicator">
            <div class="pulsing-dot"></div>
            <span>Saving your responses...</span>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.save_status == "saved":
        st.markdown(f"""
        <div class="saving-indicator saved">
            <div class="pulsing-dot"></div>
            <span>Saved at {st.session_state.last_saved}</span>
        </div>
        """, unsafe_allow_html=True)

def generate_brain_wave_animation():
    return """
    <div class="brain-wave">
        <div class="wave"></div>
    </div>
    """

def main():
    initialize_session_state()
    apply_custom_css()
    
    # Title with animation
    st.markdown("""
    <div class="animated-header">
        <h1 style="text-align: center; margin: 0;">🧠 Student Psychometric Profile</h1>
        <p style="text-align: center; margin: 10px 0 0 0; opacity: 0.8;">Discover your unique learning and cognitive preferences</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Username input if not already provided
    if not st.session_state.username:
        st.markdown('<div class="question-container">', unsafe_allow_html=True)
        st.subheader("Let's get started!")
        username = st.text_input("Enter your name or username:", key="username_input")
        if username:
            st.session_state.username = username
            save_responses_to_server()
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:  # After registration
        # Metadata section
        st.markdown(f"""
        <div class="metadata">
            <div><strong>Student:</strong> {st.session_state.student_name}</div>
            <div><strong>Class:</strong> {st.session_state.class_name}</div>
            <div><strong>Session ID:</strong> {st.session_state.user_id}</div>
            <div><strong>Started:</strong> {st.session_state.start_time}</div>
            <div><strong>Last Updated:</strong> {st.session_state.last_saved if st.session_state.last_saved else "Not saved yet"}</div>
        </div>
        {generate_brain_wave_animation()}
        """, unsafe_allow_html=True)

        if not st.session_state.test_completed:
            # Progress bar
            progress = (st.session_state.current_question + 1) / len(questions)
            st.progress(progress)
            st.write(f"Question {st.session_state.current_question + 1} of {len(questions)}")

            # Question container
            current_q = questions[st.session_state.current_question]
            st.markdown('<div class="question-container">', unsafe_allow_html=True)
            st.subheader(f"Question {st.session_state.current_question + 1}")
            st.write(current_q["question"])
            
            # Radio buttons for options
            selected_option = st.radio(
                "Choose your answer:",
                current_q["options"],
                key=f"q_{st.session_state.current_question}",
                index=None
            )

            if selected_option and f"Q{st.session_state.current_question + 1}" not in st.session_state.responses:
                st.session_state.responses[f"Q{st.session_state.current_question + 1}"] = selected_option
                save_responses_to_server()
            elif selected_option and selected_option != st.session_state.responses.get(f"Q{st.session_state.current_question + 1}"):
                st.session_state.responses[f"Q{st.session_state.current_question + 1}"] = selected_option
                save_responses_to_server()

            st.markdown('</div>', unsafe_allow_html=True)
            
            # Navigation buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.session_state.current_question > 0:
                    if st.button("Previous"):
                        st.session_state.current_question -= 1
                        st.experimental_rerun()

            with col3:
                if selected_option:
                    if st.session_state.current_question < len(questions) - 1:
                        if st.button("Next"):
                            st.session_state.current_question += 1
                            st.experimental_rerun()
                    else:
                        if st.button("Complete Test"):
                            st.session_state.test_completed = True
                            save_responses_to_server()
                            st.experimental_rerun()
                else:
                    st.button("Next", disabled=True)
            
            # Render saving indicator
            with col2:
                render_save_indicator()

        else:
            # Results section with download button
            st.markdown('<div class="results-container">', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="results-header">
                <h1>🎉 Profile Complete!</h1>
                <p>Your psychometric profile has been generated and is ready for download</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display success message
            st.markdown("""
            <div class="success-message">
                <h2>Thank You!</h2>
                <p>Your responses have been recorded. Click the download button below to save your results.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display profile information
                        # Display profile information
            st.subheader("Your Psychometric Profile")
            profile = get_profile_info()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Learning Preferences")
                st.markdown(f"**Learning Style:** {profile['Learning Style']}")
                st.markdown(f"**Problem-Solving Approach:** {profile['Problem-Solving Approach']}")
                st.markdown(f"**Social Dynamics:** {profile['Social Dynamics']}")

            with col2:
                st.markdown("### Cognitive Attributes")
                st.markdown(f"**Motivation Factor:** {profile['Motivation Factor']}")
                st.markdown(f"**Cognitive Strength:** {profile['Cognitive Strength']}")
            
            # Visualization of profile (placeholder for potential charts)
            st.markdown("### Profile Overview")
            st.markdown("""
            <div class="profile-visualization">
                <div class="brain-wave">
                    <div class="wave"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recommendations based on profile
            st.markdown("### Personalized Recommendations")
            recommendations = {
                'Visual': "Utilize diagrams, charts, and visual aids in your study materials.",
                'Auditory': "Record lectures and use audio materials for review.",
                'Reading/Writing': "Take detailed notes and use written summaries.",
                'Kinesthetic': "Incorporate hands-on activities and practical exercises."
            }
            
            st.markdown(f"Based on your learning style ({profile['Learning Style']}), we recommend:")
            st.info(recommendations.get(profile['Learning Style'], "Customize your learning approach."))
            
            # Download section
            st.markdown("### Download Your Results")
            st.markdown("""
            <div class="download-section">
                <p>Download your complete psychometric profile report in JSON format. 
                This file contains all your responses and detailed analysis.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Prepare and offer download
            download_data = prepare_data_for_download()
            download_json_button(download_data, f"psychometric_profile_{st.session_state.user_id}.json")
            
            # Reset test option
            st.markdown("### Start Fresh")
            if st.button("Reset Test"):
                for key in list(st.session_state.keys()):
                    if key != 'username':  # Preserve username
                        del st.session_state[key]
                initialize_session_state()
                st.experimental_rerun()

if __name__ == "__main__":
    main()
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

# Custom CSS for a more modern and visually appealing UI
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background-image: linear-gradient(to right, #8e2de2, #4a00e0);
        border-radius: 10px;
    }
    
    .stProgress {
        height: 15px;
    }
    
    /* Buttons */
    .stButton button {
        background-image: linear-gradient(to right, #8e2de2, #4a00e0);
        color: white;
        border-radius: 30px;
        padding: 0.6rem 2.5rem;
        border: none;
        box-shadow: 0 4px 15px rgba(142, 45, 226, 0.4);
        transition: all 0.3s ease;
        font-weight: 600;
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(142, 45, 226, 0.6);
    }
    
    .stButton button:active {
        transform: translateY(1px);
    }
    
    .stButton button:disabled {
        background-image: linear-gradient(to right, #e0e0e0, #c0c0c0);
        box-shadow: none;
        color: #888;
    }
    
    /* Question Container */
    .question-container {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #8e2de2;
        transition: all 0.3s ease;
    }
    
    .question-container:hover {
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        transform: translateY(-5px);
    }
    
    /* Metadata Section */
    .metadata {
        background-image: linear-gradient(135deg, #8e2de2, #4a00e0);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(142, 45, 226, 0.3);
    }
    
    /* Success Messages */
    .success-message {
        background-image: linear-gradient(135deg, #00c853, #00b248);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0, 200, 83, 0.3);
    }
    
    .saving-indicator {
        display: flex;
        align-items: center;
        background-color: #f5f5f5;
        border-radius: 50px;
        padding: 0.5rem 1rem;
        color: #666;
        font-size: 0.9rem;
        margin-top: 1rem;
    }
    
    .saving-indicator.saved {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    
    .pulsing-dot {
        height: 10px;
        width: 10px;
        background-color: #8e2de2;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 1.5s infinite;
    }
    
    .saving-indicator.saved .pulsing-dot {
        background-color: #2e7d32;
        animation: none;
    }
    
    @keyframes pulse {
        0% {
            transform: scale(0.95);
            opacity: 0.7;
        }
        50% {
            transform: scale(1.1);
            opacity: 1;
        }
        100% {
            transform: scale(0.95);
            opacity: 0.7;
        }
    }
    
    /* Radio Buttons */
    div.row-widget.stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
        border-color: #8e2de2;
        box-shadow: 0 5px 15px rgba(142, 45, 226, 0.1);
        transform: translateY(-2px);
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
        background-color: white;
        border-color: #8e2de2;
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] input:checked + div {
        background-color: #8e2de2;
        border-color: #8e2de2;
    }
    
    /* Header animation */
    .animated-header {
        background: linear-gradient(90deg, #8e2de2, #4a00e0, #8e2de2);
        background-size: 200% auto;
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(142, 45, 226, 0.3);
        animation: gradient 5s ease infinite;
    }
    
    @keyframes gradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    /* Results Section */
    .results-container {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        margin: 2rem 0;
    }
    
    .results-header {
        background-image: linear-gradient(135deg, #8e2de2, #4a00e0);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Username input */
    div.stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s;
    }
    
    div.stTextInput > div > div > input:focus {
        border-color: #8e2de2;
        box-shadow: 0 0 0 2px rgba(142, 45, 226, 0.2);
    }
    
    /* Dataframe styling */
    .dataframe-container {
        margin-top: 2rem;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #f0f0f0;
    }
    
    /* Brain wave animation */
    .brain-wave {
        height: 50px;
        width: 100%;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .wave {
        position: absolute;
        width: 100%;
        height: 100%;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%238e2de2' fill-opacity='0.2' d='M0,192L48,197.3C96,203,192,213,288,229.3C384,245,480,267,576,250.7C672,235,768,181,864,181.3C960,181,1056,235,1152,234.7C1248,235,1344,181,1392,154.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E");
        background-size: cover;
        animation: wave-animation 20s linear infinite;
    }
    
    @keyframes wave-animation {
        0% {
            transform: translateX(0);
        }
        100% {
            transform: translateX(-100%);
        }
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

def save_responses_to_server():
    """Simulate saving responses to a server."""
    st.session_state.save_status = "saving"
    
    # Prepare data
    final_data = {
        "user_id": st.session_state.user_id,
        "username": st.session_state.username,
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
    
    if st.session_state.username:
        # Metadata section
        st.markdown(f"""
        <div class="metadata">
            <div><strong>Student:</strong> {st.session_state.username}</div>
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
                        st.rerun()

            with col3:
                if selected_option:
                    if st.session_state.current_question < len(questions) - 1:
                        if st.button("Next"):
                            st.session_state.current_question += 1
                            st.rerun()
                    else:
                        if st.button("Complete Test"):
                            st.session_state.test_completed = True
                            save_responses_to_server()
                            st.rerun()
                else:
                    st.button("Next", disabled=True)
            
            # Render saving indicator
            with col2:
                render_save_indicator()

        else:
            # Results section
            st.markdown('<div class="results-container">', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="results-header">
                <h1>🎉 Profile Complete!</h1>
                <p>Your psychometric profile has been generated and saved</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display success message
            st.markdown("""
            <div class="success-message">
                <h2>Thank You!</h2>
                <p>Your responses have been recorded and automatically saved to our system.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display profile information
            st.subheader("Your Psychometric Profile")
            profile = get_profile_info()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Learning Preferences")
                st.markdown(f"**Learning Style:** {profile['Learning Style']}")
                st.markdown(f"**Problem-Solving:** {profile['Problem-Solving Approach']}")
                st.markdown(f"**Motivation:** {profile['Motivation Factor']}")
            
            with col2:
                st.markdown("### Personal Attributes")
                st.markdown(f"**Social Dynamics:** {profile['Social Dynamics']}")
                st.markdown(f"**Cognitive Strength:** {profile['Cognitive Strength']}")
            
            # Display responses in a stylized table
            st.subheader("Your Responses")
            responses_df = pd.DataFrame(
                [(f"Question {k[1:]}", v) for k, v in st.session_state.responses.items()],
                columns=["Question Number", "Your Answer"]
            )
            
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            st.dataframe(responses_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            render_save_indicator()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Restart button
            if st.button("Start a New Test"):
                # Reset session state
                for key in list(st.session_state.keys()):
                    if key != 'username':  # Preserve username
                        del st.session_state[key]
                initialize_session_state()
                st.experimental_rerun()

if __name__ == "__main__":
    main()
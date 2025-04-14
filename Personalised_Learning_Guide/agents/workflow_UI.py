import streamlit as st
import json
import pandas as pd
import altair as alt
from typing import Dict, Any
from workflow import run_educational_workflow


# Custom CSS for a more modern and visually appealing UI
st.markdown("""
<style>
    /* Main area styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Headers styling */
    h1 {
        color: #1E3A8A;
        padding-bottom: 1rem;
        border-bottom: 2px solid #E5E7EB;
        margin-bottom: 2rem;
    }
    
    h2 {
        color: #1E40AF;
        margin-top: 1.5rem;
    }
    
    h3 {
        color: #2563EB;
        margin-top: 1rem;
    }
    
    /* Card-like containers */
    .css-1r6slb0 {
        background-color: #F9FAFB;
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background-image: linear-gradient(to right, #2563EB, #1E40AF);
        border-radius: 10px;
    }
    
    .stProgress {
        height: 15px;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #2563EB;
        color: white;
        border-radius: 0.375rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border: none;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #1E40AF;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6);
    }
    
    .stButton button:active {
        transform: translateY(1px);
    }
    
    .stButton button:disabled {
        background-color: #E5E7EB;
        box-shadow: none;
        color: #9CA3AF;
    }
    
    /* Question Container */
    .question-container {
        background-color: #F9FAFB;
        padding: 2.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin: 1rem 0;
        border-left: 5px solid #2563EB;
        transition: all 0.3s ease;
    }
    
    .question-container:hover {
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        transform: translateY(-2px);
    }
    
    /* Metadata Section */
    .metadata {
        background-color: #EFF6FF;
        color: #1E3A8A;
        padding: 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Success Messages */
    .success-message {
        background-color: #ECFDF5;
        color: #065F46;
        padding: 2rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .saving-indicator {
        display: flex;
        align-items: center;
        background-color: #F3F4F6;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        color: #4B5563;
        font-size: 0.875rem;
        margin-top: 1rem;
    }
    
    .saving-indicator.saved {
        background-color: #ECFDF5;
        color: #065F46;
    }
    
    .pulsing-dot {
        height: 8px;
        width: 8px;
        background-color: #2563EB;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 1.5s infinite;
    }
    
    .saving-indicator.saved .pulsing-dot {
        background-color: #059669;
        animation: none;
    }
    
    /* Radio Buttons */
    div.row-widget.stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
        border-color: #2563EB;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.1);
        transform: translateY(-2px);
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
        background-color: white;
        border-color: #2563EB;
    }
    
    div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] input:checked + div {
        background-color: #2563EB;
        border-color: #2563EB;
    }
    
    /* Header animation */
    .animated-header {
        background-color: #1E3A8A;
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .animated-header h1 {
        color: white;
        border-bottom: none;
        margin-bottom: 0.5rem;
        padding-bottom: 0;
    }
    
    /* Results Section */
    .results-container {
        background-color: #F9FAFB;
        padding: 2.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin: 2rem 0;
    }
    
    .results-header {
        background-color: #1E3A8A;
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .results-header h1 {
        color: white;
        border-bottom: none;
        margin-bottom: 0.5rem;
        padding-bottom: 0;
    }
    
    /* Username input */
    div.stTextInput > div > div > input {
        border-radius: 0.5rem;
        border: 1px solid #E5E7EB;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s;
    }
    
    div.stTextInput > div > div > input:focus {
        border-color: #2563EB;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
    }
    
    /* Dataframe styling */
    .dataframe-container {
        margin-top: 2rem;
        border-radius: 0.5rem;
        overflow: hidden;
        border: 1px solid #E5E7EB;
    }
    
    /* User info display */
    .user-info {
        background-color: #EFF6FF;
        color: #1E3A8A;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        font-size: 0.875rem;
    }
    
    .timestamp {
        color: #4B5563;
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

def render_header():
    """Display the dashboard header with logo and title"""
    st.markdown("""
    <div style="display:flex; align-items:center; margin-bottom:2rem;">
        <div style="background-color:#2563EB; width:60px; height:60px; border-radius:50%; display:flex; justify-content:center; align-items:center; margin-right:15px;">
            <span style="color:white; font-size:24px;">🎓</span>
        </div>
        <div>
            <h1 style="margin:0; padding:0;">Educational Assessment Dashboard</h1>
            <p style="margin:0; padding:0; color:#6B7280;">Personalized insights and recommendations for student success</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar(run_analysis_callback):
    """Display the sidebar with student info and data options"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="background-color:#3B82F6; color:white; padding:15px; border-radius:10px; margin-bottom:20px;">
                <h2 style="margin:0; color:white;">Student Information</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        user_id = st.text_input("Student ID", value="JEE2025_78901")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        use_sample_data = True
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Run Analysis"):
            run_analysis_callback(user_id, use_sample_data)
        
        # Add additional sidebar elements
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3>Quick Links</h3>", unsafe_allow_html=True)
        
        for link in ["Student Profile", "Performance Reports", "Study Plan", "Past Tests"]:
            st.markdown(f"""
            <div style="padding:8px 12px; background-color:#EFF6FF; margin-bottom:8px; border-radius:6px; cursor:pointer;">
                {link}
            </div>
            """, unsafe_allow_html=True)
    
    return user_id, use_sample_data

def render_data_input_form():
    """Display custom data input form"""
    st.markdown("### Custom Data Input")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color:#F3F4F6; padding:15px; border-radius:8px;">
            <h4 style="margin-top:0;">Psychometric Data Input</h4>
        </div>
        """, unsafe_allow_html=True)
        
        psychometric_json = st.text_area(
            "Enter Psychometric Data (JSON)",
            value=json.dumps(load_sample_data()[0], indent=2),
            height=300
        )
        try:
            st.session_state.psychometric_data = psychometric_json
        except json.JSONDecodeError:
            st.error("Invalid JSON format for psychometric data")
    
    with col2:
        st.markdown("""
        <div style="background-color:#F3F4F6; padding:15px; border-radius:8px;">
            <h4 style="margin-top:0;">Progress Data Input</h4>
        </div>
        """, unsafe_allow_html=True)
        
        progress_json = st.text_area(
            "Enter Progress Data (JSON)",
            value=json.dumps(load_sample_data()[1], indent=2),
            height=300
        )
        try:
            st.session_state.progress_data = progress_json
        except json.JSONDecodeError:
            st.error("Invalid JSON format for progress data")

def render_welcome_screen():
    """Display welcome screen when no analysis is present"""
    st.markdown("""
    <div style="background-color:#F9FAFB; padding:30px; border-radius:10px; text-align:center; margin-top:50px;">
        <img src="https://cdn-icons-png.flaticon.com/512/1535/1535019.png" width="100" style="opacity:0.6;">
        <h2 style="margin-top:20px; color:#4B5563;">Welcome to the Educational Assessment Dashboard</h2>
        <p style="color:#6B7280; max-width:600px; margin:10px auto 30px auto;">
            Enter a student ID and click "Run Analysis" to generate personalized insights and recommendations
            based on the student's psychometric profile and academic progress.
        </p>
        <div style="background-color:#EFF6FF; padding:15px; border-radius:8px; max-width:500px; margin:0 auto; text-align:left;">
            <h4 style="margin-top:0; color:#1E40AF;">Getting Started</h4>
            <ol style="margin-bottom:0; padding-left:20px;">
                <li>Enter a Student ID or use the default sample ID</li>
                <li>Click "Run Analysis" to generate insights</li>
                <li>Explore the results across different tabs</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_student_profile_card(data):
    """Render a student profile card with data"""
    student = data["student_details"]
    st.markdown(f"""
    <div style="background-color:#F0F9FF; border-radius:10px; padding:20px; border-left:5px solid #3B82F6;">
        <h3 style="margin-top:0; color:#1E40AF;">📊 Student Profile</h3>
        <p><strong>Name:</strong> {student['name']}</p>
        <p><strong>ID:</strong> {student['student_id']}</p>
        <p><strong>Grade:</strong> {student['grade']}</p>
        <p><strong>Target Exam:</strong> {student['target_exam']}</p>
    </div>
    """, unsafe_allow_html=True)

def create_performance_summary(data):
    """Create and display performance summary charts"""
    performance = data["overall_performance"]
    
    # Create dataframe for the chart
    df = pd.DataFrame({
        'Subject': list(performance.keys()),
        'Score': list(performance.values())
    })
    
    # Create bar chart with Altair
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Subject', sort=None),
        y=alt.Y('Score', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Subject', scale=alt.Scale(
            domain=['physics', 'chemistry', 'mathematics'],
            range=['#3B82F6', '#10B981', '#F59E0B']
        )),
        tooltip=['Subject', 'Score']
    ).properties(
        width='container',
        height=300,
        title='Overall Subject Performance'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=16
    )
    
    # Display the chart
    st.altair_chart(chart, use_container_width=True)
    
    # Show metrics in columns
    cols = st.columns(len(performance))
    for i, (subject, score) in enumerate(performance.items()):
        with cols[i]:
            st.metric(
                label=subject.capitalize(),
                value=f"{score:.1f}%",
                delta=f"{score - 60:.1f}%" if score - 60 != 0 else None
            )

def create_topic_breakdown(data):
    """Create and display topic breakdown charts"""
    topic_data = data["topic_performance"]
    
    # Create tabs for each subject
    subject_tabs = st.tabs(list(topic_data.keys()))
    
    for i, subject in enumerate(topic_data.keys()):
        with subject_tabs[i]:
            topics = topic_data[subject]
            
            # Create dataframe for the chart
            df = pd.DataFrame({
                'Topic': list(topics.keys()),
                'Accuracy': [t["accuracy_percentage"] for t in topics.values()]
            })
            
            # Create horizontal bar chart
            chart = alt.Chart(df).mark_bar().encode(
                y=alt.Y('Topic', sort='-x'),
                x=alt.X('Accuracy', scale=alt.Scale(domain=[0, 100])),
                color=alt.Color('Accuracy', scale=alt.Scale(
                    domain=[40, 70, 100],
                    range=['#EF4444', '#F59E0B', '#10B981']
                )),
                tooltip=['Topic', 'Accuracy']
            ).properties(
                width='container',
                height=50 * len(topics)
            )
            
            st.altair_chart(chart, use_container_width=True)
            
            # Display progress bars with better formatting
            for topic, details in topics.items():
                score = details["accuracy_percentage"]
                color = "#10B981" if score >= 70 else "#F59E0B" if score >= 50 else "#EF4444"
                
                st.markdown(f"""
                <div style="display:flex; align-items:center; margin-bottom:10px;">
                    <div style="width:30%; font-weight:500;">{topic.replace('_', ' ').title()}</div>
                    <div style="width:60%; background-color:#E5E7EB; height:10px; border-radius:5px;">
                        <div style="width:{score}%; background-color:{color}; height:10px; border-radius:5px;"></div>
                    </div>
                    <div style="width:10%; text-align:right; padding-left:10px;">{score}%</div>
                </div>
                """, unsafe_allow_html=True)

def create_psychometric_profile(data):
    """Create and display psychometric profile visualizations"""
    assessment = data["assessment"]
    
    # Create tabs for different assessment types
    tabs = st.tabs(["Learning Style", "Personality Traits", "Cognitive Profile"])
    
    with tabs[0]:
        learning_data = assessment["learning_style"]
        df = pd.DataFrame({
            'Type': list(learning_data.keys()),
            'Score': list(learning_data.values())
        })
        
        radar_chart = alt.Chart(df).mark_area(
            line=True,
            opacity=0.3
        ).encode(
            theta=alt.Theta('Type:N', sort=None),
            r=alt.R('Score:Q', scale=alt.Scale(domain=[0, 100])),
            color=alt.value('#3B82F6'),
            tooltip=['Type', 'Score']
        ).properties(
            width='container',
            height=350
        )
        
        st.altair_chart(radar_chart, use_container_width=True)
        
        # Display scores with progress bars
        for style, score in learning_data.items():
            st.markdown(f"""
            <div style="display:flex; align-items:center; margin-bottom:10px;">
                <div style="width:30%; font-weight:500;">{style.capitalize()}</div>
                <div style="width:60%; background-color:#E5E7EB; height:10px; border-radius:5px;">
                    <div style="width:{score}%; background-color:#3B82F6; height:10px; border-radius:5px;"></div>
                </div>
                <div style="width:10%; text-align:right; padding-left:10px;">{score}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[1]:
        # Similar implementation for personality traits
        personality_data = assessment["personality_traits"]
        df = pd.DataFrame({
            'Trait': list(personality_data.keys()),
            'Score': list(personality_data.values())
        })
        
        chart = alt.Chart(df).mark_bar().encode(
            x='Trait',
            y=alt.Y('Score', scale=alt.Scale(domain=[0, 100])),
            color=alt.value('#10B981'),
            tooltip=['Trait', 'Score']
        ).properties(
            width='container',
            height=300
        )
        
        st.altair_chart(chart, use_container_width=True)
    
    with tabs[2]:
        # Similar implementation for cognitive profile
        cognitive_data = assessment["cognitive_profile"]
        df = pd.DataFrame({
            'Ability': list(cognitive_data.keys()),
            'Score': list(cognitive_data.values())
        })
        
        chart = alt.Chart(df).mark_bar().encode(
            x='Ability',
            y=alt.Y('Score', scale=alt.Scale(domain=[0, 100])),
            color=alt.value('#F59E0B'),
            tooltip=['Ability', 'Score']
        ).properties(
            width='container',
            height=300
        )
        
        st.altair_chart(chart, use_container_width=True)

def display_analysis_results(result):
    """Display the analysis results in a tabbed interface"""
    st.markdown("## Analysis Results")
    
    tabs = st.tabs([
        "📊 Overview",
        "🧠 Psychometric Insights",
        "📈 Progress Insights",
        "⚠️ Mistake Analysis",
        "📚 Recommendations"
    ])
    
    with tabs[0]:
        st.markdown("### 📊 Dashboard Overview")
        # Create a summary card
        st.markdown("""
        <div style="background-color:#F0FDF4; padding:20px; border-radius:10px; border-left:5px solid #10B981;">
            <h3 style="margin-top:0; color:#065F46;">Student Assessment Summary</h3>
            <p>This dashboard provides a comprehensive analysis of the student's performance, learning style, 
            and personalized recommendations based on their psychometric profile and academic progress.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div style="background-color:#DBEAFE; padding:15px; border-radius:8px; text-align:center;">
                <h4 style="margin-top:0; color:#1E40AF;">Strong Subjects</h4>
                <h2 style="color:#1E40AF;">Chemistry</h2>
                <p>72.8% accuracy</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color:#FEF3C7; padding:15px; border-radius:8px; text-align:center;">
                <h4 style="margin-top:0; color:#92400E;">Focus Areas</h4>
                <h2 style="color:#92400E;">Vectors</h2>
                <p>42.1% accuracy</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
            <div style="background-color:#E0E7FF; padding:15px; border-radius:8px; text-align:center;">
                <h4 style="margin-top:0; color:#3730A3;">Learning Style</h4>
                <h2 style="color:#3730A3;">Visual</h2>
                <p>78% preference</p>
            </div>
            """, unsafe_allow_html=True)
            
    
    with tabs[1]:
        st.markdown("### 🧠 Psychometric Insights")
        st.markdown(f"""
        <div style="background-color:#F8FAFC; padding:20px; border-radius:10px; border:1px solid #E2E8F0;">
            {result["psychometric_insights"]}
        </div>
        """, unsafe_allow_html=True)
    
    with tabs[2]:
        st.markdown("### 📈 Progress Insights")
        st.markdown(f"""
        <div style="background-color:#F8FAFC; padding:20px; border-radius:10px; border:1px solid #E2E8F0;">
            {result["progress_insights"]}
        </div>
        """, unsafe_allow_html=True)
    
    with tabs[3]:
        st.markdown("### ⚠️ Mistake Analysis")
        st.markdown(f"""
        <div style="background-color:#F8FAFC; padding:20px; border-radius:10px; border:1px solid #E2E8F0;">
            {result["mistake_insights"]}
        </div>
        """, unsafe_allow_html=True)
    
    with tabs[4]:
        st.markdown("### 📚 Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Syllabus Recommendations")
            st.markdown(f"""
            <div style="background-color:#F0FDF4; padding:20px; border-radius:10px; border:1px solid #DCFCE7;">
                {result["syllabus_recommendations"]}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Question Recommendations")
            st.markdown(f"""
            <div style="background-color:#EFF6FF; padding:20px; border-radius:10px; border:1px solid #DBEAFE;">
                {result["question_recommendations"]}
            </div>
            """, unsafe_allow_html=True)

def display_detailed_visualizations(psychometric_data, progress_data):
    """Display detailed visualizations based on student data"""
    st.markdown("## Student Details")
    
    # Two-column layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        create_student_profile_card(psychometric_data)
    
    with col2:
        create_performance_summary(progress_data)
    
    st.markdown("## Topic Performance Breakdown")
    create_topic_breakdown(progress_data)
    
    # st.markdown("## Psychometric Profile")
    # create_psychometric_profile(psychometric_data)

def load_sample_data() -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Load sample psychometric and progress data for demonstration"""
    psychometric_data = {
        "student_details": {
            "name": "Rohit Verma",
            "student_id": "JEE2025_78901",
            "grade": "12th",
            "target_exam": "JEE Advanced 2025"
        },
        "assessment": {
            "learning_style": {
                "visual": 78,
                "auditory": 45,
                "kinesthetic": 65
            },
            "personality_traits": {
                "analytical": 82,
                "introversion": 70,
                "conscientiousness": 85
            },
            "cognitive_profile": {
                "spatial_reasoning": 88,
                "logical_thinking": 76,
                "working_memory": 65
            }
        }
    }
    
    progress_data = {
        "overall_performance": {
            "physics": 65.3,
            "chemistry": 72.8,
            "mathematics": 58.2
        },
        "topic_performance": {
            "physics": {
                "mechanics": {"accuracy_percentage": 74.5},
                "electromagnetism": {"accuracy_percentage": 52.1},
                "modern_physics": {"accuracy_percentage": 55.6}
            },
            "chemistry": {
                "organic_chemistry": {"accuracy_percentage": 78.2},
                "physical_chemistry": {"accuracy_percentage": 58.6}
            },
            "mathematics": {
                "calculus": {"accuracy_percentage": 61.3},
                "vectors": {"accuracy_percentage": 42.1},
                "probability": {"accuracy_percentage": 48.4}
            }
        }
    }
    return psychometric_data, progress_data

def render_educational_dashboard(workflow_function):
    """Main function to render the educational dashboard
    
    Args:
        workflow_function: The function to run analysis (e.g., run_educational_workflow)
    """
    apply_custom_css()
    render_header()
    
    def run_analysis_callback(user_id, use_sample_data = True):
        if use_sample_data:
            psychometric_data, progress_data = load_sample_data()
        else:
            psychometric_data = json.loads(st.session_state.get('psychometric_data', '{}'))
            progress_data = json.loads(st.session_state.get('progress_data', '{}'))
        
        try:
            with st.spinner("Running analysis..."):
                progress_bar = st.progress(0)
                for percent_complete in range(101):
                    progress_bar.progress(percent_complete)
                    if percent_complete == 100:
                        result = workflow_function(user_id, psychometric_data, progress_data)
                        st.session_state.analysis_result = result
                        st.session_state.psychometric_data = psychometric_data
                        st.session_state.progress_data = progress_data
            
            st.success("Analysis completed successfully!")
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
    
    user_id, use_sample_data = render_sidebar(run_analysis_callback)
    
    if not use_sample_data:
        render_data_input_form()
    
    if 'analysis_result' in st.session_state:
        result = st.session_state.analysis_result
        display_analysis_results(result)
        
        if 'psychometric_data' in st.session_state and 'progress_data' in st.session_state:
            try:
                psychometric_data = st.session_state.psychometric_data
                if isinstance(psychometric_data, str):
                    psychometric_data = json.loads(psychometric_data)
                
                progress_data = st.session_state.progress_data
                if isinstance(progress_data, str):
                    progress_data = json.loads(progress_data)
                
                display_detailed_visualizations(psychometric_data, progress_data)
                
            except Exception as e:
                st.error(f"Error creating visualizations: {str(e)}")
    else:
        render_welcome_screen()

if __name__ == "__main__":
      
    render_educational_dashboard(run_educational_workflow)
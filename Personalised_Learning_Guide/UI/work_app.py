import os
import sys
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import json
from typing import Dict, Any
from agents.workflow import run_educational_workflow  # Import your existing workflow

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

def main():
    st.set_page_config(
        page_title="Educational Assessment Dashboard",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 Educational Assessment Dashboard")
    
    # Sidebar for user input
    with st.sidebar:
        st.header("Student Information")
        user_id = st.text_input("Student ID", value="JEE2025_78901")
        
        st.subheader("Data Input Options")
        use_sample_data = st.checkbox("Use Sample Data", value=True)
        
        if st.button("Run Analysis"):
            if use_sample_data:
                psychometric_data, progress_data = load_sample_data()
            else:
                # Use custom data input
                psychometric_data = json.loads(st.session_state.get('psychometric_data', '{}'))
                progress_data = json.loads(st.session_state.get('progress_data', '{}'))
            
            try:
                with st.spinner("Running analysis..."):
                    result = run_educational_workflow(user_id, psychometric_data, progress_data)
                st.session_state.analysis_result = result
                st.success("Analysis completed successfully!")
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
    
    # Main content area
    if not use_sample_data:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Psychometric Data Input")
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
            st.subheader("Progress Data Input")
            progress_json = st.text_area(
                "Enter Progress Data (JSON)",
                value=json.dumps(load_sample_data()[1], indent=2),
                height=300
            )
            try:
                st.session_state.progress_data = progress_json
            except json.JSONDecodeError:
                st.error("Invalid JSON format for progress data")
    
    # Display Results
    if 'analysis_result' in st.session_state:
        result = st.session_state.analysis_result
        
        # Create tabs for different insights
        tabs = st.tabs([
            "Psychometric Insights",
            "Progress Insights",
            "Mistake Analysis",
            "Syllabus Recommendations",
            "Question Recommendations"
        ])
        
        with tabs[0]:
            st.markdown("### 🧠 Psychometric Insights")
            st.write(result["psychometric_insights"])
        
        with tabs[1]:
            st.markdown("### 📈 Progress Insights")
            st.write(result["progress_insights"])
        
        with tabs[2]:
            st.markdown("### ⚠️ Mistake Analysis")
            st.write(result["mistake_insights"])
        
        with tabs[3]:
            st.markdown("### 📚 Syllabus Recommendations")
            st.write(result["syllabus_recommendations"])
        
        with tabs[4]:
            st.markdown("### ❓ Question Recommendations")
            st.write(result["question_recommendations"])

if __name__ == "__main__":
    main()
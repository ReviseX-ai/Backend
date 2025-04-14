from typing import Dict, Any, List, Annotated, TypedDict, Literal
from langchain_core.messages import HumanMessage, AIMessage
import os
import json
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from agno.agent import Agent
from agno.models.google import Gemini
from Syllabus_suggestion_agent import SyllabusSuggestionAgent
from question_suggestion_agent import TopicQuestionRecommender
from Psychometric_Agent import PsychometricAnalyzer
from progress_tracker import StudentProgressAnalyzer
from mistake_finder import MistakeFinder


load_dotenv()

class WorkflowState(TypedDict):
    user_id: str
    psychometric_data: Dict[str, Any]
    progress_data: Dict[str, Any]
    psychometric_insights: str
    progress_insights: str
    mistake_insights: str
    syllabus_recommendations: str
    question_recommendations: str

def init_agent(model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
    return Agent(
        model=Gemini(id=model_id),
        markdown=enable_markdown,
    )

def psychometric_agent(state: WorkflowState) -> WorkflowState:
    prompt = json.dumps(state['psychometric_data'], indent=2)
    
    try:
        pychometric_analyzer = PsychometricAnalyzer()
        response = pychometric_analyzer.analyze_psychometric_data(prompt)
        # Make sure response is a string
        if not isinstance(response, str):
            response = str(response)
        state["psychometric_insights"] = response
    except Exception as e:
        print(f"Error in psychometric_agent: {e}")
        state["psychometric_insights"] = f"Error analyzing psychometric data: {str(e)}"
    
    return state

def progress_tracker_agent(state: WorkflowState) -> WorkflowState:
    """Analyze progress data and provide insights."""
    try:
        agent = StudentProgressAnalyzer()
        sample_data = state['progress_data']
        
        response = agent.analyze_progress(json.dumps(sample_data, indent=2))
        if not isinstance(response, str):
            response = str(response)
        state["progress_insights"] = response
    except Exception as e:
        print(f"Error in progress_tracker_agent: {e}")
        state["progress_insights"] = f"Error analyzing progress data: {str(e)}"
    
    return state

def mistake_finder_agent(state: WorkflowState) -> WorkflowState:
    try:
        agent = MistakeFinder()
        sample_data = json.dumps(state['progress_data'], indent=2)
        response = agent.analyze_mistakes(sample_data)
        # Make sure response is a string
        if not isinstance(response, str):
            response = str(response)
        state["mistake_insights"] = response
    except Exception as e:
        print(f"Error in mistake_finder_agent: {e}")
        state["mistake_insights"] = f"Error analyzing mistakes: {str(e)}"
    
    return state

def syllabus_suggestion_agent(state: WorkflowState) -> WorkflowState:
    try:
        agent = SyllabusSuggestionAgent()
        psychometric_insights = state['psychometric_insights']
        progress_insights = state['progress_insights']
        
        response = agent.get_syllabus_suggestion(psychometric_insights, progress_insights)
        if not isinstance(response, str):
            response = str(response)
        state["syllabus_recommendations"] = response
    except Exception as e:
        print(f"Error in syllabus_suggestion_agent: {e}")
        state["syllabus_recommendations"] = f"Error generating syllabus recommendations: {str(e)}"
    
    return state

def question_suggestion_agent(state: WorkflowState) -> WorkflowState:
    try:
        psychometric_data = state['psychometric_insights']
        progress_data = state['progress_insights']
        mistake_data = state['mistake_insights']
        
        agent = TopicQuestionRecommender()
        response = agent.recommend_practice_focus(progress_data)
        # Handle different response types
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)
        
        state["question_recommendations"] = content
    except Exception as e:
        print(f"Error in question_suggestion_agent: {e}")
        state["question_recommendations"] = f"Error generating question recommendations: {str(e)}"
    
    return state

def create_educational_workflow():
    # Create a new workflow with a single entry point and sequential flow
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("psychometric_agent", psychometric_agent)
    workflow.add_node("progress_tracker_agent", progress_tracker_agent)
    workflow.add_node("mistake_finder_agent", mistake_finder_agent)
    workflow.add_node("syllabus_suggestion_agent", syllabus_suggestion_agent)
    workflow.add_node("question_suggestion_agent", question_suggestion_agent)
    
    # Define sequential flow
    workflow.add_edge("psychometric_agent", "progress_tracker_agent")
    workflow.add_edge("progress_tracker_agent", "mistake_finder_agent")
    workflow.add_edge("mistake_finder_agent", "syllabus_suggestion_agent")
    workflow.add_edge("syllabus_suggestion_agent", "question_suggestion_agent")
    workflow.add_edge("question_suggestion_agent", END)
    
    # Set entry point
    workflow.set_entry_point("psychometric_agent")
    
    return workflow.compile()

def run_educational_workflow(user_id: str, psychometric_data: Dict[str, Any], progress_data: Dict[str, Any]):
    workflow = create_educational_workflow()
    
    initial_state = WorkflowState(
        user_id=user_id,
        psychometric_data=psychometric_data,
        progress_data=progress_data,
        psychometric_insights="",
        progress_insights="",
        mistake_insights="",
        syllabus_recommendations="",
        question_recommendations=""
    )
    
    result = workflow.invoke(initial_state)
    
    return result

if __name__ == "__main__":
    user_id = "JEE2025_78901"
    
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
      },
      "question_performance": {
        "physics": {
          "numerical": {"accuracy": 62.5, "count": 96},
          "conceptual": {"accuracy": 70.2, "count": 84}
        },
        "chemistry": {
          "reaction_based": {"accuracy": 80.1, "count": 65},
          "numerical": {"accuracy": 55.8, "count": 52}
        },
        "mathematics": {
          "derivation": {"accuracy": 60.4, "count": 48},
          "application": {"accuracy": 49.2, "count": 65}
        }
      }
    }
    
    try:
        result = run_educational_workflow(user_id, psychometric_data, progress_data)
        
        print("=== EDUCATIONAL ASSESSMENT WORKFLOW RESULTS ===\n")
        print("PSYCHOMETRIC INSIGHTS:")
        print(result["psychometric_insights"])
        print("\nPROGRESS INSIGHTS:")
        print(result["progress_insights"])
        print("\nMISTAKE INSIGHTS:")
        print(result["mistake_insights"])
        print("\nSYLLABUS RECOMMENDATIONS:")
        print(result["syllabus_recommendations"])
        print("\nQUESTION RECOMMENDATIONS:")
        print(result["question_recommendations"])
    except Exception as e:
        print(f"Workflow execution failed: {e}")
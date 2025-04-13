import streamlit as st
import json

# Title of the application
st.title("🧠 Student Psychometric Test – Multiple Choice (MCQ)")

# Introduction
st.write("""
This is a psychometric test designed to assess your personality, cognitive preferences, and learning style. 
Answer the questions honestly to help tailor your learning experience.
""")

# Questions and options
questions = [
    {
        "question": "How do you prefer to learn new topics?",
        "options": [
            "A. Watching videos or diagrams",
            "B. Listening to explanations",
            "C. Reading books or articles",
            "D. Doing hands-on activities or experiments"
        ],
    },
    {
        "question": "How do you usually approach a difficult problem?",
        "options": [
            "A. Break it into smaller parts and analyze",
            "B. Ask someone for help or guidance",
            "C. Look for examples or tutorials online",
            "D. Try solving it repeatedly until you succeed"
        ],
    },
    {
        "question": "How do you feel when working in a group project?",
        "options": [
            "A. I enjoy it and usually take the lead",
            "B. I like it if I get to choose my role",
            "C. I prefer working alone",
            "D. I adapt to the group but don't speak much"
        ],
    },
    {
        "question": "What motivates you the most to study?",
        "options": [
            "A. Achieving high marks or rewards",
            "B. Gaining knowledge and understanding",
            "C. Parental or teacher expectations",
            "D. Curiosity and interest in the subject"
        ],
    },
    {
        "question": "When do you feel most focused while studying?",
        "options": [
            "A. Early morning",
            "B. Late at night",
            "C. After physical activity",
            "D. Doesn't matter – I can focus anytime"
        ],
    },
    {
        "question": "What best describes your reaction to failure?",
        "options": [
            "A. I try harder next time",
            "B. I feel disappointed but move on",
            "C. I get discouraged",
            "D. I analyze what went wrong and learn from it"
        ],
    },
    {
        "question": "Which subject do you find most enjoyable?",
        "options": [
            "A. Math or Science",
            "B. Literature or History",
            "C. Arts or Music",
            "D. Sports or Physical Education"
        ],
    },
    {
        "question": "How do you manage time when you have multiple tasks?",
        "options": [
            "A. I make a schedule and stick to it",
            "B. I prioritize the easiest tasks first",
            "C. I do things randomly",
            "D. I often procrastinate but finish just in time"
        ],
    },
    {
        "question": "How do you react to unfamiliar topics?",
        "options": [
            "A. I feel excited to explore them",
            "B. I get nervous but try to understand",
            "C. I avoid them unless necessary",
            "D. I ask others to explain it"
        ],
    },
    {
        "question": "Which of these best describes your personality?",
        "options": [
            "A. Logical and Analytical",
            "B. Creative and Expressive",
            "C. Calm and Observant",
            "D. Energetic and Outgoing"
        ],
    },
]

# Collect answers
responses = {}
for idx, q in enumerate(questions, 1):
    st.subheader(f"Question {idx}")
    st.write(q["question"])
    responses[f"Q{idx}"] = st.radio(
        "Your Answer:",
        q["options"],
        key=f"q_{idx}"
    )

# Submit button
if st.button("Submit"):
    # Save responses to JSON
    with open("psychometric_responses.json", "w") as file:
        json.dump(responses, file, indent=4)

    st.success("Your responses have been recorded successfully!")
    st.write("Thank you for completing the test.")
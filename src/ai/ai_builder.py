import streamlit as st
import json


def ai_quiz_builder():
    st.title("🤖 Admin / AI Quiz Builder")

    topic = st.text_input("Topic for quiz:")
    num = st.number_input("Number of questions", min_value=1, max_value=20, value=5)

    if st.button("Generate placeholder quiz"):
        quiz = []
        for i in range(num):
            quiz.append(
                {
                    "id": f"ai_q{i+1}",
                    "question": f"Sample question {i+1} on {topic}",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A",
                    "difficulty": "easy",
                    "hints": ["Example hint"],
                    "tts_text": f"Sample question {i+1} on {topic}",
                    "isl_gif": "",
                    "isl_video": "",
                }
            )
        st.success("Generated sample quiz:")
        st.json(quiz)

        st.download_button(
            "Download quiz JSON",
            data=json.dumps(quiz, indent=2),
            file_name=f"{topic}_quiz.json",
        )

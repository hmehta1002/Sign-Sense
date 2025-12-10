import streamlit as st
import json

def ai_quiz_builder():
    st.title("🤖 AI Quiz Builder")
    st.caption("Admin tool to generate or manage quizzes.")

    st.markdown("### Enter Topic")
    topic = st.text_input("Topic")

    st.markdown("### Number of Questions")
    num = st.number_input("Count", min_value=1, max_value=20, value=5)

    if st.button("Generate Quiz"):
        quiz = []
        for i in range(num):
            quiz.append({
                "id": f"ai_q{i+1}",
                "question": f"Sample question {i+1} on {topic}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A",
                "hints": ["Hint 1"],
                "difficulty": "easy",
                "isl_gif": "",
                "isl_video": "",
                "tts_text": f"Sample question {i+1} for topic {topic}"
            })

        st.success("Quiz generated!")
        st.json(quiz)

        st.download_button(
            "Download as JSON",
            data=json.dumps(quiz, indent=2),
            file_name=f"{topic}_quiz.json"
        )


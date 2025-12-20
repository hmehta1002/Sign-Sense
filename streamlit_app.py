import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / "src"
sys.path.append(str(BASE_DIR))

import streamlit as st
import time
import os
import re

# ---------------------------------------------------------
# IMPORT EXISTING MODULES
# ---------------------------------------------------------
from backend.logic import QuizEngine
from backend.cloud_store import (
    create_classroom,
    join_classroom,
    add_classroom_question,
    submit_classroom_answer,
    get_classroom_state,
)
from frontend.ui import apply_theme, render_question_UI
from frontend.dashboard import render_dashboard
from revision.revision_ui import render_revision_page
from ai.ai_builder import ai_quiz_builder

# ---------------------------------------------------------
# SESSION STATE INIT
# ---------------------------------------------------------
st.session_state.setdefault("cognitive_log", {})
st.session_state.setdefault("chat_history", [])

# ---------------------------------------------------------
# PDF HELPERS (NEW)
# ---------------------------------------------------------
def extract_text_from_pdf(pdf_file):
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception:
        return ""


def generate_questions_from_pdf(text):
    """
    Generic MCQ parser for independent dataset PDFs.
    Supports standard formats like:
    1. Question
    a) Option
    b) Option
    c) Option
    d) Option
    """

    questions = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect question (starts with number + dot)
        if re.match(r"^\d+\.", line):
            question_text = re.sub(r"^\d+\.\s*", "", line)
            options = []

            j = i + 1
            while j < len(lines) and len(options) < 4:
                if re.match(r"^[a-dA-D][\)\.]", lines[j]):
                    option = re.sub(r"^[a-dA-D][\)\.]\s*", "", lines[j])
                    options.append(option)
                j += 1

            if len(options) >= 2:
                questions.append({
                    "question": question_text,
                    "options": options,
                    "answer": options[0],  # placeholder
                })

            i = j
        else:
            i += 1

    # Fallback (never crash)
    if not questions:
        questions = [{
            "question": "Dataset loaded successfully, but no MCQs detected.",
            "options": [
                "Check PDF format",
                "Ensure MCQ structure",
                "Try another dataset"
            ],
            "answer": "Check PDF format",
        }]

    return questions

# ---------------------------------------------------------
# COGNITIVE LOGGING
# ---------------------------------------------------------
def log_cognitive(student, question, meta):
    st.session_state.cognitive_log.setdefault(student, {}).setdefault(question, []).append(meta)

# ---------------------------------------------------------
# DYNAMIC FLOW OVERLAY
# ---------------------------------------------------------
def dynamic_flow_overlay(question, subject):
    st.markdown("#### 🔄 Reasoning Flow")
    if subject == "math":
        st.code("Read numbers\n↓\nApply BODMAS\n↓\nSolve step-by-step\n↓\nAnswer")
    else:
        st.code("Read sentence\n↓\nIdentify key idea\n↓\nEliminate options\n↓\nAnswer")

# ---------------------------------------------------------
# AI LEARNING ASSISTANT
# ---------------------------------------------------------
def render_chatbot():
    st.sidebar.divider()
    st.sidebar.subheader("🤖 AI Learning Assistant")

    user_input = st.sidebar.text_input("Ask how to think:", key="chat_input")

    if st.sidebar.button("Ask AI"):
        if not user_input.strip():
            return

        st.session_state.chat_history.append(("You", user_input))

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            reply = "AI not connected. In production, this explains steps."
        else:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Explain concepts step-by-step."},
                        {"role": "user", "content": user_input},
                    ],
                    max_tokens=200,
                )
                reply = response.choices[0].message.content
            except Exception:
                reply = "AI temporarily unavailable."

        st.session_state.chat_history.append(("AI", reply))

    for who, msg in st.session_state.chat_history[-6:]:
        st.sidebar.markdown(f"**{who}:** {msg}")

# ---------------------------------------------------------
# SOLO QUIZ (WITH PDF UPLOAD)
# ---------------------------------------------------------
def solo_quiz():
    st.header("📘 Solo Quiz")

    mode = st.selectbox("Accessibility Mode", ["standard", "isl", "adhd", "dyslexia"])
    subject = st.selectbox("Subject", ["Math", "English"]).lower()

    st.markdown("### Question Source")
    source = st.radio(
        "Choose how questions are loaded:",
        ["Built-in Quiz", "Upload PDF Dataset"]
    )

    pdf_text = None
    if source == "Upload PDF Dataset":
        pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])
        if pdf_file:
            pdf_text = extract_text_from_pdf(pdf_file)
            if pdf_text.strip():
                st.success("PDF loaded successfully.")
            else:
                st.warning("Could not extract text from PDF.")

    if st.button("Start / Restart Quiz"):
        engine = QuizEngine(mode, subject)

        if source == "Upload PDF Dataset" and pdf_text:
            engine.questions = generate_questions_from_pdf(pdf_text)

        st.session_state.engine = engine
        st.session_state.q_start_time = time.time()
        st.experimental_rerun()

    engine = st.session_state.get("engine")
    if not engine:
        st.info("Click Start to begin.")
        return

    q = engine.get_current_question()
    if not q:
        st.balloons()
        st.success("🎉 Quiz completed!")
        return

    selected = render_question_UI(q, mode)

    if mode in ["isl", "adhd"]:
        dynamic_flow_overlay(q["question"], subject)

    col1, col2 = st.columns(2)

    with col1:
        if engine.current_index > 0:
            if st.button("⬅ Back"):
                engine.current_index -= 1
                st.experimental_rerun()

    with col2:
        if st.button("Next ➜"):
            if selected:
                time_spent = int(time.time() - st.session_state.q_start_time)
                log_cognitive(
                    "Solo_User",
                    q["question"],
                    {
                        "mode": mode,
                        "time_spent": time_spent,
                        "hesitation": time_spent > 10,
                    },
                )
                engine.check_answer(selected)

            engine.next_question()
            st.session_state.q_start_time = time.time()
            st.experimental_rerun()

# ---------------------------------------------------------
# STUDENT CLASSROOM
# ---------------------------------------------------------
def student_classroom():
    st.header("🎓 Student Classroom")

    name = st.text_input("Your Name")
    code = st.text_input("Classroom Code")

    if st.button("Join Classroom"):
        if join_classroom(code, name):
            st.balloons()
            st.session_state.student = name
            st.session_state.joined_code = code
            st.success("Joined classroom")
        else:
            st.error("Invalid code")

    if "joined_code" in st.session_state:
        classroom = get_classroom_state(st.session_state.joined_code)
        for i, q in enumerate(classroom.get("questions", [])):
            st.markdown(f"**Q{i+1}: {q}**")
            ans = st.text_input("Answer", key=f"ans_{i}")
            if st.button("Submit", key=f"submit_{i}"):
                submit_classroom_answer(
                    st.session_state.joined_code,
                    st.session_state.student,
                    i,
                    ans,
                )
                st.success("Submitted")

# ---------------------------------------------------------
# TEACHER CLASSROOM + COGNITIVE CARDS
# ---------------------------------------------------------
def teacher_classroom():
    st.header("🧑‍🏫 Insight Classroom")

    if "class_code" not in st.session_state:
        if st.button("Create Classroom"):
            st.session_state.class_code = create_classroom()
            st.balloons()
    else:
        st.success(f"Classroom Code: {st.session_state.class_code}")

        q = st.text_input("Upload Question")
        if st.button("Add Question") and q:
            add_classroom_question(st.session_state.class_code, q)
            st.success("Question added")

        classroom = get_classroom_state(st.session_state.class_code)
        students = classroom.get("students", {})

        st.subheader("Students")
        for name, data in students.items():
            st.write(f"• {name} — {data.get('status', 'Joined')}")

    st.divider()
    st.subheader("🧠 Cognitive Replay")

    if not st.session_state.cognitive_log:
        st.info("No cognitive data yet.")
    else:
        for student, qs in st.session_state.cognitive_log.items():
            st.markdown(f"### 👤 {student}")
            for q, entries in qs.items():
                last = entries[-1]
                if last["hesitation"]:
                    status = "🔴 Needs Attention"
                    color = "#ff4d4d"
                else:
                    status = "🟢 Confident"
                    color = "#2ecc71"

                st.markdown(
                    f"""
                    <div style="padding:12px; margin-bottom:10px;
                    border-left:6px solid {color}; background:#f9f9f9;">
                    <b>Question:</b> {q}<br>
                    <b>Time:</b> {last["time_spent"]}s<br>
                    <b>Status:</b> {status}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")
    apply_theme()

    page = st.sidebar.radio(
        "Navigation",
        [
            "📘 Solo Quiz",
            "🔁 Revision Lab",
            "📊 Dashboard",
            "🎓 Student Classroom",
            "🧑‍🏫 Teacher Classroom",
            "🤖 Admin / AI Quiz Builder",
        ],
    )

    if page == "📘 Solo Quiz":
        solo_quiz()
    elif page == "🔁 Revision Lab":
        engine = st.session_state.get("engine")
        if engine:
            render_revision_page(engine)
        else:
            st.info("Start a quiz first.")
    elif page == "📊 Dashboard":
        engine = st.session_state.get("engine")
        if engine:
            render_dashboard(engine)
        else:
            st.info("Complete a quiz first.")
    elif page == "🎓 Student Classroom":
        student_classroom()
    elif page == "🧑‍🏫 Teacher Classroom":
        teacher_classroom()
    elif page == "🤖 Admin / AI Quiz Builder":
        ai_quiz_builder()

    render_chatbot()

# ---------------------------------------------------------
if __name__ == "__main__":
    main()

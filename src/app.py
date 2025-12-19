import os
import streamlit as st
from openai import OpenAI

from frontend.ui import apply_theme, render_question_UI
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from revision.revision_ui import render_revision_page

from backend.cloud_store import (
    create_classroom,
    join_classroom,
    add_classroom_question,
    submit_classroom_answer,
    get_classroom_state,
)

# ---------------------------------------------------------
# OPENAI CLIENT (NEW SDK – FIXED)
# ---------------------------------------------------------
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

# ---------------------------------------------------------
# RESET APP
# ---------------------------------------------------------
def reset_app():
    st.session_state.clear()
    st.experimental_rerun()

# ---------------------------------------------------------
# USER PROFILE
# ---------------------------------------------------------
def render_user_profile():
    st.sidebar.subheader("User Profile")
    role = st.sidebar.selectbox("Role", ["Student", "Teacher"])
    st.session_state["role"] = role

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
def sidebar_navigation():
    pages = {
        "Solo Quiz": "solo",
        "Live Session": "live",
        "Revision Lab": "revision",
        "Dashboard": "dashboard",
        "Admin / AI Quiz Builder": "admin_ai",
    }
    return pages[st.sidebar.radio("Navigation", list(pages.keys()))]

# ---------------------------------------------------------
# AI LEARNING ASSISTANT (FIXED)
# ---------------------------------------------------------
def render_ai_learning_assistant(question_text: str, mode: str):
    st.subheader("🤖 AI Learning Assistant")

    if client is None:
        st.info("AI assistant unavailable (API key missing).")
        return

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask about the concept (not the answer)")

    if user_input:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        system_prompt = f"""
You are an AI learning assistant inside an educational quiz app.

STRICT RULES:
- Never give the final answer.
- Never select an option.
- Explain concepts only.
- Keep explanations short and clear.

Accessibility mode: {mode}

Guidelines:
- ISL → step-by-step, visual wording
- Dyslexia → short sentences, structured
- ADHD → bullet points, concise

Question:
{question_text}
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                temperature=0.3,
            )
            reply = response.choices[0].message.content

        except Exception as e:
            reply = "AI is temporarily unavailable. Please try again shortly."

        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )
        st.experimental_rerun()

# ---------------------------------------------------------
# TEACHER CLASSROOM
# ---------------------------------------------------------
def teacher_classroom():
    st.header("Insight Classroom")

    if "class_code" not in st.session_state:
        if st.button("Create Classroom"):
            st.session_state["class_code"] = create_classroom()
    else:
        st.success(f"Classroom Code: {st.session_state['class_code']}")

        st.subheader("Upload Question")
        q = st.text_input("Question for students")
        if st.button("Add Question") and q:
            add_classroom_question(st.session_state["class_code"], q)
            st.success("Question added")

        classroom = get_classroom_state(st.session_state["class_code"])

        st.subheader("Students")
        students = classroom.get("students", {})
        if not students:
            st.info("No students joined yet.")
        else:
            for name, data in students.items():
                st.write(f"• {name} — {data.get('status', 'joined')}")

# ---------------------------------------------------------
# STUDENT CLASSROOM
# ---------------------------------------------------------
def student_classroom():
    st.header("Join Classroom")

    name = st.text_input("Your Name")
    code = st.text_input("Classroom Code")

    if st.button("Join"):
        if join_classroom(code, name):
            st.session_state["student_name"] = name
            st.session_state["joined_code"] = code
            st.success("Joined classroom")
        else:
            st.error("Invalid classroom code")

    if "joined_code" in st.session_state:
        classroom = get_classroom_state(st.session_state["joined_code"])
        questions = classroom.get("questions", [])

        st.subheader("Class Questions")
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}: {q}**")
            ans = st.text_input("Your answer", key=f"ans_{i}")
            if st.button("Submit", key=f"submit_{i}"):
                submit_classroom_answer(
                    st.session_state["joined_code"],
                    st.session_state["student_name"],
                    i,
                    ans,
                )
                st.success("Submitted")

# ---------------------------------------------------------
# SOLO QUIZ
# ---------------------------------------------------------
def solo_quiz_page():
    st.header("Solo Quiz")

    mode = st.selectbox(
        "Accessibility Mode",
        ["standard", "isl", "adhd", "dyslexia"]
    )

    subject = st.selectbox("Subject", ["Math", "English"]).lower()

    if st.button("Start / Restart Quiz"):
        st.session_state["engine"] = QuizEngine(mode, subject)
        st.session_state.pop("chat_history", None)
        st.experimental_rerun()

    engine = st.session_state.get("engine")
    if not engine:
        st.info("Click Start / Restart Quiz to begin.")
        return

    q = engine.get_current_question()
    if q is None:
        st.success("Quiz completed 🎉")
        return

    selected = render_question_UI(q, mode)

    with st.expander("💡 Need help understanding this question?"):
        render_ai_learning_assistant(q["question"], mode)

    if st.button("Next"):
        if selected:
            engine.check_answer(selected)
        engine.next_question()
        st.session_state.pop("chat_history", None)
        st.experimental_rerun()

# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------
def route_page(page):
    role = st.session_state.get("role", "Student")

    if role == "Teacher":
        teacher_classroom()
        return

    if page == "solo":
        solo_quiz_page()
    elif page == "dashboard":
        render_dashboard(st.session_state.get("engine"))
    elif page == "revision":
        render_revision_page(st.session_state.get("engine"))
    elif page == "live":
        engine = st.session_state.get("engine")
        if engine:
            from live.live_sync import live_session_page
            live_session_page(engine, {})
        else:
            st.warning("Start a quiz first.")
    elif page == "admin_ai":
        ai_quiz_builder()

    st.divider()
    student_classroom()

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")
    apply_theme()

    render_user_profile()

    if st.sidebar.button("Reset App"):
        reset_app()

    page = sidebar_navigation()
    route_page(page)

if __name__ == "__main__":
    main()

import streamlit as st
import random
import re
from frontend.ui import apply_theme, render_question_UI
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from revision.revision_ui import render_revision_page

# ---------------------------------------------------------
# GLOBAL CLASSROOM STATE (PER SESSION – PROTOTYPE)
# ---------------------------------------------------------
if "classroom" not in st.session_state:
    st.session_state.classroom = {
        "code": None,
        "questions": [],
        "students": {}   # name -> status
    }

# ---------------------------------------------------------
# RESET
# ---------------------------------------------------------
def reset_app():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.experimental_rerun()

# ---------------------------------------------------------
# USER PROFILE
# ---------------------------------------------------------
def render_user_profile():
    st.sidebar.subheader("User Profile")
    role = st.sidebar.selectbox("Role", ["Student", "Teacher"])
    st.session_state.role = role

# ---------------------------------------------------------
# NAVIGATION
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
# TEACHER CLASSROOM
# ---------------------------------------------------------
def teacher_classroom():
    st.header("Insight Classroom")

    # Create classroom
    if st.session_state.classroom["code"] is None:
        if st.button("Create Classroom"):
            st.session_state.classroom["code"] = f"CLS-{random.randint(100,999)}"
    else:
        st.success(f"Classroom Code: {st.session_state.classroom['code']}")

    # Upload question
    st.subheader("Upload Question")
    q = st.text_input("Enter question for students")
    if st.button("Add Question") and q:
        st.session_state.classroom["questions"].append(q)
        st.success("Question added")

    # Student progress
    st.subheader("Student Progress")
    if not st.session_state.classroom["students"]:
        st.info("No students joined yet")
    else:
        for name, status in st.session_state.classroom["students"].items():
            st.write(f"• {name}: {status}")

# ---------------------------------------------------------
# STUDENT JOIN CLASSROOM
# ---------------------------------------------------------
def student_join_classroom():
    st.header("Join Classroom")

    name = st.text_input("Your Name")
    code = st.text_input("Classroom Code")

    if st.button("Join Classroom"):
        if code == st.session_state.classroom["code"]:
            st.session_state.student_name = name
            st.session_state.classroom["students"][name] = "Joined"
            st.success("Joined classroom")
        else:
            st.error("Invalid classroom code")

# ---------------------------------------------------------
# STUDENT ANSWER QUESTIONS
# ---------------------------------------------------------
def student_classroom_questions():
    name = st.session_state.get("student_name")
    if not name:
        return

    st.subheader("Classroom Questions")

    for i, q in enumerate(st.session_state.classroom["questions"]):
        st.markdown(f"**Q{i+1}: {q}**")
        ans = st.text_input("Your answer", key=f"ans_{i}")

        if st.button("Submit", key=f"submit_{i}"):
            st.session_state.classroom["students"][name] = "Answered"
            st.success("Answer submitted")

# ---------------------------------------------------------
# SOLO QUIZ (UNCHANGED CORE)
# ---------------------------------------------------------
def solo_quiz_page():
    st.header("Solo Quiz")

    mode = st.selectbox(
        "Accessibility Mode",
        ["standard", "dyslexia", "adhd", "isl"]
    )

    subject_label = st.selectbox("Subject", ["Math", "English"])
    subject = subject_label.lower()

    if st.button("Start / Restart Quiz"):
        st.session_state.engine = QuizEngine(mode, subject)
        st.experimental_rerun()

    engine = st.session_state.get("engine")
    if not engine:
        st.info("Click Start / Restart Quiz to begin.")
        return

    q = engine.get_current_question()
    if q is None:
        st.success("Quiz complete.")
        return

    selected = render_question_UI(q, mode)

    if st.button("Next"):
        if selected:
            engine.check_answer(selected)
        engine.next_question()
        st.experimental_rerun()

# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------
def route_page(page):
    role = st.session_state.get("role", "Student")

    if role == "Teacher":
        teacher_classroom()
        return

    if role == "Student" and st.session_state.classroom["code"]:
        student_join_classroom()
        student_classroom_questions()

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

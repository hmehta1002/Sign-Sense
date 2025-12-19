import streamlit as st
from frontend.ui import apply_theme, render_question_UI
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from revision.revision_ui import render_revision_page

# ---- Classroom backend (Firebase + local fallback) ----
from backend.cloud_store import (
    create_classroom,
    join_classroom,
    add_classroom_question,
    submit_classroom_answer,
    get_classroom_state,
)

# ---------------------------------------------------------
# RESET APP
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
# TEACHER CLASSROOM
# ---------------------------------------------------------
def teacher_classroom():
    st.header("Insight Classroom")

    # Create classroom
    if "class_code" not in st.session_state:
        if st.button("Create Classroom"):
            st.session_state["class_code"] = create_classroom()
    else:
        st.success(f"Classroom Code: {st.session_state['class_code']}")

        # Upload question
        st.subheader("Upload Question")
        q = st.text_input("Enter question for students")
        if st.button("Add Question") and q:
            add_classroom_question(st.session_state["class_code"], q)
            st.success("Question added")

        # View classroom state
        classroom = get_classroom_state(st.session_state["class_code"])

        st.subheader("Student Progress")
        students = classroom.get("students", {})
        if not students:
            st.info("No students joined yet")
        else:
            for name, data in students.items():
                st.write(f"• {name}: {data.get('status', '—')}")

        # View uploaded questions
        st.subheader("Questions")
        for i, q in enumerate(classroom.get("questions", [])):
            st.write(f"Q{i+1}: {q}")


# ---------------------------------------------------------
# STUDENT CLASSROOM
# ---------------------------------------------------------
def student_classroom():
    st.header("Join Classroom")

    name = st.text_input("Your Name")
    code = st.text_input("Classroom Code")

    if st.button("Join Classroom"):
        if join_classroom(code, name):
            st.session_state["student_name"] = name
            st.session_state["joined_code"] = code
            st.success("Joined classroom")
        else:
            st.error("Invalid classroom code")

    # If joined, show questions
    if "joined_code" in st.session_state:
        classroom = get_classroom_state(st.session_state["joined_code"])
        questions = classroom.get("questions", [])

        st.subheader("Classroom Questions")

        if not questions:
            st.info("No questions uploaded yet")
        else:
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}: {q}**")
                ans = st.text_input("Your answer", key=f"ans_{i}")
                if st.button("Submit Answer", key=f"submit_{i}"):
                    submit_classroom_answer(
                        st.session_state["joined_code"],
                        st.session_state["student_name"],
                        i,
                        ans,
                    )
                    st.success("Answer submitted")


# ---------------------------------------------------------
# SOLO QUIZ PAGE
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
        st.session_state["engine"] = QuizEngine(mode, subject)
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

    if role == "Student" and page == "solo":
        solo_quiz_page()
    elif role == "Student" and page == "dashboard":
        render_dashboard(st.session_state.get("engine"))
    elif role == "Student" and page == "revision":
        render_revision_page(st.session_state.get("engine"))
    elif role == "Student" and page == "live":
        engine = st.session_state.get("engine")
        if engine:
            from live.live_sync import live_session_page
            live_session_page(engine, {})
        else:
            st.warning("Start a quiz first.")
    elif role == "Student" and page == "admin_ai":
        ai_quiz_builder()

    # Classroom join available to students at all times
    if role == "Student":
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

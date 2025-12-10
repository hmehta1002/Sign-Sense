import streamlit as st

from frontend.ui import apply_theme, render_question_UI
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from live.live_sync import init_live_session, live_session_page
from revision.revision_ui import render_revision_page


# ---------------- reset ----------------
def reset_app():
    st.session_state.clear()
    st.rerun()


# ---------------- sidebar nav ----------------
def sidebar_navigation():
    pages = {
        "📘 Solo Quiz": "solo",
        "🌐 Live Session": "live",
        "🔁 Revision Lab": "revision",
        "📊 Dashboard": "dashboard",
        "🤖 Admin / AI Quiz Builder": "admin_ai",
    }
    choice = st.sidebar.radio("Navigation", list(pages.keys()))
    return pages[choice]


# ---------------- ensure engine ----------------
def ensure_engine(mode: str, subject: str):
    if "engine" not in st.session_state:
        st.session_state["engine"] = QuizEngine(mode, subject)
    return st.session_state["engine"]


# ---------------- solo quiz page ----------------
def solo_quiz_page():
    st.header("📘 Solo Quiz")

    # mode and subject are chosen here every time (no complex state)
    mode = st.selectbox(
        "Accessibility mode",
        ["standard", "dyslexia", "adhd", "isl", "hybrid"],
        index=0,
    )

    subject_label = st.selectbox("Subject", ["Math", "English"], index=0)
    subject = subject_label.lower()

    if st.button("Start / Restart Quiz"):
        # fresh engine
        st.session_state["engine"] = QuizEngine(mode, subject)

    engine: QuizEngine | None = st.session_state.get("engine")

    if not engine:
        st.info("Click 'Start / Restart Quiz' to begin.")
        return

    # update engine mode if user changes mode mid-quiz
    engine.mode = mode
    engine.subject = subject

    question = engine.get_current_question()
    if question is None:
        st.success("🎉 Quiz complete!")
        if st.button("📊 View Dashboard"):
            st.session_state["page"] = "dashboard"
            st.rerun()
        return

    # render question
    selected = render_question_UI(question, mode)

    col1, col2 = st.columns(2)

    with col1:
        if engine.current_index > 0:
            if st.button("⬅ Back"):
                engine.current_index -= 1
                st.rerun()

    with col2:
        if st.button("Next ➜"):
            if selected is not None:
                try:
                    engine.check_answer(selected)
                except Exception:
                    pass
            engine.next_question()
            st.rerun()


# ---------------- router ----------------
def route_page(page_name: str):
    if page_name == "solo":
        solo_quiz_page()
    elif page_name == "dashboard":
        render_dashboard(st.session_state.get("engine"))
    elif page_name == "revision":
        render_revision_page(st.session_state.get("engine"))
    elif page_name == "live":
        init_live_session()
        live_session_page(st.session_state.get("engine"), {})
    elif page_name == "admin_ai":
        ai_quiz_builder()
    else:
        st.error("Unknown page.")


# ---------------- main ----------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")
    apply_theme()

    if st.sidebar.button("🔁 Reset App"):
        reset_app()

    page = sidebar_navigation()
    st.session_state["page"] = page

    route_page(page)


if __name__ == "__main__":
    main()

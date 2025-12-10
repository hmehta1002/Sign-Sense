import streamlit as st

from frontend.ui import apply_theme, render_question_UI
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from revision.revision_ui import render_revision_page


# ---------------------------------------------------------
# RESET APP
# ---------------------------------------------------------
def reset_app():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.stop()     # <<< IMPORTANT: no rerun loop


# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
def sidebar_navigation():
    pages = {
        "📘 Solo Quiz": "solo",
        "🌐 Live Session": "live",
        "🔁 Revision Lab": "revision",
        "📊 Dashboard": "dashboard",
        "🤖 Admin / AI Quiz Builder": "admin_ai",
    }
    return pages[st.sidebar.radio("Navigation", list(pages.keys()))]


# ---------------------------------------------------------
# SOLO QUIZ PAGE
# ---------------------------------------------------------
def solo_quiz_page():
    st.header("📘 Solo Quiz")

    mode = st.selectbox(
        "Accessibility Mode",
        ["standard", "dyslexia", "adhd", "isl", "hybrid"]
    )

    subject_label = st.selectbox("Subject", ["Math", "English"])
    subject = subject_label.lower()

    # Start/Restart
    if st.button("Start / Restart Quiz"):
        st.session_state["engine"] = QuizEngine(mode, subject)
        st.session_state["solo_started"] = True
        st.stop()   # <<< STOP, don’t rerun loop

    engine = st.session_state.get("engine")

    if not engine:
        st.info("Click 'Start / Restart Quiz' to begin.")
        return

    # Sync engine parameters
    engine.mode = mode
    engine.subject = subject

    q = engine.get_current_question()

    if q is None:
        st.success("🎉 Quiz complete!")
        if st.button("📊 View Dashboard"):
            st.session_state["page"] = "dashboard"
            st.stop()
        return

    selected = render_question_UI(q, mode)

    col1, col2 = st.columns(2)

    with col1:
        if engine.current_index > 0:
            if st.button("⬅ Back"):
                engine.current_index -= 1
                st.stop()

    with col2:
        if st.button("Next ➜"):
            if selected:
                engine.check_answer(selected)
            engine.next_question()
            st.stop()


# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------
def route_page(page_name: str):

    if page_name == "solo":
        solo_quiz_page()

    elif page_name == "dashboard":
        render_dashboard(st.session_state.get("engine"))

    elif page_name == "revision":
        render_revision_page(st.session_state.get("engine"))

    elif page_name == "live":
        engine = st.session_state.get("engine")
        if not engine:
            st.warning("Start a quiz first to initialize the question engine.")
            return

        # SAFE IMPORT
        from live.live_sync import live_session_page
        live_session_page(engine, {})

    elif page_name == "admin_ai":
        ai_quiz_builder()

    else:
        st.error("Unknown page.")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
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

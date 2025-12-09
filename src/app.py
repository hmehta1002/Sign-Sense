import streamlit as st
from frontend.ui import apply_theme, render_mode_picker, render_subject_picker, render_question_UI
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from live.live_sync import init_live_session, live_session_page
from revision.revision_ui import render_revision_page


def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def sidebar_navigation():
    options = {
        "Solo Quiz": "solo",
        "Live Session": "live",
        "Revision Lab": "revision",
        "Dashboard": "dashboard",
        "Admin / AI Quiz": "admin_ai"
    }
    choice = st.sidebar.radio("Go to:", list(options.keys()))
    return options[choice]


def ensure_engine():
    """Create quiz engine if missing & selection ready."""
    if "engine" not in st.session_state:
        mode = st.session_state.get("mode")
        subject = st.session_state.get("subject")
        if mode and subject:
            st.session_state.engine = QuizEngine(mode, subject)


def solo_quiz_page():
    engine: QuizEngine = st.session_state.engine
    q = engine.get_current_question()

    if q is None:
        st.success("🎉 Quiz Finished!")
        st.balloons()
        if st.button("View Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return

    render_question_UI(q)

    prev = engine.current_index > 0
    col1, col2 = st.columns(2)
    with col1:
        if prev and st.button("⬅️ Back"):
            engine.current_index -= 1
            st.rerun()
    with col2:
        if st.button("Next ➜"):
            engine.next_question()
            st.rerun()


def main():
    st.set_page_config(page_title="SignSense", layout="wide")
    apply_theme()

    if st.sidebar.button("🔁 Reset App"):
        reset_app()

    # Navigation
    st.session_state.page = sidebar_navigation()

    # Flow control
    if st.session_state.page == "solo":
        if "mode" not in st.session_state:
            render_mode_picker()
            return
        if "subject" not in st.session_state:
            render_subject_picker()
            return

        ensure_engine()
        solo_quiz_page()

    elif st.session_state.page == "dashboard":
        engine = st.session_state.get("engine")
        render_dashboard(engine)

    elif st.session_state.page == "revision":
        engine = st.session_state.get("engine")
        render_revision_page(engine)

    elif st.session_state.page == "live":
        init_live_session()
        engine = st.session_state.get("engine")
        live_session_page(engine, {})

    elif st.session_state.page == "admin_ai":
        ai_quiz_builder()

    else:
        st.error("Unknown page route!")


if __name__ == "__main__":
    main()

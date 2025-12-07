import streamlit as st
from backend.logic import QuizEngine
from frontend.ui import (
    render_header, render_mode_selection, render_subject_selection,
    render_question, render_results
)
from frontend.dashboard import render_dashboard


def main():
    st.set_page_config(page_title="SignSense", layout="wide")

    if "mode" not in st.session_state:
        st.session_state.mode = None
    if "subject" not in st.session_state:
        st.session_state.subject = None
    if "engine" not in st.session_state:
        st.session_state.engine = None

    if st.sidebar.button("🔁 Reset"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

    if not st.session_state.mode:
        st.session_state.mode = render_mode_selection()
        return

    render_header(st.session_state.mode)

    if not st.session_state.subject:
        st.session_state.subject = render_subject_selection()
        return

    if st.session_state.engine is None:
        st.session_state.engine = QuizEngine(st.session_state.mode, st.session_state.subject)

    engine = st.session_state.engine
    q = engine.get_current_question()

    if q is None:
        render_results(engine)
        return

    selected = render_question(q, st.session_state.mode, engine.current_index + 1, len(engine.questions))

    if st.button("Submit"):
        engine.check_answer(selected)
        engine.next_question()
        st.experimental_rerun()

    st.sidebar.write("📍 Navigation")
    nav = st.sidebar.radio("",["Quiz","Dashboard"])

    if nav == "Dashboard":
        render_dashboard(engine)


if __name__ == "__main__":
    main()

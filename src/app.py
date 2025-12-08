import streamlit as st
st.set_page_config(page_title="SignSense", layout="wide")

from backend.logic import QuizEngine
from frontend.ui import (
    render_header,
    render_mode_picker,
    render_subject_picker,
    render_question,
    render_results
)
from frontend.dashboard import render_dashboard


def init_state():
    defaults = {
        "mode": None,
        "subject": None,
        "engine": None,
        "answered": False,
        "feedback": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


def sidebar():
    st.sidebar.title("📍 Navigation")

    if st.sidebar.button("🔁 Reset App"):
        reset_app()

    return st.sidebar.radio("Go to:", ["Quiz", "Dashboard"])


def quiz_flow():
    engine: QuizEngine = st.session_state.engine
    q = engine.get_current_question()

    if q is None:
        render_results(engine)
        if st.button("🔁 Restart Quiz"):
            reset_app()
        return

    answer = render_question(
        q,
        st.session_state.mode,
        engine.current_index + 1,
        len(engine.questions)
    )

    if not st.session_state.answered:
        if st.button("Submit"):
            st.session_state.feedback = engine.check_answer(answer)
            st.session_state.answered = True
    else:
        fb = st.session_state.feedback

        if fb["correct"]:
            st.success(f"✔ Correct! +{fb['points']} points 🎉")
        else:
            st.error(f"❌ Correct answer: {fb['correct_answer']}")

        if fb["time"] is not None:
            st.info(f"⏱ Time: {fb['time']} sec")

        if st.button("Next ➡"):
            engine.next_question()
            st.session_state.answered = False


def main():
    init_state()

    page = sidebar()

    if st.session_state.mode is None:
        render_mode_picker()
        return

    if st.session_state.subject is None:
        render_subject_picker()
        return

    if st.session_state.engine is None:
        st.session_state.engine = QuizEngine(
            st.session_state.mode,
            st.session_state.subject
        )

    render_header(st.session_state.mode)

    if page == "Quiz":
        quiz_flow()
    else:
        render_dashboard(st.session_state.engine)


if __name__ == "__main__":
    main()

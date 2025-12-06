import sys
from pathlib import Path

import streamlit as st

# Ensure Python can find backend and frontend modules
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.append(str(HERE))

from backend.logic import QuizEngine  # type: ignore
from frontend.ui import (
    render_header,
    render_mode_selection,
    render_subject_selection,
    render_question,
    render_results,
)


st.set_page_config(page_title="SignSense", layout="centered")

# ---------- SESSION STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "engine" not in st.session_state:
    st.session_state.engine = None
if "mode" not in st.session_state:
    st.session_state.mode = "Standard"
if "subject" not in st.session_state:
    st.session_state.subject = None

# ---------- HEADER ----------
render_header()

# ---------- PAGE FLOW ----------
page = st.session_state.page

if page == "home":
    st.write(
        "SignSense is an accessibility-focused quiz platform designed for learners with ADHD, "
        "Dyslexia, Autism, and neurotypical profiles. This prototype demonstrates adaptive "
        "questioning, supportive visuals, and basic gamification."
    )
    if st.button("Begin"):
        st.session_state.page = "mode"

elif page == "mode":
    mode = render_mode_selection()
    st.session_state.mode = mode

    if st.button("Continue"):
        st.session_state.page = "subject"

elif page == "subject":
    subject = render_subject_selection()
    st.session_state.subject = subject

    if st.button("Start Quiz"):
        st.session_state.engine = QuizEngine(st.session_state.mode, subject)
        st.session_state.page = "quiz"

elif page == "quiz":
    engine = st.session_state.engine
    if engine is None:
        st.warning("Engine not initialised. Returning to home.")
        st.session_state.page = "home"
    else:
        question = engine.get_current_question()
        if question is None:
            st.session_state.page = "result"
        else:
            selected, hint_requested = render_question(
                question, engine, engine.mode
            )

            if hint_requested:
                st.info("Hint: Think about the basic rule this question is testing (this is a placeholder for richer hints).")

            if st.button("Submit answer"):
                result = engine.check_answer(selected)
                if result["correct"]:
                    st.success("Correct! 🎉")
                else:
                    st.error(f"Incorrect. Correct answer: {result['correct_answer']}")
                engine.next_question()

elif page == "result":
    engine = st.session_state.engine
    if engine is None:
        st.session_state.page = "home"
    else:
        render_results(engine)

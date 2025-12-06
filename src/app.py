import streamlit as st
from backend.logic import QuizEngine
from frontend.ui import render_header, render_mode_selection, render_subject_selection, render_question, render_results

# ---------- INITIAL SESSION STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "engine" not in st.session_state:
    st.session_state.engine = None
if "mode" not in st.session_state:
    st.session_state.mode = "Standard"
if "subject" not in st.session_state:
    st.session_state.subject = None

# ---------- RENDER HEADER ----------
render_header()

# ---------- PAGE LOGIC ----------
if st.session_state.page == "home":
    st.write("Welcome to **SignSense**, an adaptive accessibility-focused quiz experience.")
    if st.button("Start"):
        st.session_state.page = "mode"

elif st.session_state.page == "mode":
    mode = render_mode_selection()
    st.session_state.mode = mode

    if st.button("Continue"):
        st.session_state.page = "subject"

elif st.session_state.page == "subject":
    subject = render_subject_selection()
    st.session_state.subject = subject

    if st.button("Start Quiz"):
        st.session_state.engine = QuizEngine(st.session_state.mode, subject)
        st.session_state.page = "quiz"

elif st.session_state.page == "quiz":
    engine = st.session_state.engine
    question = engine.get_current_question()

    if question is None:
        st.session_state.page = "result"

    else:
        chosen = render_question(question, engine.mode, engine.score, engine.index)

        if st.button("Submit"):
            engine.check_answer(chosen)
            engine.next_question()

elif st.session_state.page == "result":
    engine = st.session_state.engine
    render_results(engine)

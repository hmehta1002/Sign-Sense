import streamlit as st

def render_header():
    st.markdown("<h1 style='text-align:center;color:#9BE8FF;'>SignSense</h1>", unsafe_allow_html=True)

def render_mode_selection():
    modes = {"Standard 🎯": "standard", "ADHD ⚡": "adhd", "Dyslexia 🔤": "dyslexia", "Deaf/ISL ✋": "isl"}
    choice = st.radio("Choose learning mode:", list(modes.keys()), key="mode")
    if st.button("Continue ➜", key="mode_next"):
        st.session_state.mode = modes[choice]
        st.rerun()
    return st.session_state.get("mode")

def render_subject_selection():
    subjects = {"Mathematics 🧮": "math", "English ✍️": "english"}
    choice = st.radio("Choose subject:", list(subjects.keys()), key="subject")
    if st.button("Start Quiz 🚀", key="sub_next"):
        st.session_state.subject = subjects[choice]
        st.rerun()
    return st.session_state.get("subject")

def render_question(question, engine, mode):
    st.write(f"### {question['question']}")
    selected = st.radio("Your answer:", question["options"], key=f"{question['id']}_answer")

    if st.checkbox("💡 Show hint?", key=f"{question['id']}_hint"):
        st.info(question["hints"][0])

    return selected, None

def render_results(engine):
    st.success("Quiz complete! 🎉")
    st.write(f"## Final Score: {engine.score}")

    if st.button("Restart 🔁", key="restart"):
        engine.reset()
        st.session_state.subject = None
        st.session_state.mode = None
        st.rerun()

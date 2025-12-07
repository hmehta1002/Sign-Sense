import streamlit as st

def render_header():
    st.markdown("<h1 style='text-align:center;color:#9BE8FF;'>SignSense</h1>", unsafe_allow_html=True)


def render_mode_selection():
    modes = {
        "Standard 🎯": "standard",
        "Dyslexia Mode 🔤": "dyslexia",
        "ADHD Mode ⚡": "adhd",
        "Deaf/ISL ✋": "isl"
    }

    choice = st.radio("Choose Learning Mode:", list(modes.keys()))

    if st.button("Continue ➜"):
        st.session_state.mode = modes[choice]
        st.rerun()


def render_subject_selection():
    subjects = {"Mathematics 🧮": "math", "English ✍️": "english"}
    choice = st.radio("Select Subject:", list(subjects.keys()))

    if st.button("Start Quiz 🚀"):
        st.session_state.subject = subjects[choice]
        st.rerun()


def render_question(q, engine):
    st.write(f"### {q['question']}")
    answer = st.radio("Choose your answer:", q["options"], key=f"q{engine.index}")

    if "hints" in q and st.checkbox("💡 Show Hint"):
        st.info(q["hints"][0])

    return answer, None


def render_results(engine):
    st.success("🎉 Quiz Complete!")
    st.write(f"### Final Score: **{engine.score}**")

    if st.button("Restart Quiz 🔁"):
        engine.reset()
        st.session_state.subject = None
        st.session_state.engine = None
        st.session_state.mode = None
        st.rerun()

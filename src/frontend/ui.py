import streamlit as st

def render_header():
    st.markdown(
        """
        <h1 style="text-align:center; color:#9BE8FF; 
        text-shadow:0px 0px 25px cyan; font-size:50px;">
        S I G N S E N S E</h1>
        <p style="text-align:center; color:#ffffffAA; font-size:18px;">
        Accessible • Adaptive • AI Powered</p>
        """,
        unsafe_allow_html=True
    )

def render_mode_selection():
    st.subheader("Choose Learning Mode")
    options = {
        "Standard 🎯": "standard",
        "ADHD-Friendly ⚡": "adhd",
        "Dyslexia-Friendly 🔤": "dyslexia",
        "Autism-Friendly 🧩": "autism",
        "Deaf / ISL ✋": "isl"
    }

    selected = st.radio("", list(options.keys()), key="mode_radio")

    if st.button("➡ Continue", key="mode_continue"):
        st.session_state.mode = options[selected]
        st.rerun()

    return st.session_state.get("mode", None)

def render_subject_selection():
    st.subheader("Choose Subject")
    subjects = {"Mathematics 🧮": "math", "English ✍️": "english"}

    selected = st.radio("Subject:", list(subjects.keys()), key="subject_radio")

    if st.button("➡ Start Quiz", key="subject_continue"):
        st.session_state.subject = subjects[selected]
        st.rerun()

    return st.session_state.get("subject", None)

def render_question(question, engine, mode):
    st.markdown(f"### {question['question']}")
    
    selected = st.radio("Answer:", question["options"], key=f"answer_{engine.index}")

    if "hint" in question and st.checkbox("💡 Show hint", key=f"hint_{engine.index}"):
        st.info(question["hint"])
    return selected, None

def render_results(engine):
    st.success("🎉 Quiz Finished!")
    st.write(f"### Final Score: **{engine.score}**")
    if st.button("Restart", key="restart_btn"):
        engine.reset()
        del st.session_state.subject
        del st.session_state.engine
        st.rerun()

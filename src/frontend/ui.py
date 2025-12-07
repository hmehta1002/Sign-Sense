import streamlit as st


# ---------------------- HEADER ----------------------

def render_header():
    st.markdown(
        """
        <h1 style='text-align:center; color:#9BE8FF; font-size:48px; letter-spacing:4px;
        text-shadow:0 0 20px #3FF4FF;'>S I G N S E N S E</h1>

        <p style='text-align:center; color:#ffffffbb; font-size:18px;'>Accessible. Adaptive. AI-Powered.</p>
        """,
        unsafe_allow_html=True
    )


# ---------------------- MODE SELECTION ----------------------

def render_mode_selection():
    st.subheader("Choose Learning Mode")

    modes = {
        "Standard 🎯": "standard",
        "ADHD-Friendly ⚡": "adhd",
        "Dyslexia-Friendly 🔤": "dyslexia",
        "Autism-Friendly 🧩": "autism",
        "Deaf/ISL Mode ✋": "isl"
    }

    selected_label = st.radio(
        "",
        list(modes.keys()),
        key="mode_selection"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("➡ Continue", use_container_width=True):
            st.session_state.mode = modes[selected_label]
            st.rerun()

    return st.session_state.get("mode", None)



# ---------------------- SUBJECT SELECTION ----------------------

def render_subject_selection():
    st.subheader("Choose Subject")

    subjects = {
        "Mathematics 🧮": "math",
        "English ✍️": "english"
    }

    selected_label = st.radio(
        "Subject:",
        list(subjects.keys()),
        key="subject_choice"
    )

    selected_value = subjects[selected_label]

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("➡ Start Quiz", use_container_width=True):
            st.session_state.subject = selected_value
            st.rerun()

    return st.session_state.get("subject", None)



# ---------------------- QUESTION RENDER ----------------------

def render_question(question, engine, mode):
    st.write(f"### {question['question']}")

    selected = st.radio("Answer:", question["options"], key=f"q_{engine.index}")

    hint = None
    if "hint" in question:
        if st.checkbox("💡 Show hint"):
            hint = question["hint"]
            st.info(hint)

    return selected, hint



# ---------------------- RESULTS ----------------------

def render_results(engine):
    st.success("🎉 Quiz Completed!")

    st.markdown(
        f"""
        <h2 style='color:#9BE8FF; text-shadow:0 0 15px #3FF4FF;'>Final Score: {engine.score}</h2>
        """,
        unsafe_allow_html=True
    )

    st.write("#### Breakdown:")
    for entry in engine.history:
        color = "green" if entry["correct"] else "red"
        st.markdown(
            f"<p style='color:{color}; font-size:18px;'>• {entry['question_id']} → "
            f"{'Correct' if entry['correct'] else 'Wrong'} ({entry['points']} points)</p>",
            unsafe_allow_html=True,
        )

    if st.button("🔁 Restart"):
        engine.reset()
        st.session_state.mode = None
        st.session_state.subject = None
        st.rerun()

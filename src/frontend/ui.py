import streamlit as st

# ----------------------- ACCESSIBILITY STYLING -----------------------

def apply_accessibility_mode():
    mode = st.session_state.get("mode")

    # Dyslexia Mode Font
    if mode == "dyslexia":
        st.markdown("""
        <style>
        body, * { 
            font-family: 'OpenDyslexic', Arial, sans-serif !important;
            letter-spacing: 1.2px;
            line-height: 1.5em;
        }
        </style>
        """, unsafe_allow_html=True)

    # ADHD Mode (high contrast and highlight focus areas)
    elif mode == "adhd":
        st.markdown("""
        <style>
        body {
            background-color: #101726;
        }
        .stRadio > div {
            background: rgba(255,255,255,0.08);
            padding: 12px;
            border-radius: 8px;
        }
        label {
            color: #ffdd57 !important;
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Deaf/Sign Language Mode (clean & visual-first UI)
    elif mode == "isl":
        st.markdown("""
        <style>
        * {
            font-size: 1.15em;
        }
        </style>
        """, unsafe_allow_html=True)


# ----------------------- HEADER -----------------------

def render_header():
    apply_accessibility_mode()
    st.markdown(
        "<h1 style='text-align:center; color:#9BE8FF; text-shadow:0 0 10px #00C3FF;'>SignSense</h1>",
        unsafe_allow_html=True
    )

# ----------------------- MODE SELECTION -----------------------

def render_mode_selection():
    st.write("### Choose Learning Mode")

    modes = {
        "Standard 🎯": "standard",
        "Dyslexia-Friendly 🔤": "dyslexia",
        "ADHD Assist ⚡": "adhd",
        "Deaf / Indian Sign Language ✋": "isl"
    }

    choice = st.radio("Learning Mode:", list(modes.keys()))

    if st.button("Continue ➜"):
        st.session_state.mode = modes[choice]
        st.rerun()

# ----------------------- SUBJECT SELECTION -----------------------

def render_subject_selection():
    st.write("### Choose Subject")

    subjects = {
        "Mathematics 🧮": "math",
        "English ✍️": "english"
    }

    choice = st.radio("Subject:", list(subjects.keys()))

    if st.button("Start Quiz 🚀"):
        st.session_state.subject = subjects[choice]
        st.rerun()


# ----------------------- QUESTION RENDER -----------------------

def render_question(q, engine):
    apply_accessibility_mode()

    st.markdown(f"### 📝 {q['question']}")

    # ISL mode support: GIF or video
    if st.session_state.mode == "isl":
        if "isl_video" in q and q["isl_video"]:
            st.video(q["isl_video"])
        elif "isl_gif" in q and q["isl_gif"]:
            st.image(q["isl_gif"], caption="Sign Language Support")

    key = f"answer_{q['id']}"
    answer = st.radio("Choose your answer:", q["options"], key=key)

    # Hints toggle
    if "hints" in q and st.checkbox("💡 Show Hint"):
        st.info(q["hints"][0])

    return answer, None


# ----------------------- RESULTS VIEW -----------------------

def render_results(engine):
    apply_accessibility_mode()
    st.success("🎉 Quiz Completed!")
    st.markdown(f"### Final Score: **{engine.score} points**")

    if st.button("🔁 Restart Quiz"):
        engine.reset()
        st.session_state.engine = None
        st.session_state.subject = None
        st.session_state.mode = None
        st.session_state.answered = False
        st.rerun()

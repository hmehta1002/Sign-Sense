import streamlit as st

# Try to import TTS; app still works if unavailable
try:
    from gtts import gTTS  # type: ignore
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False


# ----------------------- ACCESSIBILITY / THEME -----------------------

def apply_accessibility_mode():
    mode = st.session_state.get("mode", "standard")
    adhd_profile = st.session_state.get("adhd_profile", "balanced")

    # Base background
    st.markdown("""
    <style>
    body {
        background: radial-gradient(circle at top, #101426 0, #02010f 55%, #000000 100%);
    }
    h1, h2, h3, label {
        color: #9BE8FF !important;
    }
    .stButton>button {
        border-radius: 999px;
        border: none;
        padding: 0.4rem 1.3rem;
        color: white;
        font-weight: 600;
        box-shadow: 0 0 15px rgba(123,47,247,0.45);
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    # Standard → cyber-neon
    if mode == "standard":
        st.markdown("""
        <style>
        .stButton>button {
            background: linear-gradient(90deg,#7b2ff7,#00c3ff);
        }
        </style>
        """, unsafe_allow_html=True)

    # Dyslexia → calmer, spaced text
    elif mode == "dyslexia":
        st.markdown("""
        <style>
        * {
            font-family: Arial, sans-serif !important;
            letter-spacing: 1.3px;
            line-height: 1.6em;
        }
        .stButton>button {
            background: #3a7bd5;
        }
        </style>
        """, unsafe_allow_html=True)

    # ADHD → adaptive style based on pacing profile
    elif mode == "adhd":
        if adhd_profile == "fast":
            # More neon, more energy
            st.markdown("""
            <style>
            body {
                background: radial-gradient(circle at top, #1b1036 0, #050015 55%, #000000 100%);
            }
            .stRadio > div {
                border: 1px solid #ffdd57;
                box-shadow: 0 0 12px rgba(255,221,87,0.4);
            }
            .stButton>button {
                background: linear-gradient(90deg,#ff9800,#ff2d55);
            }
            </style>
            """, unsafe_allow_html=True)
        elif adhd_profile == "calm":
            # Softer, less stimulation
            st.markdown("""
            <style>
            body {
                background: #0b1020;
            }
            .stRadio > div {
                background: rgba(255,255,255,0.04);
                border-radius: 8px;
            }
            .stButton>button {
                background: #4a6fa5;
            }
            </style>
            """, unsafe_allow_html=True)
        else:
            # Balanced
            st.markdown("""
            <style>
            .stRadio > div {
                background: rgba(255,255,255,0.06);
                border-radius: 8px;
            }
            .stButton>button {
                background: linear-gradient(90deg,#7b2ff7,#00c3ff);
            }
            </style>
            """, unsafe_allow_html=True)

    # ISL → clean, readable, video-first
    elif mode == "isl":
        st.markdown("""
        <style>
        body {
            background: #020818;
        }
        * {
            font-size: 1.08em;
        }
        .stButton>button {
            background: #005f99;
        }
        </style>
        """, unsafe_allow_html=True)


# ----------------------- HEADER -----------------------

def render_header():
    apply_accessibility_mode()
    st.markdown(
        """
        <h1 style='text-align:center; 
                   color:#9BE8FF; 
                   text-shadow:0 0 16px #00C3FF;
                   letter-spacing:0.2em;'>
            SIGNSENSE
        </h1>
        <p style='text-align:center; color:#ffffffaa;'>
            Accessibility-first quiz portal for neurodivergent & deaf learners
        </p>
        """,
        unsafe_allow_html=True
    )


# ----------------------- MODE SELECTION -----------------------

def render_mode_selection():
    st.write("### 🧠 Choose Learning Mode")

    modes = {
        "Standard 🎯": "standard",
        "Dyslexia-Friendly 🔤": "dyslexia",
        "ADHD Hybrid ⚡": "adhd",
        "Deaf / Indian Sign Language ✋": "isl",
    }

    choice = st.radio("Learning Mode:", list(modes.keys()))

    if st.button("Continue ➜", key="mode_continue"):
        st.session_state.mode = modes[choice]
        st.rerun()


# ----------------------- SUBJECT SELECTION -----------------------

def render_subject_selection():
    st.write("### 📚 Choose Subject")

    subjects = {
        "Mathematics 🧮": "math",
        "English ✍️": "english",
    }

    choice = st.radio("Subject:", list(subjects.keys()))

    if st.button("Start Quiz 🚀", key="subject_start"):
        st.session_state.subject = subjects[choice]
        st.rerun()


# ----------------------- TTS SUPPORT -----------------------

def _play_tts_for_question(text: str, q_id: str):
    if not TTS_AVAILABLE:
        st.warning("Text-to-speech is not available in this deployment.")
        return

    try:
        tts = gTTS(text)
        path = f"/tmp/tts_{q_id}.mp3"
        tts.save(path)
        st.audio(path)
    except Exception:
        st.warning("Could not generate audio right now.")


# ----------------------- QUESTION RENDER -----------------------

def render_question(q: dict, engine):
    apply_accessibility_mode()

    st.markdown(f"### 📝 {q['question']}")

    mode = st.session_state.get("mode", "standard")

    # ISL: show avatar / sign video if available
    if mode == "isl":
        col_v, col_q = st.columns([1.2, 2])
        with col_v:
            if q.get("isl_video"):
                st.video(q["isl_video"])
            elif q.get("isl_gif"):
                st.image(q["isl_gif"], caption="ISL support")
        with col_q:
            st.write("")

    # The answer widget (key = question id)
    key = f"answer_{q.get('id', engine.index)}"
    answer = st.radio("Choose your answer:", q["options"], key=key)

    # TTS: only for non-ISL modes
    if mode in ("standard", "dyslexia", "adhd"):
        tts_label = q.get("tts_text", q["question"])
        if st.button("🔊 Read question aloud", key=f"tts_{q.get('id', engine.index)}"):
            _play_tts_for_question(tts_label, str(q.get("id", engine.index)))

    # Hints
    hints = q.get("hints")
    if hints and st.checkbox("💡 Show Hint", key=f"hint_{q.get('id', engine.index)}"):
        st.info(hints[0])

    return answer, None


# ----------------------- RESULTS VIEW -----------------------

def render_results(engine):
    apply_accessibility_mode()
    st.success("🎉 Quiz Completed!")

    st.markdown(f"### Final Score: **{engine.score} points**")
    st.markdown(f"Best streak: **{engine.best_streak} correct in a row**")

    if st.button("🔁 Restart Quiz", key="restart_quiz"):
        engine.reset()
        st.session_state.engine = None
        st.session_state.subject = None
        st.session_state.mode = None
        st.session_state.answered = False
        st.session_state.adhd_profile = "balanced"
        st.rerun()

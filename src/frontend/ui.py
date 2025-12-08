import streamlit as st

# Optional TTS – app still runs if this fails
try:
    from gtts import gTTS  # type: ignore
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False


# ---------- THEME ----------

def apply_theme():
    mode = st.session_state.get("mode", "standard")

    # Base neon
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
        padding: 0.45rem 1.4rem;
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s ease-out;
    }
    .stButton>button:hover {
        transform: translateY(-1px) scale(1.02);
        box-shadow: 0 0 15px rgba(123,47,247,0.55);
    }
    .question-card {
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        border-radius: 12px;
        background: rgba(8, 13, 32, 0.9);
        border: 1px solid rgba(155, 232, 255, 0.25);
    }
    </style>
    """, unsafe_allow_html=True)

    # Mode-specific tweaks
    if mode == "standard":
        st.markdown("""
        <style>
        .stButton>button {
            background: linear-gradient(90deg,#7b2ff7,#00c3ff);
        }
        </style>
        """, unsafe_allow_html=True)

    elif mode == "dyslexia":
        st.markdown("""
        <style>
        * {
            font-family: Arial, sans-serif !important;
            letter-spacing: 1.35px;
            line-height: 1.6em;
        }
        .stButton>button {
            background: #3a7bd5;
        }
        </style>
        """, unsafe_allow_html=True)

    elif mode == "adhd":
        st.markdown("""
        <style>
        .stRadio > div {
            background: rgba(255,255,255,0.06);
            border-radius: 10px;
            padding: 8px;
            border: 1px solid rgba(255,221,87,0.5);
        }
        .stButton>button {
            background: linear-gradient(90deg,#ff9800,#ff2d55);
        }
        </style>
        """, unsafe_allow_html=True)

    elif mode == "isl":
        st.markdown("""
        <style>
        body {
            background: #020818;
        }
        * {
            font-size: 1.05em;
        }
        .stButton>button {
            background: #005f99;
        }
        </style>
        """, unsafe_allow_html=True)


# ---------- HEADER ----------

def render_header(mode: str):
    apply_theme()

    labels = {
        "standard": "Standard",
        "dyslexia": "Dyslexia-Friendly",
        "adhd": "ADHD Hybrid",
        "isl": "Deaf / ISL",
    }
    pretty = labels.get(mode, mode)

    st.markdown(
        f"""
        <h1 style='text-align:center;
                   color:#9BE8FF;
                   letter-spacing:0.18em;'>
            SIGNSENSE
        </h1>
        <p style='text-align:center;color:#ffffffaa;'>
            Mode: <b>{pretty}</b>
        </p>
        """,
        unsafe_allow_html=True
    )


# ---------- MODE & SUBJECT PICKERS ----------

def render_mode_picker():
    apply_theme()
    st.write("### 🧠 Choose Learning Mode")

    choice = st.radio(
        "",
        ["Standard 🎯", "Dyslexia-Friendly 🔤", "ADHD Hybrid ⚡", "Deaf / ISL ✋"]
    )

    if st.button("Continue ➜", key="mode_continue"):
        mapping = {
            "Standard 🎯": "standard",
            "Dyslexia-Friendly 🔤": "dyslexia",
            "ADHD Hybrid ⚡": "adhd",
            "Deaf / ISL ✋": "isl",
        }
        st.session_state.mode = mapping[choice]
        st.experimental_rerun()


def render_subject_picker():
    apply_theme()
    st.write("### 📚 Choose Subject")

    choice = st.radio(
        "",
        ["Mathematics 🧮", "English ✍️"]
    )

    if st.button("Start Quiz 🚀", key="subject_start"):
        mapping = {
            "Mathematics 🧮": "math",
            "English ✍️": "english",
        }
        st.session_state.subject = mapping[choice]
        st.experimental_rerun()


# ---------- TTS HELPER ----------

def _play_tts(text: str, q_id: str):
    if not TTS_AVAILABLE:
        st.warning("Text-to-speech is not available here.")
        return
    try:
        tts = gTTS(text)
        path = f"/tmp/tts_{q_id}.mp3"
        tts.save(path)
        st.audio(path)
    except Exception:
        st.warning("Could not generate audio right now.")


# ---------- QUESTION RENDER ----------

def render_question(q: dict, mode: str, index: int, total: int):
    apply_theme()

    st.markdown(
        f"<div class='question-card'>"
        f"<h3>📝 Question {index}/{total}</h3>"
        f"<p>{q['question']}</p>"
        f"</div>",
        unsafe_allow_html=True
    )

    # ISL layout: show sign video/gif
    if mode == "isl":
        col_v, col_t = st.columns([1.2, 2])
        with col_v:
            if q.get("isl_video"):
                st.video(q["isl_video"])
            elif q.get("isl_gif"):
                st.image(q["isl_gif"], caption="ISL support")
        with col_t:
            st.write("")

    # ADHD label
    if mode == "adhd":
        st.markdown(
            "<span style='display:inline-block; padding:4px 10px; "
            "border-radius:999px; background:#ff980022; color:#ff9800; "
            "border:1px solid #ff980099; font-size:0.85em;'>"
            "ADHD Hybrid Mode Active ⚡"
            "</span>",
            unsafe_allow_html=True
        )

    # Answer choices
    key = f"answer_{q.get('id', index)}"
    answer = st.radio("Choose your answer:", q["options"], key=key)

    # TTS for non-ISL
    if mode in ("standard", "dyslexia", "adhd"):
        label = q.get("tts_text", q["question"])
        if st.button("🔊 Read aloud", key=f"tts_{q.get('id', index)}"):
            _play_tts(label, str(q.get('id', index)))

    # Hints
    if q.get("hints") and st.checkbox("💡 Show Hint", key=f"hint_{q.get('id', index)}"):
        st.info(q["hints"][0])

    return answer


# ---------- RESULTS ----------

def render_results(engine):
    apply_theme()
    st.success("🎉 Quiz Completed!")

    st.write(f"### Final Score: **{engine.score}**")
    st.write(f"Best Streak: **{engine.best_streak}**")
    st.write(f"Total Questions: **{len(engine.questions)}**")

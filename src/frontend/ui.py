import streamlit as st

# Optional TTS – safe if not installed
try:
    from gtts import gTTS  # type: ignore
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False


# ---------- AVATARS (realistic AI-style placeholders) ----------

AVATAR_URLS = {
    "standard": "https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg",
    "dyslexia": "https://images.pexels.com/photos/1181519/pexels-photo-1181519.jpeg",
    "adhd": "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg",
    "isl": "https://images.pexels.com/photos/1557213/pexels-photo-1557213.jpeg",
}


# ---------- THEME + MODE VISUALS ----------

def apply_theme():
    """Base neon cyberpunk theme + per-mode CSS."""
    mode = st.session_state.get("mode", "standard")

    st.markdown(
        """
        <style>
        body {
            background: radial-gradient(circle at top, #13162b 0, #050316 55%, #000000 100%);
        }
        h1, h2, h3, label {
            color: #9BE8FF !important;
        }
        .question-box {
            padding: 16px;
            background: rgba(10, 15, 40, 0.9);
            border-radius: 14px;
            border: 1px solid #4dd2ff;
            margin-bottom: 16px;
            font-size: 18px;
            color: #ffffff;
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
            transform: translateY(-1px) scale(1.03);
            box-shadow: 0 0 18px rgba(123,47,247,0.75);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if mode == "standard":
        st.markdown(
            """
            <style>
            .stButton>button {
                background: linear-gradient(90deg,#7b2ff7,#00c3ff);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    elif mode == "dyslexia":
        st.markdown(
            """
            <style>
            * {
                font-family: Arial, Verdana, sans-serif !important;
                letter-spacing: 1.4px;
                line-height: 1.6em;
            }
            .stButton>button {
                background: #3a7bd5;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    elif mode == "adhd":
        st.markdown(
            """
            <style>
            .stRadio > div {
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
                padding: 6px;
                border: 1px solid rgba(255,221,87,0.65);
            }
            .stButton>button {
                background: linear-gradient(90deg,#ff9800,#ff2d55);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    elif mode == "isl":
        st.markdown(
            """
            <style>
            body {
                background: #020818;
            }
            * {
                font-size: 1.04em;
            }
            .stButton>button {
                background: #005f99;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


# ---------- HEADER + AVATAR ----------

def render_header(mode: str):
    apply_theme()

    labels = {
        "standard": "Standard Mode",
        "dyslexia": "Dyslexia-Friendly Mode",
        "adhd": "ADHD Hybrid Mode",
        "isl": "Deaf / ISL Mode",
    }
    pretty = labels.get(mode, mode)

    col1, col2 = st.columns([1, 3])

    with col1:
        avatar = AVATAR_URLS.get(mode)
        if avatar:
            st.image(avatar, caption=pretty, use_column_width=True)

    with col2:
        st.markdown(
            """
            <h1 style='color:#9BE8FF; letter-spacing:0.14em; margin-bottom:0.2em;'>
                SIGNSENSE
            </h1>
            <p style='color:#ffffffaa;'>
                Neuro-inclusive AI quiz for ADHD, Dyslexia & Deaf learners.
            </p>
            """,
            unsafe_allow_html=True,
        )


# ---------- HUD (Score, Level, XP) ----------

def render_hud(engine, xp_info: dict):
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", engine.score)
    col2.metric("Best Streak", engine.best_streak)
    col3.metric("Level", xp_info["level"])

    xp = xp_info["xp"]
    level = xp_info["level"]
    next_level_xp = level * 200
    base_level_xp = (level - 1) * 200
    span = max(1, next_level_xp - base_level_xp)
    progress = min(1.0, max(0.0, (xp - base_level_xp) / span))

    st.progress(progress, text=f"XP {xp} / {next_level_xp}")

    if xp_info["badges"]:
        st.caption("Unlocked badges: " + " · ".join(xp_info["badges"]))


# ---------- MODE & SUBJECT PICKERS ----------

def render_mode_picker():
    apply_theme()
    st.write("### 🧠 Choose Learning Mode")

    choice = st.radio(
        "",
        ["Standard 🎯", "Dyslexia-Friendly 🔤", "ADHD Hybrid ⚡", "Deaf / ISL ✋"],
    )

    if st.button("Continue ➜", key="mode_continue"):
        mapping = {
            "Standard 🎯": "standard",
            "Dyslexia-Friendly 🔤": "dyslexia",
            "ADHD Hybrid ⚡": "adhd",
            "Deaf / ISL ✋": "isl",
        }
        st.session_state.mode = mapping[choice]


def render_subject_picker():
    apply_theme()
    st.write("### 📚 Choose Subject")

    choice = st.radio(
        "",
        ["Mathematics 🧮", "English ✍️"],
    )

    if st.button("Start Quiz 🚀", key="subject_start"):
        mapping = {
            "Mathematics 🧮": "math",
            "English ✍️": "english",
        }
        st.session_state.subject = mapping[choice]


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
        st.warning("Unable to generate audio right now.")


# ---------- QUESTION RENDER ----------

def render_question(q: dict, mode: str, index: int, total: int):
    apply_theme()

    st.markdown(
        f"""
        <div class="question-box">
            <b>Question {index}/{total}</b><br><br>
            {q['question']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ISL media
    if mode == "isl":
        col_v, col_t = st.columns([1.3, 2])
        with col_v:
            if q.get("isl_video"):
                st.video(q["isl_video"])
            elif q.get("isl_gif"):
                st.image(q["isl_gif"], caption="ISL Support")
        with col_t:
            st.write("Watch the sign and pick the correct option.")

    # ADHD badge
    if mode == "adhd":
        st.markdown(
            """
            <span style='display:inline-block;
                         padding:4px 12px;
                         border-radius:999px;
                         background:#ff980022;
                         color:#ff9800;
                         border:1px solid #ff9800aa;
                         font-size:0.85em;'>
                ADHD Focus Mode ⚡
            </span>
            """,
            unsafe_allow_html=True,
        )

    # Answer options
    key = f"answer_{q.get('id', index)}"
    answer = st.radio("Choose your answer:", q["options"], key=key)

    # TTS for non-ISL modes
    if mode in ("standard", "dyslexia", "adhd"):
        label = q.get("tts_text", q["question"])
        if st.button("🔊 Read question aloud", key=f"tts_{q.get('id', index)}"):
            _play_tts(label, str(q.get("id", index)))

    # Hint
    if q.get("hints") and st.checkbox("💡 Show Hint", key=f"hint_{q.get('id', index)}"):
        st.info(q["hints"][0])

    return answer


# ---------- RESULTS ----------

def render_results(engine, xp_info: dict):
    apply_theme()
    st.success("🎉 Quiz Completed!")

    st.write(f"### Final Score: **{engine.score}**")
    st.write(f"Best Streak: **{engine.best_streak}**")
    st.write(f"Total Questions: **{len(engine.questions)}**")
    st.write(f"XP Earned: **{xp_info['xp']}** (Level {xp_info['level']})")

    if xp_info["badges"]:
        st.write("🏅 **Badges Unlocked:**")
        for b in xp_info["badges"]:
            st.markdown(f"- {b}")

    st.balloons()

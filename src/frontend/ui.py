import streamlit as st
import html
import urllib.parse

# ------------------------
# FRONTEND / UI (neon + accessibility)
# ------------------------

# ---------- small helpers ----------
def safe_text(s: str) -> str:
    """Escape text for injection into HTML snippets."""
    return html.escape(s or "")


def tts_audio_snippet(text: str, voice: str = "Brian"):
    """Return an HTML <audio> snippet that plays TTS from StreamElements (simple, no libs)."""
    # encode text for URL
    q = urllib.parse.quote(str(text))
    # using streamelements' simple speech endpoint (public demo). Works in many browsers.
    url = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={q}"
    return f'<audio autoplay><source src="{url}" type="audio/mpeg"></audio>'


# ------------------------------
# DYSLEXIA TEXT TRANSFORMS
# ------------------------------
def dyslexia_transform(text: str, view: str) -> str:
    """
    Simple dyslexia-friendly transforms.
    view: "normal" | "upper" | "lower" | "spaced"
    """
    if not text:
        return text
    if view == "normal":
        return text
    if view == "lower":
        return text.lower()
    if view == "upper":
        return text.upper()
    if view == "spaced":
        # add extra spacing between words to aid parsing
        return "  ".join(text.split())
    return text


# ------------------------------
# ADHD VISUAL HIGHLIGHT
# ------------------------------
def adhd_highlight_block(text: str):
    st.markdown(
        f"""
        <div style="
            padding: 14px;
            margin-top: 8px;
            border-radius: 10px;
            background: linear-gradient(90deg, rgba(0,180,255,0.08), rgba(123,97,255,0.04));
            border: 1px solid rgba(0,200,255,0.12);
            font-size: 18px;
            font-weight: 600;
            color: #E6F7FF;
        ">
            {safe_text(text)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------
# DYSLEXIA TEXT BLOCK
# ------------------------------
def dyslexia_text_block(text: str):
    st.markdown(
        f"""
        <div style="
            font-size:20px;
            line-height:1.6;
            padding:12px;
            border-radius:10px;
            background: rgba(255,255,255,0.03);
            border-left: 6px solid #00E5FF;
            font-family: 'Verdana', 'Arial', sans-serif;
            color: #F8FAFC;
        ">
            {safe_text(text)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------
# ISL AVATAR (GIF / Video)
# ------------------------------
def isl_avatar(url_gif: str = None, url_video: str = None, width: int = 300):
    """Render ISL avatar area; accepts gif or mp4 link."""
    if url_gif:
        try:
            st.image(url_gif, width=width, caption="ISL Assistant")
        except Exception:
            # fallback: show url as link if image fails
            st.write(f"ISL GIF: {url_gif}")
    if url_video:
        try:
            st.video(url_video)
        except Exception:
            st.write(f"ISL Video: {url_video}")


# ------------------------------
# NEON THEME (Streamlit-safe CSS)
# ------------------------------
def apply_theme():
    """Apply neon / accessible theme with mode-aware tweaks."""
    st.markdown(
        """
        <style>
        /* Page background */
        .css-18e3th9 {  /* streamlit main */
            background: radial-gradient(circle at 10% 20%, #071029 0%, #02040a 60%, #000000 100%);
            color: #E6EEF3;
        }

        /* Neon headers */
        .neon-title {
            font-size: 28px;
            font-weight: 700;
            color: #A5F3FC;
            text-shadow: 0 0 18px rgba(165,243,252,0.12);
            margin-bottom: 10px;
        }

        /* Question card */
        .neon-box {
            padding: 14px 18px;
            border-radius: 12px;
            background: rgba(10,14,24,0.8);
            border: 1px solid rgba(99,102,241,0.14);
            box-shadow: 0 6px 22px rgba(99,102,241,0.04);
            color: #F8FAFC;
            font-size: 18px;
        }

        /* Neon buttons */
        .stButton>button {
            border-radius: 999px;
            padding: 8px 18px;
            font-weight: 700;
            background: linear-gradient(90deg,#7C3AED,#06B6D4);
            color: #041425;
            border: none;
            box-shadow: 0 4px 14px rgba(124,58,237,0.18);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(6,182,212,0.18);
            color: white;
        }

        /* Radio/label color */
        div[role="radiogroup"] > label, div[role="radiogroup"] {
            color: #E6EEF3 !important;
        }

        /* File uploader look */
        div[data-testid="stFileUploader"] {
            border-radius: 12px;
            border: 2px dashed rgba(99,102,241,0.12);
            padding: 12px;
            background: rgba(255,255,255,0.01);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Per-mode CSS tweaks if user selected mode already
    m = st.session_state.get("mode", "standard")
    if m == "dyslexia":
        st.markdown(
            """
            <style>
            body, div, label {
                font-family: 'Verdana', 'Arial', sans-serif !important;
                letter-spacing: 0.04em !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    elif m == "adhd":
        st.markdown(
            """
            <style>
            div[role="radiogroup"] { background: rgba(6,182,212,0.03); border-radius:8px; padding:8px; }
            </style>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------
# RENDER MODE PICKER (exposed to app.py)
# ------------------------------
def render_mode_picker():
    """
    Renders the mode picker. Sets `st.session_state.mode` to one of:
    'standard', 'dyslexia', 'adhd', 'isl', 'hybrid'
    """
    st.markdown('<div class="neon-title">🧭 Choose Accessibility Mode</div>', unsafe_allow_html=True)

    # Show short descriptions with radio choices
    choices = [
        "Standard",
        "Dyslexia Mode (readability)",
        "ADHD Assist (focus)",
        "ISL (Indian Sign Language)",
        "Hybrid Accessibility (Best of all)"
    ]

    choice = st.radio("Mode", choices, index=0, horizontal=True)

    label_to_key = {
        "Standard": "standard",
        "Dyslexia Mode (readability)": "dyslexia",
        "ADHD Assist (focus)": "adhd",
        "ISL (Indian Sign Language)": "isl",
        "Hybrid Accessibility (Best of all)": "hybrid",
    }

    if st.button("Continue ➜"):
        st.session_state.mode = label_to_key.get(choice, "standard")
        # small default init values helpful for adhd focus
        if st.session_state.mode == "adhd":
            st.session_state.adhd_opt = 0
        st.experimental_rerun()


# ------------------------------
# RENDER SUBJECT PICKER (exposed to app.py)
# ------------------------------
def render_subject_picker():
    """
    Renders the subject picker. Sets `st.session_state.subject` to 'math' or 'english'.
    """
    st.markdown('<div class="neon-title">📚 Choose Subject</div>', unsafe_allow_html=True)

    subject = st.selectbox("Select subject", ["Math", "English"], index=0)
    if st.button("Start Quiz 🚀"):
        st.session_state.subject = subject.lower()
        st.experimental_rerun()


# ------------------------------
# MAIN QUESTION RENDERER (exposed to app.py)
# ------------------------------
def render_question_UI(question: dict):
    """
    Renders a question object. Expected fields:
    - id (str), question (str), options (list[str]), answer (str),
      difficulty (str, optional), isl_gif (url), isl_video (url), hints (list), tts_text (str)
    Sets st.session_state.selected_answer when user picks.
    Returns the selected option (also stored in session).
    """
    # ensure selected_answer key exists for this question id
    qkey = f"selected_{question.get('id', 'q')}"
    mode = st.session_state.get("mode", "standard")

    # Header
    st.markdown('<div class="neon-title">🎯 Question</div>', unsafe_allow_html=True)

    # ISL assistant (if available)
    if mode in ("isl", "hybrid"):
        st.markdown("### 🤟 ISL Assistant")
        isl_avatar(question.get("isl_gif"), question.get("isl_video"))

    # Question text (dyslexia transform if needed)
    if mode in ("dyslexia", "hybrid"):
        # show transform control
        t_choice = st.selectbox("Reading view", ["normal", "lower", "upper", "spaced"], key=f"view_{question.get('id','v')}")
        transformed = dyslexia_transform(question.get("question", ""), t_choice)
        dyslexia_text_block(transformed)
    else:
        st.markdown(f'<div class="neon-box">{safe_text(question.get("question", ""))}</div>', unsafe_allow_html=True)

    st.markdown("")  # small spacer

    # ADHD mode: show one option at a time for focus
    if mode == "adhd":
        opts = question.get("options", [])
        if "adhd_opt" not in st.session_state:
            st.session_state.adhd_opt = 0
        idx = st.session_state.adhd_opt
        total = len(opts)
        if idx >= total:
            st.session_state.adhd_opt = 0
            idx = 0

        adhd_highlight_block(f"Option {idx+1} of {total}: {opts[idx]}")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Next Option ➜", key=f"next_opt_{question.get('id','n')}") and idx < total - 1:
                st.session_state.adhd_opt = idx + 1
                st.experimental_rerun()
        with col2:
            if st.button("Select This Option", key=f"choose_opt_{question.get('id','c')}"):
                st.session_state[qkey] = opts[idx]
                # selection made — return immediately
                return st.session_state.get(qkey)

        return None  # in ADHD flow we stop here until user selects

    # Normal / dyslexia / isl / hybrid modes: show all options as radio
    options = question.get("options", [])
    # key per question so multiple questions don't clash in session
    selected = st.radio("Choose your answer:", options, key=qkey)
    st.session_state[qkey] = selected

    # Hints for dyslexia/hybrid
    if mode in ("dyslexia", "hybrid"):
        with st.expander("💡 Hints"):
            for h in question.get("hints", []):
                st.markdown(f"- {safe_text(h)}")

    # Text-to-speech control (plays short TTS)
    if question.get("tts_text") and mode in ("standard", "dyslexia", "hybrid", "adhd"):
        if st.button("🔊 Read Aloud", key=f"tts_{question.get('id','t')}"):
            try:
                snippet = tts_audio_snippet(question.get("tts_text"))
                st.markdown(snippet, unsafe_allow_html=True)
            except Exception:
                st.warning("TTS playback failed in this environment.")

    # tiny UX tips for ISL mode
    if mode == "isl":
        st.caption("Tip: Watch the ISL assistant and then select the answer.")

    return st.session_state.get(qkey)


# ------------------------------
# SMALL UTILITY: CONFETTI / CELEBRATE
# ------------------------------
def celebrate():
    # Streamlit has st.balloons(); keep it safe
    try:
        st.balloons()
    except Exception:
        pass


# ------------------------------
# DEBUG / DEV: quick status panel
# ------------------------------
def debug_panel():
    if st.checkbox("Show debug", key="debug_ui"):
        st.json({
            "mode": st.session_state.get("mode"),
            "subject": st.session_state.get("subject"),
            "adhd_opt": st.session_state.get("adhd_opt"),
        })

# src/frontend/ui.py

import streamlit as st
import html
import urllib.parse


# ---------------------------------------------------
# Small helpers
# ---------------------------------------------------
def safe_text(s: str) -> str:
    return html.escape(s or "")


def tts_audio_snippet(text: str, voice: str = "Brian") -> str:
    """Return an HTML <audio> snippet that plays TTS from StreamElements."""
    try:
        q = urllib.parse.quote(str(text))
        url = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={q}"
        return f'<audio autoplay><source src="{url}" type="audio/mpeg"></audio>'
    except Exception:
        return ""


# ---------------------------------------------------
# Dyslexia helpers
# ---------------------------------------------------
def dyslexia_transform(text: str, view: str) -> str:
    if not text:
        return text
    if view == "lower":
        return text.lower()
    if view == "upper":
        return text.upper()
    if view == "spaced":
        return "  ".join(text.split())
    return text  # normal


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


# ---------------------------------------------------
# ADHD highlight
# ---------------------------------------------------
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


# ---------------------------------------------------
# ISL avatar
# ---------------------------------------------------
def isl_avatar(url_gif: str | None = None, url_video: str | None = None, width: int = 300):
    if url_gif:
        try:
            st.image(url_gif, width=width, caption="ISL Assistant")
        except Exception:
            st.write(f"ISL GIF: {url_gif}")

    if url_video:
        try:
            st.video(url_video)
        except Exception:
            st.write(f"ISL Video: {url_video}")


# ---------------------------------------------------
# Theme (neon)
# ---------------------------------------------------
def apply_theme():
    st.markdown(
        """
        <style>
        .css-18e3th9 {
            background: radial-gradient(circle at 10% 20%, #071029 0%, #02040a 60%, #000000 100%);
            color: #E6EEF3;
        }
        .neon-title {
            font-size: 28px;
            font-weight: 700;
            color: #A5F3FC;
            text-shadow: 0 0 18px rgba(165,243,252,0.12);
            margin-bottom: 10px;
        }
        .neon-box {
            padding: 14px 18px;
            border-radius: 12px;
            background: rgba(10,14,24,0.8);
            border: 1px solid rgba(99,102,241,0.14);
            box-shadow: 0 6px 22px rgba(99,102,241,0.04);
            color: #F8FAFC;
            font-size: 18px;
        }
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
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------
# Mode picker
# ---------------------------------------------------
def render_mode_picker():
    st.markdown('<div class="neon-title">🧭 Choose Accessibility Mode</div>', unsafe_allow_html=True)

    choices = [
        "Standard",
        "Dyslexia Mode (readability)",
        "ADHD Assist (focus)",
        "ISL (Indian Sign Language)",
        "Hybrid Accessibility (Best of all)",
    ]

    choice = st.radio("Mode", choices, index=0, horizontal=True)

    mapping = {
        "Standard": "standard",
        "Dyslexia Mode (readability)": "dyslexia",
        "ADHD Assist (focus)": "adhd",
        "ISL (Indian Sign Language)": "isl",
        "Hybrid Accessibility (Best of all)": "hybrid",
    }

    if st.button("Continue ➜"):
        st.session_state["mode"] = mapping[choice]
        st.rerun()


# ---------------------------------------------------
# Subject picker
# ---------------------------------------------------
def render_subject_picker():
    st.markdown('<div class="neon-title">📚 Choose Subject</div>', unsafe_allow_html=True)
    subject = st.selectbox("Select subject", ["Math", "English"], index=0)
    if st.button("Start Quiz 🚀"):
        st.session_state["subject"] = subject.lower()
        st.rerun()


# ---------------------------------------------------
# MAIN QUESTION UI (NO manual session_state writes)
# ---------------------------------------------------
def render_question_UI(question: dict):
    """
    Render a question safely and return the selected option (or None).
    No direct writes to st.session_state except widget-managed keys.
    """

    if not question or not isinstance(question, dict):
        st.error("Invalid question data.")
        return None

    text = question.get("question")
    options = question.get("options") or []

    if not text:
        st.error("Question text missing.")
        return None

    if not options:
        st.error("No answer options for this question.")
        return None

    qid = question.get("id", "q")
    mode = st.session_state.get("mode", "standard")

    # Header
    st.markdown('<div class="neon-title">🎯 Question</div>', unsafe_allow_html=True)

    # ISL section
    if mode in ("isl", "hybrid"):
        st.markdown("### 🤟 ISL Assistant")
        isl_avatar(question.get("isl_gif"), question.get("isl_video"))

    # Question text (with dyslexia support)
    if mode in ("dyslexia", "hybrid"):
        view = st.selectbox(
            "Reading view",
            ["normal", "lower", "upper", "spaced"],
            key=f"view_{qid}",
        )
        transformed = dyslexia_transform(text, view)
        dyslexia_text_block(transformed)
    else:
        st.markdown(f'<div class="neon-box">{safe_text(text)}</div>', unsafe_allow_html=True)

    st.markdown("")  # spacer

    # ---------------- ADHD MODE ----------------
    if mode == "adhd":
        # Use a widget-managed index instead of manual session_state writes
        idx = st.number_input(
            "Focus on option number",
            min_value=1,
            max_value=len(options),
            value=1,
            step=1,
            key=f"adhd_idx_{qid}",
        )
        idx_int = int(idx)
        label = options[idx_int - 1]
        adhd_highlight_block(f"Option {idx_int} of {len(options)}: {label}")

        if st.button("Select This Option", key=f"adhd_select_{qid}"):
            return label

        return None

    # ---------------- NORMAL / DYSLEXIA / HYBRID / ISL ----------------
    selected = st.radio(
        "Choose your answer:",
        options,
        key=f"answer_{qid}",
    )

    # Hints
    if mode in ("dyslexia", "hybrid"):
        hints = question.get("hints") or []
        if hints:
            with st.expander("💡 Hints"):
                for h in hints:
                    st.markdown(f"- {safe_text(h)}")

    # TTS
    tts_text = question.get("tts_text")
    if tts_text:
        if st.button("🔊 Read Aloud", key=f"tts_{qid}"):
            snippet = tts_audio_snippet(tts_text)
            if snippet:
                st.markdown(snippet, unsafe_allow_html=True)
            else:
                st.warning("TTS playback failed.")

    if mode == "isl":
        st.caption("Watch the ISL assistant and then select your answer.")

    return selected


# ---------------------------------------------------
# Extra helpers used elsewhere (optional)
# ---------------------------------------------------
def celebrate():
    try:
        st.balloons()
    except Exception:
        pass


def debug_panel():
    if st.checkbox("Show debug (dev)", key="debug_ui"):
        st.json({k: v for k, v in st.session_state.items()})

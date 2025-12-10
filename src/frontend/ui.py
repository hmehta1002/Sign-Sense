"""
frontend/ui.py

Full, self-contained UI module for SignSense.
Contains:
- theme application (neon)
- accessibility modes: standard, dyslexia, adhd, isl, hybrid
- dyslexia transforms + dyslexia text block
- ADHD safe one-option flow
- ISL avatar (gif / mp4)
- text-to-speech snippet (StreamElements demo endpoint)
- question renderer (safe, robust)
- mode + subject pickers
- small utilities: celebrate, debug panel
"""

from typing import List, Optional
import streamlit as st
import html
import urllib.parse
import traceback

# ---------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------
def safe_text(s: str) -> str:
    """Escape text for HTML injection."""
    return html.escape(s or "")


def tts_audio_snippet(text: str, voice: str = "Brian") -> str:
    """Return an HTML audio snippet using a public StreamElements endpoint."""
    try:
        q = urllib.parse.quote(str(text))
        url = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={q}"
        return f'<audio autoplay><source src="{url}" type="audio/mpeg"></audio>'
    except Exception:
        return ""


# ---------------------------------------------------------------------
# Dyslexia helpers and styling
# ---------------------------------------------------------------------
def dyslexia_transform(text: str, view: str) -> str:
    """
    Apply simple dyslexia-friendly transforms.
    view can be: normal | lower | upper | spaced
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
        # add extra inter-word spacing
        return "  ".join(text.split())
    return text


def dyslexia_text_block(text: str):
    """Render a dyslexia-friendly paragraph block."""
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


# ---------------------------------------------------------------------
# ADHD highlight block (visual emphasis)
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# ISL avatar rendering helpers
# ---------------------------------------------------------------------
def isl_avatar(url_gif: Optional[str] = None, url_video: Optional[str] = None, width: int = 300):
    """
    Render an ISL assistant area. Accepts either a gif or mp4 link.
    Falls back to a simple link if the media fails to render.
    """
    # show gif if provided
    if url_gif:
        try:
            st.image(url_gif, width=width, caption="ISL Assistant")
        except Exception:
            st.write(f"ISL GIF: {url_gif}")

    # show video if provided
    if url_video:
        try:
            st.video(url_video)
        except Exception:
            st.write(f"ISL Video: {url_video}")


# ---------------------------------------------------------------------
# Theme + small CSS that is Streamlit-safe
# ---------------------------------------------------------------------
def apply_theme():
    """Apply a neon + accessible theme via unsafe html (Streamlit)."""
    st.markdown(
        """
        <style>
        /* Page background */
        .css-18e3th9 {  /* target common Streamlit main container */
            background: radial-gradient(circle at 10% 20%, #071029 0%, #02040a 60%, #000000 100%);
            color: #E6EEF3;
        }

        /* Neon headers and title */
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

        /* Buttons */
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

        /* File uploader style */
        div[data-testid="stFileUploader"] {
            border-radius: 12px;
            border: 2px dashed rgba(99,102,241,0.12);
            padding: 12px;
            background: rgba(255,255,255,0.01);
        }

        /* Radio text color */
        div[role="radiogroup"] > label, div[role="radiogroup"] {
            color: #E6EEF3 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Mode-specific font tweaks (optional)
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


# ---------------------------------------------------------------------
# Mode picker (exposed to app.py)
# ---------------------------------------------------------------------
def render_mode_picker():
    """
    Renders a mode picker at the top of the app. Sets st.session_state.mode.
    Possible modes: standard, dyslexia, adhd, isl, hybrid
    """
    st.markdown('<div class="neon-title">🧭 Choose Accessibility Mode</div>', unsafe_allow_html=True)

    choices = [
        "Standard",
        "Dyslexia Mode (readability)",
        "ADHD Assist (focus)",
        "ISL (Indian Sign Language)",
        "Hybrid Accessibility (Best of all)",
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
        # initialize small defaults helpful for ADHD
        if st.session_state.mode == "adhd":
            # do not collide with later per-question keys
            st.session_state["global_adhd_init"] = True
        st.experimental_rerun()


# ---------------------------------------------------------------------
# Subject picker (exposed to app.py)
# ---------------------------------------------------------------------
def render_subject_picker():
    st.markdown('<div class="neon-title">📚 Choose Subject</div>', unsafe_allow_html=True)
    subject = st.selectbox("Select subject", ["Math", "English"], index=0)
    if st.button("Start Quiz 🚀"):
        st.session_state.subject = subject.lower()
        st.experimental_rerun()


# ---------------------------------------------------------------------
# Celebrate helper
# ---------------------------------------------------------------------
def celebrate():
    try:
        st.balloons()
    except Exception:
        pass


# ---------------------------------------------------------------------
# Debug panel
# ---------------------------------------------------------------------
def debug_panel():
    if st.checkbox("Show debug", key="debug_ui"):
        # minimize sensitive info
        try:
            st.json({
                "mode": st.session_state.get("mode"),
                "subject": st.session_state.get("subject"),
                "session_keys": list(st.session_state.keys()),
            })
        except Exception:
            st.write("Debug panel error:")
            st.text(traceback.format_exc())


# ---------------------------------------------------------------------
# Main question renderer (robust full implementation)
# ---------------------------------------------------------------------
def render_question_UI(question: dict):
    """
    Renders a question object safely.
    Expected question keys:
      - id (str)
      - question (str)
      - options (list[str])
      - answer (str) [not required for rendering]
      - difficulty (str) optional
      - isl_gif, isl_video optional
      - hints optional list
      - tts_text optional
    Returns the selected option (or None).
    This function avoids modifying session_state inside layout contexts to prevent StreamlitAPIException.
    """

    # Basic sanity checks
    if not question or not isinstance(question, dict):
        st.error("❌ Invalid question object.")
        return None

    text = question.get("question")
    options = question.get("options")

    if not text:
        st.error("❌ Question text missing.")
        return None

    if not options or not isinstance(options, list) or len(options) == 0:
        st.error("❌ This question has no valid answer options.")
        return None

    qid = question.get("id", "q")
    qkey = f"selected_{qid}"
    mode = st.session_state.get("mode", "standard")

    # Header
    st.markdown('<div class="neon-title">🎯 Question</div>', unsafe_allow_html=True)

    # ISL assistant (gif/video)
    if mode in ("isl", "hybrid"):
        st.markdown("### 🤟 ISL Assistant")
        isl_avatar(question.get("isl_gif"), question.get("isl_video"))

    # Render question text — dyslexia support
    if mode in ("dyslexia", "hybrid"):
        view_key = f"view_{qid}"
        # ensure key exists to keep stable layout
        default_view = st.session_state.get(view_key, "normal")
        view = st.selectbox("Reading view", ["normal", "lower", "upper", "spaced"], index=["normal","lower","upper","spaced"].index(default_view), key=view_key)
        st.session_state[view_key] = view  # persist chosen view
        dyslexia_text_block(dyslexia_transform(text, view))
    else:
        st.markdown(f'<div class="neon-box">{safe_text(text)}</div>', unsafe_allow_html=True)

    st.markdown("")  # spacer

    # ------------------------------
    # ADHD mode (safe implementation)
    # ------------------------------
    if mode == "adhd":
        # Use a per-question index key to avoid global collisions
        idx_key = f"adhd_idx_{qid}"

        # Initialize index safely BEFORE layout calls
        if idx_key not in st.session_state:
            st.session_state[idx_key] = 0

        idx = int(st.session_state.get(idx_key, 0))
        total = len(options)

        # clamp index
        if idx < 0:
            idx = 0
            st.session_state[idx_key] = 0
        if idx >= total:
            st.session_state[idx_key] = 0
            idx = 0

        # Show highlighted single option
        adhd_highlight_block(f"Option {idx+1} of {total}: {options[idx]}")

        # Buttons — do not mutate session_state inside "with col" blocks to avoid Streamlit errors.
        # We'll use buttons returned by layout columns directly.
        col1, col2 = st.columns(2)
        # Next option
        if col1.button("Next Option ➜", key=f"adhd_next_{qid}"):
            st.session_state[idx_key] = idx + 1
            st.experimental_rerun()
        # Select this option
        if col2.button("Select This Option", key=f"adhd_select_{qid}"):
            st.session_state[qkey] = options[idx]
            return options[idx]

        # Still in ADHD flow -> return None until selection
        return None

    # ------------------------------
    # Normal / dyslexia / hybrid / isl mode
    # ------------------------------
    # Radio selection — use a stable key
    try:
        # create radio; Streamlit will handle rendering and key binding
        selected = st.radio("Choose your answer:", options, key=qkey)
    except Exception as e:
        # defensive fallback: if radio fails for any reason, show small selectbox
        st.warning("UI fallback activated due to rendering issue.")
        selected = st.selectbox("Choose your answer (fallback):", options, key=f"{qkey}_fallback")

    # Validate and persist selection safely
    if selected is not None:
        try:
            st.session_state[qkey] = selected
        except Exception:
            # As a last resort, swallow session errors and store in a safe alternate key
            st.session_state[f"_safe_{qkey}"] = selected

    # Hints for dyslexia/hybrid
    if mode in ("dyslexia", "hybrid"):
        hints = question.get("hints", [])
        if hints:
            with st.expander("💡 Hints"):
                for h in hints:
                    st.markdown(f"- {safe_text(h)}")

    # TTS playback
    tts_text = question.get("tts_text")
    if tts_text and mode in ("standard", "dyslexia", "hybrid", "adhd"):
        if st.button("🔊 Read Aloud", key=f"tts_{qid}"):
            snippet = tts_audio_snippet(tts_text)
            if snippet:
                st.markdown(snippet, unsafe_allow_html=True)
            else:
                st.warning("TTS could not be generated in this environment.")

    # Small ISL tip
    if mode == "isl":
        st.caption("Tip: Watch the ISL assistant and then select the answer.")

    return selected


# ---------------------------------------------------------------------
# Small status / developer panel (non-intrusive)
# ---------------------------------------------------------------------
def small_status_panel():
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.write("")  # reserved for future quick info
    with col2:
        if st.button("🎯 Quick Restart"):
            st.experimental_rerun()
    with col3:
        if st.button("🔁 Reset UI State"):
            # Keep only very small subset if desired, otherwise full clear
            keys_to_keep = []
            for k in list(st.session_state.keys()):
                if k not in keys_to_keep:
                    del st.session_state[k]
            st.experimental_rerun()


# ---------------------------------------------------------------------
# End of file
# ---------------------------------------------------------------------

import streamlit as st
import streamlit.components.v1 as components
import html
import urllib.parse


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def safe_text(s: str) -> str:
    return html.escape(s or "")


# ---------------------------------------------------
# NEW: Browser-based Female TTS with Controls
# ---------------------------------------------------
def browser_tts_button(text: str, key: str):
    safe_t = (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", " ")
        .replace("\r", " ")
    )

    html_code = f"""
    <div id="tts-container-{key}" style="margin-top:8px; padding:12px; border-radius:10px;
        background:rgba(15,23,42,0.45); border:1px solid rgba(148,163,184,0.28);">

      <div style="margin-bottom:6px; font-weight:600; color:#E5E7EB;">
        🔊 Read Aloud (Female Voice)
      </div>

      <div style="display:flex; flex-direction:column; gap:4px; font-size:12px; color:#E5E7EB;">
        <label>Speed: <span id="rate_val_{key}">1.0</span>x</label>
        <input type="range" id="rate_{key}" min="0.5" max="1.5" value="1.0" step="0.1" />

        <label>Pitch: <span id="pitch_val_{key}">1.1</span></label>
        <input type="range" id="pitch_{key}" min="0.5" max="2.0" value="1.1" step="0.1" />

        <label>Volume: <span id="vol_val_{key}">1.0</span></label>
        <input type="range" id="vol_{key}" min="0.2" max="1.0" value="1.0" step="0.1" />
      </div>

      <button id="speak_btn_{key}" style="
          margin-top:10px;
          padding:8px 14px;
          background:#FF4ECD;
          color:white;
          border:none;
          border-radius:8px;
          cursor:pointer;
          font-weight:600;
      ">
        ▶ Play
      </button>
    </div>

    <script>
      (function() {{
        var txt = "{safe_t}";
        var rateSlider = document.getElementById("rate_{key}");
        var pitchSlider = document.getElementById("pitch_{key}");
        var volSlider = document.getElementById("vol_{key}");
        var rateLabel = document.getElementById("rate_val_{key}");
        var pitchLabel = document.getElementById("pitch_val_{key}");
        var volLabel = document.getElementById("vol_val_{key}");
        var btn = document.getElementById("speak_btn_{key}");

        if (!rateSlider || !pitchSlider || !volSlider || !btn) {{
          return;
        }}

        function updateLabels() {{
          rateLabel.textContent = rateSlider.value;
          pitchLabel.textContent = pitchSlider.value;
          volLabel.textContent = volSlider.value;
        }}

        updateLabels();
        rateSlider.oninput = updateLabels;
        pitchSlider.oninput = updateLabels;
        volSlider.oninput = updateLabels;

        function getFemaleVoice() {{
          var voices = speechSynthesis.getVoices();
          if (!voices || voices.length === 0) return null;

          var preferred = [
            "Google UK English Female",
            "Microsoft Zira Desktop",
            "Microsoft Heera Desktop",
            "Microsoft Neerja Online",
            "Microsoft Swara Online",
            "Samantha",
            "Joanna"
          ];

          var female = null;

          for (var i = 0; i < voices.length; i++) {{
            if (preferred.includes(voices[i].name)) {{
              female = voices[i];
              break;
            }}
          }}

          if (!female) {{
            for (var i = 0; i < voices.length; i++) {{
              let name = voices[i].name.toLowerCase();
              if (name.includes("female") || name.includes("woman") || name.includes("zira")) {{
                female = voices[i];
                break;
              }}
            }}
          }}

          if (!female) female = voices[0];
          return female;
        }}

        function speak() {{
          speechSynthesis.cancel();
          var utter = new SpeechSynthesisUtterance(txt);

          var v = getFemaleVoice();
          if (v) utter.voice = v;

          utter.rate = parseFloat(rateSlider.value);
          utter.pitch = parseFloat(pitchSlider.value);
          utter.volume = parseFloat(volSlider.value);

          speechSynthesis.speak(utter);
        }}

        btn.onclick = speak;
        window.speechSynthesis.onvoiceschanged = function() {{
          // preload
        }};
      }})();
    </script>
    """

    components.html(html_code, height=220)


# ---------------------------------------------------
# Dyslexia helpers
# ---------------------------------------------------
def dyslexia_transform(text: str, view: str) -> str:
    if view == "lower":
        return text.lower()
    if view == "upper":
        return text.upper()
    if view == "spaced":
        return "  ".join(text.split())
    return text


def dyslexia_text_block(text: str):
    st.markdown(
        f"""
        <div style="
            font-size:20px;
            line-height:1.6;
            padding:12px;
            border-radius:10px;
            background: rgba(255,255,255,0.05);
            border-left: 5px solid #00E5FF;
            font-family:'Verdana', sans-serif;
            color:#F8FAFC;
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
            border-radius: 12px;
            background: rgba(6,182,212,0.16);
            border: 1px solid rgba(6,182,212,0.22);
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
def isl_avatar(url_gif=None, url_video=None, width=300):
    if url_gif:
        try:
            st.image(url_gif, width=width)
        except:
            st.write(url_gif)

    if url_video:
        try:
            st.video(url_video)
        except:
            st.write(url_video)


# ---------------------------------------------------
# Neon theme
# ---------------------------------------------------
def apply_theme():
    st.markdown(
        """
        <style>
        .neon-title {
            font-size:26px; font-weight:700;
            color:#A5F3FC;
            text-shadow:0 0 10px rgba(165,243,252,0.3);
            margin-bottom:10px;
        }
        .neon-box {
            padding:14px 18px;
            border-radius:12px;
            background:rgba(10,14,24,0.8);
            border:1px solid rgba(99,102,241,0.15);
            color:#F8FAFC;
            font-size:18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------
# MAIN QUESTION UI (SAFE)
# ---------------------------------------------------
def render_question_UI(question: dict, mode: str):

    if not question:
        st.error("Invalid question.")
        return None

    text = question.get("question", "")
    options = question.get("options", [])
    qid = question.get("id", "q")

    st.markdown('<div class="neon-title">🎯 Question</div>', unsafe_allow_html=True)

    # ISL
    if mode in ("isl", "hybrid"):
        st.subheader("🤟 ISL Assistant")
        isl_avatar(question.get("isl_gif"), question.get("isl_video"))

    # Dyslexia mode
    if mode in ("dyslexia", "hybrid"):
        view = st.selectbox(
            "Reading view",
            ["normal", "lower", "upper", "spaced"],
            key=f"view_{qid}"
        )
        dyslexia_text_block(dyslexia_transform(text, view))
    else:
        st.markdown(f'<div class="neon-box">{safe_text(text)}</div>', unsafe_allow_html=True)

    # ADHD mode
    if mode == "adhd":
        idx = st.number_input(
            "Focus on option",
            min_value=1,
            max_value=len(options),
            value=1,
            step=1,
            key=f"adhd_idx_{qid}",
        )
        idx = int(idx)
        choice = options[idx - 1]
        adhd_highlight_block(f"{choice}")

        if st.button("Select This Option", key=f"adhd_select_{qid}"):
            return choice

        return None

    # Radio for normal modes
    selected = st.radio("Choose your answer:", options, key=f"answer_{qid}")

    # Hints
    if mode in ("dyslexia", "hybrid"):
        hints = question.get("hints", [])
        if hints:
            with st.expander("💡 Hints"):
                for h in hints:
                    st.write("- ", h)

    # TTS
    tts_text = question.get("tts_text")
    if tts_text:
        browser_tts_button(tts_text, f"tts_{qid}")

    return selected

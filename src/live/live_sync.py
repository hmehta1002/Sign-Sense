import streamlit as st
import json
from pathlib import Path
import random

# ---------------------------------------------------------
# ROOM DATABASE (FOLDER)
# ---------------------------------------------------------
ROOMS_DIR = Path(__file__).parent / "rooms"
ROOMS_DIR.mkdir(exist_ok=True)


def room_path(code: str) -> Path:
    return ROOMS_DIR / f"{code}.json"


# ---------------------------------------------------------
# SAVE / LOAD DATA
# ---------------------------------------------------------
def load_room(code: str):
    try:
        with open(room_path(code), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_room(code: str, data: dict):
    with open(room_path(code), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------
# CREATE NEW ROOM (HOST)
# ---------------------------------------------------------
def create_room():
    code = str(random.randint(10000, 99999))
    room = {
        "code": code,
        "state": "waiting",      # waiting → playing → finished
        "question_index": 0,
        "players": {},           # {name: {"answer": "", "score": 0}}
    }
    save_room(code, room)
    return room


# ---------------------------------------------------------
# HOST INTERFACE
# ---------------------------------------------------------
def host_interface(engine):
    st.subheader("🎮 Host Dashboard")

    # Remember last room code in session so host doesn't retype
    if "host_room_code" not in st.session_state:
        st.session_state.host_room_code = ""

    if st.button("🆕 Create New Room"):
        room = create_room()
        st.session_state.host_room_code = room["code"]
        st.success(f"Room Created: **{room['code']}** – share this with players.")

    code = st.text_input(
        "Enter Room Code to Host:",
        value=st.session_state.host_room_code,
        key="host_code_input",
    ).strip()

    if not code:
        st.info("Create a room or enter an existing room code.")
        return

    room = load_room(code)
    if not room:
        st.error("Room not found.")
        return

    st.success(f"Hosting Room **{code}**")

    # Player list
    st.markdown("### 👥 Players Joined")
    if room["players"]:
        for p in room["players"].keys():
            st.write(f"• {p}")
    else:
        st.write("_No players yet._")

    # Host Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("▶ Start Quiz"):
            room["state"] = "playing"
            save_room(code, room)
    with col2:
        if st.button("➡ Next Question"):
            room["question_index"] += 1
            save_room(code, room)
    with col3:
        if st.button("⛔ End Session"):
            room["state"] = "finished"
            save_room(code, room)

    # Current question preview
    if room["state"] == "playing":
        q_index = room["question_index"]
        if 0 <= q_index < len(engine.questions):
            q = engine.questions[q_index]
            st.markdown(f"### 📖 Current Question ({q_index + 1})")
            st.write(q.get("question", ""))
            st.write("Options:", q.get("options", []))
        else:
            st.info("No more questions in the quiz.")

    # Scoreboard
    st.markdown("### 📊 Scores")
    if room["players"]:
        for name, info in room["players"].items():
            st.write(f"**{name}** – {info.get('score', 0)} points")
    else:
        st.write("_No scores yet._")

    # Manual refresh
    st.caption("Tip: Click the 🔄 Refresh button to see latest joins/answers.")
    if st.button("🔄 Refresh Host View"):
        st.experimental_rerun()


# ---------------------------------------------------------
# PLAYER INTERFACE
# ---------------------------------------------------------
def player_interface(engine):
    st.subheader("🎮 Join as Player")

    name = st.text_input("Your Name:", key="player_name").strip()
    code = st.text_input("Room Code:", key="player_room_code").strip()

    if not name or not code:
        st.info("Enter your name and the room code shared by the host.")
        return

    room = load_room(code)
    if not room:
        st.error("Room not found. Check the code with your host.")
        return

    # Register player if new
    if name not in room["players"]:
        room["players"][name] = {"answer": "", "score": 0}
        save_room(code, room)

    st.success(f"Joined Room **{code}** as **{name}**")

    # Waiting for host
    if room["state"] == "waiting":
        st.warning("⏳ Waiting for host to start the quiz...")
        if st.button("🔄 Refresh"):
            st.experimental_rerun()
        return

    # Session finished
    if room["state"] == "finished":
        st.success("Session finished! 🎉")
        st.markdown("### Your Final Score")
        st.write(room["players"][name]["score"])
        if st.button("🔄 Refresh"):
            st.experimental_rerun()
        return

    # Show current question
    q_index = room["question_index"]
    if q_index >= len(engine.questions):
        st.info("No more questions. Waiting for host to end session.")
        if st.button("🔄 Refresh"):
            st.experimental_rerun()
        return

    q = engine.questions[q_index]
    st.markdown(f"### Question {q_index + 1}")
    st.write(q.get("question", ""))

    options = q.get("options", [])
    if not options:
        st.error("Question data missing options.")
        return

    # Pre-select previously given answer if any
    previous = room["players"][name].get("answer", "")
    try:
        default_index = options.index(previous) if previous in options else 0
    except ValueError:
        default_index = 0

    selected = st.radio(
        "Your Answer:",
        options,
        index=default_index,
        key=f"player_answer_{q_index}",
    )

    if st.button("✅ Submit Answer"):
        room = load_room(code) or room
        room["players"][name]["answer"] = selected

        # Update score
        if selected == q.get("answer"):
            room["players"][name]["score"] += 100

        save_room(code, room)
        st.success("Answer submitted! Click 🔄 Refresh after host moves to next question.")

    if st.button("🔄 Refresh"):
        st.experimental_rerun()


# ---------------------------------------------------------
# MAIN LIVE SESSION PAGE
# ---------------------------------------------------------
def live_session_page(engine, ctx):
    st.title("🌐 Live Multiplayer Quiz")

    role = st.radio("Choose Role:", ["Host", "Player"], horizontal=True)

    if role == "Host":
        host_interface(engine)
    else:
        player_interface(engine)


def init_live_session():
    # kept for compatibility with imports – does nothing
    pass

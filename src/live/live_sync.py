import streamlit as st
import json
import time
from pathlib import Path
import random

# ---------------------------------------------------------
# ROOM DATABASE (FOLDER)
# ---------------------------------------------------------
ROOMS_DIR = Path(__file__).parent / "rooms"
ROOMS_DIR.mkdir(exist_ok=True)


def room_path(code):
    return ROOMS_DIR / f"{code}.json"


# ---------------------------------------------------------
# SAVE / LOAD DATA
# ---------------------------------------------------------
def load_room(code):
    try:
        with open(room_path(code), "r") as f:
            return json.load(f)
    except:
        return None


def save_room(code, data):
    with open(room_path(code), "w") as f:
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
        "players": {},
    }
    save_room(code, room)
    return room


# ---------------------------------------------------------
# HOST INTERFACE
# ---------------------------------------------------------
def host_interface(engine):
    st.title("🎮 Live Host Dashboard")

    # Auto-refresh safely every 2 seconds
    st_autorefresh(interval=2000, key="host_refresh")

    if st.button("Create New Room"):
        room = create_room()
        st.success(f"Room Created: **{room['code']}**")
        st.info("Share this code with players.")
        return

    code = st.text_input("Enter Room Code to Host:")

    if not code:
        st.info("Create or enter a room.")
        return

    room = load_room(code)
    if not room:
        st.error("Room not found.")
        return

    st.success(f"Hosting Room **{code}**")

    # Player list
    st.subheader("👥 Players Joined")
    if room["players"]:
        for p in room["players"]:
            st.write(f"• {p}")
    else:
        st.write("No players joined yet.")

    # Controls
    col1, col2, col3 = st.columns(3)
    if col1.button("▶ Start Quiz"):
        room["state"] = "playing"
        save_room(code, room)

    if col2.button("➡ Next Question"):
        room["question_index"] += 1
        save_room(code, room)

    if col3.button("⛔ End Session"):
        room["state"] = "finished"
        save_room(code, room)

    # Current question
    if room["state"] == "playing":
        q_index = room["question_index"]
        if q_index < len(engine.questions):
            q = engine.questions[q_index]
            st.subheader(f"Question {q_index + 1}")
            st.write(q["question"])
            st.write("Options:", q["options"])
        else:
            st.info("All questions completed.")

    # Scoreboard
    st.subheader("📊 Scores")
    for player, info in room["players"].items():
        st.write(f"**{player}** – {info.get('score', 0)} points")


# ---------------------------------------------------------
# PLAYER INTERFACE
# ---------------------------------------------------------
def player_interface(engine):
    st.title("🎮 Join Live Room")

    # Safe autorefresh for players
    st_autorefresh(interval=2000, key="player_refresh")

    name = st.text_input("Your Name:")
    code = st.text_input("Room Code:")

    if not name or not code:
        st.info("Enter your name + room code.")
        return

    room = load_room(code)
    if not room:
        st.error("Room not found.")
        return

    # Add player if first time
    if name not in room["players"]:
        room["players"][name] = {"answer": "", "score": 0}
        save_room(code, room)

    st.success(f"Joined Room {code} as **{name}**")

    # Waiting screen
    if room["state"] == "waiting":
        st.warning("⏳ Waiting for host to start...")
        return

    if room["state"] == "finished":
        st.success("Session finished!")
        st.subheader("Your Final Score:")
        st.write(room["players"][name]["score"])
        return

    # Current question
    q_index = room["question_index"]

    if q_index >= len(engine.questions):
        st.info("No more questions available.")
        return

    q = engine.questions[q_index]
    st.subheader(f"Question {q_index + 1}")
    st.write(q["question"])

    selected = st.radio(
        "Your Answer:",
        q["options"],
        key=f"player_answer_{q_index}"
    )

    if st.button("Submit Answer"):
        room = load_room(code)

        room["players"][name]["answer"] = selected
        if selected == q["answer"]:
            room["players"][name]["score"] += 100

        save_room(code, room)
        st.success("Answer submitted!")


# ---------------------------------------------------------
# MAIN LIVE SESSION PAGE
# ---------------------------------------------------------
def live_session_page(engine, ctx):
    st.title("🌐 Live Multiplayer Quiz")

    role = st.radio("Select Mode:", ["Host", "Player"], horizontal=True)

    if role == "Host":
        host_interface(engine)
    else:
        player_interface(engine)


def init_live_session():
    pass


# ---------------------------------------------------------
# Safe Auto Refresh Wrapper
# ---------------------------------------------------------
def st_autorefresh(interval, key):
    """
    Wrapper to prevent Streamlit Cloud errors.
    """
    try:
        st.experimental_rerun  # check existence without calling
    except:
        pass

    # NEW SAFE METHOD
    st.markdown(
        f"""
        <script>
            setTimeout(function(){{
                window.location.reload();
            }}, {interval});
        </script>
        """,
        unsafe_allow_html=True
    )

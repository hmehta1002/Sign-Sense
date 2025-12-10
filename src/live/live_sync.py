import streamlit as st
import json
import random
from pathlib import Path
import time

ROOMS_DIR = Path(__file__).parent / "rooms"
ROOMS_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------
# Utility: load + save room safely
# ---------------------------------------------------
def load_room(code):
    path = ROOMS_DIR / f"{code}.json"
    if not path.exists():
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None


def save_room(code, data):
    path = ROOMS_DIR / f"{code}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------
# Create new room (Host)
# ---------------------------------------------------
def create_room():
    code = str(random.randint(10000, 99999))
    room = {
        "code": code,
        "state": "waiting",   # waiting → playing → finished
        "current_question": 0,
        "players": {},        # { "Himani": {"score": 0, "answer": ""} }
        "question_index": 0
    }
    save_room(code, room)
    return room


# ---------------------------------------------------
# HOST PAGE
# ---------------------------------------------------
def host_page(engine):
    st.header("🎮 Live Host Dashboard")

    # create or resume room
    if "room_code" not in st.session_state:
        room = create_room()
        st.session_state.room_code = room["code"]
    else:
        room = load_room(st.session_state.room_code)

    if not room:
        st.error("Room file not found. Resetting…")
        st.session_state.clear()
        st.rerun()

    st.success(f"Room Code: **{room['code']}**")

    st.subheader("Players Joined")
    players = room.get("players", {})
    if players:
        for p in players.keys():
            st.write(f"👤 {p}")
    else:
        st.info("Waiting for players to join…")

    # ---------------------------
    # Host controls
    # ---------------------------
    col1, col2, col3 = st.columns(3)

    if col1.button("▶ Start Quiz"):
        room["state"] = "playing"
        save_room(room["code"], room)
        st.rerun()

    if col2.button("➡ Next Question"):
        room["question_index"] += 1
        save_room(room["code"], room)
        st.rerun()

    if col3.button("⛔ End Session"):
        room["state"] = "finished"
        save_room(room["code"], room)
        st.rerun()

    # Auto-refresh
    time.sleep(1)
    st.rerun()


# ---------------------------------------------------
# PLAYER PAGE
# ---------------------------------------------------
def player_page(engine):
    st.header("🎮 Join Live Session")

    code = st.text_input("Enter Room Code:")
    name = st.text_input("Enter your name:")

    if st.button("Join"):
        if not code or not name:
            st.warning("Enter both fields.")
            return

        room = load_room(code)
        if not room:
            st.error("Room not found.")
            return

        # register player
        players = room.get("players", {})
        if name not in players:
            players[name] = {"score": 0, "answer": ""}
        room["players"] = players
        save_room(code, room)

        st.session_state.room_code = code
        st.session_state.player_name = name
        st.rerun()

    # After joining:
    if "room_code" in st.session_state and "player_name" in st.session_state:
        room = load_room(st.session_state.room_code)
        if not room:
            st.error("Room lost.")
            return

        if room["state"] == "waiting":
            st.info("Waiting for host to start…")
            time.sleep(1)
            st.rerun()

        if room["state"] == "finished":
            st.success("Session Finished!")
            return

        # Show current question
        q_index = room["question_index"]
        q = engine.questions[q_index]

        st.subheader(f"Question {q_index+1}")
        st.write(q["question"])

        selected = st.radio("Choose:", q["options"], key=f"q_{q_index}")

        if st.button("Submit Answer"):
            # Store player's answer
            name = st.session_state.player_name
            room["players"][name]["answer"] = selected
            save_room(room["code"], room)
            st.success("Answer Submitted!")

        time.sleep(1)
        st.rerun()


# ---------------------------------------------------
# MAIN ENTRY FOR LIVE SESSION
# ---------------------------------------------------
def live_session_page(engine, ctx):
    st.title("🌐 Live Multiplayer Quiz")

    mode = st.radio("Choose Mode", ["Host", "Player"], horizontal=True)

    if mode == "Host":
        host_page(engine)
    else:
        player_page(engine)

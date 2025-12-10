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
# SAVE / LOAD ROOM
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
        "players": {},           # "Himani": {"answer": "", "score": 0}
    }
    save_room(code, room)
    return room


# ---------------------------------------------------------
# HOST INTERFACE
# ---------------------------------------------------------
def host_interface(engine):
    st.title("🎮 Live Host Dashboard")

    # Host creates a room each time
    if st.button("Create New Room"):
        room = create_room()
        st.write(f"🔐 **Room Code:** `{room['code']}`")
        st.write("Share this code with players.")
        st.stop()

    code = st.text_input("Enter an existing Room Code to host:")

    if not code:
        st.info("Create or enter a room.")
        return

    room = load_room(code)
    if not room:
        st.error("Room not found.")
        return

    st.success(f"Hosting Room **{code}**")

    # Player list
    st.subheader("Players Joined")
    for p in room["players"].keys():
        st.write(f"👤 {p}")

    # Host controls
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

    # Show current question
    if room["state"] == "playing":
        q_index = room["question_index"]
        if q_index < len(engine.questions):
            q = engine.questions[q_index]
            st.subheader(f"Current Question ({q_index + 1})")
            st.write(q["question"])
            st.write("Options:", q["options"])
        else:
            st.info("No more questions.")

    # Scoreboard
    st.subheader("📊 Scores")
    for name, info in room["players"].items():
        st.write(f"**{name}** – {info.get('score', 0)} points")

    # Auto-refresh
    time.sleep(1)
    st.experimental_rerun()


# ---------------------------------------------------------
# PLAYER INTERFACE
# ---------------------------------------------------------
def player_interface(engine):
    st.title("🎮 Join Live Room")

    name = st.text_input("Your name:")
    code = st.text_input("Room Code:")

    if not name or not code:
        st.info("Enter name + room code.")
        return

    room = load_room(code)
    if not room:
        st.error("Room not found.")
        return

    # Register player if not already in room
    if name not in room["players"]:
        room["players"][name] = {"answer": "", "score": 0}
        save_room(code, room)

    st.success(f"Joined Room {code} as {name}")

    # Wait for host
    if room["state"] == "waiting":
        st.info("Waiting for host to start…")
        time.sleep(1)
        st.experimental_rerun()

    # Session finished
    if room["state"] == "finished":
        st.success("Session finished!")
        st.subheader("Your Final Score:")
        st.write(room["players"][name]["score"])
        return

    # Show current question
    q_index = room["question_index"]

    if q_index >= len(engine.questions):
        st.info("No more questions.")
        return

    q = engine.questions[q_index]
    st.subheader(f"Question {q_index + 1}")
    st.write(q["question"])

    selected = st.radio("Your answer:", q["options"], key=f"ans_{q_index}")

    if st.button("Submit Answer"):
        # Save answer
        room = load_room(code)
        room["players"][name]["answer"] = selected

        # Score if correct
        if selected == q["answer"]:
            room["players"][name]["score"] += 100

        save_room(code, room)
        st.success("Answer submitted!")

    # Auto-refresh
    time.sleep(1)
    st.experimental_rerun()


# ---------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------
def live_session_page(engine, ctx):
    st.title("🌐 Live Multiplayer Quiz")

    mode = st.radio("Mode:", ["Host", "Player"], horizontal=True)

    if mode == "Host":
        host_interface(engine)
    else:
        player_interface(engine)


def init_live_session():
    pass

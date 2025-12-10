import streamlit as st


def init_live_session():
    # No special init yet, but kept for future
    pass


def live_session_page(engine, ctx):
    st.title("🌐 Live Session (Multiplayer)")

    st.info(
        "Multiplayer logic is simplified for now. "
        "You can extend this page later with real-time rooms and syncing."
    )

    st.write("Engine available:" if engine else "No engine initialized yet.")

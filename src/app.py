import streamlit as st
from frontend.ui import apply_theme, render_mode_picker, render_subject_picker, render_question_UI
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from live.live_sync import init_live_session, live_session_page
from revision.revision_ui import render_revision_page

def reset_app():
    st.session_state.clear()
    st.experimental_rerun()

def sidebar_navigation():
    pages={"📘 Solo Quiz":"solo","🌐 Live Session":"live","🔁 Revision Lab":"revision","📊 Dashboard":"dashboard","🤖 Admin / AI Quiz":"admin_ai"}
    return pages[st.sidebar.radio("Navigation",list(pages.keys()))]

def ensure_engine():
    if "engine" not in st.session_state:
        mode=st.session_state.get("mode")
        subject=st.session_state.get("subject")
        if mode and subject:
            st.session_state.engine=QuizEngine(mode,subject)

def solo_quiz_page():
    engine=st.session_state.engine
    q=engine.get_current_question()
    if q is None:
        st.success("🎉 Quiz Complete!")
        st.balloons()
        if st.button("📊 View Dashboard"):
            st.session_state.page="dashboard"
            st.experimental_rerun()
        return
    render_question_UI(q)
    c1,c2=st.columns(2)
    if engine.current_index>0 and c1.button("⬅ Back"):
        engine.current_index-=1
        st.experimental_rerun()
    if c2.button("Next ➜"):
        engine.next_question()
        st.experimental_rerun()

def main():
    st.set_page_config(page_title="SignSense",layout="wide")
    apply_theme()
    if st.sidebar.button("🔁 Reset"): reset_app()
    page=sidebar_navigation()
    st.session_state.page=page
    if page=="solo":
        if "mode"not in st.session_state:render_mode_picker();return
        if "subject"not in st.session_state:render_subject_picker();return
        ensure_engine();solo_quiz_page()
    elif page=="dashboard":render_dashboard(st.session_state.get("engine"))
    elif page=="revision":render_revision_page(st.session_state.get("engine"))
    elif page=="live":init_live_session();live_session_page(st.session_state.get("engine"),{})
    elif page=="admin_ai":ai_quiz_builder()
    else:st.error("⚠ Unknown route")

if __name__=="__main__":main()

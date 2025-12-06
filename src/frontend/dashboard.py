import streamlit as st
import pandas as pd
import plotly.express as px


def render_dashboard(engine):

    if not engine or not engine.history:
        st.warning("⚠ No quiz data yet. Complete at least one quiz to unlock analytics.")
        return

    st.markdown("## 📊 Performance Dashboard")
    st.write("Your learning progress based on completed quizzes.")

    df = pd.DataFrame(engine.history)

    # ==================== METRICS ====================
    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 Total Score", engine.score)
    col2.metric("🎯 Accuracy", f"{(df.correct.mean() * 100):.1f}%")
    col3.metric("⚡ Best Streak", engine.best_streak)

    st.divider()

    # ==================== DIFFICULTY ANALYSIS ====================
    st.subheader("📌 Accuracy by Difficulty")

    diff_accuracy = df.groupby("difficulty").correct.mean().reset_index()
    fig_diff = px.bar(
        diff_accuracy,
        x="difficulty",
        y="correct",
        text="correct",
        labels={"correct": "Accuracy"},
        color="difficulty",
        color_discrete_sequence=["#00eaff", "#c084fc", "#ff0080"]
    )
    fig_diff.update_traces(texttemplate="%{y:.0%}")
    st.plotly_chart(fig_diff, use_container_width=True)

    # ==================== TIME VS PERFORMANCE ====================
    if "time_taken" in df and df.time_taken.notnull().any():
        st.subheader("⏱️ Time Taken vs Points Earned")

        fig_time = px.scatter(
            df,
            x="time_taken",
            y="points_earned",
            color="correct",
            labels={"time_taken": "Time (seconds)", "points_earned": "Points"},
            color_discrete_sequence=["#ff4f8b", "#00ff95"]
        )
        st.plotly_chart(fig_time, use_container_width=True)

    # ==================== SCORE TREND ====================
    st.subheader("📈 Score Progression")

    df["running_score"] = df["points_earned"].cumsum()
    line_fig = px.line(df, y="running_score", markers=True)
    st.plotly_chart(line_fig, use_container_width=True)

    # ==================== MISTAKE REVIEW ====================
    st.subheader("❌ Mistakes to Review")

    wrong = df[df.correct == False]

    if wrong.empty:
        st.success("🎉 Perfect! No mistakes to review.")
    else:
        for _, row in wrong.iterrows():
            st.markdown(
                f"""
                <div style="
                    background:rgba(255,255,255,0.05);
                    border:1px solid #ff4f8b;
                    padding:12px;
                    margin:8px;
                    border-radius:10px;">
                    ❌ <b>{row['question_id']}</b><br>
                    Correct Answer: <b>{row['correct_answer']}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

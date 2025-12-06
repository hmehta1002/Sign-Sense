
import streamlit as st
import pandas as pd
import plotly.express as px


def render_dashboard(engine):

    if not engine.history:
        st.warning("No quiz data yet — complete at least one quiz to view analytics.")
        return

    st.markdown("### 📊 Performance Dashboard")
    st.divider()

    df = pd.DataFrame(engine.history)

    # Score summary
    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 Total Score", engine.score)
    col2.metric("🎯 Accuracy", f"{sum(df.correct) / len(df) * 100:.1f}%")
    col3.metric("⚡ Best Streak", engine.best_streak)

    # Accuracy by difficulty
    st.subheader("📌 Accuracy by Difficulty Level")
    diff_accuracy = df.groupby("difficulty").correct.mean().reset_index()
    fig_diff = px.bar(diff_accuracy, x="difficulty", y="correct", color="difficulty",
                      labels={"correct": "Accuracy"},
                      color_discrete_sequence=["#00eaff", "#c084fc", "#ff0080"])
    st.plotly_chart(fig_diff, use_container_width=True)

    # Time vs Correctness Scatter
    if df.time_taken.notnull().any():
        st.subheader("⏱️ Time Taken vs Accuracy")
        fig_time = px.scatter(df, x="time_taken", y="points_earned", color="correct",
                              color_discrete_sequence=["#ff355e", "#32ff7e"])
        st.plotly_chart(fig_time, use_container_width=True)

    # Trend line: performance growth
    st.subheader("📈 Score Growth Trend")
    df["running_score"] = df["points_earned"].cumsum()
    line_fig = px.line(df, y="running_score", markers=True)
    st.plotly_chart(line_fig, use_container_width=True)

    # Mistakes review list
    st.subheader("❌ Mistakes to Review")
    wrong = df[df.correct == False]
    if wrong.empty:
        st.success("Amazing — No mistakes detected 🎉")
    else:
        for _, row in wrong.iterrows():
            st.markdown(
                f"""
                <div style="padding:10px;border-radius:10px;background:#1b1b32;border:1px solid #ff4f8b">
                    ❌ <b>{row['question_id']}</b> — correct answer: <b>{row['correct_answer']}</b>
                </div>
                """, 
                unsafe_allow_html=True
            )

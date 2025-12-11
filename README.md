# Sign-Sense
SignSense – AI-Powered Accessible Quiz Platform
An inclusive, adaptive, and multimodal quiz system designed for learners with Dyslexia, ADHD, and hearing impairments.

SignSense is an AI-driven quiz platform that enhances learning accessibility through Indian Sign Language (ISL) avatars, Dyslexia-friendly text modes, ADHD focus modes, adaptive scoring, and optional real-time quiz hosting.
This project demonstrates a functional prototype developed for IIT Bombay AI Sprint – Round 2, focusing on technical feasibility, core AI integration, and stable end-to-end functionality.

📘 1. Project Overview

Traditional quiz platforms lack support for learners with diverse accessibility needs. SignSense bridges this gap by introducing:

🔹 Accessibility Features

Dyslexia Mode (readability transformations)

ADHD Mode (one-option-at-a-time reveal for focus)

ISL Mode (GIF/video-based signing assistant)

Hybrid Mode (all accessibility features combined)

🔹 AI Features

AI quiz generator (text/PDF/topic → auto-generated MCQs)

Adaptive difficulty (prototype)

Text-to-speech integration

🔹 Engagement & Analytics

Neon cyber UI

Adaptive scoring (speed, streak, difficulty)

Performance dashboard with charts

Revision mode for incorrect questions

🔹 Real-Time Prototype

Live quiz session (host + participants)

Basic leaderboard logic

This prototype achieves the intended 60–80% functional completion expected for Round 2.


⚙️ 2. Setup Instructions
Clone the repository
git clone <your-repo-url>
cd sign-sense

Install dependencies
pip install -r requirements.txt

Run the application
streamlit run streamlit_app.py

Access the app
http://localhost:8501


🏗️ 3. Architecture Overview
SignSense follows a modular, layered architecture:
Frontend Layer (Streamlit)
Renders quiz UI, dashboards, revision pages
Applies accessibility transformations
Renders ISL GIF/video
Builds AI quiz form interfaces
Manages session state and navigation
Core Logic Layer (QuizEngine)
Loads questions
Manages progression, scoring, timing, streaks
Logs user responses for analytics
Supports adaptive difficulty foundations

🔌 4. How to Run Locally (Step-By-Step)

1️⃣ Create a virtual environment (recommended)

python -m venv venv
source venv/bin/activate  # (Mac/Linux)
venv\Scripts\activate     # (Windows)


2️⃣ Install the required dependencies

pip install -r requirements.txt


3️⃣ Ensure the following folder structure exists

sign-sense/
 ├── streamlit_app.py
 ├── /src
 │    ├── /frontend
 │    ├── /backend
 │    ├── /ai
 │    ├── /live
 │    └── /revision
 ├── requirements.txt
 └── README.md


4️⃣ Run the platform

streamlit run streamlit_app.py


5️⃣ Open the app in your browser

http://localhost:8501

🔗 5. APIs & Endpoints (Prototype Level)

Even though Streamlit abstracts backend routes, your architecture includes API-like callable modules.

A. Quiz Engine Functions
Function	Description
QuizEngine(mode, subject)	Initializes quiz session
load_questions()	Loads JSON question bank
get_current_question()	Returns active question object
check_answer(user_answer)	Evaluates correctness + scoring
next_question()	Moves to next question

🔗 5. APIs & Endpoints (Prototype Level)

Although Streamlit does not use HTTP routes directly, SignSense exposes modular backend endpoints through Python modules that behave like API calls.

🔹 A. Quiz Engine Functional Endpoints
Function	Input	Output	Purpose
QuizEngine(mode, subject)	mode: str, subject: str	Engine object	Initializes quiz state
load_questions()	None	List of MCQs	Loads JSON question banks
get_current_question()	None	Question dict	Returns the current active question
check_answer(answer)	User answer	dict: correctness, points, streak	Evaluates answer & updates scores
next_question()	None	None	Moves to next question
history	–	List of records	Complete attempt log

🔹 B. AI Quiz Builder Endpoints
Endpoint	Input	Output	Purpose
generate_quiz_from_text(text)	Educational text/topic	5–10 MCQs	Auto-generates quiz questions
parse_pdf(pdf_file)	PDF	Extracted text	For PDF-based quiz creation
format_mcq_output()	Raw AI output	Clean MCQ JSON	Ensures consistency

🔹 C. Live Session API (Prototype)
Function	Input	Output	Description
init_live_session()	Host ID	Room code	Initializes hosting session
join_session(room_code)	Room code	Participant added	Join session prototype
broadcast_question()	Question	Synced clients	Pushes question to all participants
update_scores()	User responses	Leaderboard	Updates live leaderboard

🔹 D. Revision Engine
Function	Purpose
get_incorrect_questions()	Returns all incorrectly answered MCQs
render_revision_page(engine)	UI to practice weak topics

📝 6. Example Inputs & Outputs
Example Question (JSON Input)
{
  "id": "ENG_Q1",
  "question": "Choose the synonym of 'happy':",
  "options": ["sad", "joyful", "angry", "silent"],
  "answer": "joy

7. List of Dependencies

The following libraries are required for running SignSense:

Core Dependencies
Library	Purpose
streamlit	Frontend UI, state management, layout
pandas	Dashboard analytics, charts, tabular logs
numpy	Numerical ops (future adaptive difficulty)
python-multipart	File uploads (PDF, text)
PyPDF2	PDF text extraction
regex	Cleaning input text
uuid	Generating unique session IDs
requests	External API hooks (future AI integration)
AI & NLP
Library	Purpose
transformers (optional)	HuggingFace model loading
sentencepiece	Tokenization (if using LLMs)
Visualization
Library	Purpose
matplotlib	Base-level charting
altair	Charts via Streamlit
plotly (optional)	Advanced dashboard visuals
Backend Logic
Library	Purpose
pathlib	File system handling
json	Reading/writing question banks
time	Time-based scoring
random	Question shuffling
Full Example requirements.txt
streamlit
pandas
numpy
PyPDF2
regex
plotly
altair
matplotlib
requests
uuid
transformers
sentencepiece

👥 8. Contributors
Project Lead & Developer

Himani Mehta-

Full-stack development (frontend + backend + AI integration)

Designed accessibility modes (Dyslexia, ADHD, ISL, Hybrid)

Developed QuizEngine, dashboard analytics, and revision mode

Modeled Live Session prototype

Created question datasets (Math + English)

Implemented UI/UX themes and animations

Shreya Sareen-

Frontend Development

Dattavi Solanki-

Frontend Development

Ashrit-

Backend development




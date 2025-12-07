import json
import os
import time

class QuizEngine:
    def __init__(self, mode, subject):
        self.mode = mode
        self.subject = subject.lower().strip()
        self.questions = self.load_questions(self.subject)
        self.index = 0
        self.score = 0
        self.streak = 0
        self.history = []
        self.start_time = None

    def load_questions(self, subject):
        # Get absolute path of project root (works on Streamlit Cloud)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(project_root, "data")

        filename_map = {
            "math": "questions_math.json",
            "english": "questions_english.json",
        }

        if subject not in filename_map:
            raise ValueError(f"Unknown subject selected: {subject}")

        filepath = os.path.join(data_path, filename_map[subject])

        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"❌ Question file missing at: {filepath}\n"
                f"📂 Expected files in /data:\n - questions_math.json\n - questions_english.json"
            )

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_current_question(self):
        if self.index < len(self.questions):
            self.start_time = time.time()
            return self.questions[self.index]
        return None

    def check_answer(self, selected):
        question = self.questions[self.index]
        correct = (question["answer"] == selected)
        time_taken = time.time() - self.start_time if self.start_time else None

        points = 10
        if correct:
            self.streak += 1
            points += self.streak * 2
            self.score += points
        else:
            self.streak = 0

        self.history.append({
            "question_id": question["question"],
            "selected": selected,
            "correct": correct,
            "correct_answer": question["answer"],
            "time_taken": time_taken,
            "points": points
        })

        return {
            "correct": correct,
            "correct_answer": question["answer"],
            "time_taken": time_taken,
            "points": points
        }

    def next_question(self):
        self.index += 1

    def reset(self):
        self.index = 0
        self.score = 0
        self.streak = 0
        self.history = []

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
        # Correct path for Streamlit Cloud & local usage
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

        filename_map = {
            "math": "questions_math.json",
            "english": "questions_english.json",
        }

        if subject not in filename_map:
            raise ValueError(f"❌ Unknown subject selected: {subject}")

        filename = filename_map[subject]
        filepath = os.path.join(base_path, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"❌ Question file missing at: {filepath}")

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

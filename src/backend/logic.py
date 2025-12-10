import json
import time
import random
from pathlib import Path


class QuizEngine:
    def __init__(self, mode: str, subject: str):
        self.mode = mode
        self.subject = subject

        self.current_index = 0
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.history = []
        self.start_time = None

        self.questions = self.load_questions()
        random.shuffle(self.questions)

    # -----------------------------
    # LOAD JSON QUESTIONS
    # -----------------------------
    def load_questions(self):
        file_map = {
            "math": "questions_math.json",
            "english": "questions_english.json",
        }
        filename = file_map.get(self.subject)
        if not filename:
            raise ValueError(f"Unknown subject: {self.subject}")

        backend_dir = Path(__file__).parent
        filepath = backend_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"❌ Questions file missing: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Questions file must contain a JSON list.")

        return data

    # -----------------------------
    # SAFELY FETCH CURRENT QUESTION
    # -----------------------------
    def get_current_question(self):
        if self.current_index >= len(self.questions):
            return None

        q = self.questions[self.current_index]

        # SAFETY FIX: skip broken questions
        if (
            "question" not in q
            or "options" not in q
            or not isinstance(q["options"], list)
            or len(q["options"]) == 0
        ):
            self.current_index += 1
            return self.get_current_question()

        self.start_time = time.time()
        return q

    # -----------------------------
    # CHECK ANSWER
    # -----------------------------
    def check_answer(self, user_answer: str):
        q = self.questions[self.current_index]
        correct = (user_answer == q["answer"])

        if self.start_time is not None:
            time_taken = round(time.time() - self.start_time, 2)
        else:
            time_taken = None

        base_points = 100
        speed_bonus = 0
        if time_taken is not None:
            if time_taken <= 5:
                speed_bonus = 50
            elif time_taken <= 10:
                speed_bonus = 20

        if correct:
            self.streak += 1
            streak_bonus = self.streak * 10
            points = base_points + streak_bonus + speed_bonus
            self.score += points
        else:
            self.streak = 0
            points = 0

        self.best_streak = max(self.best_streak, self.streak)

        record = {
            "id": q.get("id"),
            "question": q["question"],
            "subject": self.subject,
            "mode": self.mode,
            "selected": user_answer,
            "correct": correct,
            "correct_answer": q["answer"],
            "difficulty": q.get("difficulty", "unknown"),
            "time_taken": time_taken,
            "points": points,
        }
        self.history.append(record)

        return {
            "correct": correct,
            "points": points,
            "correct_answer": q["answer"],
            "time": time_taken,
        }

    # -----------------------------
    # NEXT QUESTION
    # -----------------------------
    def next_question(self):
        self.current_index += 1

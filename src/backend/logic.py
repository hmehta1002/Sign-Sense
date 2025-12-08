import json
import time
import random
from pathlib import Path


class QuizEngine:
    def __init__(self, mode: str, subject: str):
        self.mode = mode
        self.subject = subject

        self.current_index = 0  # IMPORTANT: main index
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.history = []
        self.start_time = time.time()

        self.questions = self.load_questions(subject)

        # Shuffle questions for variety (like Kahoot)
        random.shuffle(self.questions)

    def load_questions(self, subject: str):
        file_map = {
            "English": "questions_english.json",
            "Mathematics": "questions_math.json"
        }

        filename = file_map.get(subject)
        filepath = Path(__file__).parent / filename

        if not filepath.exists():
            raise FileNotFoundError(f"❌ Missing questions file: {filepath}")

        with open(filepath, "r") as f:
            return json.load(f)

    def get_current_question(self):
        """Return current question or None if quiz finished."""
        if self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index]

    def check_answer(self, user_answer: str):
        q = self.get_current_question()
        correct = (user_answer == q["answer"])
        time_taken = time.time() - self.start_time

        base_points = 100
        time_bonus = max(0, 50 - int(time_taken * 2))

        if correct:
            self.streak += 1
            points = base_points + time_bonus + (self.streak * 20)
            self.score += points
        else:
            self.streak = 0
            points = 0

        self.best_streak = max(self.best_streak, self.streak)

        self.history.append({
            "id": q["id"],
            "question": q["question"],
            "difficulty": q["difficulty"],
            "correct": correct,
            "user_answer": user_answer,
            "correct_answer": q["answer"],
            "time_taken": round(time_taken, 2),
            "points_earned": points
        })

        self.start_time = time.time()

        return {"correct": correct, "points": points, "correct_answer": q["answer"]}

    def next_question(self):
        """Move to the next question."""
        self.current_index += 1


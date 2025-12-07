import json
import os
import time

class QuizEngine:
    def __init__(self, mode, subject):
        self.mode = mode
        self.subject = subject.lower()
        self.questions = self.load_questions()
        self.index = 0
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.history = []
        self.start_time = None

    def load_questions(self):
        backend_path = os.path.dirname(os.path.abspath(__file__))
        filename = f"questions_{self.subject}.json"
        filepath = os.path.join(backend_path, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Missing: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_current_question(self):
        if self.index < len(self.questions):
            self.start_time = time.time()
            return self.questions[self.index]
        return None

    def check_answer(self, selected):
        q = self.questions[self.index]
        correct = (selected == q["answer"])
        time_taken = round(time.time() - self.start_time, 2)

        points = 10
        if correct:
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak
            points += self.streak * 2
            self.score += points
        else:
            self.streak = 0

        self.history.append({
            "question": q["question"],
            "selected": selected,
            "correct": correct,
            "correct_answer": q["answer"],
            "difficulty": q.get("difficulty", "unknown"),
            "time_taken": time_taken,
            "points": points
        })

        return {"correct": correct, "time": time_taken, "points": points, "correct_answer": q["answer"]}

    def next_question(self):
        self.index += 1

    def reset(self):
        self.index = 0
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.history = []

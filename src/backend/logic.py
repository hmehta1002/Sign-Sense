from pathlib import Path
import json

class QuizEngine:
    def __init__(self, mode, subject):
        self.mode = mode
        self.subject = subject
        self.index = 0
        self.score = 0
        self.questions = self.load_questions(subject)

    def load_questions(self, subject):
        base = Path(__file__).resolve().parents[2]
        filepath = base / "data" / f"questions_{subject}.json"
        with open(filepath, "r") as f:
            return json.load(f)

    def get_current_question(self):
        if self.index < len(self.questions):
            return self.questions[self.index]
        return None

    def check_answer(self, chosen):
        correct = self.questions[self.index]["answer"]
        difficulty = self.questions[self.index]["difficulty"]

        if chosen == correct:
            if difficulty == "easy":
                self.score += 1
            elif difficulty == "medium":
                self.score += 2
            elif difficulty == "hard":
                self.score += 3

    def next_question(self):
        self.index += 1


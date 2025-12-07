import json
import os
import time


class QuizEngine:
    def __init__(self, mode, subject):
        self.mode = mode
        self.subject = subject.lower().strip()

        # Load questions based on subject
        self.questions = self.load_questions(self.subject)

        # Quiz state
        self.index = 0
        self.score = 0
        self.streak = 0
        self.best_streak = 0  # <-- Needed for dashboard
        self.history = []
        self.start_time = None

    def load_questions(self, subject):
        """Loads the correct question file based on subject choice."""

        backend_folder = os.path.dirname(os.path.abspath(__file__))

        filename_map = {
            "math": "questions_math.json",
            "english": "questions_english.json"
        }

        if subject not in filename_map:
            raise ValueError(f"❌ Invalid subject: {subject}")

        filepath = os.path.join(backend_folder, filename_map[subject])

        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"❌ Missing file: {filepath}\n"
                "➡ Ensure the JSON files are inside src/backend/"
            )

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_current_question(self):
        """Returns the current question or None if the quiz is finished."""
        if self.index < len(self.questions):
            self.start_time = time.time()
            return self.questions[self.index]
        return None

    def check_answer(self, selected):
        """Evaluates the selected answer and updates score/streak history."""

        question = self.questions[self.index]
        correct = (question["answer"] == selected)

        time_taken = (
            time.time() - self.start_time
            if self.start_time is not None
            else None
        )

        points = 10

        if correct:
            self.streak += 1

            # Track highest streak
            if self.streak > self.best_streak:
                self.best_streak = self.streak

            # Bonus based on streak
            points += self.streak * 2
            self.score += points

        else:
            self.streak = 0

        result = {
            "question_id": question["question"],
            "selected": selected,
            "correct": correct,
            "correct_answer": question["answer"],
            "time_taken": time_taken,
            "points": points
        }

        self.history.append(result)
        return result

    def next_question(self):
        """Moves to the next question."""
        self.index += 1

    def reset(self):
        """Resets quiz state for a fresh run."""
        self.index = 0
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.history = []

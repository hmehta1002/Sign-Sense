import json
import os
import time


class QuizEngine:
    """
    Core quiz logic:
    - Loads questions from questions_<subject>.json in the same folder
    - Tracks score, streak, best_streak, history
    - Tracks response times for ADHD hybrid pacing
    """

    def __init__(self, mode: str, subject: str):
        self.mode = (mode or "standard").lower().strip()
        self.subject = (subject or "math").lower().strip()

        self.questions = self.load_questions()

        self.index = 0
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.history = []
        self.start_time = None
        self.times = []  # store time per question for pacing profile

    # -------------------- DATA LOADING --------------------

    def load_questions(self):
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        filename = f"questions_{self.subject}.json"
        filepath = os.path.join(backend_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Question file not found: {filepath}. "
                "Make sure questions_math.json and questions_english.json "
                "are placed inside src/backend/."
            )

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Question file must contain a JSON array of question objects.")

        return data

    # -------------------- QUIZ FLOW --------------------

    def get_current_question(self):
        if self.index < len(self.questions):
            self.start_time = time.time()
            return self.questions[self.index]
        return None

    def check_answer(self, selected: str):
        q = self.questions[self.index]
        correct_answer = q["answer"]
        correct = (selected == correct_answer)

        # Time taken
        if self.start_time is not None:
            time_taken = round(time.time() - self.start_time, 2)
        else:
            time_taken = None

        # Store for ADHD pacing
        if time_taken is not None:
            self.times.append(time_taken)

        # Scoring (Kahoot-ish: base + streak + speed bonus)
        base_points = 10
        speed_bonus = 0
        if time_taken is not None:
            if time_taken <= 5:
                speed_bonus = 5
            elif time_taken <= 10:
                speed_bonus = 2

        if correct:
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak
            points = base_points + self.streak * 2 + speed_bonus
            self.score += points
        else:
            self.streak = 0
            points = 0

        entry = {
            "id": q.get("id"),
            "question": q["question"],
            "selected": selected,
            "correct": correct,
            "correct_answer": correct_answer,
            "difficulty": q.get("difficulty", "unknown"),
            "time_taken": time_taken,
            "points": points,
            "mode": self.mode,
            "subject": self.subject,
        }

        self.history.append(entry)

        return {
            "correct": correct,
            "correct_answer": correct_answer,
            "time": time_taken,
            "points": points,
        }

    def next_question(self):
        self.index += 1

    def reset(self):
        self.index = 0
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.history = []
        self.start_time = None
        self.times = []

    # -------------------- ADHD HYBRID PROFILE --------------------

    def get_pacing_profile(self) -> str:
        """
        Returns 'fast', 'calm', or 'balanced' based on recent response times.
        Only meaningful in ADHD mode, but safe to call always.
        """
        if self.mode != "adhd" or not self.times:
            return "balanced"

        # Use last 5 questions to compute profile
        recent = self.times[-5:]
        avg = sum(recent) / len(recent)

        if avg <= 5:
            return "fast"
        elif avg >= 12:
            return "calm"
        else:
            return "balanced"

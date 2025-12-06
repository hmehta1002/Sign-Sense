from pathlib import Path
import json
from typing import List, Dict, Any


class QuizEngine:
    """
    Core quiz engine:
    - loads questions by subject
    - tracks score, index, and history
    - exposes summary statistics for analytics
    """

    def __init__(self, mode: str, subject: str):
        self.mode = mode                    # "Standard", "ADHD-Friendly", etc.
        self.subject = subject              # "math" or "english"
        self.index = 0                      # current question index
        self.score = 0                      # weighted score
        self.questions = self.load_questions(subject)
        self.history: List[Dict[str, Any]] = []  # list of {id, correct, difficulty}

    def load_questions(self, subject: str) -> List[Dict[str, Any]]:
        """
        Load questions from data/questions_<subject>.json
        """
        base = Path(__file__).resolve().parents[2]
        filepath = base / "data" / f"questions_{subject}.json"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # sort for stable progression: easy -> medium -> hard
        difficulty_order = {"easy": 0, "medium": 1, "hard": 2}
        data.sort(key=lambda q: difficulty_order.get(q.get("difficulty", "easy"), 0))
        return data

    def get_current_question(self) -> Dict[str, Any] | None:
        """
        Return the current question dictionary or None if quiz is over.
        """
        if 0 <= self.index < len(self.questions):
            return self.questions[self.index]
        return None

    def _score_for_difficulty(self, difficulty: str) -> int:
        if difficulty == "easy":
            return 1
        if difficulty == "medium":
            return 2
        if difficulty == "hard":
            return 3
        return 1

    def _record_history(self, correct: bool, difficulty: str, qid: int):
        self.history.append(
            {"question_id": qid, "correct": correct, "difficulty": difficulty}
        )

    def check_answer(self, chosen: str) -> Dict[str, Any]:
        """
        Check user answer, update score and history.
        Returns a dict with correctness and correct_answer.
        """
        q = self.get_current_question()
        if q is None:
            return {"correct": False, "correct_answer": None}

        correct_answer = q["answer"]
        difficulty = q.get("difficulty", "easy")
        is_correct = (chosen == correct_answer)

        if is_correct:
            self.score += self._score_for_difficulty(difficulty)

        self._record_history(is_correct, difficulty, q["id"])

        return {
            "correct": is_correct,
            "correct_answer": correct_answer,
            "difficulty": difficulty,
        }

    def next_question(self):
        """
        Simple progression for now: go to next index.
        (In Round 3 this is where ML-based adaptivity can hook in.)
        """
        self.index += 1

    def is_finished(self) -> bool:
        return self.index >= len(self.questions)

    def summary(self) -> Dict[str, Any]:
        """
        Return aggregated stats for analytics view.
        """
        total = len(self.history)
        correct = sum(1 for h in self.history if h["correct"])
        difficulty_counts: Dict[str, int] = {"easy": 0, "medium": 0, "hard": 0}
        difficulty_correct: Dict[str, int] = {"easy": 0, "medium": 0, "hard": 0}

        for h in self.history:
            d = h["difficulty"]
            difficulty_counts[d] += 1
            if h["correct"]:
                difficulty_correct[d] += 1

        accuracy_by_difficulty = {}
        for d in ["easy", "medium", "hard"]:
            c = difficulty_counts[d]
            if c > 0:
                accuracy_by_difficulty[d] = difficulty_correct[d] / c
            else:
                accuracy_by_difficulty[d] = None

        max_possible = total * 3  # treat all as hard for upper bound
        percentage = (self.score / max_possible) * 100 if max_possible > 0 else 0

        return {
            "total_answered": total,
            "correct_answered": correct,
            "score": self.score,
            "percentage": percentage,
            "difficulty_counts": difficulty_counts,
            "accuracy_by_difficulty": accuracy_by_difficulty,
        }

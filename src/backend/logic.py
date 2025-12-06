from pathlib import Path
import json
import time
from typing import List, Dict, Any, Optional


class QuizEngine:
    """
    Backend quiz engine for SignSense.

    Features:
    - Loads questions by subject from data/questions_<subject>.json
    - Kahoot-style scoring: base points + time bonus + streak bonus
    - Tracks per-question history (correct, time, points, difficulty)
    - Accessibility-aware scoring modifiers per mode:
        * Standard           -> balanced time + streak scoring
        * ADHD-Friendly      -> stronger streak rewards, softer penalty
        * Dyslexia-Friendly  -> removes time pressure, focuses on correctness
        * Autism-Friendly    -> no time component, consistent scoring
        * Deaf/ISL Mode      -> stable scoring, no time pressure
    """

    def __init__(self, mode: str, subject: str):
        self.mode: str = mode
        self.subject: str = subject

        self.questions: List[Dict[str, Any]] = self._load_questions(subject)
        self.index: int = 0

        # scoring + analytics
        self.score: int = 0
        self.history: List[Dict[str, Any]] = []
        self.streak: int = 0
        self.best_streak: int = 0
        self.current_start_time: Optional[float] = None  # when current question appeared

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _load_questions(self, subject: str) -> List[Dict[str, Any]]:
        """
        Load questions from the data folder and sort by difficulty.
        """
        base = Path(__file__).resolve().parents[2]
        filepath = base / "data" / f"questions_{subject}.json"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        difficulty_order = {"easy": 0, "medium": 1, "hard": 2}
        data.sort(key=lambda q: difficulty_order.get(q.get("difficulty", "easy"), 0))
        return data

    def _base_points_for_difficulty(self, difficulty: str) -> int:
        if difficulty == "easy":
            return 500
        if difficulty == "medium":
            return 700
        if difficulty == "hard":
            return 900
        return 500

    def _mode_modifiers(self) -> Dict[str, Any]:
        """
        Returns scoring modifiers depending on accessibility mode.
        """
        # Defaults: Standard
        mods = {
            "time_weight": 1.0,       # how much speed matters
            "streak_weight": 1.0,     # strength of streak bonus
            "min_fraction": 0.3,      # minimum fraction of base points
        }

        if self.mode == "ADHD-Friendly":
            # More rewarding streaks, less punishing for slower responses
            mods["time_weight"] = 0.8
            mods["streak_weight"] = 1.4
            mods["min_fraction"] = 0.5
        elif self.mode == "Dyslexia-Friendly":
            # Remove speed pressure almost completely
            mods["time_weight"] = 0.2
            mods["streak_weight"] = 1.0
            mods["min_fraction"] = 0.7
        elif self.mode == "Autism-Friendly":
            # Predictable, consistent scoring
            mods["time_weight"] = 0.0
            mods["streak_weight"] = 1.0
            mods["min_fraction"] = 0.8
        elif self.mode == "Deaf/ISL Mode":
            # Visual-first, no rush scoring
            mods["time_weight"] = 0.0
            mods["streak_weight"] = 1.2
            mods["min_fraction"] = 0.7

        return mods

    def _compute_points(
        self, difficulty: str, correct: bool, time_taken: Optional[float]
    ) -> int:
        """
        Compute points based on difficulty, correctness, time, and streak.
        Inspired by Kahoot scoring (base + time factor + streak).
        """
        if not correct:
            # Reset streak on wrong answer
            self.streak = 0
            return 0

        base = self._base_points_for_difficulty(difficulty)
        mods = self._mode_modifiers()

        # Time factor: map [0s, 30s+] to fraction [1.0, min_fraction]
        if time_taken is None:
            time_factor = 1.0
        else:
            capped = max(0.0, min(30.0, time_taken))
            # 0 seconds -> 1.0, 30 seconds -> 0.0
            raw_fraction = (30.0 - capped) / 30.0
            # blend with min_fraction based on time_weight
            min_frac = mods["min_fraction"]
            time_weight = mods["time_weight"]
            # if time_weight = 0 -> always 1.0
            effective_fraction = (1 - time_weight) * 1.0 + time_weight * (
                min_frac + (1.0 - min_frac) * raw_fraction
            )
            time_factor = max(min_frac, effective_fraction)

        # streak update
        self.streak += 1
        self.best_streak = max(self.best_streak, self.streak)

        streak_weight = mods["streak_weight"]
        streak_bonus = int(50 * (self.streak - 1) * streak_weight)

        points = int(base * time_factor) + streak_bonus
        return points

    # -------------------------------------------------------------------------
    # Public API used by app.py and UI
    # -------------------------------------------------------------------------

    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """
        Return the current question dict or None if finished.
        Starts the timer for this question on first access.
        """
        if self.index >= len(self.questions):
            return None

        if self.current_start_time is None:
            self.current_start_time = time.time()

        return self.questions[self.index]

    def check_answer(self, chosen: str) -> Dict[str, Any]:
        """
        Evaluate the chosen answer, update score + history, and
        return feedback dict: {correct, correct_answer, difficulty, points, time_taken}.
        """
        q = self.get_current_question()
        if q is None:
            return {
                "correct": False,
                "correct_answer": None,
                "difficulty": None,
                "points": 0,
                "time_taken": None,
            }

        correct_answer = q["answer"]
        difficulty = q.get("difficulty", "easy")

        # calculate reaction time
        if self.current_start_time is None:
            time_taken = None
        else:
            time_taken = max(0.0, time.time() - self.current_start_time)

        is_correct = chosen == correct_answer
        points = self._compute_points(difficulty, is_correct, time_taken)

        if is_correct:
            self.score += points

        # record history entry
        entry = {
            "question_id": q.get("id"),
            "difficulty": difficulty,
            "chosen": chosen,
            "correct_answer": correct_answer,
            "correct": is_correct,
            "time_taken": time_taken,
            "points_earned": points,
            "streak_after": self.streak,
        }
        self.history.append(entry)

        # after checking answer, stop timing; next question will start new timer
        self.current_start_time = None

        return {
            "correct": is_correct,
            "correct_answer": correct_answer,
            "difficulty": difficulty,
            "points": points,
            "time_taken": time_taken,
        }

    def next_question(self) -> None:
        """
        Advance to next question.
        """
        self.index += 1
        self.current_start_time = None  # reset timer; will be set when next question is shown

    def is_finished(self) -> bool:
        return self.index >= len(self.questions)

    # -------------------------------------------------------------------------
    # Summary & analytics
    # -------------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Aggregate stats for result screen & analytics.
        Returns at least:
          - total_answered
          - correct_answered
          - score
          - percentage
          - difficulty_counts
          - accuracy_by_difficulty
        plus extra fields for richer feedback.
        """
        total = len(self.history)
        correct = sum(1 for h in self.history if h["correct"])
        max_possible_base = sum(
            self._base_points_for_difficulty(h["difficulty"]) for h in self.history
        )
        max_possible = max_possible_base + 50 * max(0, total - 1)  # assume max streak bonus

        percentage = (self.score / max_possible * 100) if max_possible > 0 else 0.0

        difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
        difficulty_correct = {"easy": 0, "medium": 0, "hard": 0}
        times: List[float] = []

        for h in self.history:
            d = h["difficulty"]
            difficulty_counts[d] += 1
            if h["correct"]:
                difficulty_correct[d] += 1
            if h["time_taken"] is not None:
                times.append(h["time_taken"])

        accuracy_by_difficulty: Dict[str, Optional[float]] = {}
        for d in ["easy", "medium", "hard"]:
            c = difficulty_counts[d]
            accuracy_by_difficulty[d] = (
                difficulty_correct[d] / c if c > 0 else None
            )

        avg_time = sum(times) / len(times) if times else None

        accessibility_feedback = self._build_accessibility_feedback(
            percentage, avg_time
        )

        return {
            "total_answered": total,
            "correct_answered": correct,
            "score": self.score,
            "percentage": round(percentage, 1),
            "difficulty_counts": difficulty_counts,
            "accuracy_by_difficulty": accuracy_by_difficulty,
            "average_time": avg_time,
            "best_streak": self.best_streak,
            "mode": self.mode,
            "subject": self.subject,
            "accessibility_feedback": accessibility_feedback,
        }

    def _build_accessibility_feedback(
        self, percentage: float, avg_time: Optional[float]
    ) -> str:
        """
        Generate a short, mode-specific feedback string that the frontend
        can show as a "smart coach" message.
        """
        base_msg = f"Overall performance: {percentage:.1f}%."

        if self.mode == "ADHD-Friendly":
            if self.best_streak >= 3:
                return (
                    base_msg
                    + " Strong streaks detected – this learner responds well to burst-style question sets and rewards."
                )
            else:
                return (
                    base_msg
                    + " Consider shorter sessions with frequent breaks and higher streak rewards."
                )

        if self.mode == "Dyslexia-Friendly":
            if avg_time and avg_time > 15:
                return (
                    base_msg
                    + " Reading time is higher, which is expected; the system de-emphasised speed to prioritise comprehension."
                )
            else:
                return (
                    base_msg
                    + " Timing stayed comfortable; keep using overlays and fonts that feel easiest to read."
                )

        if self.mode == "Autism-Friendly":
            return (
                base_msg
                + " Consistent scoring without time pressure supports predictable learning – ideal for routine-building."
            )

        if self.mode == "Deaf/ISL Mode":
            return (
                base_msg
                + " Visual-first learning with ISL avatars can be expanded with richer sign sequences in later versions."
            )

        # Standard
        return (
            base_msg
            + " This is a balanced mode; try accessibility modes to see if performance or comfort improves further."
        )

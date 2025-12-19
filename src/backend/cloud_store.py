import os
import random
from typing import List, Dict

# -------------------------------
# EXISTING SCORE STORAGE
# -------------------------------
LOCAL_SCORES: Dict[str, List[Dict]] = {}

CLOUD_ENABLED = False
db = None

try:
    import firebase_admin  # type: ignore
    from firebase_admin import credentials, firestore  # type: ignore

    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path:
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        CLOUD_ENABLED = True
    else:
        CLOUD_ENABLED = False
except Exception:
    CLOUD_ENABLED = False
    db = None


def add_score(session_code: str, name: str, score: int, mode: str, subject: str) -> bool:
    record = {
        "name": name or "Anonymous",
        "score": int(score),
        "mode": mode,
        "subject": subject,
    }

    if CLOUD_ENABLED and db is not None:
        try:
            scores_ref = (
                db.collection("sessions")
                .document(session_code)
                .collection("scores")
            )
            scores_ref.add(record)
            return True
        except Exception:
            pass

    LOCAL_SCORES.setdefault(session_code, []).append(record)
    return False


def get_leaderboard(session_code: str) -> List[Dict]:
    records: List[Dict] = []

    if CLOUD_ENABLED and db is not None:
        try:
            scores_ref = (
                db.collection("sessions")
                .document(session_code)
                .collection("scores")
            )
            query = scores_ref.order_by(
                "score", direction=firestore.Query.DESCENDING
            ).limit(20)
            for doc in query.stream():
                data = doc.to_dict()
                if data:
                    records.append(data)
        except Exception:
            records = []

    if not records:
        records = LOCAL_SCORES.get(session_code, [])

    return sorted(records, key=lambda r: r.get("score", 0), reverse=True)


# ===============================
# NEW: CLASSROOM STORAGE
# ===============================

LOCAL_CLASSROOMS: Dict[str, Dict] = {}


def create_classroom() -> str:
    code = f"CLS-{random.randint(100,999)}"

    classroom = {
        "questions": [],
        "students": {},   # name -> {status, answers}
    }

    if CLOUD_ENABLED and db is not None:
        try:
            db.collection("classrooms").document(code).set(classroom)
        except Exception:
            LOCAL_CLASSROOMS[code] = classroom
    else:
        LOCAL_CLASSROOMS[code] = classroom

    return code


def join_classroom(code: str, student_name: str) -> bool:
    if not student_name:
        return False

    if CLOUD_ENABLED and db is not None:
        try:
            ref = db.collection("classrooms").document(code)
            if not ref.get().exists:
                return False
            ref.update({
                f"students.{student_name}": {
                    "status": "Joined",
                    "answers": {}
                }
            })
            return True
        except Exception:
            return False

    classroom = LOCAL_CLASSROOMS.get(code)
    if not classroom:
        return False

    classroom["students"][student_name] = {
        "status": "Joined",
        "answers": {}
    }
    return True


def add_classroom_question(code: str, question: str):
    if CLOUD_ENABLED and db is not None:
        try:
            ref = db.collection("classrooms").document(code)
            ref.update({
                "questions": firestore.ArrayUnion([question])
            })
            return
        except Exception:
            pass

    if code in LOCAL_CLASSROOMS:
        LOCAL_CLASSROOMS[code]["questions"].append(question)


def submit_classroom_answer(code: str, student_name: str, q_index: int, answer: str):
    if CLOUD_ENABLED and db is not None:
        try:
            ref = db.collection("classrooms").document(code)
            ref.update({
                f"students.{student_name}.answers.{q_index}": answer,
                f"students.{student_name}.status": "Answered"
            })
            return
        except Exception:
            pass

    classroom = LOCAL_CLASSROOMS.get(code)
    if classroom and student_name in classroom["students"]:
        classroom["students"][student_name]["answers"][q_index] = answer
        classroom["students"][student_name]["status"] = "Answered"


def get_classroom_state(code: str) -> Dict:
    if CLOUD_ENABLED and db is not None:
        try:
            doc = db.collection("classrooms").document(code).get()
            if doc.exists:
                return doc.to_dict() or {}
        except Exception:
            pass

    return LOCAL_CLASSROOMS.get(code, {})

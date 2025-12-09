import os
from typing import List, Dict

# Local in-memory fallback if Firebase is not configured
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
        # No credentials path set; run in local mode
        CLOUD_ENABLED = False
except Exception:
    # firebase_admin not installed or failed → stay in local mode
    CLOUD_ENABLED = False
    db = None


def add_score(session_code: str, name: str, score: int, mode: str, subject: str) -> bool:
    """
    Save score for a session. Returns True if saved to cloud, False if only local.
    Never raises an exception; always safe.
    """
    record = {
        "name": name or "Anonymous",
        "score": int(score),
        "mode": mode,
        "subject": subject,
    }

    # Try Firebase first
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
            # Fall through to local
            pass

    # Local in-memory fallback
    LOCAL_SCORES.setdefault(session_code, []).append(record)
    return False


def get_leaderboard(session_code: str) -> List[Dict]:
    """
    Return a list of score records sorted by score desc.
    Uses cloud if available, otherwise local fallback.
    """
    records: List[Dict] = []

    # Try Firebase
    if CLOUD_ENABLED and db is not None:
        try:
            from firebase_admin import firestore  # type: ignore

            scores_ref = (
                db.collection("sessions")
                .document(session_code)
                .collection("scores")
            )
            query = scores_ref.order_by(
                "score", direction=firestore.Query.DESCENDING
            ).limit(20)
            docs = query.stream()
            for doc in docs:
                data = doc.to_dict()
                if data:
                    records.append(data)
        except Exception:
            records = []

    # Fallback to local
    if not records:
        records = LOCAL_SCORES.get(session_code, [])

    records = sorted(records, key=lambda r: r.get("score", 0), reverse=True)
    return records

"""
models/result.py
────────────────
Result model – handles all DB operations for the 'results' collection.

Collection schema:
  {
    _id:        ObjectId   (auto by MongoDB)
    user_id:    str        (ObjectId string of the user)
    user_name:  str        (denormalised for easy display)
    score:      int        (number of correct answers)
    total:      int        (total number of questions)
    percentage: float      (score/total * 100)
    answers:    list       (list of {question_id, selected, correct, is_correct})
    date:       datetime
  }
"""

from datetime import datetime, timezone
from db import get_db


def save_result(user_id: str, user_name: str, score: int,
                total: int, answers: list) -> dict:
    """
    Save a quiz result to the database and return the saved document.
    """
    db = get_db()

    percentage = round((score / total) * 100, 1) if total > 0 else 0

    result_doc = {
        "user_id":    user_id,
        "user_name":  user_name,
        "score":      score,
        "total":      total,
        "percentage": percentage,
        "answers":    answers,
        "date":       datetime.now(timezone.utc),
    }

    inserted = db.results.insert_one(result_doc)
    result_doc["_id"] = str(inserted.inserted_id)
    return result_doc


def get_user_results(user_id: str) -> list:
    """
    Fetch all past quiz results for a given user, newest first.
    Returns a list of result dicts (with ObjectId converted to str).
    """
    db = get_db()
    cursor = db.results.find(
        {"user_id": user_id},
        sort=[("date", -1)]
    )
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


def get_leaderboard(limit: int = 10) -> list:
    """
    Return the top N scores across all users (for a leaderboard page).
    """
    db = get_db()
    cursor = db.results.find(
        {},
        sort=[("percentage", -1)],
        limit=limit
    )
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results

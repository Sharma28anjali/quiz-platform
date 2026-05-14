"""
utils/score_calculator.py
─────────────────────────
Pure-function utilities for scoring a quiz submission.
Keeping this logic separate makes it easy to unit-test.
"""

import json
import os

# Path to the question bank
QUESTIONS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "questions.json"
)


def load_questions() -> list:
    """Load and return the full question list from the JSON file."""
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_score(user_answers: dict) -> dict:
    """
    Compare user answers against the correct answers from the JSON bank.

    Parameters
    ----------
    user_answers : dict
        A mapping of  { question_id (str) : selected_option (str) }
        Example: { "1": "JavaScript", "2": "Stack", ... }

    Returns
    -------
    dict with keys:
        score      – number of correct answers
        total      – total questions attempted
        percentage – rounded percentage score
        breakdown  – list of per-question dicts for the result page
    """
    questions = load_questions()

    # Build a fast lookup: id → question dict
    question_map = {str(q["id"]): q for q in questions}

    score = 0
    breakdown = []

    for q_id, selected in user_answers.items():
        question = question_map.get(str(q_id))
        if not question:
            continue  # Skip unknown question IDs

        correct = question["correct_answer"]
        is_correct = (selected.strip() == correct.strip())

        if is_correct:
            score += 1

        breakdown.append({
            "question_id":  int(q_id),
            "question":     question["question"],
            "selected":     selected,
            "correct":      correct,
            "is_correct":   is_correct,
            "category":     question.get("category", "General"),
        })

    total = len(breakdown)
    percentage = round((score / total) * 100, 1) if total > 0 else 0

    return {
        "score":      score,
        "total":      total,
        "percentage": percentage,
        "breakdown":  breakdown,
    }


def get_grade(percentage: float) -> dict:
    """
    Convert a percentage score into a letter grade + message.
    """
    if percentage >= 90:
        return {"grade": "A+", "message": "Outstanding! 🏆", "color": "#22c55e"}
    elif percentage >= 80:
        return {"grade": "A",  "message": "Excellent work! 🎉", "color": "#84cc16"}
    elif percentage >= 70:
        return {"grade": "B",  "message": "Good job! 👍",      "color": "#eab308"}
    elif percentage >= 60:
        return {"grade": "C",  "message": "Not bad, keep going! 📚", "color": "#f97316"}
    else:
        return {"grade": "F",  "message": "Keep practising! 💪", "color": "#ef4444"}

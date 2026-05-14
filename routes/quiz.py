"""
routes/quiz.py
──────────────
Quiz Blueprint – handles:
  GET  /dashboard            – user home (requires login)
  GET  /quiz                 – display quiz questions
  POST /quiz/submit          – evaluate answers, save result
  GET  /result/<result_id>   – show result page
  GET  /history              – user's past results
"""

import json
from functools import wraps
from flask import (
    Blueprint, render_template, session,
    redirect, url_for, request, flash
)
from utils.score_calculator import load_questions, calculate_score, get_grade
from models.result import save_result, get_user_results

quiz_bp = Blueprint("quiz", __name__)


# ── Login-required decorator ──────────────────────────────────────────────────

def login_required(f):
    """Redirect to login page if user is not in session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


# ── Home / landing ────────────────────────────────────────────────────────────

@quiz_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("quiz.dashboard"))
    return redirect(url_for("auth.login"))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@quiz_bp.route("/dashboard")
@login_required
def dashboard():
    user_name    = session.get("user_name")
    past_results = get_user_results(session["user_id"])

    # Stats for the dashboard cards
    stats = {
        "attempts":    len(past_results),
        "best_score":  max((r["percentage"] for r in past_results), default=0),
        "avg_score":   round(
            sum(r["percentage"] for r in past_results) / len(past_results), 1
        ) if past_results else 0,
    }

    return render_template(
        "dashboard.html",
        user_name=user_name,
        past_results=past_results[:5],   # Show last 5 on dashboard
        stats=stats,
        total_questions=len(load_questions()),
    )


# ── Quiz page ─────────────────────────────────────────────────────────────────

@quiz_bp.route("/quiz")
@login_required
def quiz():
    questions = load_questions()
    return render_template("quiz.html", questions=questions,
                           total=len(questions))


# ── Submit answers ────────────────────────────────────────────────────────────

@quiz_bp.route("/quiz/submit", methods=["POST"])
@login_required
def submit_quiz():
    """
    Accepts form data: answer_<question_id> = selected_option
    e.g.  answer_1=JavaScript, answer_2=Stack …
    """
    questions = load_questions()

    # Extract answers from form: { "1": "JavaScript", "2": "Stack", … }
    user_answers = {}
    for question in questions:
        key = f"answer_{question['id']}"
        value = request.form.get(key)
        if value:
            user_answers[str(question["id"])] = value

    if not user_answers:
        flash("No answers submitted!", "error")
        return redirect(url_for("quiz.quiz"))

    # Score calculation (pure function – easy to test)
    result = calculate_score(user_answers)
    grade  = get_grade(result["percentage"])

    # Save to MongoDB
    saved = save_result(
        user_id   = session["user_id"],
        user_name = session["user_name"],
        score     = result["score"],
        total     = result["total"],
        answers   = result["breakdown"],
    )

    # Pass everything to result template
    return render_template(
        "result.html",
        score      = result["score"],
        total      = result["total"],
        percentage = result["percentage"],
        grade      = grade,
        breakdown  = result["breakdown"],
        result_id  = saved["_id"],
        user_name  = session["user_name"],
    )


# ── History ───────────────────────────────────────────────────────────────────

@quiz_bp.route("/history")
@login_required
def history():
    results = get_user_results(session["user_id"])
    return render_template("history.html",
                           results=results,
                           user_name=session.get("user_name"))

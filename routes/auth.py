"""
routes/auth.py
──────────────
Authentication Blueprint – handles:
  POST /auth/register  – create a new account
  POST /auth/login     – verify credentials, set session
  GET  /auth/logout    – clear session
"""

from flask import (
    Blueprint, request, session,
    redirect, url_for, render_template, flash
)
from models.user import create_user, find_user_by_email, verify_password

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ── Register ──────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # If already logged in, go to dashboard
    if "user_id" in session:
        return redirect(url_for("quiz.dashboard"))

    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        # ── Validation ────────────────────────────────────────────────────────
        if not all([name, email, password, confirm]):
            flash("All fields are required.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        # ── Create user ───────────────────────────────────────────────────────
        user = create_user(name, email, password)
        if user is None:
            flash("An account with that email already exists.", "error")
            return render_template("register.html")

        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("quiz.dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        user = find_user_by_email(email)

        if user is None or not verify_password(password, user["password"]):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        # ── Set session ───────────────────────────────────────────────────────
        session["user_id"]   = str(user["_id"])
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("quiz.dashboard"))

    return render_template("login.html")


# ── Logout ────────────────────────────────────────────────────────────────────

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

"""
app.py
──────
Flask application entry point.

How it works:
  1. Load environment variables from .env
  2. Create the Flask app
  3. Register the two Blueprints (auth + quiz)
  4. Run the dev server (or let gunicorn use `app`)
"""

import os
from flask import Flask
from dotenv import load_dotenv

# Load .env BEFORE any other import that reads env vars
load_dotenv()


def create_app() -> Flask:
    """Application factory – returns a configured Flask instance."""
    app = Flask(__name__)

    # ── Secret key (required for sessions) ────────────────────────────────────
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # ── Session cookie settings ───────────────────────────────────────────────
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # ── Register Blueprints ───────────────────────────────────────────────────
    from routes.auth import auth_bp
    from routes.quiz import quiz_bp

    app.register_blueprint(auth_bp)   # /auth/login, /auth/register, /auth/logout
    app.register_blueprint(quiz_bp)   # /, /dashboard, /quiz, /quiz/submit, /history

    return app


# ── Run directly (development only) ──────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)

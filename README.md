# QuizMaster – Online Quiz Platform

A full-stack quiz platform built with Flask, MongoDB, and HTML/CSS/JS.

---

## Project Structure

quiz-platform/
├── app.py                  # Flask entry point
├── db.py                   # MongoDB connection
├── requirements.txt
├── .env                    # Environment variables (never commit)
├── data/questions.json     # Question bank
├── routes/
│   ├── auth.py             # Login, Register, Logout
│   └── quiz.py             # Dashboard, Quiz, Submit, History
├── models/
│   ├── user.py             # User DB operations
│   └── result.py           # Result DB operations
├── utils/
│   └── score_calculator.py # Scoring logic
└── templates/              # HTML pages

---

## Local Setup

1. Create virtual environment
   python -m venv venv
   venv\Scripts\activate

2. Install dependencies
   pip install -r requirements.txt

3. Create .env file and fill in values
   SECRET_KEY=any-random-string
   MONGO_URI=mongodb://localhost:27017/quizdb
   JWT_SECRET=any-random-string
   FLASK_ENV=development

4. Run
   python app.py
   Open: http://localhost:5000

---

## Adding Questions

Edit data/questions.json:

{
  "id": 11,
  "question": "Your question?",
  "options": ["A", "B", "C", "D"],
  "correct_answer": "A",
  "category": "Category"
}

Note: correct_answer must exactly match one of the options.

---

## Tech Stack

Flask · MongoDB · bcrypt · HTML/CSS/JS
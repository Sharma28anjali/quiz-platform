# QuizMaster – Online Quiz Platform

A full-stack quiz/test platform built with **Flask**, **MongoDB**, and vanilla **HTML/CSS/JS**.

---

## 📁 Project Structure

```
quiz-platform/
│
├── app.py                     # Flask entry point & app factory
├── db.py                      # MongoDB connection (singleton)
├── requirements.txt           # Python dependencies
├── Procfile                   # For Render/Heroku deployment
├── render.yaml                # Render auto-deploy config
├── .env.example               # Environment variable template
├── .gitignore
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                # /auth/register, /auth/login, /auth/logout
│   └── quiz.py                # /dashboard, /quiz, /quiz/submit, /history
│
├── models/
│   ├── __init__.py
│   ├── user.py                # User CRUD + password hashing
│   └── result.py              # Quiz result CRUD
│
├── utils/
│   ├── __init__.py
│   └── score_calculator.py    # Pure scoring logic (easy to test)
│
├── data/
│   └── questions.json         # Question bank (edit to add questions)
│
└── templates/
    ├── base.html              # Shared layout, nav, flash messages
    ├── login.html             # Login form
    ├── register.html          # Registration form
    ├── dashboard.html         # User home + stats
    ├── quiz.html              # Quiz interface with timer
    ├── result.html            # Score + answer breakdown
    └── history.html           # Past attempts
```

---

## ⚙️ How Everything Works

### 1. Authentication Flow
```
User visits /  →  redirected to /auth/login
POST /auth/login  →  verify email+password (bcrypt)
                  →  set session cookie
                  →  redirect to /dashboard
```
- Passwords are **hashed with bcrypt** (never stored in plain text)
- **Flask sessions** (server-side signed cookies) track login state
- `login_required` decorator protects all quiz routes

### 2. Quiz Flow
```
GET  /quiz          →  load questions from data/questions.json
User selects answers (no page reload – JS manages question navigation)
POST /quiz/submit   →  { answer_1: "...", answer_2: "...", ... }
                    →  score_calculator.calculate_score()
                    →  save to MongoDB results collection
                    →  render result.html
```

### 3. Scoring Logic (`utils/score_calculator.py`)
Pure function – takes `{ question_id: selected_answer }` dict, compares
against the JSON file, returns `{ score, total, percentage, breakdown }`.

### 4. MongoDB Collections

**users**
```json
{
  "_id": "ObjectId",
  "name": "Alex",
  "email": "alex@example.com",
  "password": "<bcrypt hash>",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**results**
```json
{
  "_id": "ObjectId",
  "user_id": "...",
  "user_name": "Alex",
  "score": 8,
  "total": 10,
  "percentage": 80.0,
  "answers": [...],
  "date": "2024-01-01T00:00:00Z"
}
```

---

## Local Setup (Step-by-Step)

### Step 1 – Clone and create virtual environment
```bash
git clone https://github.com/yourusername/quiz-platform.git
cd quiz-platform

python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### Step 2 – Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 – Set up MongoDB Atlas
1. Go to [https://cloud.mongodb.com](https://cloud.mongodb.com) and create a free account
2. Create a **free M0 cluster**
3. Under **Database Access**, create a user with read/write permissions
4. Under **Network Access**, add `0.0.0.0/0` (allow all IPs) for development
5. Click **Connect → Drivers** and copy your connection string:
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/quizdb?retryWrites=true&w=majority
   ```

### Step 4 – Configure environment
```bash
cp .env.example .env
```
Edit `.env` and fill in:
```
SECRET_KEY=any-random-string-here
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/quizdb?...
JWT_SECRET=another-random-string
```

### Step 5 – Run the app
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000)

---

## Adding More Questions

Edit `data/questions.json`. Each question follows this format:
```json
{
  "id": 11,
  "question": "Your question text here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": "Option A",
  "category": "Your Category"
}
```
**Rules:**
- `id` must be unique
- `correct_answer` must exactly match one of the `options`
- No restart needed – questions reload on each quiz start

---

## Deploy to Render (Free Tier)

### Step 1 – Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/quiz-platform.git
git push -u origin main
```

### Step 2 – Create a Render account
Go to [https://render.com](https://render.com) and sign up.

### Step 3 – New Web Service
1. Click **New → Web Service**
2. Connect your GitHub repo
3. Render detects `render.yaml` automatically, OR configure manually:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Python version:** 3.11

### Step 4 – Set Environment Variables
In the Render dashboard → Environment tab, add:
```
SECRET_KEY     = (generate a random string)
MONGO_URI      = mongodb+srv://...  (your Atlas connection string)
JWT_SECRET     = (generate a random string)
FLASK_ENV      = production
```

### Step 5 – Deploy
Click **Deploy**. Your app will be live at `https://quizmaster.onrender.com`.

---

## Deploy to VPS (Ubuntu via SSH)

```bash
# SSH into your server
ssh user@your-server-ip

# Install Python & nginx
sudo apt update && sudo apt install python3-pip python3-venv nginx -y

# Clone your repo
git clone https://github.com/yourusername/quiz-platform.git
cd quiz-platform

# Virtual environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Create .env
nano .env  # paste your variables

# Test it works
gunicorn app:app --bind 0.0.0.0:5000

# Create a systemd service for auto-restart
sudo nano /etc/systemd/system/quizmaster.service
```

Paste this into the service file:
```ini
[Unit]
Description=QuizMaster Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/quiz-platform
Environment="PATH=/home/ubuntu/quiz-platform/venv/bin"
ExecStart=/home/ubuntu/quiz-platform/venv/bin/gunicorn app:app --bind 0.0.0.0:5000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start quizmaster
sudo systemctl enable quizmaster

# Configure nginx as reverse proxy
sudo nano /etc/nginx/sites-available/quizmaster
```

Paste:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/quizmaster /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

Your app is live! Add a free SSL cert with:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 🔐 Security Notes

| Feature | Implementation |
|---------|---------------|
| Password storage | bcrypt with auto-generated salt |
| Session protection | Flask signed session cookies |
| Secret key | Environment variable (never committed) |
| MongoDB URI | Environment variable (never committed) |
| Input validation | Server-side in routes before DB calls |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web framework |
| `pymongo[srv]` | MongoDB driver |
| `bcrypt` | Password hashing |
| `python-dotenv` | Load `.env` file |
| `gunicorn` | Production WSGI server |
| `dnspython` | Required for `mongodb+srv://` URIs |
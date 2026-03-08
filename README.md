# Bhavya Chaudhary — Portfolio Website

A modern, minimal personal portfolio built with Flask (backend) and vanilla HTML/CSS/JS (frontend).

## Features
- Animated particle canvas background
- Smooth scroll-reveal animations
- Responsive (mobile + desktop)
- Working contact form with email notifications
- Rate-limited API (5 messages/min per IP)
- Projects API endpoint (`/api/projects`)
- Full pytest test suite
- Docker ready

## Tech Stack
`Python` `Flask` `HTML5` `CSS3` `JavaScript` `Docker` `Gunicorn`

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill .env
cp .env.example .env

# Run dev server
python app.py
# → http://localhost:5000
```

### Docker
```bash
docker build -t portfolio .
docker run -p 5000:5000 --env-file .env portfolio
```

## Contact Form Setup (Email)
1. Enable 2FA on your Gmail account
2. Go to: Google Account → Security → App Passwords
3. Create a new app password
4. Add to `.env`: `SMTP_USER`, `SMTP_PASS`, `OWNER_EMAIL`

If SMTP is not configured, messages are logged to console (no email sent).

## Run Tests
```bash
pytest --cov=. --cov-report=term-missing
```

## Deploy to Render (Free)
1. Push repo to GitHub
2. New Web Service on render.com → connect repo
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app`
5. Add env vars in Render dashboard

## Project Structure
```
portfolio/
├── app.py              # Flask backend
├── templates/
│   └── index.html      # Full frontend (single file)
├── static/             # CSS, JS, images (optional)
├── test_app.py         # pytest tests
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

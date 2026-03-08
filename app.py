from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re
import logging
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Rate limiter — prevent spam
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USER     = os.getenv("SMTP_USER", "")        # your Gmail
SMTP_PASS     = os.getenv("SMTP_PASS", "")        # app password
OWNER_EMAIL   = os.getenv("OWNER_EMAIL", "bhavya09chaudhary@gmail.com")
PORTFOLIO_URL = os.getenv("PORTFOLIO_URL", "http://localhost:5000")


# ── Routes ────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


@app.route("/api/contact", methods=["POST"])
@limiter.limit("5 per minute")
def contact():
    """Handle contact form submission."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name    = (data.get("name") or "").strip()
    email   = (data.get("email") or "").strip()
    subject = (data.get("subject") or "Portfolio Contact").strip()
    message = (data.get("message") or "").strip()

    # ── Validation ────────────────────────────────────────────
    errors = []
    if not name or len(name) < 2:
        errors.append("Name must be at least 2 characters.")
    if not email or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        errors.append("A valid email address is required.")
    if not message or len(message) < 10:
        errors.append("Message must be at least 10 characters.")
    if len(name) > 100 or len(email) > 200 or len(message) > 5000:
        errors.append("Input too long.")

    if errors:
        return jsonify({"error": " ".join(errors)}), 400

    logger.info(f"Contact form: from={email}, subject={subject}")

    # ── Send email (if configured) ────────────────────────────
    if SMTP_USER and SMTP_PASS:
        try:
            _send_email(name, email, subject, message)
            logger.info(f"Email sent successfully from {email}")
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            # Still return success to user — log the message server-side
    else:
        logger.info(f"[NO SMTP] Contact from {name} <{email}>: {message[:80]}...")

    return jsonify({"success": True, "message": "Message received!"}), 200


def _send_email(name: str, sender_email: str, subject: str, message: str):
    """Send notification email to portfolio owner."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Portfolio] {subject} — from {name}"
    msg["From"]    = SMTP_USER
    msg["To"]      = OWNER_EMAIL
    msg["Reply-To"] = sender_email

    html_body = f"""
    <html><body style="font-family:monospace;background:#0D0D0D;color:#E8EBF0;padding:2rem;">
    <div style="max-width:560px;margin:0 auto;border:1px solid #2A3340;padding:2rem;">
      <h2 style="color:#C8A96E;font-size:1.2rem;margin-bottom:1rem;">New Portfolio Contact</h2>
      <table style="width:100%;border-collapse:collapse;">
        <tr><td style="color:#7A8A9A;padding:0.4rem 0;width:80px;">Name</td>
            <td style="color:#E8EBF0;">{name}</td></tr>
        <tr><td style="color:#7A8A9A;padding:0.4rem 0;">Email</td>
            <td><a href="mailto:{sender_email}" style="color:#C8A96E;">{sender_email}</a></td></tr>
        <tr><td style="color:#7A8A9A;padding:0.4rem 0;">Subject</td>
            <td style="color:#E8EBF0;">{subject}</td></tr>
      </table>
      <hr style="border:none;border-top:1px solid #2A3340;margin:1.2rem 0;" />
      <p style="color:#7A8A9A;font-size:0.85rem;margin-bottom:0.5rem;">Message:</p>
      <p style="color:#E8EBF0;line-height:1.7;">{message.replace(chr(10), '<br>')}</p>
      <hr style="border:none;border-top:1px solid #2A3340;margin:1.2rem 0;" />
      <p style="color:#3A4A5A;font-size:0.75rem;">{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
    </div></body></html>
    """
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, OWNER_EMAIL, msg.as_string())


@app.route("/api/projects")
def projects():
    """Return projects data as JSON (useful for any future dynamic rendering)."""
    data = [
        {
            "id": 1, "num": "01",
            "title": "URL Shortener API",
            "stack": ["FastAPI", "PostgreSQL", "Redis", "Docker", "GitHub Actions"],
            "bullets": [
                "Production-grade REST API with custom slugs, click tracking, and auto-link expiration.",
                "Redis caching reducing database load by ~80% under concurrent requests.",
                "CI/CD via GitHub Actions with automated pytest coverage on every push."
            ],
            "github": "https://github.com/bhavya09chaudhary/url-shortener"
        },
        {
            "id": 2, "num": "02",
            "title": "Real-Time Weather ETL Pipeline",
            "stack": ["Apache Airflow", "PostgreSQL", "pandas", "Docker"],
            "bullets": [
                "Airflow DAG ingesting hourly weather data, transforming with pandas, loading to PostgreSQL.",
                "Automated data quality checks at each pipeline stage.",
                "Idempotent incremental loads preventing duplicate ingestion."
            ],
            "github": "https://github.com/bhavya09chaudhary/weather-etl"
        },
        {
            "id": 3, "num": "03",
            "title": "Expense Tracker REST API",
            "stack": ["FastAPI", "JWT Auth", "SQLAlchemy", "pytest", "Docker"],
            "bullets": [
                "Full-CRUD API with JWT authentication and per-user data isolation.",
                "40+ tests via pytest, 85%+ code coverage, Pydantic validation.",
                "Deployed on AWS Lambda with environment-based configuration."
            ],
            "github": "https://github.com/bhavya09chaudhary/expense-tracker"
        },
        {
            "id": 4, "num": "04",
            "title": "ML Spam Email Classifier",
            "stack": ["scikit-learn", "Flask", "TF-IDF", "Docker"],
            "bullets": [
                "Naive Bayes + Logistic Regression ensemble achieving 95%+ accuracy.",
                "Flask REST API returning real-time spam probability scores.",
                "Reusable scikit-learn Pipeline with joblib model versioning."
            ],
            "github": "https://github.com/bhavya09chaudhary/spam-classifier"
        },
    ]
    return jsonify(data)


# ── Error handlers ────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(429)
def rate_limited(e):
    return jsonify({"error": "Too many requests. Please slow down."}), 429

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "production") == "development"
    logger.info(f"Starting portfolio server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)

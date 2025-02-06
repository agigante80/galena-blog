import openai
import os
import re
import pandas as pd
from datetime import datetime
import random
import logging
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='script.log', filemode='a')

# OpenAI API Key (stored in GitHub Secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.error("❌ ERROR: OPENAI_API_KEY is missing! Please set it as an environment variable.")
    raise ValueError("❌ ERROR: OPENAI_API_KEY is missing! Please set it as an environment variable.")
else:
    logging.info("✅ OPENAI_API_KEY successfully loaded.")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Email for notifications
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # App password for email sending
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")  # Recipient for failure notifications
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
BLOG_URL = os.getenv("BLOG_URL")  # Base URL for the blog
CSV_FILE = "articles_log.csv"
TOPIC_FILE = "topics.txt"
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")  # GitHub repository URL for editing topics

# OpenAI Client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# List of fallback topics
TRENDING_TOPICS = [
    "The Importance of Galena in Mining and Jewelry",
    "The Role of Precious Metals in Technology",
    "Sustainable Mining Practices",
    "The History of Gemstone Trade",
    "How Minerals Impact Global Economies",
    "The Science Behind Gemstone Formation",
    "The Future of Mining Technology",
    "Cultural Significance of Precious Stones",
    "How Jewelry Trends Evolve Over Time",
    "The Environmental Impact of Gemstone Mining"
]

def send_email_notification(subject, body):
    """Sends an email notification."""
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(body, "html"))
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        logging.info("Notification email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email notification: {e}")

# Rest of the script remains unchanged...

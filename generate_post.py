import openai
import os
import re
import platform
import psutil
import socket
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
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Your email for notifications
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # App password for email sending
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")  # Where to send failure notifications
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
BLOG_URL = os.getenv("BLOG_URL")  # Base URL for the blog
CSV_FILE = "articles_log.csv"
TOPIC_FILE = "topics.txt"
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")  # GitHub repository URL where topics.txt is stored

# Set up OpenAI API key
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# List of trending topics for automatic generation
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

def send_manual_topics_exhausted_email():
    """Sends an email notification when the manual topics list is empty."""
    topic_edit_link = f"{GITHUB_REPO_URL}/edit/main/{TOPIC_FILE}" if GITHUB_REPO_URL else "(Update manually in repository)"
    
    subject = "⚠️ Manual Topics List Exhausted"
    body = f"""
    <html>
    <body>
        <h2 style='color: red;'>⚠️ Manual Topics List Exhausted ⚠️</h2>
        <p>All manual topics have been used. The script is now selecting trending topics automatically.</p>
        <p>Please update the <strong>topics.txt</strong> file if you want to prioritize manual topics.</p>
        <p><a href='{topic_edit_link}' target='_blank'>📄 Click here to update topics.txt</a></p>
        <hr>
        <p>This is an automated message from your AI Blog System.</p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(body, "html"))
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        logging.info("Manual topics exhausted email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send manual topics exhausted email: {e}")

def get_manual_topic():
    """Fetches a topic from the manual topics file and removes it after use."""
    if os.path.exists(TOPIC_FILE):
        with open(TOPIC_FILE, "r", encoding="utf-8") as file:
            topics = file.readlines()
        if topics:
            topic = topics[0].strip()
            with open(TOPIC_FILE, "w", encoding="utf-8") as file:
                file.writelines(topics[1:])  # Remove the used topic
            if len(topics) == 1:
                send_manual_topics_exhausted_email()
            return topic, "Manual"
    return None, "Automatic"

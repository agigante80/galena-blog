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

print("✅ Script started...")

# OpenAI API Key (stored in GitHub Secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.error("❌ ERROR: OPENAI_API_KEY is missing! Please set it as an environment variable.")
    print("❌ ERROR: OPENAI_API_KEY is missing! Please set it as an environment variable.")
    raise ValueError("❌ ERROR: OPENAI_API_KEY is missing! Please set it as an environment variable.")
else:
    logging.info("✅ OPENAI_API_KEY successfully loaded.")
    print("✅ OPENAI_API_KEY successfully loaded.")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Email for notifications
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # App password for email sending
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")  # Recipient for failure notifications
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
BLOG_URL = os.getenv("BLOG_URL")  # Base URL for the blog
CSV_FILE = "articles_log.csv"
TOPIC_FILE = "topics.txt"
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")  # GitHub repository URL for editing topics
POSTS_DIR = "_posts"

print("🔍 Checking other environment variables...")
print(f"EMAIL_ADDRESS: {EMAIL_ADDRESS}")
print(f"RECIPIENT_EMAIL: {RECIPIENT_EMAIL}")
print(f"SMTP_SERVER: {SMTP_SERVER}")
print(f"SMTP_PORT: {SMTP_PORT}")
print(f"BLOG_URL: {BLOG_URL}")
print(f"GITHUB_REPO_URL: {GITHUB_REPO_URL}")

print("🔄 Initializing OpenAI client...")
client = openai.OpenAI(api_key=OPENAI_API_KEY)
print("✅ OpenAI client initialized successfully.")

# Ensure the posts directory exists
if not os.path.exists(POSTS_DIR):
    os.makedirs(POSTS_DIR)
    print(f"✅ Ensured directory exists: {POSTS_DIR}")

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
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not RECIPIENT_EMAIL:
        print("⚠️ Email credentials are missing. Skipping email notification.")
        logging.warning("⚠️ Email credentials are missing. Skipping email notification.")
        return
    
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

def test_openai_api():
    """Tests OpenAI API connection before making actual requests."""
    try:
        response = client.models.list()
        print("✅ OpenAI API is working.")
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        logging.error(f"❌ OpenAI API error: {e}")
        raise

def generate_blog_post():
    """Generates and saves a blog post."""
    try:
        topic = random.choice(TRENDING_TOPICS)
        filename = f"{datetime.now().strftime('%Y-%m-%d')}-{topic.replace(' ', '-').lower()}.md"
        file_path = os.path.join(POSTS_DIR, filename)
        
        # Simulate AI-generated content
        article_content = f"# {topic}\n\nThis is an AI-generated article about {topic}."
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(article_content)
        
        logging.info(f"✅ Blog post saved to {file_path}")
        print(f"✅ Blog post saved to {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"❌ Failed to generate blog post: {e}")
        print(f"❌ Failed to generate blog post: {e}")
        return None

def main():
    """Main execution function."""
    logging.info("🔄 Running main() function...")
    print("🚀 Running main script logic...")
    
    test_openai_api()
    
    post_path = generate_blog_post()
    if not post_path:
        error_msg = "⚠️ No new blog post was generated. Please check the logs."
        logging.warning(error_msg)
        print(error_msg)
        send_email_notification("⚠️ Blog Post Generation Failed", error_msg)
    else:
        print("✅ Main script logic completed.")

if __name__ == "__main__":
    main()

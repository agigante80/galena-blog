import openai
import os
import re
import pandas as pd
from datetime import datetime
import random
import logging
import time
import requests

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

# Telegram API Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BLOG_URL = os.getenv("BLOG_URL")  # Base URL for the blog
CSV_FILE = "articles_log.csv"
TOPIC_FILE = "topics.txt"
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")  # GitHub repository URL for editing topics
POSTS_DIR = "_posts"

print("🔍 Checking other environment variables...")
print(f"BLOG_URL: {BLOG_URL}")
print(f"GITHUB_REPO_URL: {GITHUB_REPO_URL}")

print("🔄 Initializing OpenAI client...")
client = openai.OpenAI(api_key=OPENAI_API_KEY)
print("✅ OpenAI client initialized successfully.")

# Ensure the posts directory exists
if not os.path.exists(POSTS_DIR):
    os.makedirs(POSTS_DIR)
    print(f"✅ Ensured directory exists: {POSTS_DIR}")

def initialize_csv():
    """Creates the CSV file and populates it with existing blog posts if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        logging.info("📂 CSV file not found. Creating a new one and scanning existing posts...")
        print("📂 CSV file not found. Creating a new one and scanning existing posts...")
        
        entries = []
        for filename in os.listdir(POSTS_DIR):
            if filename.endswith(".md"):
                date = filename.split("-")[0]
                title = filename.replace(".md", "").replace("-", " ")
                post_url = f"{BLOG_URL}/{filename}" if BLOG_URL else "Unknown"
                entries.append([date, title, "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", post_url])
        
        df = pd.DataFrame(entries, columns=["Date", "Title", "Summary", "Word Count", "Topic", "Topic Source", "Execution Time (seconds)", "Post URL"])
        df.to_csv(CSV_FILE, index=False)
        logging.info("✅ CSV file initialized with existing posts.")
        print("✅ CSV file initialized with existing posts.")

def send_telegram_notification(message):
    """Sends a Telegram notification."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials are missing. Skipping Telegram notification.")
        logging.warning("⚠️ Telegram credentials are missing. Skipping Telegram notification.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logging.info("✅ Telegram notification sent successfully.")
        else:
            logging.error(f"⚠️ Failed to send Telegram notification: {response.text}")
    except Exception as e:
        logging.error(f"❌ Telegram notification error: {e}")

def main():
    """Main execution function."""
    logging.info("🔄 Running main() function...")
    print("🚀 Running main script logic...")
    
    initialize_csv()
    
    post_path = generate_blog_post()
    if not post_path:
        print("⚠️ No new blog post was generated. Check logs.")
    else:
        print("✅ Main script logic completed.")

if __name__ == "__main__":
    main()

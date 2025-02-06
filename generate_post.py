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

def update_csv_log(title, summary, word_count, topic, topic_source, execution_time, post_url):
    """Adds a new entry to the CSV log file."""
    new_entry = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), title, summary, word_count, topic, topic_source, execution_time, post_url]],
                             columns=["Date", "Title", "Summary", "Word Count", "Topic", "Topic Source", "Execution Time (seconds)", "Post URL"])
    if not os.path.exists(CSV_FILE):
        new_entry.to_csv(CSV_FILE, index=False)
    else:
        new_entry.to_csv(CSV_FILE, mode='a', header=False, index=False)
    print(f"✅ Added to CSV log: {title}")
    logging.info(f"✅ Added to CSV log: {title}")

def generate_blog_post():
    """Generates and saves a blog post."""
    start_time = time.time()
    try:
        if os.path.exists(TOPIC_FILE) and os.path.getsize(TOPIC_FILE) > 0:
            with open(TOPIC_FILE, "r") as file:
                topics = file.readlines()
            topic = topics[0].strip()
            remaining_topics = topics[1:]
            with open(TOPIC_FILE, "w") as file:
                file.writelines(remaining_topics)
            topic_source = "Manual"
        else:
            topic = random.choice(TRENDING_TOPICS)
            topic_source = "Fallback"
        
        filename = f"{datetime.now().strftime('%Y-%m-%d')}-{topic.replace(' ', '-').lower()}.md"
        file_path = os.path.join(POSTS_DIR, filename)
        post_url = f"{BLOG_URL}/{filename}" if BLOG_URL else "Unknown"
        
        # Simulate AI-generated content
        article_content = f"# {topic}\n\nThis is an AI-generated article about {topic}."
        article_summary = article_content[:200] + "..."  # Trimmed summary
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(article_content)
        
        execution_time = round(time.time() - start_time, 2)
        logging.info(f"✅ Blog post saved to {file_path}")
        print(f"✅ Blog post saved to {file_path}")
        
        # Add to CSV log
        update_csv_log(topic, "Auto-generated blog post", len(article_content.split()), topic, topic_source, execution_time, post_url)
        
        # Send two Telegram notifications
        send_telegram_notification(f"📝 *New Article: {topic}*\n\n_{article_summary}_\n🔗 [Read More]({post_url})")
        send_telegram_notification(f"📊 *Article Details*\n📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n✍️ Topic: {topic}\n📖 Words: {len(article_content.split())}\n🔍 Topic Source: {topic_source}\n⏳ Time Taken: {execution_time} sec\n🔗 [Read Post]({post_url})")
        
        return file_path
    except Exception as e:
        logging.error(f"❌ Failed to generate blog post: {e}")
        print(f"❌ Failed to generate blog post: {e}")
        send_telegram_notification("❌ Blog post generation failed! Check logs.")
        return None

def main():
    """Main execution function."""
    logging.info("🔄 Running main() function...")
    print("🚀 Running main script logic...")
    
    post_path = generate_blog_post()
    if not post_path:
        print("⚠️ No new blog post was generated. Check logs.")
    else:
        print("✅ Main script logic completed.")

if __name__ == "__main__":
    main()

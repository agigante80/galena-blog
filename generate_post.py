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
    """Creates the CSV file if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["Date", "Title", "Summary", "Keywords", "Topic", "Topic Source", "Word Count", "Execution Time (seconds)", "Post URL"])
        df.to_csv(CSV_FILE, index=False)
        print("✅ Initialized CSV file.")
        logging.info("✅ Initialized CSV file.")

def get_topic():
    """Fetches the next topic from topics.txt or generates a fallback topic."""
    if os.path.exists(TOPIC_FILE) and os.path.getsize(TOPIC_FILE) > 0:
        with open(TOPIC_FILE, "r", encoding="utf-8") as file:
            topics = file.readlines()
        if topics:
            selected_topic = topics[0].strip()
            with open(TOPIC_FILE, "w", encoding="utf-8") as file:
                file.writelines(topics[1:])
            return selected_topic, "Manual"
    
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        used_topics = df["Topic"].dropna().unique().tolist()
    else:
        used_topics = []
    
    fallback_topics = [
        "The Role of Precious Metals in Technology",
        "Sustainable Mining Practices",
        "The History of Gemstone Trade",
        "How Minerals Impact Global Economies",
        "The Science Behind Gemstone Formation",
        "The Future of Mining Technology",
        "Cultural Significance of Precious Stones",
        "How Jewelry Trends Evolve Over Time",
        "The Environmental Impact of Gemstone Mining",
        "Jewelry in a specific era",
        "Jewelry in a specific country/area and period of time",
        "The Importance of a specific mineral in Mining and Jewelry"
    ]
    
    available_topics = [topic for topic in fallback_topics if topic not in used_topics]
    if not available_topics:
        available_topics = fallback_topics
    
    return random.choice(available_topics), "Fallback"
        
def generate_blog_post():
    """Generates a blog post using OpenAI API and saves it."""
    logging.info("📝 Generating a new blog post...")
    try:
        start_time = time.time()
        topic, source = get_topic()
        prompt = f"Write a 1500-word detailed blog post on {topic}. Include history, significance, examples, and expert quotes. Provide an external reference link. Ensure it's engaging and informative."
        
        response = client.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000
        )
        
        article_content = response.choices[0].message.content.strip()
        title = topic
        execution_time = round(time.time() - start_time, 2)
        word_count = len(article_content.split())
        filename = f"{datetime.now().strftime('%Y-%m-%d')}-{title.replace(' ', '-').lower()}.md"
        file_path = os.path.join(POSTS_DIR, filename)
        
        metadata = (
            "---\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Title: {title}\n"
            f"Summary: Generated\n"
            f"Keywords: SEO Keywords\n"
            f"Topic: {topic}\n"
            f"Topic Source: {source}\n"
            f"Word Count: {word_count}\n"
            f"Execution Time: {execution_time} seconds\n"
            f"Post URL: {BLOG_URL}/{filename}\n"
            "---\n\n"
        )
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(metadata + f"# {title}\n\n{article_content}")
        
        logging.info(f"✅ Blog post saved: {file_path}")
        print(f"✅ Blog post saved: {file_path}")
        
        df = pd.DataFrame([[datetime.now().strftime('%Y-%m-%d'), title, "Generated", "SEO Keywords", topic, source, word_count, execution_time, f"{BLOG_URL}/{filename}" ]], 
                          columns=["Date", "Title", "Summary", "Keywords", "Topic", "Topic Source", "Word Count", "Execution Time (seconds)", "Post URL"])
        df.to_csv(CSV_FILE, mode='a', header=not os.path.exists(CSV_FILE), index=False)
        
        return file_path
    except Exception as e:
        logging.error(f"❌ Blog post generation failed: {e}")
        print(f"❌ Blog post generation failed: {e}")
        return None

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

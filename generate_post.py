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

logging.info("✅ Script started...")

def check_env_variable(var_name):
    """Checks if an environment variable is set and logs the result."""
    value = os.getenv(var_name)
    if not value:
        logging.error(f"❌ ERROR: {var_name} is missing! Please set it as an environment variable.")
        logging.info(f"❌ ERROR: {var_name} is missing! Please set it as an environment variable.")
        raise ValueError(f"❌ ERROR: {var_name} is missing! Please set it as an environment variable.")
    else:
        logging.info(f"✅ {var_name} successfully loaded.")
        logging.info(f"✅ {var_name} successfully loaded.")
    return value

logging.info("✅ Script started...")

# OpenAI API Key (stored in GitHub Secrets)
OPENAI_API_KEY = check_env_variable("OPENAI_API_KEY")

# Telegram API Credentials
TELEGRAM_BOT_TOKEN = check_env_variable("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = check_env_variable("TELEGRAM_CHAT_ID")

BLOG_URL = os.getenv("BLOG_URL")  # Base URL for the blog
CSV_FILE = "articles_log.csv"
TOPIC_FILE = "topics.txt"
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")  # GitHub repository URL for editing topics
POSTS_DIR = "_posts"

logging.info("🔍 Checking other environment variables...")
logging.info(f"BLOG_URL: {BLOG_URL}")
logging.info(f"GITHUB_REPO_URL: {GITHUB_REPO_URL}")

logging.info("🔄 Initializing OpenAI client...")
client = openai.OpenAI(api_key=OPENAI_API_KEY)
logging.info("✅ OpenAI client initialized successfully.")

# Ensure the posts directory exists
os.makedirs(POSTS_DIR, exist_ok=True)
logging.info(f"✅ Ensured directory exists: {POSTS_DIR}")

def initialize_csv():
    """Creates the CSV file if it doesn't exist, handling missing cases properly."""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["Date", "Title", "Topic", "Topic Source", "Word Count", "Execution Time (seconds)", "Post URL"])
        df.to_csv(CSV_FILE, index=False)
        logging.info("✅ Initialized CSV file.")
    else:
        try:
            df = pd.read_csv(CSV_FILE)  # Validate CSV integrity
            logging.info("✅ CSV file found and verified.")
        except Exception as e:
            logging.error(f"❌ CSV file corrupted, reinitializing. Error: {e}")
            df = pd.DataFrame(columns=["Date", "Title", "Topic", "Topic Source", "Word Count", "Execution Time (seconds)", "Post URL"])
            df.to_csv(CSV_FILE, index=False)


def log_post_to_csv(date, title, topic, source, word_count, execution_time, post_url):
    """Logs the generated post metadata to the CSV file."""
    try:
        if not os.path.exists(CSV_FILE):
            initialize_csv()

        df = pd.read_csv(CSV_FILE)
        new_entry = pd.DataFrame([{
            "Date": date,
            "Title": title,
            "Summary": "Generated",
            "Keywords": "SEO Keywords",
            "Topic": topic,
            "Topic Source": source,
            "Word Count": word_count,
            "Execution Time (seconds)": execution_time,
            "Post URL": post_url
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        logging.info("✅ Blog post logged in CSV file.")
    except Exception as e:
        logging.error(f"❌ Failed to log post in CSV: {e}")


def send_telegram_message(message):
    """Sends a Telegram message."""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                logging.info("✅ Telegram message sent successfully.")
            else:
                logging.error(f"❌ Failed to send Telegram message: {response.text}")
        except Exception as e:
            logging.error(f"❌ Error sending Telegram message: {e}")

def get_topic():
    """Fetches the next topic from topics.txt or generates a fallback topic."""
    print("🔍 Fetching topic...")
    if os.path.exists(TOPIC_FILE) and os.path.getsize(TOPIC_FILE) > 0:
        with open(TOPIC_FILE, "r", encoding="utf-8") as file:
            topics = file.readlines()
        if topics:
            selected_topic = topics[0].strip()
            with open(TOPIC_FILE, "w", encoding="utf-8") as file:
                file.writelines(topics[1:])
            print(f"🎯 Selected Topic: {selected_topic} (Source: Manual)")
            return selected_topic, "Manual"
    
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
    selected_topic = random.choice(fallback_topics)
    print(f"🎯 Selected Topic: {selected_topic} (Source: Fallback)")
    return selected_topic, "Fallback"
        
def generate_blog_post():
    """Generates a blog post using OpenAI API, saves it, and logs it to CSV."""
    logging.info("📝 Generating a new blog post...")
    try:
        start_time = time.time()
        topic, source = get_topic()
        prompt = f"Write a 1500-word detailed blog post on {topic}. Include history, significance, examples, and expert quotes. Provide an external reference link. Ensure it's engaging and informative."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an expert in minerals, mining, and gemstones."},
                      {"role": "user", "content": prompt}]
        )

        # Ensure response contains valid content
        if not response.choices or not response.choices[0].message.content.strip():
            raise ValueError("❌ OpenAI API returned an empty response.")

        article_content = response.choices[0].message.content.strip()
        if len(article_content.split()) < 200:  # Ensuring at least 200 words are generated
            raise ValueError("❌ OpenAI API response is too short.")

        title = topic
        execution_time = round(time.time() - start_time, 2)
        word_count = len(article_content.split())

        filename = f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{title.replace(' ', '-').lower()}.md"
        file_path = os.path.join(POSTS_DIR, filename)

        post_url = f"{BLOG_URL}/{filename}" if BLOG_URL else "BLOG_URL_NOT_SET"

        metadata = (
            "---\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Title: {title}\n"
            f"Topic: {topic}\n"
            f"Topic Source: {source}\n"
            f"Word Count: {word_count}\n"
            f"Execution Time: {execution_time} seconds\n"
            f"Post URL: {post_url}\n"
            "---\n\n"
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(metadata + article_content)

        log_post_to_csv(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), title, topic, source, word_count, execution_time, post_url)
        send_telegram_message(f"✅ New blog post generated: {title}\n{post_url}")
        logging.error(f"✅ New blog post generated: \n{title}\n{topic}\n{source}\n{post_url}\nend\n")

        return file_path

    except Exception as e:
        logging.error(f"❌ Blog post generation failed: {e}")
        send_telegram_message(f"❌ Blog post generation failed: {e}")
        return None


def main():
    start_time = time.time()
    logging.info("🔄 Running main() function...")
    print("🚀 Running main script logic...")
    initialize_csv()
    post_path = generate_blog_post()
    end_time = round(time.time() - start_time, 2)
    print(f"✅ Main script completed in {end_time} seconds.")
    logging.info(f"✅ Main script completed in {end_time} seconds.")
    if not post_path:
        print("⚠️ No new blog post was generated. Check logs.")
    else:
        print("✅ Main script logic completed.")

if __name__ == "__main__":
    main()

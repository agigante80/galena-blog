import openai
import os
import re
import platform
import psutil
import socket
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

# Set up OpenAI API key
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_system_info():
    """Collects system information for debugging."""
    return f"""
    Hostname: {socket.gethostname()}
    OS: {platform.system()} {platform.release()} ({platform.version()})
    Processor: {platform.processor()}
    RAM: {round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB
    CPU Usage: {psutil.cpu_percent()}%
    Memory Usage: {psutil.virtual_memory().percent}%
    """

def send_summary_email(execution_time, article_title, article_filename, article_summary, topic, word_count):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not RECIPIENT_EMAIL:
        logging.warning("Email credentials not set. Skipping summary notification.")
        return
    
    subject = "✅ AI Article Generation Completed Successfully"
    system_info = get_system_info()
    article_url = f"{BLOG_URL}/{article_filename}" if BLOG_URL else "(URL not configured)"
    
    # Format email content
    body = f"""
    <html>
    <body>
        <h2 style='color: green;'>✅ AI Article Generation Completed Successfully ✅</h2>
        <p><strong>Article Title:</strong> {article_title}</p>
        <p><strong>Topic:</strong> {topic}</p>
        <p><strong>Execution Time:</strong> {execution_time:.2f} seconds</p>
        <p><strong>Word Count:</strong> {word_count}</p>
        <p><strong>Summary:</strong> {article_summary}</p>
        <p><strong>Read the Article:</strong> <a href='{article_url}' target='_blank'>{article_url}</a></p>
        <p><strong>System Information:</strong></p>
        <pre style='background-color: #eef; padding: 10px; border-left: 4px solid gray;'>{system_info}</pre>
        <p>The article has been generated and saved successfully.</p>
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
        logging.info("Summary email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send summary email: {e}")

# Define the prompt for AI article generation
def generate_article(retries=3, delay=5):
    topic = "The Importance of Galena in Mining and Jewelry"
    prompt = f"""
    Write a blog post about {topic}. 
    Include sections: Introduction, History, Properties, Uses, and Benefits. 
    Make it SEO-friendly and informative.
    """
    
    attempt = 0
    start_time = time.time()
    while attempt < retries:
        try:
            logging.info(f"Generating AI article... Attempt {attempt + 1}/{retries}")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a professional mining and jewelry blogger."},
                          {"role": "user", "content": prompt}]
            )
            
            content = response.choices[0].message.content
            execution_time = time.time() - start_time
            logging.info(f"Article generated successfully in {execution_time:.2f} seconds.")
            
            # Extract title and generate filename
            article_title = content.split('\n')[0].replace('# ', '').strip()
            article_summary = " ".join(content.split("\n")[1:3]).strip()
            word_count = len(content.split())
            article_filename = f"_posts/{datetime.today().strftime('%Y-%m-%d')}-{re.sub(r'[^a-z0-9]+', '-', article_title.lower())}.md"
            return content, article_title, article_filename, article_summary, topic, word_count
        
        except Exception as e:
            attempt += 1
            logging.error(f"Error generating article (Attempt {attempt}): {e}")
            if attempt < retries:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                execution_time = time.time() - start_time
                logging.error(f"Max retries reached. Failed to generate article in {execution_time:.2f} seconds.")
                return "Error generating article.", "Unknown Title", "Unknown Filename", "No Summary", topic, 0

# Run the script
if __name__ == "__main__":
    logging.info("Script execution started.")
    script_start_time = time.time()
    article_content, article_title, article_filename, article_summary, topic, word_count = generate_article()
    total_execution_time = time.time() - script_start_time
    if "Error generating article." not in article_content:
        save_article(article_content)
        logging.info(f"Script execution completed successfully in {total_execution_time:.2f} seconds.")
        send_summary_email(total_execution_time, article_title, article_filename, article_summary, topic, word_count)
    else:
        logging.error(f"Script execution failed in {total_execution_time:.2f} seconds.")
    logging.info("Script execution finished.")

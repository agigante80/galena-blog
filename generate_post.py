import openai
import os
from datetime import datetime

# OpenAI API Key (Stored in GitHub Secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define the prompt for AI article generation
def generate_article():
    prompt = """
    Write a blog post about the importance of Galena in mining and jewelry. 
    Include sections: Introduction, History, Properties, Uses, and Benefits. 
    Make it SEO-friendly and informative.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

# Save the article as a Markdown file in the `_posts/` folder
def save_article(content):
    today = datetime.today().strftime('%Y-%m-%d')
    filename = f"_posts/{today}-galena-mining-jewelry.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"---\n")
        f.write(f"title: 'Galena Mining & Jewelry'\n")
        f.write(f"date: {today}\n")
        f.write(f"categories: Mining Jewelry\n")
        f.write(f"---\n\n")
        f.write(content)

    print(f"✅ Article saved: {filename}")

# Run the script
if __name__ == "__main__":
    article_content = generate_article()
    save_article(article_content)

import openai
import os
import re
from datetime import datetime
import random

# OpenAI API Key (stored in GitHub Secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up OpenAI API key
openai.api_key = OPENAI_API_KEY

# Define the prompt for AI article generation
def generate_article():
    prompt = """
    Write a blog post about the importance of Galena in mining and jewelry. 
    Include sections: Introduction, History, Properties, Uses, and Benefits. 
    Make it SEO-friendly and informative.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a professional mining and jewelry blogger."},
                  {"role": "user", "content": prompt}]
    )
    
    content = response["choices"][0]["message"]["content"]
    
    # Append a relevant link to a real website
    reference_links = [
        "For more information, visit [Mindat.org](https://www.mindat.org/).",
        "Learn more at [Geology.com](https://www.geology.com/).",
        "Read about minerals at [USGS](https://www.usgs.gov/).",
        "Explore mining insights at [Mining.com](https://www.mining.com/).",
        "Get geological data at [Minerals.net](https://www.minerals.net/).",
        "Find industry news at [Mining Technology](https://www.mining-technology.com/).",
        "Learn about gemstones at [GIA](https://www.gia.edu/).",
        "Visit [National Mining Association](https://nma.org/) for policy updates.",
        "Understand mining regulations at [ICMM](https://www.icmm.com/).",
        "Explore global mining data at [World Mining Data](https://www.world-mining-data.info/).",
        "Check mineral pricing at [London Metal Exchange](https://www.lme.com/).",
        "Find educational resources at [Mindat](https://www.mindat.org/).",
        "Discover jewelry trends at [Jewelry Council](https://www.responsiblejewellery.com/).",
        "Read mining reports at [Mining Weekly](https://www.miningweekly.com/).",
        "Explore sustainability in mining at [World Gold Council](https://www.gold.org/).",
        "Visit [American Geosciences Institute](https://www.americangeosciences.org/) for research.",
        "Learn about mining finance at [Mining Journal](https://www.mining-journal.com/).",
        "Check mineral rights policies at [US Bureau of Land Management](https://www.blm.gov/).",
        "Understand mineral classification at [Mindat](https://www.mindat.org/).",
        "Learn about rock formation at [Smithsonian National Museum of Natural History](https://naturalhistory.si.edu/)."
    ]
    content += "\n\n" + random.choice(reference_links)
    
    return content

# Convert title to a URL-safe format
def format_title_for_filename(title):
    title = title.lower().strip()
    title = re.sub(r'[^a-z0-9\s]', '', title)  # Remove special characters
    title = re.sub(r'\s+', '-', title)  # Replace spaces with dashes
    return title

# Extract category from content
def extract_category(content):
    lines = content.split('\n')
    for line in lines:
        if line.lower().startswith("category:"):
            return line.split(":", 1)[1].strip()
    return "General"  # Default category if none found

# Save the article as a Markdown file
def save_article(content):
    today = datetime.today().strftime('%Y-%m-%d')
    
    # Extract the title from the first line of the content
    first_line = content.split('\n')[0].strip()
    title = first_line.replace('# ', '').strip()  # Remove Markdown heading symbol
    filename_title = format_title_for_filename(title)
    category = extract_category(content)
    
    filename = f"_posts/{today}-{filename_title}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"---\n")
        f.write(f"title: '{title}'\n")
        f.write(f"date: {today}\n")
        f.write(f"categories: {category}\n")
        f.write(f"---\n\n")
        f.write(content)

    print(f"✅ Article saved: {filename}")

# Run the script
if __name__ == "__main__":
    article_content = generate_article()
    save_article(article_content)

# pip install requests beautifulsoup4 markdownify

import json
import re
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from html2markdown import convert

def parse_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the date using a regular expression
    date_pattern = re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}')
    posting_date_tag = soup.find(lambda tag: tag.name and tag.get_text(strip=True, separator=" ") and date_pattern.search(tag.get_text(strip=True, separator=" ")))

    if posting_date_tag:
        posting_date = date_pattern.search(posting_date_tag.get_text(strip=True, separator=" ")).group()
        content_start = posting_date_tag
    else:
        posting_date = None
        content_start = soup.body

    title = soup.find('title').get_text(strip=True)
    # content = content_start.find_all_next()
    # md_content = md(str(content))

    # Find the content between <br/><br/> and the final </p>
    content_start.br.find_next('br').find_next_sibling()
    content = content_start.find_all_next()
    content.pop()  # Remove the last element, which is the closing </p> tag

    # Convert the HTML formatting to Markdown formatting
    markdown_content = convert(''.join(str(item) for item in content))

    return {
        "url": url,
        "title": title,
        "date": posting_date,
        "content": markdown_content
    }

def main():
    # Load JSON file containing URLs
    with open("essay_links.json", "r") as file:
        data = json.load(file)

    # Iterate through URLs and parse content
    for url in data["urls"]:
        parsed_data = parse_url(url)
        print(parsed_data)
        # Save content as markdown
        with open(f"{parsed_data['title']}.md", "w") as outfile:
            outfile.write(f"# {parsed_data['title']}\n")
            outfile.write(f"*Posting Date: {parsed_data['date']}*\n\n")
            outfile.write(parsed_data["content"])

if __name__ == "__main__":
    main()

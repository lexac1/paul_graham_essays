import os
import json
from bs4 import BeautifulSoup
import requests
from html2markdown import convert

# Read the list of URLs from the JSON file
with open('essay_links.json', 'r') as file:
    data = json.load(file)
    urls = data['urls']

# Create the 'essays' subdirectory if it doesn't exist
if not os.path.exists('essays'):
    os.makedirs('essays')

# Loop over each URL
for url in urls:
    # Load the HTML from the URL
    response = requests.get(url)
    html = response.content

    # Parse the HTML using Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')

    # Extract the title, date, and content
    title = soup.title.string
    content = soup.find('table').contents
    print(content[0])
    date = content[0].strip() if len(content) > 1 else ''

    # Remove the date from the content
    content.pop(1)

    # Convert the HTML formatting to Markdown formatting
    markdown_content = convert(''.join(str(item) for item in content))

    # Write the content to a markdown file in the 'essays' subdirectory
    with open(f'essays/{title}.md', 'w') as file:
        file.write(f'# {title}\n\n')
        file.write(f'[Source]({url})\n\n')
        if date:
            file.write(f'*Posted on {date}*\n\n')
        file.write(markdown_content)

    print(f"{url}\nScrapped Successfully!")

# Import required libraries
from asyncio.log import logger
import feedparser
import urllib.request
import time
import os.path
import html2text
import unidecode
import regex as re
from htmldate import find_date
import csv

# Set up the HTML to Markdown converter
h = html2text.HTML2Text()
h.ignore_images = True
h.ignore_tables = True
h.escape_all = True
h.reference_links = True
h.mark_code = True

# Initialize variables
ART_NO = 1
FILE = "./essays.csv"

# Remove the CSV file if it exists and this is the first article
if ART_NO == 1:
    if os.path.isfile(FILE):
        os.remove(FILE)

# Parse the RSS feed of Paul Graham's essays
rss = feedparser.parse("http://www.aaronsw.com/2002/feeds/pgessays.rss")

# Process each entry in the RSS feed in reverse order
for entry in reversed(rss.entries):
    URL = entry['link']
    TITLE = entry['title']

    try:
        # Download the essay content
        with urllib.request.urlopen(URL) as website:
            content = website.read().decode('unicode_escape', "utf-8")
            parsed = h.handle(content)
            
            # Create a file name based on the essay title
            title = "_".join(TITLE.split(" ")).lower()
            title = re.sub(r'[\W\s]+', '', title)
            
            # Save the essay as a markdown file
            with open(f"./essays/{ART_NO:03}_{title}.md", 'wb+') as file:
                file.write(f"# {ART_NO:03} {TITLE}\n\n".encode())
                parsed = parsed.replace("[](index.html)  \n  \n", "")

                # Add line breaks for paragraphs in the markdown content
                parsed = [(p.replace("\n", " ")
                          if re.match(r"^[\p{Z}\s]*(?:[^\p{Z}\s][\p{Z}\s]*){5,100}$", p)
                          else "\n"+p+"\n") for p in parsed.split("\n")]

                # Write the formatted content to the file
                file.write(" ".join(parsed).encode())
                
                # Print a success message
                print(f"✅ {ART_NO:03} {TITLE}")

                # Add the essay information to the CSV file
                with open(FILE, 'a+', newline='\n') as f:
                    csvwriter = csv.writer(
                        f,
                        quoting=csv.QUOTE_MINIMAL,
                        delimiter=',',
                        quotechar='"')

                    # Write the header row if this is the first article
                    if ART_NO == 1:
                        fieldnames = ["Article no.", "Title", "Date", "URL"]
                        csvwriter = csv.DictWriter(
                            f, fieldnames=fieldnames)
                        csvwriter.writeheader()

                    # Find the publication date of the essay
                    DATE = find_date(entry['link'])

                    # Write the essay information to a new row in the CSV file
                    line = [ART_NO,
                            TITLE,
                            DATE,
                            URL]
                    csvwriter.writerow(line)

    # Handle exceptions and print an error message
    except Exception as e:
        print(f"❌ {ART_NO:03} {entry['title']}, ({e})")
    ART_NO += 1
    time.sleep(0.05)  # half sec/article is ~2min, be nice with servers!

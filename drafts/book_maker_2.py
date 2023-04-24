import feedparser
import urllib.request
import time
import os
import html2text
import regex as re
from htmldate import find_date
import csv

# Function to download and save essays as markdown files
def download_essays(rss, output_dir="./essays"):
    os.makedirs(output_dir, exist_ok=True)
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_tables = True
    h.escape_all = True
    h.reference_links = True
    h.mark_code = True

    for art_no, entry in enumerate(reversed(rss.entries), start=1):
        url = entry['link']
        title = entry['title']

        try:
            with urllib.request.urlopen(url) as website:
                content = website.read().decode('unicode_escape', "utf-8")
                parsed = h.handle(content)

                # Create a sanitized file name based on the essay title
                file_title = "_".join(title.split(" ")).lower()
                file_title = re.sub(r'[\W\s]+', '', file_title)

                file_path = os.path.join(output_dir, f"{art_no:03}_{file_title}.md")
                parsed = parsed.replace("[](index.html)  \n  \n", "")

                # Add line breaks for paragraphs in the markdown content
                parsed_lines = [
                    p.replace("\n", " ") if re.match(r"^[\p{Z}\s]*(?:[^\p{Z}\s][\p{Z}\s]*){5,100}$", p) else f"\n{p}\n"
                    for p in parsed.split("\n")
                ]

                # Save the essay as a markdown file
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(f"# {art_no:03} {title}\n\n")
                    file.write(" ".join(parsed_lines))

                print(f"✅ {art_no:03} {title}")

        except Exception as e:
            print(f"❌ {art_no:03} {title}, ({e})")

        time.sleep(0.05)  # Be nice with servers!

# Function to create a CSV file with essay information
def create_csv(rss, file_path="./essays.csv"):
    header = ["Article no.", "Title", "Date", "URL"]

    with open(file_path, 'w', newline='\n', encoding='utf-8') as f:
        csvwriter = csv.writer(f, quoting=csv.QUOTE_MINIMAL, delimiter=',', quotechar='"')
        csvwriter.writerow(header)

        for art_no, entry in enumerate(reversed(rss.entries), start=1):
            url = entry['link']
            title = entry['title']
            date = find_date(url)
            row = [art_no, title, date, url]
            csvwriter.writerow(row)

def main():
    rss_url = "http://www.aaronsw.com/2002/feeds/pgessays.rss"
    rss = feedparser.parse(rss_url)

    download_essays(rss)
    create_csv(rss)

if __name__ == "__main__":
    main()

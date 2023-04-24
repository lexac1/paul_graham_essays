import feedparser
import urllib.request
import time
import os
import html2text
import regex as re
from htmldate import find_date
import csv

def download_and_parse_essay(url, h):
    with urllib.request.urlopen(url) as website:
        content = website.read().decode('unicode_escape', "utf-8")
        parsed = h.handle(content)
    return parsed

# Create a sanitized file name based on the essay title
def sanitize_title(title):
    file_title = "_".join(title.split(" ")).lower()
    file_title = re.sub(r'[\W\s]+', '', file_title)
    return file_title

# Add line breaks for paragraphs in the markdown content
def format_parsed_content(parsed):
    parsed = parsed.replace("[](index.html)  \n  \n", "")
    parsed_lines = [
        p.replace("\n", " ") if re.match(r"^[\p{Z}\s]*(?:[^\p{Z}\s][\p{Z}\s]*){5,100}$", p) else f"\n{p}\n"
        # # Simpler regex if \p is not supported
        # p.replace("\n", " ") if re.match(r"^\s*\S+(\s+\S+){4,}\s*$", p) else f"\n{p}\n"
        for p in parsed.split("\n")
    ]
    return " ".join(parsed_lines)

def save_essay_to_file(art_no, title, parsed, output_dir):
    file_title = sanitize_title(title)
    file_path = os.path.join(output_dir, f"{art_no:03}_{file_title}.md")
    
    if os.path.isfile(file_path):
        print(f"⏭️ {art_no:03} {title} (file already exists, skipping)")
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# {art_no:03} {title}\n\n")
            file.write(parsed)
        print(f"✅ {art_no:03} {title}")

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
            parsed = download_and_parse_essay(url, h)
            formatted_parsed = format_parsed_content(parsed)
            save_essay_to_file(art_no, title, formatted_parsed, output_dir)
            print(f"✅ {art_no:03} {title}")

        except Exception as e:
            print(f"❌ {art_no:03} {title}, ({e})")

        time.sleep(0.05)  # Be nice with servers!

def create_csv(rss, output_file="./essays.csv"):
    with open(output_file, 'w', newline='\n') as f:
        fieldnames = ["Article no.", "Title", "Date", "URL"]
        csvwriter = csv.writer(f, quoting=csv.QUOTE_MINIMAL, delimiter=',', quotechar='"')
        csvwriter.writerow(fieldnames)

        for art_no, entry in enumerate(reversed(rss.entries), start=1):
            url = entry['link']
            title = entry['title']

            try:
                date = find_date(url)
            except Exception as e:
                print(f"❌ Error finding date for {art_no:03} {title}: ({e})")
                date = "N/A"

            line = [art_no, title, date, url]

            try:
                csvwriter.writerow(line)
                print(f"✅ Added to CSV: {art_no:03} {title}")
            except Exception as e:
                print(f"❌ Error writing to CSV for {art_no:03} {title}: ({e})")


def main():
    rss_url = "http://www.aaronsw.com/2002/feeds/pgessays.rss"
    rss = feedparser.parse(rss_url)

    download_essays(rss)
    create_csv(rss)

if __name__ == "__main__":
    main()

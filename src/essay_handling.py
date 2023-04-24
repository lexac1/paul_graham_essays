import urllib.request
# import time
import os
import asyncio
from utils import fetch_content, parse_content, sanitize_title

def download_and_parse_essay(url, h):
    with urllib.request.urlopen(url) as website:
        content = website.read().decode('unicode_escape', "utf-8")
        parsed = h.handle(content)
    return parsed

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
    os.makedirs(output_dir, exist_ok=True)  # Add this line to create the directory if it doesn't exist

    file_title = sanitize_title(title)
    file_path = os.path.join(output_dir, f"{art_no:03}_{file_title}.md")
    
    if os.path.isfile(file_path):
        print(f"⏭️ {art_no:03} {title} (file already exists, skipping)")
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# {art_no:03} {title}\n\n")
            file.write(parsed)
        print(f"✅ {art_no:03} {title}")

# def download_and_save_essay(art_no, entry, output_dir):
#     url = entry['link']
#     title = entry['title']
#     content = fetch_content(url)
#     parsed = parse_content(content)
#     save_essay_to_file(art_no, title, parsed, output_dir)

# def download_essays(rss, output_dir="../essays"):
#     for art_no, entry in enumerate(reversed(rss.entries), start=1):
#         try:
#             download_and_save_essay(art_no, entry, output_dir)
#         except Exception as e:
#             print(f"❌ {art_no:03} {entry['title']}, ({e})")
#         time.sleep(0.05)  # Be nice to the servers

async def download_and_save_essay(art_no, entry, output_dir):
    url = entry['link']
    title = entry['title']
    try:
        content = await fetch_content(url)
        parsed = parse_content(content)
        save_essay_to_file(art_no, title, parsed, output_dir)
    except Exception as e:
        print(f"❌ {art_no:03} {entry['title']}, ({e})")

async def download_essays(rss, output_dir="../essays"):
    tasks = []
    for art_no, entry in enumerate(reversed(rss.entries), start=1):
        task = asyncio.create_task(download_and_save_essay(art_no, entry, output_dir))
        tasks.append(task)
        if len(tasks) >= 20:  # Adjust the batch size as needed
            await asyncio.gather(*tasks)
            tasks = []

    # Process any remaining tasks
    if tasks:
        await asyncio.gather(*tasks)

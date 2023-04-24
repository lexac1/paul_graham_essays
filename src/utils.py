import aiohttp
# import urllib.request
import html2text
import regex as re

# Create a sanitized file name based on the essay title
def sanitize_title(title):
    file_title = "_".join(title.split(" ")).lower()
    file_title = re.sub(r'[\W\s]+', '', file_title)
    return file_title

async def fetch_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            content = await resp.text(encoding='unicode_escape')
    return content

# def fetch_content(url):
#     with urllib.request.urlopen(url) as website:
#         content = website.read().decode('unicode_escape', "utf-8")
#     return content

def parse_content(content):
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_tables = True
    h.escape_all = True
    h.reference_links = True
    h.mark_code = True
    parsed = h.handle(content)
    parsed = parsed.replace("[](index.html)  \n  \n", "")
    parsed_lines = parsed.split("\n")
    parsed_lines = [(p.replace("\n", " ")
                     if re.match(r"^[\p{Z}\s]*(?:[^\p{Z}\s][\p{Z}\s]*){5,100}$", p)
                     else "\n" + p + "\n") for p in parsed_lines]
    return " ".join(parsed_lines)

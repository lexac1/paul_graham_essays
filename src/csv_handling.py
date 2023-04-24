import csv
from htmldate import find_date

def add_entry_to_csv(art_no, entry, csvwriter):
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


def create_csv(rss, output_file="../output/essays.csv"):
    with open(output_file, 'w', newline='\n') as f:
        fieldnames = ["Article no.", "Title", "Date", "URL"]
        csvwriter = csv.writer(f, quoting=csv.QUOTE_MINIMAL, delimiter=',', quotechar='"')
        csvwriter.writerow(fieldnames)
        for art_no, entry in enumerate(reversed(rss.entries), start=1):
            add_entry_to_csv(art_no, entry, csvwriter)

#  As Batch for memory concerns with large files
# def create_csv(rss, output_file="./essays.csv", batch_size=10):
#     with open(output_file, 'w', newline='\n') as f:
#         fieldnames = ["Article no.", "Title", "Date", "URL"]
#         csvwriter = csv.writer(f, quoting=csv.QUOTE_MINIMAL, delimiter=',', quotechar='"')
#         csvwriter.writerow(fieldnames)

#         # Process entries in batches
#         entries = list(reversed(rss.entries))
#         num_batches = len(entries) // batch_size + (1 if len(entries) % batch_size > 0 else 0)

#         for batch_idx in range(num_batches):
#             start_idx = batch_idx * batch_size
#             end_idx = min((batch_idx + 1) * batch_size, len(entries))

#             for art_no, entry in enumerate(entries[start_idx:end_idx], start=start_idx + 1):
#                 add_entry_to_csv(art_no, entry, csvwriter)

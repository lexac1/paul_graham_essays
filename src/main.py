import feedparser
import asyncio
from essay_handling import download_essays
from csv_handling import create_csv

async def main():
    rss_url = "http://www.aaronsw.com/2002/feeds/pgessays.rss"
    rss = feedparser.parse(rss_url)

    await download_essays(rss)
    create_csv(rss)

if __name__ == "__main__":
    asyncio.run(main())

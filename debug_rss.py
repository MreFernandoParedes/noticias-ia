import feedparser
from dateutil import parser
from datetime import datetime

feeds = [
    ("Cancilleria", "https://news.google.com/rss/search?q=Ministerio+de+Relaciones+Exteriores+Per%C3%fa&hl=es-419&gl=PE&ceid=PE:es-419"),
    ("Peru", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWvfSUwyMHZNREZ5Y3pUeU1Db2dFQXE1Z0FQAQ?hl=es-419&gl=PE&ceid=PE%3Aes-419"),
    ("Mundo", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWvfSUwyMHZNRGx1YlY4U0FBUW5HZ0FQAQ?hl=es-419&gl=PE&ceid=PE%3Aes-419")
]

for section, url in feeds:
    print(f"--- {section} ---")
    feed = feedparser.parse(url)
    print(f"Entries found: {len(feed.entries)}")
    if feed.entries:
        e = feed.entries[0]
        print(f"First entry title: {e.title}")
        print(f"First entry published: {e.published}")
        try:
            dt = parser.parse(e.published)
            print(f"Parsed Date: {dt}")
        except Exception as err:
            print(f"Date Parse Error: {err}")
    print("\n")

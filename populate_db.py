from rss_fetcher import update_news
from database import save_news

print("Fetching and saving news...")
try:
    news = update_news()
    print(f"Fetched {len(news)} items.")
    save_news(news)
    print("News saved to database.")
except Exception as e:
    print(f"Error: {e}")

from rss_fetcher import update_news
from datetime import datetime

print("Starting update...")
news = update_news()
print(f"Total items fetched: {len(news)}")
if news:
    print("Example item:")
    print(news[0]['title'])
    print(news[0]['published_date'])
    
    # Check date range
    now = datetime.now()
    deltas = [(now - n['published_date']).total_seconds()/3600 for n in news]
    print(f"Oldest news (hours ago): {max(deltas):.2f}")
    print(f"Newest news (hours ago): {min(deltas):.2f}")

import feedparser
from bs4 import BeautifulSoup
from textblob import TextBlob
from datetime import datetime, timedelta
import dateutil.parser
import re

# Keywords for simple sentiment analysis (fallback since no heavy ML models)
POS_WORDS = [
    'avanza', 'crecimiento', 'éxito', 'logro', 'mejora', 'gana', 'beneficio', 
    'paz', 'triunfo', 'acuerdo', 'solución', 'bueno', 'positivo', 'aprobado',
    'felicidad', 'celebración', 'victoria', 'récord', 'supera', 'destaca'
]
NEG_WORDS = [
    'muerte', 'crisis', 'caída', 'pierde', 'error', 'conflicto', 'guerra', 
    'crimen', 'denuncia', 'trágico', 'fallece', 'asesinato', 'baja', 'pérdida',
    'déficit', 'fracaso', 'malo', 'negativo', 'rechazo', 'protesta', 'accidente'
]

def analyze_sentiment(text):
    """
    Returns 'red', 'yellow', or 'green' based on text analysis.
    """
    text_lower = text.lower()
    score = 0
    
    for word in POS_WORDS:
        if word in text_lower:
            score += 1
    for word in NEG_WORDS:
        if word in text_lower:
            score -= 1
            
    if score > 0:
        return 'green'
    elif score < 0:
        return 'red'
    else:
        return 'yellow'

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()

import requests
from openai import OpenAI
from database import url_exists

def extract_article_content(url):
    """
    Scrapes the URL to get the main text content.
    Returns the text or None if failed.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        response = requests.get(url, headers=headers, timeout=4) # Short timeout
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # Simple heuristic: grab all paragraphs
            paragraphs = soup.find_all('p')
            text = " ".join([p.get_text() for p in paragraphs])
            # Clean formatting
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:3000] # Limit to ~3000 chars for token efficiency
    except Exception:
        pass
    return None

def analyze_with_ai(rss_title, rss_summary, article_content, api_key):
    """
    Uses OpenAI to generate content. Preference given to article_content.
    """
    if not api_key:
        return rss_title, rss_summary, 'yellow'

    client = OpenAI(api_key=api_key)
    
    # Decide what context to use
    context = ""
    if article_content and len(article_content) > 200:
        context = f"Article Content: {article_content}"
    else:
        context = f"RSS Title: {rss_title}\nRSS Summary: {rss_summary}"
    
    prompt = f"""
    You are a professional news editor for the Ministry of Foreign Affairs of Peru. 
    
    Context:
    {context}

    Tasks:
    1. Title: Create a NEW, unique headline in Spanish (5-12 words). Do NOT copy the original title. Make it descriptive and professional.
    2. Summary: Write a clear, neutral summary in Spanish (approx 50 words) based on the context.
    3. Sentiment: Analyze the sentiment (positive/neutral/negative) for the institution/country.

    Output format:
    Title: [Nuevo Título]
    Summary: [Nuevo Resumen]
    Sentiment: [Red/Yellow/Green]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful news assistant. Always output in Spanish."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=250
        )
        content = response.choices[0].message.content
        
        # Parse output
        lines = content.split('\n')
        new_title = rss_title
        new_summary = rss_summary
        sentiment = 'yellow'
        
        for line in lines:
            if line.strip().startswith('Title:'):
                new_title = line.replace('Title:', '').strip()
            elif line.strip().startswith('Summary:'):
                new_summary = line.replace('Summary:', '').strip()
            elif line.strip().startswith('Sentiment:'):
                s_text = line.replace('Sentiment:', '').strip().lower()
                if 'red' in s_text or 'negative' in s_text: sentiment = 'red'
                elif 'green' in s_text or 'positive' in s_text: sentiment = 'green'
                else: sentiment = 'yellow'
                
        return new_title, new_summary, sentiment
        
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return rss_title, rss_summary, 'yellow'

def fetch_feed(section, url, api_key=None):
    """
    Fetches RSS feed and transforms it into a list of dicts.
    """
    print(f"Fetching {section} from {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    cookies = {'CONSENT': 'YES+'}
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        content = response.content
    except Exception as e:
        print(f"Failed to fetch URL {url}: {e}")
        return []

    feed = feedparser.parse(content)
    news_items = []
    
    if not feed.entries:
        print(f"No entries found for {section}")
        return []

    # Limit items to scrape to avoid timeouts (e.g., top 10 recent)
    entries_to_process = feed.entries[:10]

    for entry in entries_to_process:
        link = entry.link
        title_raw = entry.title
        
        # Skip if exists by link or by title similarity (basic check)
        if url_exists(link):
            continue
            
        # Extraer fecha
        dt = datetime.now()
        if 'published' in entry:
            try:
                dt_aware = dateutil.parser.parse(entry.published)
                dt = dt_aware.replace(tzinfo=None)
            except:
                pass
            
        # Basic RSS info
        summary_raw = entry.get('summary', '') or entry.get('description', '')
        rss_summary = clean_html(summary_raw)
        rss_title = title_raw # Use raw title initially
        
        article_content = None
        
        # AI Processing with Scraping
        sentiment = 'yellow'
        new_title = rss_title
        new_summary = rss_summary
        
        if api_key:
            # Scrape content
            article_content = extract_article_content(link)
            new_title, new_summary, sentiment = analyze_with_ai(rss_title, rss_summary, article_content, api_key)
        else:
            # Fallback
            full_text = f"{rss_title} {rss_summary}"
            sentiment = analyze_sentiment(full_text)

        # Fix Source
        source_title = 'Unknown'
        if 'source' in entry:
            if isinstance(entry.source, dict):
                source_title = entry.source.get('title', 'Unknown')
            elif hasattr(entry.source, 'title'):
                source_title = entry.source.title
            else:
                source_title = str(entry.source)

        item = {
            'link': link,
            'title': new_title,
            'summary': new_summary,
            'section': section,
            'published_date': dt,
            'sentiment': sentiment,
            'source': source_title
        }
        news_items.append(item)
        
    return news_items

def update_news(api_key=None):
    # Updated queries for better coverage
    feeds = [
        # Simplified query to ensure results
        ("Cancilleria", "https://www.bing.com/news/search?q=Cancilleria+Peru&format=RSS&setmkt=es-PE"),
        # General Peru news
        ("Peru", "https://www.bing.com/news/search?q=Peru&format=RSS&setmkt=es-PE"),
        # International news related to Peru (Diplomacy, Treaties, APEC, etc)
        ("Mundo", "https://www.bing.com/news/search?q=Peru+(ONU+OR+OEA+OR+APEC+OR+Tratado+OR+Diplomacia+OR+Embajada)&format=RSS&setmkt=es-PE")
    ]
    
    all_news = []
    for section, url in feeds:
        try:
            items = fetch_feed(section, url, api_key)
            all_news.extend(items)
        except Exception as e:
            print(f"Error fetching {section}: {e}")
            
    return all_news

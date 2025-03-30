import requests
from config import NEWS_API_KEY

def get_newsapi_news(ticker, num_articles=10):
    url = f"https://newsapi.org/v2/everything?q={ticker}&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()
        if data.get("status") != "ok" or "articles" not in data:
            return []

        return [
            {
                "title": article.get("title", "Нет заголовка"),
                "link": article.get("url", "#"),
                "summary": article.get("description", "Нет описания"),
            }
            for article in data["articles"][:num_articles]
        ]
    except Exception:
        return []

import requests
from bs4 import BeautifulSoup


def get_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return "Error fetching the article."

        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('h1')
        article_text = title.get_text() if title else ""

        body = soup.find('div', class_='body-wrap')
        if body:
            article_text += "\n".join(p.get_text() for p in body.find_all('p'))

        return article_text

    except Exception:
        return "Error fetching the article."


def parse_yahoo_news(ticker):
    print(ticker)
    url = f"https://finance.yahoo.com/quote/{ticker}/news/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка при получении страницы: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    news_items = []

    for article in soup.find_all("section", class_="container sz-x-large stream yf-82qtw3 responsive"):
        link_tag = article.find("a", class_="subtle-link")
        title_tag = article.find("h3", class_="clamp yf-82qtw3")

        if link_tag and title_tag:
            link = link_tag["href"] if link_tag["href"].startswith("http") else "https://finance.yahoo.com" + link_tag[
                "href"]
            title = title_tag.text.strip()


            if "yahoo.com" in link:
                article_text = get_text(link)
                summary = article_text[:512] if len(article_text) > 512 else article_text
                news_items.append({
                    "title": title,
                    "link": link,
                    "summary": summary
                })

    return news_items
from services.news.yahoo_news import parse_yahoo_news
from services.news.news_api import get_newsapi_news
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_NAME = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()


def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

    labels = ["Negative", "Neutral", "Positive"]
    return {labels[i]: probabilities[0][i].item() for i in range(3)}


def get_combined_news(ticker):
    yahoo_news = parse_yahoo_news(ticker)

    if len(yahoo_news) < 10:
        needed = 10 - len(yahoo_news)
        newsapi_news = get_newsapi_news(ticker, num_articles=needed)
        yahoo_news.extend(newsapi_news)

    return yahoo_news


def get_top_5_news(ticker):
    news_data = parse_yahoo_news(ticker)
    if not news_data:
        return "Новостей по тикеру не найдено."

    news_text = "📰 <b>Последние 5 новостей:</b>\n\n"
    for article in news_data[:5]:
        news_text += f"  <a href='{article['link']}'>{article['title']}</a>\n\n"
    return news_text


def get_news_with_sentiment(ticker):
    news_data = parse_yahoo_news(ticker)
    if not news_data:
        return "Новостей по тикеру не найдено."

    sentiment_scores = {"Positive": 0, "Neutral": 0, "Negative": 0}
    news_text = "📰 <b>Анализ последних 10 новостей:</b>\n\n"

    for article in news_data[:10]:
        title, link = article["title"], article["link"]
        summary = article.get("summary", "").strip()
        text_to_analyze = summary if summary else title
        sentiment = analyze_sentiment(text_to_analyze)
        dominant = max(sentiment, key=sentiment.get)
        sentiment_scores[dominant] += 1

        news_text += f"    <a href='{link}'>{title}</a>\n"
        news_text += f"    <b>Тональность:</b> {dominant}\n\n"

    if sentiment_scores["Positive"] > sentiment_scores["Negative"]:
        forecast = "📈 Высока вероятность роста акций."
    elif sentiment_scores["Negative"] > sentiment_scores["Positive"]:
        forecast = "📉 Высока вероятность падения акций."
    else:
        forecast = "⚖️ Нейтральный прогноз, акции могут оставаться стабильными."

    return news_text + "\n" + forecast

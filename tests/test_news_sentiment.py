
from services.news.news_analysis import analyze_sentiment
from services.news.news_analysis import get_top_5_news, get_news_with_sentiment

def test_sentiment_analysis_structure():
    result = analyze_sentiment("Stocks are going up")
    assert isinstance(result, dict)
    assert all(key in result for key in ["Positive", "Neutral", "Negative"])

def test_get_top_5_news_russian_ticker():
    result = get_top_5_news("GAZP")
    assert "не найдено" in result.lower()

def test_get_news_with_sentiment_russian_ticker():
    result = get_news_with_sentiment("GAZP")
    assert "не найдено" in result.lower()

def test_get_top_5_news_valid_foreign_ticker():
    result = get_top_5_news("AAPL")
    assert "📰" in result and "<a href=" in result

def test_get_news_with_sentiment_valid_foreign_ticker():
    result = get_news_with_sentiment("AAPL")
    assert "Тональность" in result or "📈" in result or "📉" in result or "⚖️" in result


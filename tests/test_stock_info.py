
from services.stock_info import get_stock_info

def test_stock_info_contains_required_blocks():
    text = get_stock_info("AAPL").lower()
    assert "веб-сайт" in text
    assert "дивиденд" in text
    assert "рыночная капитализация" in text
    assert "сектор" in text or "отрасль" in text

def test_stock_info_russian_ticket():
    text = get_stock_info("SBER").lower()
    assert "не нашел" in text


import pytest
from handlers.user_actions import is_valid_yahoo_ticker, is_valid_moex_ticker

def test_valid_yahoo_ticker():
    assert is_valid_yahoo_ticker("AAPL") is True

def test_invalid_yahoo_ticker():
    assert is_valid_yahoo_ticker("INVALID123") is False

def test_valid_moex_ticker():
    assert is_valid_moex_ticker("SBER") is True

def test_invalid_moex_ticker():
    assert is_valid_moex_ticker("INVALID123") is False

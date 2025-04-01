
import pytest
from handlers.user_actions import is_valid_ticker

def test_valid_ticker():
    assert is_valid_ticker("AAPL") is True

def test_invalid_ticker():
    assert is_valid_ticker("INVALID123") is False


import os
import pytest
from unittest.mock import patch
import requests_mock

from backend.scrapers.walmart import check_walmart_price
from backend.scrapers.types import ParseError, RateLimitedError, NotFoundError

@pytest.fixture
def mock_sleep():
    """Mock time.sleep to avoid slow tests due to backoff/delays"""
    with patch("time.sleep", return_value=None):
        yield

def test_walmart_happy_path(mock_sleep):
    html = """
    <html>
        <head><title>Walmart.com</title></head>
        <body>
            <h1 itemprop="name">Nintendo Switch OLED Model</h1>
            <span itemprop="price">$349.99</span>
        </body>
    </html>
    """
    with requests_mock.Mocker() as m:
        m.get("https://www.walmart.com/ip/12345", text=html)
        result = check_walmart_price("12345")
        
        assert result.source == "walmart"
        assert result.external_id == "12345"
        assert result.title == "Nintendo Switch OLED Model"
        assert result.in_stock is True
        assert result.price == 349.99
        assert result.currency == "USD"

def test_walmart_rate_limited(mock_sleep):
    html = "<html><body>Verify your identity - px-captcha</body></html>"
    with requests_mock.Mocker() as m:
        m.get("https://www.walmart.com/ip/12345", text=html)
        
        with pytest.raises(RateLimitedError, match="PerimeterX"):
            check_walmart_price("12345")

def test_walmart_out_of_stock(mock_sleep):
    html = """
    <html>
        <body>
            <h1 itemprop="name">Nintendo Switch</h1>
            <div>Out of stock</div>
        </body>
    </html>
    """
    with requests_mock.Mocker() as m:
        m.get("https://www.walmart.com/ip/12345", text=html)
        result = check_walmart_price("12345")
        
        assert result.in_stock is False
        assert result.price is None

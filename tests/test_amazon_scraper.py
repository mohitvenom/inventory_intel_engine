import os
import pytest
from unittest.mock import patch
import requests_mock

from backend.scrapers.amazon import check_amazon_price
from backend.scrapers.types import ParseError, RateLimitedError, NotFoundError

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def load_fixture(filename: str) -> str:
    with open(os.path.join(FIXTURES_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def mock_sleep():
    """Mock time.sleep to avoid slow tests due to backoff/delays"""
    with patch("time.sleep", return_value=None):
        yield

def test_amazon_happy_path(mock_sleep):
    html = load_fixture("amazon_product_page.html")
    with requests_mock.Mocker() as m:
        m.get("https://www.amazon.com/dp/B08N5WRWNW", text=html)
        
        result = check_amazon_price("B08N5WRWNW")
        
        assert result.source == "amazon"
        assert result.external_id == "B08N5WRWNW"
        assert result.title == "Apple Mac Mini with Apple M1 Chip"
        assert result.in_stock is True
        assert result.price == 699.00
        assert result.currency == "USD"

def test_amazon_out_of_stock(mock_sleep):
    html = load_fixture("amazon_out_of_stock.html")
    with requests_mock.Mocker() as m:
        m.get("https://www.amazon.com/dp/B09G9FPHY6", text=html)
        
        result = check_amazon_price("B09G9FPHY6")
        
        assert result.title == "Apple Mac Mini with Apple M1 Chip"
        assert result.in_stock is False
        assert result.price is None

def test_amazon_malformed_html(mock_sleep):
    # No title element should raise ParseError
    html = "<html><body><div>Just some random html</div></body></html>"
    with requests_mock.Mocker() as m:
        m.get("https://www.amazon.com/dp/B000000000", text=html)
        
        with pytest.raises(ParseError, match="Could not find product title"):
            check_amazon_price("B000000000")

def test_amazon_rate_limited(mock_sleep):
    with requests_mock.Mocker() as m:
        # Simulate 503 response all 3 times
        m.get("https://www.amazon.com/dp/B000000000", status_code=503)
        
        with pytest.raises(RateLimitedError):
            check_amazon_price("B000000000")

def test_amazon_not_found(mock_sleep):
    with requests_mock.Mocker() as m:
        m.get("https://www.amazon.com/dp/B000000000", status_code=404)
        
        with pytest.raises(NotFoundError):
            check_amazon_price("B000000000")

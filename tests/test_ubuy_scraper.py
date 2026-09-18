import os
import pytest
from unittest.mock import patch, MagicMock

from backend.scrapers.ubuy import check_ubuy_stock
from backend.scrapers.types import ParseError, RateLimitedError

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def load_fixture(filename: str) -> str:
    with open(os.path.join(FIXTURES_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def mock_sleep():
    """Mock time.sleep to avoid slow tests"""
    with patch("time.sleep", return_value=None):
        yield

@pytest.fixture
def mock_cloudscraper():
    """Mock cloudscraper to return standard requests-like responses"""
    with patch("cloudscraper.create_scraper") as mock_create:
        mock_session = MagicMock()
        mock_create.return_value = mock_session
        yield mock_session

def test_ubuy_happy_path(mock_sleep, mock_cloudscraper):
    html = load_fixture("ubuy_product_page.html")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = html
    mock_cloudscraper.get.return_value = mock_response
    
    url = "https://www.ubuy.hk/en/product/12345"
    result = check_ubuy_stock(url, "HK")
    
    assert result.source == "ubuy"
    assert result.external_id == url
    assert result.title == "Sony WH-1000XM4 Wireless Headphones"
    assert result.in_stock is True
    assert result.price == 1234.56
    assert result.currency == "HKD"

def test_ubuy_out_of_stock(mock_sleep, mock_cloudscraper):
    html = """
    <html>
        <h1 class="product-title">Some Item</h1>
        <span>This product is out of stock.</span>
    </html>
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = html
    mock_cloudscraper.get.return_value = mock_response
    
    result = check_ubuy_stock("https://www.ubuy.hk/en/product/123", "HK")
    
    assert result.in_stock is False
    assert result.price is None

def test_ubuy_malformed_html(mock_sleep, mock_cloudscraper):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Empty</body></html>"
    mock_cloudscraper.get.return_value = mock_response
    
    with pytest.raises(ParseError):
        check_ubuy_stock("https://www.ubuy.hk/en/product/123", "HK")

def test_ubuy_rate_limited(mock_sleep, mock_cloudscraper):
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_cloudscraper.get.return_value = mock_response
    
    with pytest.raises(RateLimitedError):
        check_ubuy_stock("https://www.ubuy.hk/en/product/123", "HK")

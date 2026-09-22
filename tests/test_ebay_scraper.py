import os
import pytest
from unittest.mock import patch
import requests_mock

from backend.scrapers.ebay import check_ebay_price
from backend.scrapers.types import ParseError, RateLimitedError, NotFoundError

@pytest.fixture
def mock_sleep():
    """Mock time.sleep to avoid slow tests due to backoff/delays"""
    with patch("time.sleep", return_value=None):
        yield

def test_ebay_happy_path(mock_sleep):
    html = """
    <html>
        <body>
            <div class="x-item-title__mainTitle"><span>Red Dragon DVD</span></div>
            <div class="x-price-primary"><span class="ux-textspans">US $4.00</span></div>
        </body>
    </html>
    """
    with requests_mock.Mocker() as m:
        m.get("https://www.ebay.com/itm/12345", text=html)
        result = check_ebay_price("12345")
        
        assert result.source == "ebay"
        assert result.external_id == "12345"
        assert result.title == "Red Dragon DVD"
        assert result.in_stock is True
        assert result.price == 4.00
        assert result.currency == "USD"

def test_ebay_rate_limited(mock_sleep):
    html = "<html><body>Security Measure captcha</body></html>"
    with requests_mock.Mocker() as m:
        m.get("https://www.ebay.com/itm/12345", text=html)
        
        with pytest.raises(RateLimitedError):
            check_ebay_price("12345")

def test_ebay_out_of_stock(mock_sleep):
    html = """
    <html>
        <body>
            <div class="x-item-title__mainTitle"><span>Red Dragon DVD</span></div>
            <div>This listing was ended</div>
        </body>
    </html>
    """
    with requests_mock.Mocker() as m:
        m.get("https://www.ebay.com/itm/12345", text=html)
        result = check_ebay_price("12345")
        
        assert result.in_stock is False
        assert result.price is None

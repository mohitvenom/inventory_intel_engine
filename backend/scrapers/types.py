from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ScrapeResult:
    source: str
    external_id: str
    region: Optional[str]
    price: Optional[float]
    currency: Optional[str]
    in_stock: bool
    title: Optional[str]
    checked_at: datetime

class ScrapeError(Exception):
    """Base class for all scraping-related errors."""
    pass

class RateLimitedError(ScrapeError):
    """Raised when the target site blocks the request (e.g., 429 or CAPTCHA)."""
    pass

class ParseError(ScrapeError):
    """Raised when the expected HTML elements are missing or malformed."""
    pass

class NotFoundError(ScrapeError):
    """Raised when the product page returns a 404."""
    pass

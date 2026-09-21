import time
import random
import requests
import cloudscraper
from typing import Callable, Optional
from requests.exceptions import RequestException

from .types import RateLimitedError, NotFoundError, ScrapeError

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
]

import threading

# Global state for cross-request rate limiting across the agent run
_GLOBAL_SCRAPE_LOCK = threading.Lock()
_LAST_SCRAPE_TIME = 0.0
MIN_DELAY_BETWEEN_SCRAPES = 2.0

def _enforce_global_delay():
    global _LAST_SCRAPE_TIME
    with _GLOBAL_SCRAPE_LOCK:
        now = time.time()
        elapsed = now - _LAST_SCRAPE_TIME
        if elapsed < MIN_DELAY_BETWEEN_SCRAPES:
            time.sleep(MIN_DELAY_BETWEEN_SCRAPES - elapsed)
        _LAST_SCRAPE_TIME = time.time()

def make_request_with_backoff(
    url: str, 
    use_cloudscraper: bool = False, 
    max_attempts: int = 3
) -> str:
    """
    Makes an HTTP GET request with exponential backoff, user-agent rotation,
    and random delays between requests.
    """
    attempt = 0
    
    if use_cloudscraper:
        session = cloudscraper.create_scraper()
    else:
        session = requests.Session()

    while attempt < max_attempts:
        attempt += 1
        
        # Enforce global delay across all requests to prevent hammering
        _enforce_global_delay()
        
        # Random delay before request (0.5 to 2.0 seconds) to avoid hammering
        time.sleep(random.uniform(0.5, 2.0))
        
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        try:
            response = session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 429 or response.status_code == 503:
                # E.g. CAPTCHA or Rate Limited
                if attempt == max_attempts:
                    raise RateLimitedError(f"Rate limited or blocked on {url} after {max_attempts} attempts.")
            elif response.status_code == 404:
                raise NotFoundError(f"Product not found: {url}")
            elif response.status_code != 200:
                if attempt == max_attempts:
                    raise ScrapeError(f"Failed to fetch {url}, status code: {response.status_code}")
            else:
                # Success
                # Some sites return 200 but contain a CAPTCHA page.
                # A robust scraper checks for bot-challenge strings here, but we will
                # assume 200 OK means HTML is loaded for now.
                return response.text
                
        except RequestException as e:
            if attempt == max_attempts:
                raise ScrapeError(f"Network error fetching {url}: {e}")
                
        # Exponential backoff (2s, 4s, 8s) + some jitter
        backoff_time = (2 ** attempt) + random.uniform(0, 1)
        time.sleep(backoff_time)
        
    raise ScrapeError(f"Failed to fetch {url} after {max_attempts} attempts.")

# Known Issues

## Scraper Limitations and Bot Detection

### Amazon Bot Detection (CAPTCHA / Robot check)
**Failure Mode:** `Could not find product title on Amazon page`
**Symptom:** In some runs, Amazon's aggressive anti-bot defenses trigger and intercept the scraper request. Instead of serving the product page, Amazon serves a CAPTCHA page ("Robot Check") with the `<title>Amazon.com</title>` and a body asking the user to solve a CAPTCHA or "Click the button below to continue shopping". 
**Impact:** Because the expected HTML structure (like `#productTitle`) is missing on the CAPTCHA page, the `amazon.py` scraper throws a `ParseError: Could not find product title on Amazon page`. This prevents price and stock updates for the affected Amazon products during that run.
**Mitigation:** The current scraper relies on `cloudscraper` to evade basic blocks, but this is sometimes insufficient against Amazon's dynamic detection. No reliable bypass is currently implemented.

### Ubuy JS-Rendering
**Failure Mode:** `price: null` returned for successful stock checks
**Symptom:** The `ubuy.py` scraper can successfully load the Ubuy product page and determine stock status (by checking for "Out of stock" text), but it consistently fails to extract the price.
**Impact:** Ubuy prices remain `null` in the database, even when the product is verified to be in stock.
**Mitigation:** None currently. Ubuy relies on client-side JavaScript execution to render pricing information, which our current static HTML parser (`BeautifulSoup`) cannot evaluate.

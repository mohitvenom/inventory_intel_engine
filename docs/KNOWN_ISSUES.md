# Known Issues

* **Ubuy Price Scraping:** Ubuy prices are rendered client-side via JavaScript and aren't visible to a plain HTTP scraper. Currently, `check_ubuy_stock` returns the stock status correctly but not the price for most Ubuy listings. A future iteration could add Playwright-based rendering to handle this specific case.

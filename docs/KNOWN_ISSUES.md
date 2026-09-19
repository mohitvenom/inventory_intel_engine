# Known Issues

* **Ubuy Price Scraping:** Ubuy prices are rendered client-side via JavaScript and aren't visible to a plain HTTP scraper. Currently, `check_ubuy_stock` returns the stock status correctly but not the price for most Ubuy listings. A future iteration could add Playwright-based rendering to handle this specific case.
* **Amazon Regional Restrictions:** When running locally or on certain cloud environments, Amazon physical product pages often enforce regional shipping restrictions based on the IP address, resulting in a `RegionRestrictedError`. Digital goods (like Gift Cards) and Ubuy products do not usually suffer from this in our dev environment.

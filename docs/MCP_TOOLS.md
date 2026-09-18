# Inventory Intel - MCP Tools Documentation

This document describes the tools exposed by the FastMCP server for the Inventory Intel Agent. These tools are designed to be consumed by an LLM-powered orchestrator (like LangGraph) to scrape e-commerce pages and persist the structured results into a PostgreSQL database.

## 1. `check_amazon_price`
**Description:** Scrapes the live Amazon product page for the given ASIN.
**Arguments:**
- `asin` (string): The Amazon Standard Identification Number.
**Returns:** Dictionary containing `status`, `title`, `price`, `currency`, `in_stock`, and `checked_at`. If parsing fails or rate limits are hit, returns a structured error dictionary with `status`, `error_type`, and `message`.

## 2. `check_ubuy_stock`
**Description:** Scrapes the live Ubuy product page for the given URL and region.
**Arguments:**
- `product_url` (string): The Ubuy product URL.
- `region` (string): The region code (e.g. "HK", "NG").
**Returns:** Dictionary containing `status`, `title`, `price` (if visible), `currency`, `in_stock`, and `checked_at`. Structured error dict on failure.

## 3. `list_watchlist`
**Description:** Retrieves the list of products from the database that are currently being monitored.
**Arguments:**
- `active_only` (bool, default True): If True, returns only products marked as active.
**Returns:** List of product dictionaries (id, name, source, external_id, region, currency, thresholds).

## 4. `get_price_history`
**Description:** Retrieves the most recent price history records for a given product ID from the database.
**Arguments:**
- `product_id` (int): The ID of the product.
- `limit` (int, default 10): Maximum number of records to return.
**Returns:** List of price history dictionaries.

## 5. `get_stock_history`
**Description:** Retrieves the most recent stock history records for a given product ID from the database.
**Arguments:**
- `product_id` (int): The ID of the product.
- `limit` (int, default 10): Maximum number of records to return.
**Returns:** List of stock history dictionaries.

## 6. `record_price_check`
**Description:** Inserts a new price history record for a given product ID into the database. Use this to persist the results of a successful price scrape.
**Arguments:**
- `product_id` (int): The ID of the product.
- `price` (float): The recorded price.
- `currency` (string): The currency of the price.
**Returns:** Dictionary containing the inserted record details or error.

## 7. `record_stock_check`
**Description:** Inserts a new stock history record for a given product ID into the database. Use this to persist the results of a successful stock scrape.
**Arguments:**
- `product_id` (int): The ID of the product.
- `in_stock` (bool): The stock status.
**Returns:** Dictionary containing the inserted record details or error.

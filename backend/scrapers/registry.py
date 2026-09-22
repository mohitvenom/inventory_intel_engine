from backend.scrapers.amazon import check_amazon_price
from backend.scrapers.ubuy import check_ubuy_stock
from backend.scrapers.walmart import check_walmart_price
from backend.scrapers.ebay import check_ebay_price

MARKETPLACES = {
    "amazon": {
        "scraper_function": check_amazon_price,
        "mcp_tool_name": "check_amazon_price",
        "display_name": "Amazon",
        "mcp_args_mapper": lambda p: {"asin": p.get("external_id")}
    },
    "ubuy": {
        "scraper_function": check_ubuy_stock,
        "mcp_tool_name": "check_ubuy_stock",
        "display_name": "Ubuy",
        "mcp_args_mapper": lambda p: {"product_url": p.get("external_id"), "region": p.get("region")}
    },
    "walmart": {
        "scraper_function": check_walmart_price,
        "mcp_tool_name": "check_walmart_price",
        "display_name": "Walmart",
        "mcp_args_mapper": lambda p: {"external_id": p.get("external_id")}
    },
    "ebay": {
        "scraper_function": check_ebay_price,
        "mcp_tool_name": "check_ebay_price",
        "display_name": "eBay",
        "mcp_args_mapper": lambda p: {"external_id": p.get("external_id")}
    }
}

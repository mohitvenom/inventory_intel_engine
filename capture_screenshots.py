import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1536, "height": 730})
        
        await page.goto("http://localhost:3000/")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="docs/screenshots/homepage_watchlist_1789971052226.png")
        
        await page.goto("http://localhost:3000/products/6")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="docs/screenshots/product_detail_chart_1789971635935.png")
        
        await page.goto("http://localhost:3000/alerts")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="docs/screenshots/alerts_log_1789971707445.png")
        
        await page.goto("http://localhost:3000/runs")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="docs/screenshots/runs_detail_trace_1789972149282.png")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

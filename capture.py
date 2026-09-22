import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:3000")
        
        print("Waiting for page to load...")
        await page.wait_for_selector("text=Watchlist")
        
        # 1. Check MacBook Air
        print("Clicking Check Now on MacBook Air...")
        row = page.locator("a", has_text="MacBook Air").first
        check_btn = row.locator("button[title='Check Now']")
        await check_btn.click()
        
        error_span = row.locator("span.text-critical")
        await error_span.wait_for(state="visible", timeout=45000)
        
        err_text = await error_span.inner_text()
        print("MacBook Error text:", err_text)
        await row.screenshot(path="c:\\Users\\U73\\.gemini\\antigravity-ide\\brain\\dba6c17a-14ed-43e6-9dfe-7ff2b8a6b09c\\scratch\\screenshot_macbook.webp")
        
        # 2. Check Xbox Gift Card
        print("Clicking Check Now on Xbox Gift Card...")
        row2 = page.locator("a", has_text="Xbox Gift Card").first
        check_btn2 = row2.locator("button[title='Check Now']")
        await check_btn2.click()
        
        success_span = row2.locator("span:has-text('OK:')")
        await success_span.wait_for(state="visible", timeout=45000)
        
        succ_text = await success_span.inner_text()
        print("Xbox Success text:", succ_text)
        await row2.screenshot(path="c:\\Users\\U73\\.gemini\\antigravity-ide\\brain\\dba6c17a-14ed-43e6-9dfe-7ff2b8a6b09c\\scratch\\screenshot_xbox.webp")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

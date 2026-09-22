import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:3000/")
        await page.wait_for_timeout(2000)
        
        # Get the header text
        header_text = await page.evaluate('''() => {
            const header = document.querySelector('header');
            return header ? header.innerText.replace(/\\n/g, ' ') : 'No header found';
        }''')
        print(f"HEADER_TEXT: {header_text}")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

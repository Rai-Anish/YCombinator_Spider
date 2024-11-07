import asyncio
from playwright.async_api import async_playwright
from scrapy.selector import Selector



async def extract_data(playwright, url):
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto(url)

    # Wait for selector as an indicator of page load
    
    await page.wait_for_selector("div._facet_86jzd_85", timeout=7000)
 

    # Extract content
    html = await page.content()

    selector = Selector(text=html)
    batches = selector.xpath("//div[2]/section[2]/div/div[2]/div[1]/div/div[5]")
    for batch in batches.css('div label span._label_86jzd_224::text').getall():
        print(batch)

    

    await browser.close()
# Main async function to run Playwright script
async def main():
    url = "https://www.ycombinator.com/companies"
    async with async_playwright() as playwright:
        data = await extract_data(playwright, url)
        print(data)

# Run the main function
asyncio.run(main())

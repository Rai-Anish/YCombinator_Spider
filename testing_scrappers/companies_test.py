import asyncio
from playwright.async_api import async_playwright
from scrapy.selector import Selector

async def run(playwright):
    # Launch the browser
    browser = await playwright.chromium.launch(headless=False)  # Set headless=True to run without GUI
    page = await browser.new_page()

    # Navigate to the target URL
    url = "https://www.ycombinator.com/companies"  # Replace with your target URL
    await page.goto(url)

    # Wait for a specific element to load (more efficient)
    await page.wait_for_selector('a._company_86jzd_338')  # Adjust the selector as needed

    # Extract the page content
    html = await page.content()

    # Use Scrapy's Selector to parse the HTML
    
    selector = Selector(text=html)
    # Now you can use Scrapy selectors
    for company in selector.css('a._company_86jzd_338'):
        slug_url = company.css('a._company_86jzd_338::attr(href)').get()   
        name= company.css('span._coName_86jzd_453::text').get()
        logo_url= company.css('img::attr(src)').get()
        region= company.css('span._coLocation_86jzd_469::text').get()
        batch= company.css('a._tagLink_86jzd_1023 span.pill::text').re_first(r'^[A-Z]{1,2}\d{2}') 
        industry= company.css('a._tagLink_86jzd_1023 span.pill::text').getall()[1:]
        print(f"""name:{name} 
              \n slug_url={slug_url} 
              \n logo_url:{logo_url} 
              \n region:{region} 
              \n batch:{batch} 
              \n industry:{industry}
              """)

    # Close the browser
    await browser.close()

# Run the Playwright script
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())

import asyncio
from playwright.async_api import async_playwright
from scrapy.selector import Selector

async def run(playwright):
    # Launch the browser
    browser = await playwright.chromium.launch(headless=False)  # Set headless=True to run without GUI
    page = await browser.new_page()

    # Navigate to the target URL
    url = "https://www.ycombinator.com/companies/airbnb"  # Replace with your target URL
    await page.goto(url)

    # Wait for a specific element to load (more efficient)
    await page.wait_for_selector('footer')  # Adjust the selector as needed

    # Extract the page content
    html = await page.content()

    # Use Scrapy's Selector to parse the HTML
    
    selector = Selector(text=html)
    name = selector.css('div div h1.font-extralight::text').get()
    short_desc = selector.css('div div.text-xl::text').get()
    founders = selector.css('div div.leading-snug div.font-bold::text').getall()
    founded = selector.xpath('//div[2]/section[1]/div[2]/div[2]/div/div[2]/div[1]/span[2]/text()').get()
    status = selector.css('div.align-center.flex.flex-row.flex-wrap.gap-x-2.gap-y-2 div div::text').get()
    Website = selector.css('div a div.inline-block.group-hover\\:underline::text').get()
    Team_Size = selector.xpath('//div[2]/section[1]/div[2]/div[2]/div/div[2]/div[2]/span[2]/text()').get()
    Location = selector.xpath('//div[2]/section[1]/div[2]/div[2]/div/div[2]/div[3]/span[2]/text()').get()
    Tags = selector.css('div.align-center.flex.flex-row.flex-wrap.gap-x-2.gap-y-2 a div::text').getall()[:-1]

    Jobs  = selector.xpath('//div[2]/section[1]/div[2]/div[1]/div[2]/div/nav/div[2]/span/text()').get()
    Long_desc = selector.xpath('//div[2]/section[1]/div[2]/div[1]/section[1]/div/p/text()').get()

    print(f"""name: {name} 
          \n short_desc: {short_desc} 
          \n founders: {founders} 
          \n founded: {founded} 
          \n team size: {Team_Size} 
          \n location: {Location}
          \n status: {status}
          \n Tag: {Tags}
          \n Jobs: {Jobs}
          \n Website: {Website}
          \n long_desc: {Long_desc}

          """)
    

    # Close the browser
    await browser.close()

# Run the Playwright script
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())

import scrapy
from scrap_yc.items import CompanyItem
from helpers.helpers import scroll_to_bottom, should_abort_request, batch_url_generator
    #length 41 go till 40
class AllCompaniesSpider(scrapy.Spider):
    name = "all_companies"
    urls = batch_url_generator()

    custom_settings = { 
        "PLAYWRIGHT_ABORT_REQUEST": should_abort_request,
        'RETRY_TIMES': 5,
        'DOWNLOAD_TIMEOUT': 60,
        'RETRY_ENABLED': True,  # Enable retries
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408],   
        "CONCURRENT_REQUESTS": 10,  # Limits concurrent requests
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT": 5, 
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 50000
    }

    # Track the number of processed pages
    page_counter = 0
    restart_interval = 100  # Restart context every 100 requests

    def start_requests(self):
        urls = self.start_urls
        for url in urls:
            yield scrapy.Request(
            url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
            },  # Ensures Playwright is used
            callback=self.parse
        )

    async def parse(self, response): 
        # Check if the context needs to restart
        self.page_counter += 1
        if self.page_counter >= self.restart_interval:
            # Close the existing context
            await response.meta["playwright_page"].context.close()
            # Create a new context and reset the counter
            context = await response.meta["playwright_page"].browser.new_context()
            page = await context.new_page()
            await page.goto(response.url)
            self.page_counter = 0

            # Restart parsing with the new context
            content = await page.content()
            selector = scrapy.Selector(text=content)
            await page.close()
        else:
            page = response.meta["playwright_page"]
            # Wait for the initial content to load
            await page.wait_for_selector('a._company_86jzd_338', timeout=7000)

            # Scroll to load more content
            await scroll_to_bottom(page)

            # After scrolling, get the page content
            content = await page.content()
            selector = scrapy.Selector(text=content)

        # Extract company links and additional data
        for company in selector.css('a._company_86jzd_338'):
            slug_url = company.css('::attr(href)').get()   
            name = company.css('span._coName_86jzd_453::text').get()
            logo_url = company.css('img::attr(src)').get()
            region = company.css('span._coLocation_86jzd_469::text').get()
            batch = company.css('a._tagLink_86jzd_1023 span.pill::text').re_first(r'^[A-Z]{1,2}\d{2}') 
            industry = company.css('a._tagLink_86jzd_1023 span.pill::text').getall()[1:]

            # Use the original response object for following links
            yield response.follow(
                slug_url, 
                callback=self.parse_company, 
                 meta={ 
                    "playwright": True,
                    "playwright_include_page": True,  # Ensures Playwright is used for company pages
                    "name": name,
                    "logo_url": logo_url,
                    "region": region,
                    "batch": batch,
                    "industry": industry,
                } 
            )
        
        # Close the Playwright page after scraping all companies
        await page.close()

    async def parse_company(self, response): 
        page = response.meta["playwright_page"]
        # Wait for specific elements to load on the company page
        await page.wait_for_selector("footer", timeout=30000)

        #Response data 
        company_item = CompanyItem()
        # Basic info passed from previous page
        company_item["name"] = response.meta["name"]
        company_item["logo"] = response.meta["logo_url"]
        company_item["region"] = response.meta["region"]
        company_item["batch"] = response.meta["batch"]
        company_item["industry"] = response.meta["industry"]

        # Additional details extracted from the individual company page
        content = await page.content()
        selector = scrapy.Selector(text=content)

        company_item["founded"] = selector.xpath("//div[2]/section[1]/div[2]/div[2]/div/div[2]/div[1]/span[2]/text()").get()
        company_item["website"] = selector.css("div a div.inline-block.group-hover\\:underline::text").get()
        company_item["team_size"] = selector.xpath("//div[2]/section[1]/div[2]/div[2]/div/div[2]/div[2]/span[2]/text()").get()
        company_item["location"] = selector.xpath("//div[2]/section[1]/div[2]/div[2]/div/div[2]/div[3]/span[2]/text()").get()
        company_item["status"] = selector.css("div.align-center.flex.flex-row.flex-wrap.gap-x-2.gap-y-2 div div::text").get()
        company_item["tags"] = selector.css("div.align-center.flex.flex-row.flex-wrap.gap-x-2.gap-y-2 a div::text").getall()[:-1]
        company_item["jobs"] = selector.xpath("//div[2]/section[1]/div[2]/div[1]/div[2]/div/nav/div[2]/span/text()").get()
        company_item["short_description"] = selector.css("div div.text-xl::text").get()
        company_item["long_description"] = selector.xpath("//div[2]/section[1]/div[2]/div[1]/section[1]/div/p/text()").get()
        company_item["active_founders"] = selector.css("div div.leading-snug div.font-bold::text").getall()

        yield company_item

        # Close the Playwright page after data extraction to free up resources
        await page.close()
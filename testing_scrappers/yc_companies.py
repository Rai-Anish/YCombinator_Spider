import scrapy
from scrapy_playwright.page import PageMethod
from scrap_yc.items import CompanyItem  # Assuming `CompanyItem` is defined in items.py

class YcCompaniesSpider(scrapy.Spider):
    name = "yc_companies"
    allowed_domains = ["ycombinator.com"]
    start_urls = ["https://www.ycombinator.com/companies"]


    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0], 
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "a._company_86jzd_338"),
                    PageMethod("evaluate", """
                        async () => {
                            let prevHeight = 0;
                            while (prevHeight !== document.body.scrollHeight) {
                                prevHeight = document.body.scrollHeight;
                                window.scrollBy(0, document.body.scrollHeight);
                                await new Promise(r => setTimeout(r, 1000));  // Adjust delay as needed
                            }
                        }
                    """)
                ]
            },
            callback=self.parse,
            errback=self.close_page
        )

    async def close_page(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()  # Close the page after extraction to save resources
               
        companies = response.css("a._company_86jzd_338")

        if not companies:
            self.logger.info("No companies found. Check if the selectors have changed.")
            return

        for company in companies:
            # Extract basic info from the company list page
            name = company.css("span._coName_86jzd_453::text").get()
            slug_url = company.css("a._company_86jzd_338::attr(href)").get()
            logo_url = company.css("img::attr(src)").get()
            region = company.css("span._coLocation_86jzd_469::text").get()
            batch = company.css("a._tagLink_86jzd_1023 span.pill::text").re_first(r'^[A-Z]{1,2}\d{2}')

            if slug_url:
                slug = slug_url.split('/')[-1]
                # Follow the link to the detailed company page
                yield response.follow(
                    slug_url,
                    callback=self.parse_company_details,
                    meta={
                        "name": name,
                        "slug": slug,
                        "logo_url": logo_url,
                        "region": region,
                        "batch": batch,
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [PageMethod("wait_for_selector", "footer")]
                    }
                )

    def parse_company_details(self, response):
        if response.status != 200:
            self.logger.error(f"Failed to retrieve details for {response.url} with status {response.status}")
            return
        # Create item and fill with data from the detailed company page
        company_item = CompanyItem()
        
        # Basic info passed from previous page
        company_item["Name"] = response.meta["name"]
        company_item["Logo"] = response.meta["logo_url"]
        company_item["Region"] = response.meta["region"]
        company_item["Batch"] = response.meta["batch"]

        # Additional details extracted from the individual company page
        company_item["Industry"] = response.css("div a._tagLink_86jzd_1023::text").getall()[1:]  # Industry tags
        company_item["Founded"] = response.xpath("//div[2]/section[1]/div[2]/div[2]/div/div[2]/div[1]/span[2]/text()").get()
        company_item["Website"] = response.css("div a div.inline-block.group-hover\\:underline::text").get()
        company_item["Team_Size"] = response.xpath("//div[2]/section[1]/div[2]/div[2]/div/div[2]/div[2]/span[2]/text()").get()
        company_item["Location"] = response.xpath("//div[2]/section[1]/div[2]/div[2]/div/div[2]/div[3]/span[2]/text()").get()
        company_item["Status"] = response.css("div.align-center.flex.flex-row.flex-wrap.gap-x-2.gap-y-2 div div::text").get()
        company_item["Tags"] = response.css("div.align-center.flex.flex-row.flex-wrap.gap-x-2.gap-y-2 a div::text").getall()[:-1]
        company_item["Jobs"] = response.xpath("//div[2]/section[1]/div[2]/div[1]/div[2]/div/nav/div[2]/span/text()").get()
        company_item["Short_Description"] = response.css("div div.text-xl::text").get()
        company_item["Long_Description"] = response.xpath("//div[2]/section[1]/div[2]/div[1]/section[1]/div/p/text()").get()
        company_item["Active_Founders"] = response.css("div div.leading-snug div.font-bold::text").getall()

        yield company_item




        
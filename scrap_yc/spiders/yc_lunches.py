import scrapy
from scrapy_playwright.page import PageMethod

class YcLunchesSpider(scrapy.Spider):
    name = "yc_lunches"

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.ycombinator.com/launches", 
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", 'div.post.row.align-center'),
                    PageMethod("evaluate", """
                        async () => {
                            let prevHeight = 0;
                            while (prevHeight !== document.body.scrollHeight) {
                                prevHeight = document.body.scrollHeight;
                                window.scrollBy(0, document.body.scrollHeight);
                                await new Promise(r => setTimeout(r, 10000));
                            }
                        }
                    """) 
                ]                  
            },
            errback=self.close_page
        )

    async def parse(self, response):
        page = response.meta['playwright_page']
        await page.close()
        
        # Extracting the company names from each 'post' div
        company_names = response.css("a.post-title::text").getall()
        for name in company_names:
            yield {"name": name}

    async def close_page(self, failure):
        page = failure.request.meta['playwright_page']
        await page.close()

    def spider_closed(self, spider):
        """Custom cleanup when spider closes."""
        self.crawler.stop()


# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapYcItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class CompanyItem(scrapy.Item):
    name = scrapy.Field()
    logo = scrapy.Field()
    region = scrapy.Field()
    batch = scrapy.Field()
    industry = scrapy.Field()

    founded = scrapy.Field()
    website = scrapy.Field()
    team_size = scrapy.Field()
    location = scrapy.Field()
    status = scrapy.Field()
    tags = scrapy.Field()
    jobs = scrapy.Field()
    short_description = scrapy.Field()
    long_description = scrapy.Field()
    active_founders = scrapy.Field()
    


    
  

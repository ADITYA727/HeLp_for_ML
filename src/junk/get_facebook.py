import scrapy
from scrapy.crawler import CrawlerProcess

class FacebookSpider(scrapy.Spider):
    name = "FacebookSpider"
    allowed_domain = ["facebook.com"]
    start_urls = [
         'https://www.facebook.com/search/groups/?q=orissa'
    ]

    @staticmethod
    def parse(response):
       print("this is the response")
       print(response.headers)

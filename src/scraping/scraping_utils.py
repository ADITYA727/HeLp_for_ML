
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import tldextract
import requests
from bs4 import BeautifulSoup


def get_first_name(fullname):
    """

    :param fullname:
    :return:
    """
    firstname = ''
    try:
        firstname = fullname.split()[0]
    except Exception as e:
        print(str(e))
    return firstname

def get_last_name(fullname):
    """

    :param fullname:
    :return:
    """
    lastname = ''
    try:
        lastname = fullname.split()[-1]
    except Exception as e:
        print(str(e))
    lastname = lastname.strip('.')
    if len(lastname) < 2:
        lastname = ''
    return lastname


class newSpider(CrawlSpider):
    name = 'newSpider'
    allowed_domains = ['harvard.edu','hbs.edu']
    start_urls = ['http://www.harvard.edu',]

    rules = (
        # Extract links matching 'category.php' (butt not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=()),callback='parse_item'),
        Rule(LinkExtractor(deny_domains=['alumni','twitter','facebook','boxoffice','snapchat','instagram','community','news','docs','blog','/calendar','hvd','community','library','hup','/news','/event','boxoffice','vpal'])),
        
    )
    
    def clean_url(self,link,parent_url): 
        for i in link:                                  #adding links parent url
            dom=tldextract.extract(i).domain
            if dom is '':
                ur=i.replace('/','')
                link[link.index(i)]=parent_url+ur    
        return link
    def parse_item(self, response):
                
        urls1= response.css('a::attr(href)').extract() 
        urls1=self.clean_url(urls1,response.url)
        for i in urls1:
            yield{'url': i}

    def scrape_sangli(self):
        full_text = []
        urls = ["http://www.lokmat.com/sangli/", "http://www.lokmat.com/sangli/page/2/"]
        for url in urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            headlines = soup.findAll('h2')
            for headline in headlines:
                if len(headline.text) > 15:
                    full_text.append(headline.text)
            soup = BeautifulSoup(response.text, 'html.parser')
            summary_text = soup.select('body > section > section > aside.lk-leftwrap > section > section > figure > figcaption > p')
            for text in summary_text:
                if len(text.text) > 65:
                    full_text.append(text.text.split('...')[0].strip('\n').strip(' ').strip('\n'))

        join_text = '. '.join(full_text)


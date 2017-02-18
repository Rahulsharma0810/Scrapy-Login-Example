import scrapy
from loginform import fill_login_form
from ScrapyLoginExample.items import PropertiesItem
from scrapy.loader import ItemLoader
import datetime
import socket
from scrapy.http import FormRequest


class MySpiderWithLogin(scrapy.Spider):
    name = 'login'

    start_urls = [
        'https://github.com/',
    ]

    login_url = 'https://github.com/login'

    login_user = 'Secure_username'
    login_password = 'Secure_password'

    def start_requests(self):
        # let's start by sending a first request to login page
        yield scrapy.Request(self.login_url, self.parse_login)

    def parse_login(self, response):
        # got the login page, let's fill the login form...
        data, url, method = fill_login_form(
            response.url, response.body,
            self.login_user, self.login_password)

        # ... and send a request with our login data
        return FormRequest(url, formdata=dict(data),
                           method=method, callback=self.start_crawl)

    def start_crawl(self, response):
        # OK, we're in, let's start crawling the protected pages
        item = ItemLoader(item=PropertiesItem(), response=response)

        # Load fields using XPath expressions
        item.add_xpath(
            'title', '//*[@id="repo_listing"]/li/a/span/span/text()')

        item.add_value('url', response.url)
        item.add_value('project', self.settings.get('BOT_NAME'))
        item.add_value('spider', self.name)
        item.add_value('server', socket.gethostname())
        item.add_value('date', datetime.datetime.now())
        return item.load_item()

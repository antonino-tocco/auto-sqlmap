from http.client import responses

from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
from urllib.parse import urlparse, urljoin


from scrapy import Spider, Request

from classes.logger import Logger


class IntranetCrawler(Spider):
    name = "intranet_crawler"

    def __init__(self, start_url=None, cookies=None, url_callback=None, *args, **kwargs):
        super(IntranetCrawler, self).__init__(*args, **kwargs)
        self.start_url = start_url
        self.cookies = cookies
        self.start_urls = [start_url]
        self.url_callback = url_callback
        self.urls = []

    def start_requests(self):
        for url in self.start_urls:
            if self.never_visited(url=url):
                yield Request(url=url, cookies=self.cookies, callback=self.parse)


    def parse(self, response, **kwargs):
        self.save_url(response.url)
        if self.url_callback:
            self.url_callback(response.url)
        sleep(1)
        yield {
            "date": datetime.now(),
            "url": self.normalize_url(response.url),
            "method": response.request.method,
        }
        base_url = self.base_url(response.url)
        for form_data in self.retrieve_forms(response):
            full_url = f"{base_url}{form_data['url']}"
            yield {
                "date": datetime.now(),
                "url": full_url,
                "method": form_data["method"] if "method" in form_data
                    and form_data["method"] is not None else "GET",
                "params": form_data["params"],
            }
        for url in response.css('a::attr(href)').getall():
            if self.never_visited(url=url) and self.is_valid_url(url):
                yield response.follow(url=url, cookies=self.cookies, callback=self.parse)


    def never_visited(self, url):
        normalized_url = self.normalize_url(url)
        return normalized_url not in self.urls


    def is_valid_url(self, url):
        return url.startswith(self.start_url)


    def save_url(self, url):
        if self.never_visited(url):
            self.urls.append(url)

    def base_url(self, url):
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def normalize_url(self, url):
        return url.split("?")[0]


    def retrieve_forms(self, response):
        forms = response.css('form').getall()
        for form in forms:
            form_data = {
                "params": {}
            }
            try:
                form_object = BeautifulSoup(form, 'html.parser')
                method = form_object.find('form').get('method')
                action = form_object.find('form').get('action')
                for input_field in form_object.find_all('input'):
                    name = input_field.get('name')
                    value = input_field.get('value')
                    form_data["params"][name] = value
                form_data['method'] = method
                form_data['url'] = action
                yield form_data
            except Exception as e:
                Logger.error(f"Error while parsing form: {e}")
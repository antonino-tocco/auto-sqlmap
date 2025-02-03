import shlex
import subprocess
from functools import reduce
from urllib.parse import urlparse
from argparse import ArgumentParser

from scrapy.crawler import CrawlerProcess

from classes import IntranetCrawler
from classes.logger import Logger

COOKIES_ENABLED=True


def run_sql_map(url=None, cookies:str = None, params:dict=None, level:int = 3, risk:int = 1):
    assert(url is not None)
    command = f"sqlmap -u '{url}' --cookie='{cookies}' --level {level} --risk {risk} --batch --random-agent"
    if params is not None:
        params_string = ",".join(params.keys())
        data_string = reduce(lambda x, key: f"{key}={params[key]}", params.keys())
        command += f" --data='{data_string}' --p='{params_string}'"
    Logger.info(f"Running command: {command}")
    subprocess.run(shlex.split(command), shell=True)


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--url', type=str, required=True)
    parser.add_argument('--cookies', type=str, default=None)
    parser.add_argument('--level', type=int, default=3)
    parser.add_argument('--risk', type=int, default=1)
    args = parser.parse_args()

    cookies = {}
    if args.cookies:
        cookies = dict([tuple(x.split('=')) for x in args.cookies.split(';')])

    process = CrawlerProcess(settings={
        "COOKIES_ENABLED": COOKIES_ENABLED,
        "FEEDS": {
            "intranet.json": {
                "format": "json",
                "overwrite": True,
            },
        },
        "FEED_EXPORT_FIELDS": ["date", "url", "method", "params"],
    })

    process.crawl(IntranetCrawler, start_url=args.url, cookies=cookies, url_callback=lambda url: run_sql_map(url=url, cookies=args.cookies, level=args.level, risk=args.risk))
    process.start()
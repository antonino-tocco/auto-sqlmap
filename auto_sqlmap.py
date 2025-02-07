import os
import json
import shlex
import subprocess
from functools import reduce
from argparse import ArgumentParser

from scrapy.crawler import CrawlerProcess

from classes import IntranetCrawler
from classes.logger import Logger

COOKIES_ENABLED=True


def run_sql_map(url=None, method:str = None, cookies:str = None, params:dict=None, level:int = 3, risk:int = 1, dbms=None, output_dir="."):
    assert(url is not None)
    if output_dir is None:
        output_dir = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname(__file__), "sqlmap_output")))
    command = f"sqlmap --batch -u \"{url}\" --cookie=\"{cookies}\""
    if dbms is not None:
        command += f" --dbms=\"{dbms}\""
    command += f" --level={level} --risk={risk} --output-dir=\"{output_dir}\" --random-agent --delay 0.1"
    if params is not None and len(params.keys()) > 0:
        params_string = ",".join(params.keys())
        data_string = "&".join([f"{k}={v}" for k, v in params.items()])
        command += f" --data=\"{data_string}\" -p \"{params_string}\""
    command += " --tamper=charencode.py --threads 4 --timeout 10"
    Logger.info(f"Running command: {command}")
    subprocess.run(shlex.split(command), shell=False)


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--url', type=str, required=True)
    parser.add_argument('--cookies', type=str, default=None)
    parser.add_argument('--level', type=int, default=3)
    parser.add_argument('--risk', type=int, default=1)
    parser.add_argument("--crawler_output_file", type=str, default="crawler.json")
    parser.add_argument("--sqlmap_output_dir", type=str, default="sqlmap_output")
    parser.add_argument("--dbms", type=str, default=None)
    args = parser.parse_args()

    cookies = {}
    if args.cookies:
        cookies = dict([tuple(x.split('=')) for x in args.cookies.split(';')])

    process = CrawlerProcess(settings={
        "COOKIES_ENABLED": COOKIES_ENABLED,
        "FEEDS": {
            args.crawler_output_file: {
                "format": "json",
                "overwrite": True,
            },
        },
        "FEED_EXPORT_FIELDS": ["date", "url", "method", "params"],
    })
    # if the output file does not exist, run the crawler
    # otherwise, run sqlmap on the urls in the output file
    if not os.path.exists(args.crawler_output_file):
        process.crawl(IntranetCrawler, start_url=args.url, cookies=cookies)
        process.start()
    with open(args.crawler_output_file, "r") as f:
        items = json.loads(f.read())
        for item in items:
            run_sql_map(item["url"], method=item["method"], cookies=args.cookies, params=item["params"], level=args.level, risk=args.risk, dbms=args.dbms, output_dir=args.sqlmap_output_dir)
import os
import json
import re
import shlex
import subprocess
from functools import reduce
from argparse import ArgumentParser

from scrapy.crawler import CrawlerProcess

from classes import IntranetCrawler
from classes.logger import Logger
from utils import get_path_from_url

COOKIES_ENABLED=True


def run_sql_map(url=None, method:str = None, cookies:str = None, params:dict=None, level:int = 3, risk:int = 1, dbms=None, output_dir="."):
    assert(url is not None)
    test_regex = r"(?i)(parameter\s?'?[\w\-]+'?[\s\w]*\s?(is\s?vulnerable|appears\s?to\s?be\s?injectable|found\s?SQL\s?injection|vulnerable\s?to\s?(blind\s?SQL\s?injection|time-based\s?SQL\s?injection|boolean-based\s?SQL\s?injection|reflected\s?XSS|stored\s?XSS)))"
    output = []
    if output_dir is None:
        output_dir = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname(__file__), "sqlmap_output")))
    command = f"sqlmap --batch -u \"{url}\" --cookie=\"{cookies}\""
    if dbms is not None:
        command += f" --dbms=\"{dbms}\""
    command += f" --level={level} --risk={risk} --random-agent --delay 0.1"
    if params is not None and len(params.keys()) > 0:
        params_string = ",".join(params.keys())
        data_string = "&".join([f"{k}={v}" for k, v in params.items()])
        command += f" --data=\"{data_string}\" -p \"{params_string}\""
    command += " --tamper=charencode.py --threads 4 --timeout 10"
    Logger.info(f"Running command: {command}")
    url_path = get_path_from_url(url)
    file_output_dir = os.path.join(output_dir, *url_path.split("/")[:-1])
    os.makedirs(file_output_dir, exist_ok=True)
    file_path = os.path.join(file_output_dir, f"{url_path.split('/')[-1]}.txt")
    Logger.info(f"SQLMap output for {url} at file path {file_path}")
    command_output = subprocess.getoutput(command)
    lines = command_output.splitlines()
    for line in lines:
        if re.match(test_regex, line):
            Logger.warning(f"Potential SQL injection found in {url}: {line}")
            output.append(line)
    with open(os.path.join(file_path), "w") as f:
        f.write(command_output)
    return output

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
    sql_map_output = dict()
    with open(args.crawler_output_file, "r") as f:
        items = json.loads(f.read())
        for item in items:
            output = run_sql_map(item["url"], method=item["method"], cookies=args.cookies, params=item["params"], level=args.level, risk=args.risk, dbms=args.dbms, output_dir=args.sqlmap_output_dir)
            sql_map_output[item["url"]] = output
    with open("sqlmap_output.json", "w") as f:
        f.write(json.dumps(sql_map_output, indent=4))
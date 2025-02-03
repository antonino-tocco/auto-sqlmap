# Auto SQLMap

## Description

This python script automates the process of scanning a website for SQL injection vulnerabilities using SQLMap.
It use scrapy to crawl the website and find the URLs to scan and also parse the pages responses to find the forms to scan.
When a new URL is found, it is added to the queue to be scanned with SQLMap.

## Setup

1. Install SQLMap using the following command:
```sudo apt-get install sqlmap``` or ```sudo apt-get install sqlmap -y```
2. Install the required libraries using the following command:
```pip install -r requirements.txt```

## Run

1. Run the script using the following command:
```python auto_sqlmap.py --url <URL> --cookie <COOKIE> --level <LEVEL> --risk <RISK>```

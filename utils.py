from urllib.parse import urlparse, urljoin

def get_path_from_url(url):
    return urlparse(url).path
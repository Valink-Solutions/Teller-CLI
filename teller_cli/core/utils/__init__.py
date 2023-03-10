from urllib.parse import urlparse


def check_for_shared_url(url: str):
    try:
        urlparse(url)
        return True
    except ValueError:
        return False

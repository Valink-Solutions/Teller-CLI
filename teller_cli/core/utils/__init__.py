from urllib.parse import urlparse


def check_for_shared_url(url: str):
    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            return True
        else:
            return False
    except ValueError:
        return False

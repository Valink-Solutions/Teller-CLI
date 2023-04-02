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


def format_bytes(size_in_bytes):
    suffixes = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    for suffix in suffixes:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {suffix}"
        size_in_bytes /= 1024.0

    return f"{size_in_bytes:.2f} {suffixes[-1]}"

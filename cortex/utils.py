from furl import furl


def parse_url(url):
    f_url = furl(url)
    return f_url.scheme, f_url.host, f_url.port

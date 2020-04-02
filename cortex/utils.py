from furl import furl


def parse_url(url):
    f_url = furl(url)
    return f_url.scheme, f_url.host, f_url.port


def strip_str(ctx, param, value):
    value = value.strip('\'')
    value = value.strip('\"')
    return value

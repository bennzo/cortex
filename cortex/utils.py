from furl import furl


def parse_url(url):
    """ Breaks down URL strings into scheme, host, port

    Args:
        url (:obj:`str`): URL string

    Returns:
        :obj:`tuple`: Tuple of strings (scheme, host, port)
    """
    f_url = furl(url)
    return f_url.scheme, f_url.host, f_url.port


def strip_str(ctx, param, value):
    """ Strips strings of encompassing quotes/double quotes

    Intended to work with the callback argument of Click's parameters

    Args:
        value (:obj:`str`): Quoted string

    Returns:
        :obj:`str`: Unquotted string
    """
    value = value.strip('\'')
    value = value.strip('\"')
    return value

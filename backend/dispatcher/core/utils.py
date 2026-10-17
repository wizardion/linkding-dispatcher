from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit


def encode_url(url: str) -> str:
    split_url = urlsplit(url)
    escaped_path = quote(split_url.path, safe="/")
    query_params = parse_qsl(split_url.query)
    escaped_query = urlencode(query_params)

    return urlunsplit(
        (
            split_url.scheme,
            split_url.netloc,
            escaped_path,
            escaped_query,
            split_url.fragment,
        )
    )

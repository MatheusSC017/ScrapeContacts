from urllib.parse import urlparse


def get_base_links(links):
    base_links = set()
    for link in links:
        parsed_url = urlparse(link)
        base_link = f"{parsed_url.scheme}://{parsed_url.netloc}/"
        base_links.add(base_link)

    return list(base_links)

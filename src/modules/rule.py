import urlparse

class Container:
    def __init__(self, title):
        #data = dict()
        self.title = title

def scrape(url, bs):
    # for testing - this is scrapping article titles from www.businessinsider.com
    domain = urlparse.urlsplit(url)[1].split(':')[0]

    # extracting data from businessInsider
    if domain == "www.businessinsider.com":
        stories = bs.find("div", {"class": "sl-layout-post"})
        title = stories.find("h1")
        if title is not None:
            return Container(title.get_text().encode('ascii', 'ignore'))

    return Container(None)

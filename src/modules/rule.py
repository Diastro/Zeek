import urlparse

class Container:
    def __init__(self):
        #data = dict()
        self.hasData = False

        self.title = None
        self.date = None

def scrape(url, bs):
    # for testing - this is scrapping article titles from www.businessinsider.com
    container = Container()
    domain = urlparse.urlsplit(url)[1].split(':')[0]

    # extracting data from businessInsider
    if domain == "www.nytimes.com":
        headline = bs.find("h1", {"itemprop": "headline"})
        if headline is not None:
            title = headline.find("nyt_headline")
            if title is not None:
                container.title = title.get_text().encode('ascii', 'ignore')

        return container

    return Container()
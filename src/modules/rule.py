import urlparse

class Container:
    def __init__(self):
        #data = dict()
        self.hasData = False

        self.title = None
        self.author = None

def scrape(url, bs):
    # for testing - this is scrapping article titles from www.nytimes.com
    container = Container()
    domain = urlparse.urlsplit(url)[1].split(':')[0]

    # extracting data from NYTimes
    if domain == "www.nytimes.com":
        headline = bs.find("h1", {"itemprop": "headline"})
        if headline is not None:
            title = headline.find("nyt_headline")
            if title is not None:
                container.title = title.get_text().encode('ascii', 'ignore')

        byline = bs.find("h6", {"class": "byline"})
        if byline is not None:
            author = byline.find("span", {"itemprop": "name"})
            if author is not None:
                container.author = author.get_text().encode('ascii', 'ignore')

        return container

    return Container()
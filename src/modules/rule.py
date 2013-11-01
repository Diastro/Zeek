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
    if domain == "www.businessinsider.com":
        stories = bs.find("div", {"class": "sl-layout-post"})
        if stories is not None:
            title = stories.find("h1")
            if title is not None:
                container.title = title.get_text().encode('ascii', 'ignore')

        stories = bs.find("div", {"class": "sl-layout-post"})
        if stories is not None:
            date = stories.find("span", {"class": "date format-date"})
            if date is not None:
                container.date = date.get_text().encode('ascii', 'ignore')
        return container

    return Container()

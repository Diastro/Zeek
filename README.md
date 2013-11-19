Zeek
====

Python distributed web crawling / web scraper

***More info to come...***

### Use cases
 * Visit a predetermined list of URLs and scrape specific data on these pages
 * Visit or dynamicly visit web pages on a periodic bases and scrap data on these pages
 * Dynamicly visit pages on a given domain and scrape data on these pages
 * Dynamicly visit pages all over the internet and scrape data on these pages
 
<small>All the scrapped data can be stored in an output file (ie: `.csv`, `.txt`) or in a database</small>

*David Albertson*

##Execution
1) Take a look at the configuration file and :
  * change the server `listeningAddress / listeningPort`to the right info;
  * change the client `hostAddr / hostPort` to the right info.

2) Launch the server on the **master** node

~~~ sh
pyhton server.py
~~~

3) Launch the client on the **working** nodes

~~~ sh
pyhton client.py
~~~

####Third party library
- [BeautifulSoup4](http://www.crummy.com/software/BeautifulSoup/)
- [lxml](http://lxml.de/)

##Usage example
### Numero uno - BusinessInsider
The following example dynamicly scrapes the titles of BusinessInsider article.

1) config
~~~ sh
[server]
listeningAddr = 127.0.0.1
#listeningAddr = 132.207.114.185
listeningPort = 5050

[client]
hostAddr = 127.0.0.1
#hostAddr = kepler.step.polymtl.ca
hostPort = 5050

[common]
verbose = False
logPath = logs/
userAgent = Zeek-1.0a
crawling = dynamic
robotParser = true
crawlDelay = 0

[dynamic]
domainRestricted = false
requestLimit = 0
rootUrls = http://www.businessinsider.com

[static]
rootUrlsPath = url.txt
~~~

2) rule.py
``` python
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
```

3) storage.py
``` python
import logging
import logger
import atexit

data = None
error = None

def writeToFile(session, container):
    global data, error
    try:
        if (not session.failed) and (session.dataContainer.title is not None):
            if data is None:
                data = open('output.txt', 'w')
            data.write(container.title.replace(",","") + "," + container.date.replace(",","").replace(".","") + "," + session.url +"\n")
        elif session.failed:
            if error is None:
                error = open('error.txt', 'w')
            error.write(str(session.returnCode).replace(",","") + "," + str(session.errorMsg).replace(",","") + "." + session.url.replace(",","") + "\n")
        #else:
        #    raise Exception("..")
    except:
        logger.log(logging.ERROR, "Unhandled exception in storage.py")

def writeToDb(session, container):
    a = "Will come soon - Happy Halloween"

def atexitfct():
    """Cleanly closes file objects"""
    if data is not None:
        data.close()
    if error is not None:
        error.close()

atexit.register(atexitfct)
```

### Numero dos - NYTimes
The following example dynamicly scrapes the authors and article titles of the NYtimes.

1) config
~~~ sh
[server]
listeningAddr = 127.0.0.1
#listeningAddr = 132.207.114.185
listeningPort = 5050

[client]
hostAddr = 127.0.0.1
#hostAddr = kepler.step.polymtl.ca
hostPort = 5050

[common]
verbose = False
logPath = logs/
userAgent = Zeek-1.0a
crawling = dynamic
robotParser = true
crawlDelay = 0

[dynamic]
domainRestricted = true
requestLimit = 0
rootUrls = http://www.nytimes.com/

[static]
rootUrlsPath = url.txt
~~~

2) rule.py
``` python
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
```

3) storage.py
``` python
import logging
import logger
import atexit

dataFd = None
errorFd = None

def writeToFile(session, container):
    global dataFd, errorFd
    try:
        if (not session.failed) and (session.dataContainer.title is not None):
            if dataFd is None:
                dataFd = open('output.txt', 'w')
            dataFd.write(container.author.replace(",","") + "," + container.title.replace(",","") + "," + session.url +"\n")
        elif session.failed:
            if errorFd is None:
                errorFd = open('error.txt', 'w')
            errorFd.write(str(session.returnCode).replace(",","") + "," + str(session.errorMsg).replace(",","") + "." + session.url.replace(",","") + "\n")
        #else:
        #    raise Exception("..")
    except:
        logger.log(logging.ERROR, "Unhandled exception in storage.py")

def writeToDb(session, container):
    a = "Will come soon - Happy Halloween"

def atexitfct():
    """Cleanly closes file objects"""
    if dataFd is not None:
        dataFd.close()
    if errorFd is not None:
        errorFd.close()

atexit.register(atexitfct)
```

##References
### WebCrawling / WebScraping
- [DummyLink](http://www.google.com)

### General
- [DummyLink](http://www.google.com)

### Other
- [DummyLink](http://www.google.com)

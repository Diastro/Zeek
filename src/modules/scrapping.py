import urllib2
import logging
import logger
import time
from bs4 import BeautifulSoup

class Session:
    def __init__(self, url, code, info, requestTime, bsParsingTime, bsDict, scrappedURLs):
        self.url = url
        self.returnCode = code
        self.returnInfo = info
        self.requestTime = requestTime
        self.bsParsingTime = bsParsingTime
        self.bsDict = bsDict

        self.scrappedURLs = scrappedURLs

def visit(url):
    """Visits a given URL and return all the data"""
    logger.log(logging.INFO, "Scrapping : " + str(url))

    start_time = time.time()
    request = urllib2.Request(url)
    request.add_header('User-agent', 'Zeek-Bot/1.0a')
    data = urllib2.urlopen(request,  timeout=4)
    urlRequestTime = time.time() - start_time

    start_time = time.time()
    bs = BeautifulSoup(data)
    bsParsingTime = time.time() - start_time

    # for testing
    #illegal symbols
    illegal = [".mp4", ".mp3", ".flv", ".m4a", \
               ".jpg", ".png", ".gif", \
               ".xml", ".pdf", ".gz", ".zip"]

    links = bs.find_all('a')
    links = [s.get('href') for s in links]
    links = [unicode(s) for s in links]
    for ext in illegal:
        links = [s for s in links if ext not in s]
    links = [s for s in links if s.startswith("http:") or s.startswith("https:")]
    foundUrl = set(links)

    logger.log(logging.DEBUG, "Scrapping complete.")
    return Session(url, data.getcode(), data.info(), urlRequestTime, bsParsingTime , bs, foundUrl)
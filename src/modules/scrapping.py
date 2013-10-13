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
    logger.log(logging.DEBUG, "Scrapping..." + str(url))

    start_time = time.time()
    request = urllib2.Request(url)
    request.add_header('User-agent', 'Zeek/1.0')
    data = urllib2.urlopen(request,  timeout=4)
    urlRequestTime = time.time() - start_time

    start_time = time.time()
    bs = BeautifulSoup(data)
    bsParsingTime = time.time() - start_time

    # for testing
    links = bs.find_all('a')
    links = [s.get('href') for s in links]
    links = [str(s).strip().encode('ascii', 'ignore') for s in links]
    links = [s for s in links if s.startswith("http:") or s.startswith("https:")]
    links = [s for s in links if not s.endswith(".mp4") or s.endswith(".mp3") or s.endswith(".jpg") or s.endswith(".xml")]
    foundUrl = set(links)
    #print(str(links[0]))

    logger.log(logging.DEBUG, "Scrapping done...")
    return Session(url, data.getcode(), data.info(), urlRequestTime, bsParsingTime , bs, foundUrl)
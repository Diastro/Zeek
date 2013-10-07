import urllib2
import logging
import logger
import time
from bs4 import BeautifulSoup

class Session:
    def __init__(self, url, code, info, requestTime, bsParsingTime, bsDict):
        self.url = url
        self.returnCode = code
        self.returnInfo = info
        self.requestTime = requestTime
        self.bsParsingTime = bsParsingTime
        self.bsDict = bsDict

def visit(url):
    """Visits a given URL and return all the data"""
    logger.log(logging.DEBUG, "Scrapping...")

    start_time = time.time()
    request = urllib2.Request(url)
    request.add_header('User-agent', 'Zeek/1.0')
    data = urllib2.urlopen(request)
    urlRequestTime = time.time() - start_time

    start_time = time.time()
    bs = BeautifulSoup(data)
    bsParsingTime = time.time() - start_time

    # for testing
    links = bs.find_all('a')
    #print(str(links[0]))

    return Session(url, data.getcode(), data.info(), urlRequestTime, bsParsingTime , bs)
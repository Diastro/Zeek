import urllib2
import logging
import logger
import time
import socket
from bs4 import BeautifulSoup

class Session:
    def __init__(self, url, failed, code, info, requestTime, bsParsingTime, bsDict, scrappedURLs):
        self.url = url
        self.failed = failed
        self.returnCode = code
        self.returnInfo = info
        self.requestTime = requestTime
        self.bsParsingTime = bsParsingTime
        self.bsDict = bsDict

        self.scrappedURLs = scrappedURLs

        # add error handling
        # err.msg

def visit(url):
    """Visits a given URL and return all the data"""
    logger.log(logging.INFO, "Scrapping : " + str(url))

    try:
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
        logger.log(logging.INFO, "Scrapping complete" + str(data.info()))
        return Session(url, False, data.getcode(), data.info(), urlRequestTime, bsParsingTime , bs, foundUrl)

    except urllib2.HTTPError, err:
        logger.log(logging.INFO, "Scrapping failed - HTTPError " + str(err.msg) + " " + str(err.code))
        return Session(url, True, err.code, "no data", 0, 0 , "", "")
    except socket.timeout:
        logger.log(logging.INFO, "Scrapping failed - Timeout")
        return Session(url, True, -1, "no data", 0, 0 , "", "")
    except:
        logger.log(logging.INFO, "Scrapping failed - Un-handled")
        return Session(url, True, -1, "no data", 0, 0 , "", "")
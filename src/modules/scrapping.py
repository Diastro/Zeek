import cookielib
import urllib2
import logging
import logger
import time
import robotparser
import rule
import socket
import sys
import traceback
import urlparse
from bs4 import BeautifulSoup

robotDict = {}

class Session:
    def __init__(self, url, failed, code, info, requestTime, bsParsingTime, scrappedURLs, dataContainer=None, errorMsg=None):
        self.url = url
        self.failed = failed
        self.returnCode = code
        self.returnInfo = info
        self.requestTime = requestTime
        self.bsParsingTime = bsParsingTime

        self.scrappedURLs = scrappedURLs
        self.dataContainer = dataContainer

        # add error handling
        # err.msg

        #url error
        self.errorMsg = errorMsg

class Scrapper:
    def __init__(self, userAgent, robotParserEnabled, domainRestricted, crawlingType):
        self.userAgent = userAgent
        self.robotParserEnabled = robotParserEnabled
        self.domainRestricted = domainRestricted
        self.crawlingType = crawlingType

        # eventually move this to client.py
        reload(rule)

    def visit(self, url):
        """Visits a given URL and return all the data"""
        logger.log(logging.INFO, "Scrapping : " + str(url))

        # in the case the rootUrl wasnt formatted the right way
        if (url.startswith("http://") or url.startswith("https://")) is False:
            url = "http://" + url

        domain = urlparse.urlsplit(url)[1].split(':')[0]
        httpDomain = "http://" + domain

        try:
            # robot parser
            if self.robotParserEnabled:
                if httpDomain not in robotDict:
                    parser = robotparser.RobotFileParser()
                    parser.set_url(urlparse.urljoin(httpDomain, 'robots.txt'))
                    parser.read()
                    robotDict[httpDomain] = parser
                parser = robotDict[httpDomain]

                isParsable = parser.can_fetch(self.userAgent, url)
                if not isParsable:
                    raise Exception("RobotParser")

            # request
            start_time = time.time()
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            request = urllib2.Request(url)
            request.add_header('User-agent', self.userAgent)
            data = opener.open(request, timeout=4)
            urlRequestTime = time.time() - start_time

            # parsing
            start_time = time.time()
            bs = BeautifulSoup(data)
            bsParsingTime = time.time() - start_time

            # url scrapping - dynamic crawling
            if self.crawlingType == "dynamic":
                illegal = [".mp4", ".mp3", ".flv", ".m4a", \
                           ".jpg", ".png", ".gif", \
                           ".xml", ".pdf", ".gz", ".zip", ".rss"]

                links = bs.find_all('a')
                links = [s.get('href') for s in links]
                links = [unicode(s) for s in links]
                if self.domainRestricted:
                    links = [s for s in links if s.startswith("http://" + domain + "/") or s.startswith("https://" + domain )]
                for ext in illegal:
                    links = [s for s in links if ext not in s]
                links = [s for s in links if s.startswith("http:") or s.startswith("https:")]
                foundUrl = set(links)

            # data scrapping
            dataContainer = rule.scrape(url, bs)
            if dataContainer is None:
                raise("None data container object")

            logger.log(logging.DEBUG, "Scrapping complete")
            return Session(url, False, data.getcode(), data.info(), urlRequestTime, bsParsingTime , foundUrl, dataContainer)

        except urllib2.HTTPError, err:
            logger.log(logging.INFO, "Scrapping failed - HTTPError " + str(err.msg) + " " + str(err.code))
            return Session(url, True, err.code, "no data", 0, "", "", errorMsg=err.msg.replace('\n', ""))
        except socket.timeout:
            logger.log(logging.INFO, "Scrapping failed - Timeout")
            return Session(url, True, -1, "no data", 0, "", "", errorMsg="Request timeout")
        except Exception as e:
            if e.message == "RobotParser":
                logger.log(logging.INFO, "Scrapping failed - RobotParser")
                return Session(url, True, -2, "no data", 0, "", "", errorMsg="Request is not allowed as per Robot.txt")
            else:
                logger.log(logging.INFO, "Scrapping failed - Un-handled")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = "\n" + ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.log(logging.ERROR, message)
                return Session(url, True, -100, "no data", 0, "", "", errorMsg=traceback.format_exception(exc_type, exc_value, exc_traceback)[-1].replace('\n', ""))
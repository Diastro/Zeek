import ConfigParser
import inspect
import os
import sys


class Configuration():
    def __init__(self):
        self.host = ""
        self.port = ""
        self.logPath = ""
        self.userAgent = ""
        self.verbose = False

        self.crawling = ""
        self.robotParserEnabled = False
        self.domainRestricted = False
        self.requestLimit = 0
        self.crawlDelay = 0.0
        self.rootUrls = []

        self.rule_py = ""
        self.scrapping_py = ""

def readStaticUrl(path):
    urls = []
    file = open(path, 'r')
    for url in file:
        url = "".join(url.split()).replace(",","")
        urls.append(url)
    return urls

def readFile(path):
    content = ""
    file = open(path, 'r')
    for line in file:
        content = content + line
    return content

def configParser():
    path = os.path.dirname(sys.argv[0])
    if path:
        path = path + "/"

    config = Configuration()
    configParser = ConfigParser.RawConfigParser(allow_no_value=True)

    configParser.read(path + 'config')
    config.host = configParser.get('server', 'listeningAddr')
    config.port = configParser.getint('server', 'listeningPort')
    config.logPath = configParser.get('common', 'logPath')
    verbose = configParser.get('common', 'verbose')
    if verbose == "True" or verbose == "true":
        config.verbose = True
    else:
        config.verbose = False

    config.userAgent = configParser.get('common', 'userAgent')
    config.crawlDelay = configParser.getfloat('common', 'crawlDelay')
    robotParserEnabled = configParser.get('common', 'robotParser')
    if robotParserEnabled == "True" or robotParserEnabled == "true":
        config.robotParserEnabled = True
    else:
        config.robotParserEnabled = False

    config.crawling = configParser.get('common', 'crawling')
    if config.crawling == 'dynamic':
        domainRestricted = configParser.get('dynamic', 'domainRestricted')
        config.requestLimit = configParser.getint('dynamic', 'requestLimit')
        rootUrls = configParser.get('dynamic', 'rootUrls')
        rootUrls = "".join(rootUrls.split())
        config.rootUrls = rootUrls.split(',')

        if domainRestricted == "True" or domainRestricted == "true":
            config.domainRestricted = True
        else:
            config.domainRestricted = False
    else:
        config.rootUrls = readStaticUrl(configParser.get('static', 'rootUrlsPath'))

    # dynamic module reload
    config.rule_py = readFile(path + "modules/rule.py")
    config.scrapping_py = readFile(path + "modules/scrapping.py")

    return config
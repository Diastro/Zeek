import urllib2, cookielib
from bs4 import BeautifulSoup

# url to test the parsing
urls = ["http://www.nytimes.com/2013/11/19/us/politics/republicans-block-another-obama-nominee-for-key-judgeship.html"]

for u in urls:
	# cookie
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

	# builds request
	request = urllib2.Request(u)
	request.add_header('User-agent', "test")
	response = opener.open(request)

	# parsing response
	bs = BeautifulSoup(response)

    # - Test your parsing here -

    # example :
    #
    #    headline = bs.find("h1", {"itemprop": "headline"})
    #    if headline is not None:
    #        title = headline.find("nyt_headline")
    #        if headline is not None:
    #            print title.get_text().encode('ascii', 'ignore')

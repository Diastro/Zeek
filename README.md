Zeek
====

Python distributed web crawling / web scraper

This the first version of my distributed web crawler. It isn't perfect yet but I'm sharing it because it because the end result is far better then what I expected and it can easily be adapted to your needs. Feel free to improve/fork/report issues.

I'm planning to continue working on it and probably release an updated version in the future but i'm not sure when yet.

### Use cases
 * Visit a **predetermined** list of URLs and scrape specific data on these pages
 * Visit or **dynamicly visit** web pages on a periodic bases and **scrape** data on these pages
 * Dynamicly visit pages on a **given domain** and scrape data on these pages
 * Dynamicly visit pages **all over the internet** and scrape data on these pages
 
<small>All the scrapped data can be stored in an output file (ie: `.csv`, `.txt`) or in a database</small>

*David Albertson*

##Execution
1) Download/Install the required third party library
~~~ sh
$ easy_install beautifulsoup4
$ easy_install lxml
~~~

2) Update the configuration files :
  * change the server `listeningAddress / listeningPort` to the right info;
  * change the client `hostAddr / hostPort` to the right info.

3) Update the /modules/rule.py and modules/storage.py :
  * See the documentation for more information on how to adapt these files.

4) Launch the server on the **master** node

~~~ sh
$ pyhton server.py
~~~

5) Launch the client on the **working** nodes

~~~ sh
$ pyhton client.py
~~~

####Third party library
- [BeautifulSoup4](http://www.crummy.com/software/BeautifulSoup/)
- [lxml](http://lxml.de/)

## Recommended topologies
Zeek can be lunch in 2 different topologies depending on which resource is limiting you. When you want to crawl a large quantity of web pages, you need a large bandwith (when executing multiple parallel requests) and you need computing power (CPU). Depending on which of these 2 is limiting you, you should use the appropriate topology for the fastes crawl time.
Keep in mind that if time isn't a constrain for you, a 1-1 approach is always the safest and less expensive!
 * Bandwith limitation : see the 1-n topology

### 1-1 Topology

### 1-n Topology
* If you are limited

##References
### WebCrawling / WebScraping
- [DummyLink](http://www.google.com)

### General
- [DummyLink](http://www.google.com)

### Other
- [DummyLink](http://www.google.com)

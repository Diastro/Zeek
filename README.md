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
 * Basic topology (recommended) : see the 1-1 topology
 * Best performance topology : see the 1-n topology

### 1-1 Topology
The 1-1 Topology is probably the easyest to achieve. It only requires 1 computer so it makes it easy for anyone to deploy Zeek this way. Using this type of topology you first deploy the server.py (using 127.0.0.1 as the listeningAddr) and connect as many client.py process to it (using 127.0.0.1 as the hostAddr) and everything runs on the same machine. Be aware that depending on the specs of you computer, you will end up being limited by the number of thread launch by the serve.py process at some point. server.py launches 3 threads per client that connects to it so if your computer allows you to create 300 thread per process, the maximum number of client.py that you will be able to launch will be approximately 100. If you end up lunching that many client, you might end up being limited by your bandwith at some point.<br>
[1-1 Topology schema](http://i.imgur.com/7NJGodN.jpg)

### 1-n Topology
This topology is perfect if you want to achieve best performance but requires that you have more than 1 computer at your disposal. The only limitation you have using this topology is regarding the number of clients that can connect to the server.py process. As explained above, server.py launches 3 threads per client that connects to it so if your computer allows you to create 300 thread per process, the maximum number of client.py that you will be able to launch will be approximately 100. Though in this case, if each computer uses a seperate connection, bandwith shouldn't be a problem.<br>
[1-n Topology schema](http://i.imgur.com/lXCEAk6.jpg)

## Stats - Benchmark
*** Coming soon ***

## Warning
Using a distributed crawler/scrapper can make you life easier but also comes with great responsabilities. When you are using a crawler to make request to a website, you generate connections to this website and if the targeted web site isn't configured properly, it can have desastrous consequences. You're probalby asking yourself "What exactly does he mean". What I mean is that by using 10 computers each having 30 client.py instances running you could (in a perfect world) generate 300 parallels requests. If these 300 parallel request are targetting the same website/domain, you will be downloading a lot a data pretty quickly and if the targeted domain isn't prepared for it, you could protentially shut it down.<br>
During the development of Zeek I happened to experience something similar while doing approximatly 250 parallel request to a pretty well known website. The sysadmins of this website ended contacting the sysadmin where I have my own server hosted being worried that something strange was happenning (they were probably thinking of an attack). During this period of time I ended up downloading 7Gb of data in about 30 minutes. This alone trigged some internal alert on their side. That being now said, I'm not responsible of the usage you will be doing of Zeek. Simply try to be careful and respectful of others online!

##References
- [Wikipedia - WebCrawler](http://en.wikipedia.org/wiki/Web_crawler)
- [Wikipedia - Distributed crawling](http://en.wikipedia.org/wiki/Distributed_web_crawling)
- [How to Parse data using BeautifulSoup4](http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html)
- [Understanding Robot.txt](http://www.robotstxt.org/faq.html)

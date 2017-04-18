Zeek
====

Python distributed web crawling / web scraper

This the first version of my distributed web crawler. It isn't perfect yet but I'm sharing it because the end result is far better then what I expected and it can easily be adapted to your needs. Feel free to improve/fork/report issues.

I'm planning to continue working on it and probably release an updated version in the future but i'm not sure when yet.

### Use cases
 * Visit a **predetermined** list of URLs and scrape specific data on these pages
 * Visit or **dynamically visit** web pages on a periodic bases and **scrape** data on these pages
 * Dynamically visit pages on a **given domain** and scrape data on these pages
 * Dynamically visit pages **all over the internet** and scrape data on these pages
 
<small>All the scraped data can be stored in an output file (ie: `.csv`, `.txt`) or in a database</small>

*David Albertson*

## Execution
1) Download the source and install the required third party library
~~~ sh
$ git clone https://github.com/Diastro/Zeek.git
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
$ python server.py
~~~

5) Launch the client on the **working** nodes

~~~ sh
$ python client.py
~~~

#### Third party library
- [BeautifulSoup4](http://www.crummy.com/software/BeautifulSoup/)
- [lxml](http://lxml.de/)

## Configuration fields
**[server]**<br>
*listeningAddr* : Address on which the server listens for incoming connections from clients (ex : 127.0.0.1)<br>
*listeningPort* : Port on which the server listens for incoming connections from clients (ex : 5050)<br>

**[client]**<br>
*hostAddr* : Address to connect to, on which the server listens for incoming connections (ex : 127.0.0.1)<br>
*hostPort* : Port to connect to, on which the server listens for incoming connections (ex : 5050)<br>

**[common]**<br>
*verbose* : Enables or disables verbose output in the console (ex: True, False)<br>
*logPath* : Path where to save the ouput logfile of each process (ex : logs/)<br>
*userAgent* : Usually the name of your crawler or bot (ex : MyBot 1.0)<br>
*crawling* : Type of crawling (ex : dynamic, static)<br>
*robotParser* : Obey or ignore the robots.txt rule while visiting a domain (ex : True, False)<br>
*crawlDelay* : Delay, in seconds, between the 2 subsequent request (ex : 0, 3, 5)<br>

**[dynamic]** (Applies only if the crawling type is set to dynamic)<br>
*domainRestricted* : If set to true, the crawler will only visit url that are same as the root url (ex : True, False)<br>
*requestLimit* : Stops the crawler after the limit is reach (after visiting x pages) (ex : 0, 2, 100, ...)<br>
*rootUrls* : Url to start from (ex : www.businessinsider.com)<br>

**[static]** (Applies only if the crawling type is set to static)<br>
*rootUrlsPath* : Path to the file which contains a list of url to visit (ex : url.txt)<br>

## How it works
***Coming soon***

### Rule.py Storage.py
***Coming soon***

### Testing your rule.py
***Coming soon***

## Recommended topologies
Zeek can be launched in 2 different topologies depending on which resource is limiting you. When you want to crawl a large quantity of web pages, you need a large bandwidth (when executing multiple parallel requests) and you need computing power (CPU). Depending on which of these 2 is limiting you, you should use the appropriate topology for the fastest crawl time.
Keep in mind that if time isn't a constraint for you, a 1-1 approach is always the safest and less expensive!
 * Basic topology (recommended) : see the **1-1 topology**
 * Best performance topology : see the **1-n topology**

No matter which topology you are using, you can always use the `launch-clients.sh` to launch multiple instance of client.py on a same computer.

### 1-1 Topology
The 1-1 Topology is probably the easiest to achieve. It only requires 1 computer so it makes it easy for anyone to deploy Zeek this way. Using this type of topology you first deploy the server.py (using 127.0.0.1 as the listeningAddr) and connect as many client.py processes to it (using 127.0.0.1 as the hostAddr) and everything runs on the same machine. Be aware that depending on the specs of you computer, you will end up being limited by the number of threads launched by the serve.py process at some point. server.py launches 3 threads per client that connects to it so if your computer allows you to create 300 thread per process, the maximum number of client.py that you will be able to launch will be approximately 100. If you end up launching that many client, you might end up being limited by your bandwidth at some point.<br>
[1-1 Topology schema](http://i.imgur.com/7NJGodN.jpg)

### 1-n Topology
This topology is perfect if you want to achieve best performance but requires that you have more than 1 computer at your disposal. The only limitation you have using this topology is regarding the number of clients that can connect to the server.py process. As explained above, server.py launches 3 threads per client that connects to it so if your computer allows you to create 300 thread per process, the maximum number of client.py that you will be able to launch will be approximately 100. Though in this case, if each computer uses a seperate connection, bandwidth shouldn't be a problem.<br>
[1-n Topology schema](http://i.imgur.com/lXCEAk6.jpg)

## Stats - Benchmark
***Coming soon***

## Warning
Using a distributed crawler/scraper can make your life easier but also comes with great responsibilities. When you are using a crawler to make request to a website, you generate connections to this website and if the targeted web site isn't configured properly, it can have disastrous consequences. You're probably asking yourself "What exactly does he mean?". What I mean is that by using 10 computers each having 30 client.py instances running you could (in a perfect world) generate 300 parallels requests. If these 300 parallel request are targetting the same website/domain, you will be downloading a lot a data pretty quickly and if the targeted domain isn't prepared for it, you could potentially shut it down.<br>
During the development of Zeek I happened to experience something similar while doing approximatly 250 parallel request to a pretty well known website. The sysadmins of this website ended up contacting the sysadmin where I have my own server hosted being worried that something strange was happenning (they were probably thinking of an attack). During this period of time I ended up downloading 7Gb of data in about 30 minutes. This alone trigged some internal alert on their side. That being now said, I'm not responsible for your usage of Zeek. Simply try to be careful and respectful of others online!

## References
- [Wikipedia - WebCrawler](http://en.wikipedia.org/wiki/Web_crawler)
- [Wikipedia - Distributed crawling](http://en.wikipedia.org/wiki/Distributed_web_crawling)
- [How to Parse data using BeautifulSoup4](http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html)
- [Understanding Robots.txt](http://www.robotstxt.org/faq.html)

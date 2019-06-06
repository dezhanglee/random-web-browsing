import random
import config
import requests
import re
import time

from bs4 import BeautifulSoup
import urllib.request

from urllib.parse import urlparse

# initialize our global variables
dataMeter = 0
goodRequests = 0
badRequests = 0


def doRequest(url, shouldSleep = True):
    global dataMeter
    global goodRequests
    global badRequests
    
    if (not shouldSleep):
        config.debug = False
    sleepTime = random.randrange(config.minWait,config.maxWait)
    
    if config.debug:
        print("requesting: %s" % url)
    
    headers = {'user-agent': config.userAgent}
    #print(headers)
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
    except:
        time.sleep(30) # else we'll enter 100% CPU loop in a net down situation
        return False
    
    #print(r)
    #print(r.status_code)
    status = r.status_code
    
    pageSize = len(r.content)
    dataMeter = dataMeter + pageSize


    
    if config.debug:
        print("Page size: %s" % pageSize)
        if ( dataMeter > 1000000 ):
            print("Data meter: %s MB" % (dataMeter / 1000000))
        else:
            print("Data meter: %s bytes" % dataMeter)
    if ( status != 200 ):
        badRequests+=1
        if config.debug:
            print("Response status: %s" % r.status_code)
        if ( status == 429 ):
            if config.debug:
                print("We're making requests too frequently... sleeping longer...")
            sleepTime+=30
    else:
        goodRequests+=1
    
    # need to sleep for random number of seconds!
    if config.debug:
        print("Good requests: %s" % goodRequests)
        print("Bad reqeusts: %s" % badRequests)
        print("Sleeping for %s seconds..." % sleepTime)
    if (shouldSleep):
        time.sleep(sleepTime)
    return r

def getLinks(page, url):

    #get the domainName, protocol (http/https/ftp, etc.)
    parsed_uri = urlparse(url)
    domainName = parsed_uri.netloc
    protocol = parsed_uri.scheme
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    resp = urllib.request.urlopen(url)
    soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'), features="lxml")
    
    collectedLinks = []
    
    for link in soup.find_all('a', href=True):
        itemToAppend = ""
        currLink = link['href']
        
        #if current link links to a fully formed webpage
        if (domainName in currLink or protocol in currLink):
            itemToAppend = link['href']
            
        #when linking within same domain, they leave out the domain sometimes
        else:
            new_link = str(result) + str(currLink)
            itemToAppend = new_link

        #remove any whitespaces as a result of string manipulation
        itemToAppend = ''.join(itemToAppend.split())
        collectedLinks.append(itemToAppend)
        
    return collectedLinks



def crawlRecursive(url, depthLeft, urlSet = set(), onlySameDomain = True):
    print("depthLeft = {}".format(depthLeft))
    if (depthLeft == 0):
        return  
    links = getLinks(None, url)
    if (not links):
        return
    if (onlySameDomain):
        links = [i for i in links if url in i]
    urlSet.update(links)
    for i in links:
        crawlRecursive(i, depthLeft - 1, urlSet)
    return list(urlSet)
        
    
def crawl(url = "https://ncl.sg", maxDepth = 3, onlySameDomain = True):
    urlSet = set()
    return crawlRecursive(url, maxDepth, urlSet, onlySameDomain)

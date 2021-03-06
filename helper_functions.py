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

userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) ' \
	'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

SLEEP_429_TIME = 30

def doRequest(url, debug = False):


    global dataMeter
    global goodRequests
    global badRequests
    
    if debug:
        print("requesting: %s" % url)
    
    headers = {'user-agent': userAgent}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        raise Exception("Unable to access {}".format(url))
        return False
    
    status = r.status_code
    
    pageSize = len(r.content)
    dataMeter = dataMeter + pageSize
 
    if ( status != 200 ):
        badRequests+=1
        #todo - implement logging 
        if ( status == 429 ):
            print("We're making requests too frequently... sleeping for \
                %d secs" % SLEEP_429_TIME)
            time.sleep(SLEEP_429)
            
    else:
        goodRequests+=1
    
    if debug:
        print("Response status: %s" % r.status_code)
        print("Page size: %s" % pageSize)
        if ( dataMeter > 1000000 ):
            print("Data meter: %s MB" % (dataMeter / 1000000))
        else:
            print("Data meter: %s bytes" % dataMeter)
        print("Good requests: %s" % goodRequests)
        print("Bad reqeusts: %s" % badRequests)
    return r

'''
return domain name of a given url
eg if url = https://ncl.sg/about/xx/yy
getDomainName(url) returns ncl.sg
'''
def getDomainName(url):
    parsed_uri = urlparse(url)
    return parsed_uri.netloc


'''
gets protocol of a given url
eg if url = https://ncl.sg/about/xx/yy
getProtocol(url) returns https
'''
def getProtocol(url):
    parsed_uri = urlparse(url)
    return parsed_uri.scheme
'''
url is valid iff scheme is one of
http/https/ftp
'''
def isValidWebsite(url):
    return (getProtocol(url) in {'http', 'https', 'ftp'})
    
def getLinks(url):

    #get the domainName, protocol (http/https/ftp, etc.)
    domainName = getDomainName(url)
    protocol = getProtocol(url)
    result = '{}://{}/'.format(protocol, domainName)

    resp = urllib.request.urlopen(url)
    soup = BeautifulSoup(resp, \
        from_encoding=resp.info().get_param('charset'), features="lxml")
    
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



def crawlRecursive(url, depthLeft, urlSet = set(), onlySameDomain = True, \
                    debug = False):
    
    
    if debug:
        print("depthLeft = {}".format(depthLeft))
    if (depthLeft == 0):
        return
    try:
        links = getLinks(url)
    except Exception as e:
        print("Error accessing %s" % url)
        raise e
    if (not links):
        return
    
    #not a perfect method
    #but P(a link has the exact domain name as a contiguous substr)
    #is quite low...
    if (onlySameDomain):
        domainName = getDomainName(url)
        links = [i for i in links if domainName in i and isValidWebsite(i)]
    
    #make a copy of prior crawled sites
	#and update the posterior crawled sites (this iteration)
    priorUrlSet = urlSet.copy()
    urlSet.update(links) 
    
    for i in links:
        if (i not in priorUrlSet): #avoid redundant crawling 
            crawlRecursive(i, depthLeft - 1, urlSet)
    
    return list(urlSet)
        
    
def crawl(url = "https://ncl.sg", maxDepth = 3, onlySameDomain = True, debug = False):
    urlSet = set()
    return crawlRecursive(url, maxDepth, urlSet, onlySameDomain, debug)

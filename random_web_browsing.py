dataMeter = 0
goodRequests = 0
badRequests = 0

MAX_DEPTH = 10 #hardcoded for now, change later

from helper_functions import *
import random
import config
import time
import sys

def randomBrowsing(url = "https://ncl.sg", timeAllowed = 1000, \
                maxDepth = 10, debug = False):
    
    
    print("Starting URL = %s" % url);
    page = doRequest(url)
    
    if page:
        links = getLinks(page)
        linkCount = len(links)
        
        if not linkCount:
            raise Exception("Base addr does not have any link")
    else:
        raise Exception("Error requesting %s" % inputUrl)
    
    
    
    currDepth = 0
   
    #todo, implement time 
    currTime = time.time()
    finishTime = currTime + timeAllowed
    
    #implement stack to make it easier to go back when hit dead link 
    while (currDepth < MAX_DEPTH and time.time() < finishTime):

        if (debug):
            print(links)
            
            
        linkCount = len(links)
        
        if (linkCount == 0):
            # go back to top again
            links = getLinks(page)
            continue
        
        randomLinkIdx = random.randrange(0, linkCount - 1)
        
        randomLink = links[randomLinkIdx]
        
        
        try:
            sub_page = doRequest(randomLink)
            if (sub_page):
                sub_page_links = getLinks(sub_page)
                checkLinkCount = len(sub_page_links)
            elif (not sub_page or checkLinkCount == 0):
                #that link cannot access or no links to click
                print("Following link cant be accessed or does not have any \
                links to follow up with: %s " % links[randomLinkIdx])
                del links[randomLinkIdx]
                continue #restart without curr link
                
            links = sub_page_links

            currDepth += 1
            print("Currently at: %s " % randomLink)
            
        except Exception as e:
            raise e

def crawlThenBrowse(url = "https://ncl.sg", timeAllowed = 1000, \
                maxDepth = 3, onlySameDomain = True, debug = False):
                
    listOfPages = crawl(url, maxDepth, onlySameDomain)   
    print(listOfPages)
    
    currTime = time.time()
    endTime = currTime + timeAllowed
    nLink = len(listOfPages)
    
    while(currTime < endTime):
        
        randIdx = random.randint(0, nLink - 1)
        
        randPage = listOfPages[randIdx]
        
        if (debug):
            print("Currrently at {}".format(randPage))
        
        doRequest(randPage)
        
        currTime = time.time()
        
    
    
    
if __name__ == "__main__":
    
    if (int(sys.argv[1]) == 1):
        randomBrowsing()
    
    else:
        crawlThenBrowse()
        
            
            
            
        

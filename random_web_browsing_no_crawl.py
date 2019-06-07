dataMeter = 0
goodRequests = 0
badRequests = 0

MAX_DEPTH = 10 #hardcoded for now, change later
MIN_SLEEP_TIME = 3
MAX_SLEEP_TIME = 5

from helper_functions import *
import random
import config
import time
import sys
import os

def randomBrowsing(url = "https://ncl.sg", timeAllowed = 1000, \
                maxDepth = MAX_DEPTH, debug = False, sleep = True, \
                noOfInstances = 1):
    
    
    linkStack = [url]
    
    print("Starting URL = %s" % url);
    page = doRequest(url)
    
    if page:
        links = getLinks(page)
        linkCount = len(links)
        
        if not linkCount:
            raise Exception("Base addr does not have any link")
    else:
        raise Exception("Error requesting %s" % inputUrl)
    
    #if want a few accesses concurrently
    parentPid = os.getpid()
    
    while(noOfInstances > 1 and os.getpid() == parentPid):
        os.fork()
        noOfInstances -= 1
    
    currDepth = 0
   
    currTime = time.time()
    finishTime = currTime + timeAllowed
    
    #use PID as seed, shouldnt use time 
    #since its possible some instances may start at the
    #same time 
    random.seed(os.getpid())
    
    #implement stack to make it easier to go back when hit dead link 
    while (currDepth < MAX_DEPTH and time.time() < finishTime):

        if (debug):
            print(links)
            
            
        linkCount = len(links)
        
        if (linkCount == 0):
            # go back to prev page again
            links = linkStack.pop()
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
            
            #if can access the link, put it on stack 
            linkStack.append(randomLink)
            
            #then sleep
            sleepTime = random.randint(MIN_SLEEP_TIME, MAX_SLEEP_TIME)
            time.sleep(sleepTime)
            
        except Exception as e:
            raise e
            
           

    
if __name__ == "__main__":
    
    randomBrowsing()
    
        
            
            
            
        

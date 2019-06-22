# -*- coding: utf-8 -*-
"""
Tree Extending Hint Scraper
BYU Record Linking Lab

@version:   1.2
@author:    Clark Brown
@date:      Apr 11 2019
"""

import os
import platform
import time
import datetime as dt
import random
import logging
import getpass  as gp
import pandas   as pd
from bs4      import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException


'''CONFIG'''
SCRAPE_FILE = '' #in ./data directory
TEMP_BATCH_SIZE = 20 #records
LOAD_DELAY_TIME = 6 #seconds
RANDOMIZE_MAX = 6 #seconds
CLOSE_DELAY_TIME = 3 #seconds
MAX_FAILED_AUTH = 3 #attempts
IMPLICITLY_WAIT = 5 #seconds
PAGE_LOAD_TIMEOUT = 20 #seconds
MAX_TIMEOUTS = 3 #excpetions


'''Logging Config'''
logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


"""
Function to get the appropriate driver based on the OS and architecture.

@return: path (string)
"""
def getDriverPath():
    system = platform.system()
    architecture = platform.architecture()[0]
    path = r'./webdrivers'
    if(system == 'Windows'):
        if(architecture == '64bit'):
            path += r'\win64'
        else:
            path += r'\win32'
    elif(system == 'Darwin'):
        path += r'/darwin'
    else:
        path += r'/linux'
        
    #Chrome assumed
    path += r'/chromedriver'
    
    if(system == 'Windows'):
        path += r'.exe'

    logging.info('Using webdriver at %s' % path)
    return path
#end getDriverPath()
    

"""
Take a rest on the day of rest.

@return: True if paused for Sunday, False otherwise
"""
def pauseIfSunday():
    SUNDAY = 6
    sunday = (dt.datetime.today().weekday() == SUNDAY)
    wasSunday = sunday
    if (sunday):
        logging.info('It is now Sunday. Pausing for the day of rest.')
    while (sunday):
        time.sleep(600)
        sunday = (dt.datetime.today().weekday() == SUNDAY)
    if (wasSunday):
        logging.info('Sunday is over. Resume program.')
    return wasSunday
#end pauseIfSunday()


"""
Delay using time.sleep() for a randomized amount of time.

@global: LOAD_DELAY_TIME, RANDOMIZE_MAX
@return: the amount of time delayed in seconds
"""
def loadDelay():
    time.sleep(LOAD_DELAY_TIME)
    randomized = random.random()*RANDOMIZE_MAX
    time.sleep(randomized)
    return (LOAD_DELAY_TIME + randomized)
#end loadDelay()


"""
Scrape the given page to get information about the usefulness of the hint.

@param:  page_source  selenium webdriver page_source type
@return: data formatted as dictionary
"""
def scrape(page_source):
    #Selenium hands of the source of the specific job page to Beautiful Soup
    soup = BeautifulSoup(page_source, 'lxml')

    #Beautiful Soup grabs the HTML tables on the page
    try:
        parentTable = soup.select('#parentTable')[0]
    except (IndexError):
        logging.error('HTTP error made scrape impossible.')
        return {'error': 1} #page failed to load properly
    pofrTable = soup.select('#PersonOfRecordTableDiv > table.nospc')[0]
    childTable = soup.select('#childTable')[0]
    siblingTable = soup.select('#siblingTable')[0]
    otherTable = soup.select('#otherTable')[0]
    
    tables = [parentTable, pofrTable, childTable, siblingTable, otherTable]
    
    # initialize data with counts of zero
    data = {'addable': 0, 'attachable': 0, 'attached': 0, 'duplicates': 0, 'missing': 0}

    #iterate through each table
    for table in tables:        
        ng_bindings = table.select('button.action > span.ng-binding')

        for tag in ng_bindings:
            text = tag.getText()
            if(text == 'Add'):
                data['addable'] += 1
            elif(text == 'Compare'):
                data['attachable'] += 1
            elif(text == 'Edit'):
                data['attached'] += 1
            elif(text == ' '):
                data['duplicates'] += 1
            else:
                data['missing'] += 1              
        #end tag loop
    # end table loop

    return data 
# end scrape()
    

"""
Takes a csv of URLs and scrapes them for information about tree extending hints.

Stores everything in 'results.csv'
"""
if __name__ == '__main__':
    print("Tree Extending Hint Scraper")
    print("v1 - April 2019 - BYU RLL")
    
    logging.info('Start of program.')
    startTime = time.time()
    
    '''Input File'''
    if (SCRAPE_FILE == ''):
        print("\nEnter scrape file (csv) path below.")
        SCRAPE_FILE = input("path: ./data/")
    
    '''Authentication'''
    auth_attempts = 0
    auth = False
    while(not auth):
        print("\nEnter FamilySearch credentials below.")
        userName = input("username: ")
        password = gp.getpass("password: ")
        print("\nAuthenticating...")
        
        # create a new Chrome session
        driver = webdriver.Chrome(executable_path=getDriverPath())
        driver.implicitly_wait(IMPLICITLY_WAIT)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        logging.info('Chrome session start.')
        
        # login url
        login_url = "https://ident.familysearch.org/cis-web/oauth2/v3/authorization?client_secret=ERTcF1Wo2jxolL9E6iFpPjfa5wDNe%2BO5DHUheUz8TOMbCli%2BceoQJaNB7LakFczILaOqrANIbCDX72tLKImeKM%2F18WN%2BKV4pve2xNnyTWSSsaPnO9kcfWiMH0nKOybkVCUiG4ox%2FTQRBr%2FO4KUgT%2FgemDgiQVJoN3dcGu1PfWDbX%2Bu7eR8gH6rI6RfYzNBy9fiBRYAJyY2lGCT%2F0%2BYPFTR42BG7PxdE0agvhD71exxEzSgSR0kb%2BjiCZipLKOxTZ1iqvDb8gMuEhKOfl%2BBOniT8t9%2BUnwVVy5EPq9hM9E3O663e%2BaLJq1GigCHYJvNDkeSFrOkl1iVaUrod5b8%2FYCA%3D%3D&response_type=code&redirect_uri=https%3A%2F%2Fwww.familysearch.org%2Fauth%2Ffamilysearch%2Fcallback&state=%2F&client_id=3Z3L-Z4GK-J7ZS-YT3Z-Q4KY-YN66-ZX5K-176R"
        driver.get(login_url)
        
        userInputElement = driver.find_element_by_name("userName")
        passwordInputElement = driver.find_element_by_name("password")
        
        userInputElement.send_keys(userName)
        passwordInputElement.send_keys(password)
        
        login_button = driver.find_element_by_id("login")
        login_button.click() #click login button
        auth_attempts += 1
        
        if(driver.current_url == 'https://ident.familysearch.org/cis-web/oauth2/v3/authorization'):
            driver.quit()
            logging.info('Chrome session end.')
            logging.warning('Failed to authenticate user: %s.', userName)
            if(auth_attempts == MAX_FAILED_AUTH):
                print("Too many attempts!\nExit.")
                logging.error('Excesive failed authentication attempts. Exit.')
                exit(1)
            print("Signin Error! Try again...")
            auth = False
        else:
            auth = True
            logging.info('Authenticated user: %s.', userName)
            # Clear user credentials for security
            userName = None
            password = None
    print("\nSuccess!")
    ''' End Authentication'''
    
    
    '''Processing'''
    df = pd.read_csv('data/' + SCRAPE_FILE)
    path = os.getcwd()
    results = []
    exceptions = 0
    scraped = 0

    print("\nScraping tree extending hints from url file...")                     
    for index, hint in df.iterrows():
        pauseIfSunday()
        
        url = hint['url']
        print("   " + url)
        logging.info('Scrape url: %s' % url)
        
        try:
            timeout = False
            driver.get(url)
        except (TimeoutException):
            timeout = True
            exceptions += 1
            logging.warning('Caught selenium.common.exceptions.TimeoutException for url: %s' % url)
        # end except(TimeoutException)
        
        if(timeout):
            if (exceptions <= MAX_TIMEOUTS):
                print("  ... Page loading timed out. Refreshing...")
                logging.info('Refreshed browser.')
                driver.get('http://rll.byu.edu/')
                driver.refresh()
                driver.get(url)
            else:
                logging.error('Exceeded %s TimeoutExceptions. End itteration.' % MAX_TIMEOUTS)
                break 
        # end if(timeout)   
        
        loadDelay() #time for page to render AngularJS values
        
        #use Beatiful Soup to scrape the given url
        data = scrape(driver.page_source)
        data['hint_id'] = hint['hint_id']
        data['url'] = url
        results.append(data)
        scraped += 1
        
        if((index % TEMP_BATCH_SIZE) == 0):
            pd.DataFrame(results).to_csv(path + '/results_temp.csv', index=False)
            logging.info('Wrote to temp file %s' % (path + '/results_temp.csv'))
    # end hint loop
    '''End Processing'''
                      
    
    '''Write Output'''    
    pd.DataFrame(results).to_csv(path + '/results.csv', index=False)
    logging.info('Wrote to file %s' % (path + '/results.csv'))
    
    if os.path.exists("results_temp.csv"):
        print('Removing temporary files.')
        os.remove("results_temp.csv")
    '''End Write Output'''
    
    
    #end the Selenium browser session
    time.sleep(CLOSE_DELAY_TIME)
    driver.quit()
    logging.info('Chrome session end.')
    
    print('\n\nDone.')
    logging.info('Scraped %s records.' % scraped)
    logging.info('Total runtime: %s minutes.' % ((time.time()-startTime)/60))
    
    time.sleep(CLOSE_DELAY_TIME)
    
    logging.info('End of program.')
    exit(0)
# end main()
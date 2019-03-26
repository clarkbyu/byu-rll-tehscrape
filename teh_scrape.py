# -*- coding: utf-8 -*-
"""
Tree Extending Hint Scraper (v1)
BYU Record Linking Lab

@author: Clark Brown
@date: Mar 26 2019
"""

import os
import platform
import time
import getpass as gp
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd


def getDriverPath():
    system = platform.system()
    architecture = platform.architecture()[0]
    path = r'.\webdrivers'
    if(system == 'Windows'):
        if(architecture == '64bit'):
            path += r'\win64'
        else:
            path += r'\win32'
    elif(system == 'Darwin'):
        path += r'\darwin'
    else:
        path += r'\linux'
        
    #Chrome assumed
    path += r'\chromedriver'
    
    if(system == 'Windows'):
        path += r'.exe'

    return path
#end getDriverPath()


def scrape(page_source):
    #Selenium hands of the source of the specific job page to Beautiful Soup
    soup = BeautifulSoup(page_source, 'lxml')

    #Beautiful Soup grabs the HTML tables on the page
    parentTable = soup.select('#parentTable')[0]
    pofrTable = soup.select('#PersonOfRecordTableDiv > table.nospc')[0]
    childTable = soup.select('#childTable')[0]
    siblingTable = soup.select('#siblingTable')[0]
    otherTable = soup.select('#otherTable')[0]
    
    tables = [parentTable, pofrTable, childTable, siblingTable, otherTable]
    
    # initialize data with counts of zero
    data = {'addable': 0, 'attachable': 0, 'duplicates': 0, 'warnings': 0}

    #iterate through each table
    for table in tables:
        warnings = table.select('td.mid-col p.no-link-living')
        hidden_warnings = table.select('div.attached.ng-hide > p.no-link-living')
        duplicates = table.select('td.mid-col p.no-link-living.clickable')
        #cells = table.select('td.mid-col div.attached')
        #hidden_cells = table.select('td.mid-col div.attached.ng-hide')
        
        attachable = table.select('button.action.link')
        addable = table.select('button.action.create')
        
        data['duplicates'] += len(duplicates)
        data['warnings'] += len(warnings) - len(hidden_warnings) - len(duplicates)
        data['attachable'] += len(attachable) 
        data['addable'] += len(addable)
        #cells_count = len(cells) - len(hidden_cells)
        #attached_count = cells_count - (duplicate_count + attachable_count + addable_count)
    # end table loop

    return data 
# end scrape()
    

if __name__ == '__main__':
    print("Tree Extending Hint Scraper")
    print("v1 - March 2019 - BYU RLL")
    
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
        driver.implicitly_wait(30)
        
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
            if(auth_attempts == 3):
                print("Too many attempts!\nExit.")
                exit(1)
            print("Signin Error! Try again...")
            auth = False
        else:
            auth = True
            # Clear user credentials for security
            userName = None
            password = None
    print("\nSuccess!")
    ''' End Authentication'''
    
    
    '''Processing'''
    df = pd.read_csv('data/teh_urls_tiny.csv')
    
    results = []

    print("\nScraping tree extending hints from url file...")                     
    for index, hint in df.iterrows():
        url = hint['url']
        print("   " + url)
        
        driver.get(url)
        time.sleep(0.25)
        
        data = scrape(driver.page_source)
        data['hint_id'] = hint['hint_id']
        data['url'] = url
        #use Beatiful Soup to scrape the given url
        results.append(data)
    # end hint loop
    
    print(results)
    '''End Processing'''
                        
    #get current working directory
    path = os.getcwd()
    
    pd.DataFrame(results).to_csv(path + '/results.csv', index=False)
    
    #end the Selenium browser session
    time.sleep(3)
    driver.quit()
    
    print('\n\nDone.')
    time.sleep(3)
    
    exit(0)
# end main()
# Tree Extending Hint Scrape for FamilySearch
#### Version 1.2
#### BYU Record Linking Lab

[![BYU|RLL](http://rll.byu.edu/Plugins/SCE/Images/logo_full.jpg)](http://rll.byu.edu/)

A simple Python program that employs Selenium and BeautifulSoup to scrape information for Tree Extending Hints from Source Linker pages on [FamilySearch](http://familysearch.org).

## Input
Program takes a *csv* type stored in the `data\` directory. Must include:
 - hint_id
 - url

## Output
Results are saved to `results.csv` in the root directory. 

| Header | Meaning |
| ------ | ------ |
| Addable | Number of new people to be added to the tree from the hint |
| Attachable | Number of people in the tree that can have the record attached to them |
| Attached | Number of people in the tree who already have the record attached to them |
| Duplicates | Number of people on the record already attached to someone different in the tree |
| Error | Page for this hint didn't load for some reason |
| Hint_ID | The hint ID that lines up with the input file |
| Missing | People in the family on the tree who aren't included on the record |
| URL | The URL of the hint source linker page (what gets scraped) |

#### Logs
 - **app.log**: log of last run of `teh_scrape.py`
 - **debug.log**: log from Selenium about webdriver details
 - **results_temp.csv**: created during processings, deleted upon successful completion

## Installation

Requires Python 3.6+, Selenium 2, Google Chrome 72+, and BeautifulSoup 4 to run.

Install Chrome and Python. Then install the dependencies.
```
$ python
>>> pip install selenium BeautifulSoup
```

Upload your csv file to `.\data\`. Each time you run the program you will be asked for the input file unless explicitly stated in the configuration. (To configure the program to use the same input file name, in `teh_scrape.py` you can set `SCRAPE_FILE` under `CONFIG` to the name of your url data file.)

Run the program in dedicated console:
```
$ python
>>> runfile(teh_scrape.py)
```

#### Default Configuration
```
SCRAPE_FILE = '' #in ./data directory
TEMP_BATCH_SIZE = 20 #records
LOAD_DELAY_TIME = 6 #seconds
RANDOMIZE_MAX = 6 #seconds
CLOSE_DELAY_TIME = 3 #seconds
MAX_FAILED_AUTH = 3 #attempts
IMPLICITLY_WAIT = 5 #seconds
PAGE_LOAD_TIMEOUT = 20 #seconds
MAX_TIMEOUTS = 3 #excpetions
```

## About

##### Authors
Clark Brown, Brigham Young University

##### License
MIT

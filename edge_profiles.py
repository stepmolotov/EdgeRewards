from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time
import random
import string

##### VARIABLES #####
EDGE_EXE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
EDGE_USER_DATA_PATH = "C:\\Users\\Stefan\\AppData\\Local\\Microsoft\\Edge\\User Data"
BING_SEARCH_LINK = "https://www.bing.com/search?q="

N_DESKTOP_SEARCHES = 34
N_MOBILE_SEARCHES = 20
WORD_LENGTH = 6
SLEEP_TIME = 2
##### ##### #####

options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.binary_location = EDGE_EXE_PATH
options.add_argument("user-data-dir=" + EDGE_USER_DATA_PATH)
options.add_argument('--profile-directory=Profile 1')
#options.add_argument("headless")

driver = webdriver.Edge(options=options)

driver.get(BING_SEARCH_LINK + "hello")

time.sleep(2*SLEEP_TIME)
driver.quit()
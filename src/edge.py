import os
from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time
import random
import string

##### VARIABLES #####
USERNAME = "Stepm"
PROFILES = ['Default', 'Profile 1', 'Default2', 'Profile 2', 'Profile 3', 'Profile 4']
# PROFILES = ['Personale', 'Personale 1', 'Personale 2']

EDGE_EXE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
EDGE_USER_DATA_PATH = "C:\\Users\\" + USERNAME + "\\AppData\\Local\\Microsoft\\Edge\\User Data"
BING_SEARCH_LINK = "https://www.bing.com/search?q="

N_DESKTOP_SEARCHES = 34
N_MOBILE_SEARCHES = 20
WORD_LENGTH = 6
SLEEP_TIME = 1

PORT = 0

EDGE_KILL_COMMAND = "taskkill /f /im msedge.exe"


##### ##### #####


##### AUX FUN #####
def getSearchWords(n=10, length=WORD_LENGTH):
    # Generates a list of N words with chosen length
    words = []
    letters = string.ascii_lowercase
    for i in range(n):
        random_word = ''.join(random.choice(letters) for l in range(length))
        words.append(random_word)
    # print('\t' + str(words))
    return words


def printProgression(word, current, total):
    # prints searched word to track progression
    print("\t[" + str(current + 1) + "/" + str(total) + "]" + "\t Searched for: " + word)


def killEdgeProcesses():
    os.system(EDGE_KILL_COMMAND)


##### ##### #####

# class SearchSession():
#
# 	def __init__(self):
# 		self.__options = self.__options_setup()
#
# 	def __options_setup(self) -> Options:
# 		options = Options()
# 		options.add_experimental_option('excludeSwitches', ['enable-logging'])
# 		options.binary_location = EDGE_EXE_PATH
# 		options.add_argument("user-data-dir=" + EDGE_USER_DATA_PATH)
# 		options.add_argument('--profile-directory=' + profile)
# 		# options.add_argument("headless")
# 		return options

##### WEBDRIVER #####
def run_searches():
    killEdgeProcesses()
    for i, profile in enumerate(PROFILES):
        print("\n* Profile: " + profile + " [" + str(i + 1) + "/" + str(len(PROFILES)) + "]")
        print("*** Generating random words:")
        desktop_search_words = getSearchWords(n=N_DESKTOP_SEARCHES)
        mobile_search_words = getSearchWords(n=N_MOBILE_SEARCHES)
        print(" ")

        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.binary_location = EDGE_EXE_PATH
        options.add_argument("user-data-dir=" + EDGE_USER_DATA_PATH)
        options.add_argument('--profile-directory=' + profile)
        # options.add_argument("headless")

        # Desktop Searches
        print("*** Desktop Searches: " + str(N_DESKTOP_SEARCHES))
        driver = webdriver.Edge(options=options)
        for i, word in enumerate(desktop_search_words):
            driver.get(BING_SEARCH_LINK + word)
            printProgression(word, i, N_DESKTOP_SEARCHES)
            time.sleep(SLEEP_TIME)
        time.sleep(2 * SLEEP_TIME)
        print(" ")
        driver.quit()

        # Mobile Searches
        mobile_emulation = {
            "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        # options.add_argument("headless")
        # options.add_argument('--remote-debugging-port=' + str(PORT))
        print("*** Mobile Searches: " + str(N_MOBILE_SEARCHES))
        driver = webdriver.Edge(options=options)
        for i, word in enumerate(mobile_search_words):
            driver.get(BING_SEARCH_LINK + word)
            printProgression(word, i, N_MOBILE_SEARCHES)
            time.sleep(SLEEP_TIME)
        time.sleep(2 * SLEEP_TIME)
        print(" ")
        driver.quit()

##### ##### #####


if __name__ == '__main__':
    run_searches()

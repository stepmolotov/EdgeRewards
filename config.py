##### VARIABLES #####
USERNAME = "Stepm"
# PROFILES = ["Default", "Profile 1", "Default2", "Profile 2", "Profile 3", "Profile 4"]
PROFILES = ["Profile 4"]

EDGE_EXE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
EDGE_USER_DATA_PATH = (
    "C:\\Users\\" + USERNAME + "\\AppData\\Local\\Microsoft\\Edge\\User Data"
)
BING_SEARCH_LINK = "https://www.bing.com/search?q="
REWARDS_HOMEPAGE = "https://rewards.bing.com/"

N_DESKTOP_SEARCHES = 34
N_MOBILE_SEARCHES = 20
WORD_LENGTH = 6
SLEEP_TIME = 1

PORT = 0

EDGE_KILL_COMMAND = 'taskkill /f /im msedge.exe /t /fi "status eq running">nul'
##### ##### #####

##### VARIABLES #####
#
# All configuration values can be overridden via environment variables.
# Defaults below are tuned for the original Windows setup so the script
# continues to work locally with no env changes.
#
import os
import sys

USERNAME = os.environ.get("USERNAME", "Stepm")

# Comma-separated list, e.g. "Default,Profile 1,Profile 2"
PROFILES = [
    p.strip() for p in os.environ.get("EDGE_PROFILES", "Default").split(",") if p.strip()
]

if sys.platform.startswith("win"):
    EDGE_EXE_PATH = os.environ.get(
        "EDGE_EXE_PATH",
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    )
    EDGE_USER_DATA_PATH = os.environ.get(
        "EDGE_USER_DATA_PATH",
        "C:\\Users\\" + USERNAME + "\\AppData\\Local\\Microsoft\\Edge\\User Data",
    )
    EDGE_KILL_COMMAND = os.environ.get(
        "EDGE_KILL_COMMAND",
        'taskkill /f /im msedge.exe /t /fi "status eq running">nul',
    )
else:
    # Linux / macOS defaults (used inside the Docker container)
    EDGE_EXE_PATH = os.environ.get("EDGE_EXE_PATH", "/usr/bin/microsoft-edge")
    EDGE_USER_DATA_PATH = os.environ.get("EDGE_USER_DATA_PATH", "/profile")
    EDGE_KILL_COMMAND = os.environ.get(
        "EDGE_KILL_COMMAND",
        "pkill -f msedge >/dev/null 2>&1 || true",
    )

# Optional: path to a pre-installed msedgedriver binary. When set,
# webdriver_manager will not attempt to download a driver at runtime.
EDGE_DRIVER_PATH = os.environ.get("EDGE_DRIVER_PATH", "")

# Optional: space-separated extra Edge args (e.g. "--no-sandbox --disable-dev-shm-usage")
# Required when running Edge as root inside a Docker container.
EDGE_EXTRA_ARGS = os.environ.get("EDGE_EXTRA_ARGS", "")

BING_SEARCH_LINK = "https://www.bing.com/search?q="
QUERY_PLACEHOLDER = "#####"
BING_UPDATED_SEARCH_LINK = f"https://www.bing.com/search?pglt=41&PC=U523&q={QUERY_PLACEHOLDER}&FORM=ANNTA1"
REWARDS_HOMEPAGE = "https://rewards.bing.com/"

WORD_LIST_PATH = "resources/1000_parole_italiane_comuni.txt"

N_DESKTOP_SEARCHES = 12  # 34
N_MOBILE_SEARCHES = 6  # 22
WORD_LENGTH = 6
SLEEP_TIME = 2

PORT = 0
##### ##### #####

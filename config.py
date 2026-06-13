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

# Legacy search runner (src/edge.py) — collect_points.py uses SEARCH_COUNT_* instead.
N_DESKTOP_SEARCHES = 12  # 34
N_MOBILE_SEARCHES = 6  # 22
WORD_LENGTH = 6
SLEEP_TIME = 2

# Rewards dashboard search (desktop only, via textbox on rewards.bing.com)
ENABLE_DESKTOP_SEARCHES = (
    os.environ.get("ENABLE_DESKTOP_SEARCHES", "true").lower() == "true"
)
SEARCH_COUNT_MIN = int(os.environ.get("SEARCH_COUNT_MIN", "4"))
SEARCH_COUNT_MAX = int(os.environ.get("SEARCH_COUNT_MAX", "12"))
SEARCH_QUERY_MIN_LENGTH = int(os.environ.get("SEARCH_QUERY_MIN_LENGTH", "4"))
SEARCH_USE_PHRASES = os.environ.get("SEARCH_USE_PHRASES", "true").lower() == "true"
SEARCH_PHRASE_CHANCE = float(os.environ.get("SEARCH_PHRASE_CHANCE", "0.3"))

# Human-like delays between searches (seconds)
SEARCH_BETWEEN_MIN = float(os.environ.get("SEARCH_BETWEEN_MIN", "8"))
SEARCH_BETWEEN_MAX = float(os.environ.get("SEARCH_BETWEEN_MAX", "18"))
SEARCH_RESULTS_READ_MIN = float(os.environ.get("SEARCH_RESULTS_READ_MIN", "4"))
SEARCH_RESULTS_READ_MAX = float(os.environ.get("SEARCH_RESULTS_READ_MAX", "10"))
SEARCH_LONG_PAUSE_EVERY = int(os.environ.get("SEARCH_LONG_PAUSE_EVERY", "4"))
SEARCH_LONG_PAUSE_MIN = float(os.environ.get("SEARCH_LONG_PAUSE_MIN", "45"))
SEARCH_LONG_PAUSE_MAX = float(os.environ.get("SEARCH_LONG_PAUSE_MAX", "90"))

PORT = 0
##### ##### #####

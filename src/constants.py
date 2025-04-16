import json
import os

sep = os.sep


with open("config.json") as f:
    JSON_CONFIG = json.load(f)

def get_path(key: str, default:str):
    return JSON_CONFIG.get(key,  default).replace("/", os.sep) 

USERS_SAVE_PATH = get_path("USERS_SAVE_PATH",  "save/users")
TWEETS_SAVE_PATH = get_path("TWEETS_SAVE_PATH",  "save/tweets")
MEDIA_SAVE_PATH = get_path("MEDIA_SAVE_PATH",  "save/media")
DM_SAVE_PATH = get_path("DM_SAVE_PATH",  "save/dms")
DM_USERS_SAVE_PATH = get_path("DM_USERS_SAVE_PATH",  "save/dms/users")

FEATURES = JSON_CONFIG["FEATURES"]

USER_ID = JSON_CONFIG["USER_ID"]
USERNAME = JSON_CONFIG["USERNAME"]

HEADERS = JSON_CONFIG["HEADERS"]


ALREADY_KNOWN_BOOKMARKS: list = []
bp = f"{TWEETS_SAVE_PATH}{sep}bookmarks.json"
if os.path.exists(bp):
    with open(bp) as f:
        ALREADY_KNOWN_BOOKMARKS = json.load(f)

ALREADY_KNOWN_BOOKMARK_SORT_INDEXES: list[str] = [x["sort_index"] for x in ALREADY_KNOWN_BOOKMARKS]


DM_INITIAL_URL_PARAMETERS = JSON_CONFIG["DM_INITIAL_URL_PARAMETERS"]

DM_TIMELINE_URL_PARAMETER = JSON_CONFIG["DM_TIMELINE_URL_PARAMETER"]

GOOD_REPORT_URL = JSON_CONFIG.get("GOOD_REPORT_URL")
BAD_REPORT_URL = JSON_CONFIG.get("BAD_REPORT_URL")
WARN_REPORT_URL = JSON_CONFIG.get("WARN_REPORT_URL")

CLIENT_NAME = JSON_CONFIG.get("CLIENT_NAME", "unspecified")
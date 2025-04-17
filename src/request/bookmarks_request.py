
import json
from typing import Optional

import httpx

from constants import ALREADY_KNOWN_BOOKMARK_SORT_INDEXES, FEATURES, HEADERS
from objects.tweet import Tweet

import urllib.parse

from utilities.logger import LOGGER
from utils import Err


class BookmarkRequest:
    user_id: str
    cursor: Optional[str]
    vars: str

    action_id = "ztCdjqsvvdL0dE8R5ME0hQ"
    action_name = "Bookmarks"
    
    # Result
    content: dict
    tweets: list[Tweet]
    next_cursor: str | None
    found_known_tweet: bool

    def __init__(self, user_id: str, cursor: str | None = None):
        self.user_id = user_id
        self.cursor = cursor
        self.found_known_tweet = False

        self.tweets: list[Tweet] = []
        self.next_cursor = None

        vars = f"%7B%22count%22%3A20%2C%22"
        if (cursor is not None):
            vars += f"cursor%22%3A%22{urllib.parse.quote(cursor, safe='')}%22%2C%22"

        vars += "includePromotedContent%22%3Atrue%7D" # true bc its like that on the web.
        self.vars = vars
    
    # Should do everything and handle error logging.
    # TODO: HANDLE ERRORS BETTER.
    def do_all(self):
        try:
            self.request_content()
            self.perform_instructions()
        except Exception as e:
            LOGGER.error(f"Couldn't perform/parse bookmark request.", additional=[Err.from_exception(e), Err("Request Content", self.content)])

    def request_content(self):
        r = httpx.get(
            f"https://x.com/i/api/graphql/{self.action_id}/{self.action_name}?variables={self.vars}&features={FEATURES}",
            headers=HEADERS
        )
        if (r.status_code != 200):
            raise Exception(f"Non 200 error code: {r.status_code}")

        self.content = json.loads(r.content.decode())
    
    def perform_instructions(self):
        assert self.content is not None, "The content is empty. Make sure you've requested the content before."

        found_entries = False

        instructions = self.content['data']['bookmark_timeline_v2']['timeline']['instructions']

        for instruction in instructions:
            type: str = instruction['type']
            if type == 'TimelineAddEntries':
                found_entries = True
                self.parse_entries(instruction)
            else:
                LOGGER.warn(f"Unknown bookmark instruction type: {type}", additional=[Err("Instruction", instruction), Err("Request Content", self.content)])

        assert found_entries is True, "Couldn't find the entries instruction"
                
    
    def parse_entries(self, entries_instruction):
        for entry in entries_instruction['entries']:
            try:
                id: str = entry['entryId']
                content = entry['content']
                type: str = id.split("-")[0]
                if type == "cursor":
                    cursor_type = content['cursorType']
                    if cursor_type == 'Bottom': # Ignore top ones, we always start at the top.
                        self.next_cursor = content['value']
                
                elif type == "tweet":
                    sort_index = entry["sortIndex"]
                    user_res = content['itemContent']['tweet_results']['result']
                    self.tweets.append(Tweet(user_res, sort_index))
                    if sort_index in ALREADY_KNOWN_BOOKMARK_SORT_INDEXES:
                        self.found_known_tweet = True
                else:
                    LOGGER.warn(f"Unknown bookmark entry type: {type}", additional=[Err("Current entry", entry), Err("All content", self.content)])
            except Exception as e:
                LOGGER.error(f"Couldn't parse bookmark entry of type {type}", additional=[Err.from_exception(e), Err("Current entry", entry), Err("Request Content", self.content)])
import json
from typing import Literal, Optional

import httpx
from constants import FEATURES, HEADERS
from objects.person import Person
import urllib.parse

from utilities.logger import LOGGER
from utils import Err


class FollowTabRequest:
    user_id: str
    action_id: str
    action_name: str
    cursor: Optional[str]
    vars: str

    # Result
    content: dict
    people: list[Person]
    next_cursor: str | Literal[False] | None

    def __init__(self, user_id: str, action_id: str, action_name: str, cursor: str | None = None):
        self.user_id = user_id
        self.action_id = action_id
        self.action_name = action_name
        self.cursor = cursor

        self.people = []
        self.next_cursor = None

        vars = f"%7B%22userId%22%3A%22{user_id}%22%2C%22count%22%3A20%2C%22"
        if (cursor is not None):
            vars += f"cursor%22%3A%22{urllib.parse.quote(cursor, safe='')}%22%2C%22"

        vars += "includePromotedContent%22%3Afalse%7D"
        self.vars = vars

    
    # Should do everything and handle error logging.
    # TODO: HANDLE ERRORS BETTER.
    def do_all(self):
        self.request_content()
        self.perform_instructions()

    def request_content(self):
        r = httpx.get(
            f"https://x.com/i/api/graphql/{self.action_id}/{self.action_name}?variables={self.vars}&features={FEATURES}",
            headers=HEADERS
        )
        if (r.status_code != 200):
            raise Exception(f"Non 200 error code: {r.status_code}")

        self.content = json.loads(r.content.decode())
    
    def perform_instructions(self):
        assert self.content is not None

        found_entries = False

        instructions = self.content['data']['user']['result']['timeline']['timeline']['instructions']

        for instruction in instructions:
            type: str = instruction['type']
            if type == 'TimelineClearCache':
                pass # ignore
            elif type == 'TimelineTerminateTimeline':
                direction: str = instruction['direction']
                pass # todo: Maybe do smth? Can just use the cursor tho for that so unsure if rly required.
            elif type == 'TimelineAddEntries':
                found_entries = True
                self.parse_entries(instruction)
            else:
                LOGGER.warn(f"Unknown follow tab ({self.action_name}) instruction type: {type}", additional=[Err("Instruction", instruction), Err("Request Content", self.content)])
        

        assert found_entries is True
                
    
    def parse_entries(self, entries_instruction):
        for entry in entries_instruction['entries']:
            id: str = entry['entryId']
            content = entry['content']
            # type: str = "-".join(id.split("-")[:-1])
            type: str = id.split("-")[0]
            if type == "cursor":
                cursor_type = content['cursorType']
                if cursor_type == 'Bottom': # Ignore top ones, we always start at the top.
                    # if first id is 0, that means we're at the bottom so all good.
                    next_cursor_val = content['value']
                    if next_cursor_val.split("|")[0] == '0':
                        self.next_cursor = False
                    else:
                        self.next_cursor = next_cursor_val
            
            elif type == "user":
                user_res = content['itemContent']['user_results']['result']
                self.people.append(Person(user_res))
            else:
                LOGGER.warn(f"Unknown follow tab ({self.action_name}) entry type: {type}", additional=[Err("Current entry", entry), Err("Request Content", self.content)])

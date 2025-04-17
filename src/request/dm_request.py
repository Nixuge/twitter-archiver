
import json
from typing import Callable, Optional

import httpx

from constants import DM_INITIAL_URL_PARAMETERS, DM_TIMELINE_URL_PARAMETER, HEADERS
from objects.dm_conversation import DmConversation
from objects.dm_person import DmPerson
from utilities.logger import LOGGER
from utils import Err


class DmRequest:
    cursor: Optional[str]
    
    # TODO: Save DMs too.
    # Result
    # entries: list[DmMessageEntry]
    users: list[DmPerson]
    conversations: list[DmConversation]
    next_id: str | None

    content: dict
    processor: Callable

    def __init__(self, start_id: str | None = None):
        self.cursor = start_id
        self.next_id = None

        self.entries = []
        self.users = []
        self.conversations = []
    
    # Should do everything and handle error logging.
    # TODO: HANDLE ERRORS BETTER.
    def do_all(self):
        try:
            self.request_content()
            self.processor()
        except Exception as e:
            LOGGER.error(f"Couldn't perform/parse DMs request.", additional=[Err.from_exception(e), Err("Request Content", self.content)])

    def request_content(self):
        if self.cursor == None:
            url = "https://x.com/i/api/1.1/dm/user_updates.json" + DM_INITIAL_URL_PARAMETERS
            self.processor = self._parse_initial
        else:
            url = "https://x.com/i/api/1.1/dm/inbox_timeline/trusted.json" + DM_TIMELINE_URL_PARAMETER.replace("%MAX_ID%", self.cursor)
            self.processor = self._parse_next
        
        r = httpx.get(url, headers=HEADERS)
        if (r.status_code != 200):
            raise Exception(f"Non 200 error code: {r.status_code}")
        
        self.content = json.loads(r.content.decode())
    
    def _parse_initial(self):
        assert self.content is not None, "The content is empty. Make sure you've requested the content before."
        data = self.content["inbox_initial_state"]

        # There's also untrusted & untrusted_low_quality but assuming
        # we don't rly need those.
        status = data["inbox_timelines"]["trusted"]["status"]
        if status == "HAS_MORE":
            self.next_id = data["inbox_timelines"]["trusted"]["min_entry_id"]
        elif status == "AT_END":
            pass
        else:
            LOGGER.warn(f"Unknown DM request status: {status}", additional=[Err("Data", data), Err("DM Request Content", self.content)])
        
        self._parse_shared(data)


    def _parse_next(self, content: dict):
        self._parse_shared(content["inbox_timeline"])
    
    def _parse_shared(self, inner_content: dict):
        for _user_id, user_dict in inner_content["users"].items():
            self.users.append(DmPerson(user_dict))
        
        for _conv_id, conv_dict in inner_content["conversations"].items():
            self.conversations.append(DmConversation(conv_dict))

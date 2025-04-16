import json

from constants import USER_ID, USERS_SAVE_PATH
from objects.person import Person
from request.follow_tab_request import FollowTabRequest
from utilities.logger import LOGGER


class Saver:
    user_id: str
    action_id: str
    action_name: str
    action_title: str

    grabbed: list[Person]

    def __init__(self, user_id: str, action_id: str, action_name: str):
        self.user_id = user_id
        self.action_id = action_id
        self.action_name = action_name
        self.action_title = action_name.lower()

        self.grabbed = []
    
    def _perform_iteration(self, cursor: str | None = None):
        LOGGER.debug("Performing iteration.")
        req = FollowTabRequest(
            user_id=USER_ID,
            action_id=self.action_id,
            action_name=self.action_name,
            cursor=cursor
        )

        req.do_all()

        self.grabbed += req.people
        return req.next_cursor

    def grab_all_for_action(self):
        next_cursor = self._perform_iteration()
        while next_cursor:
            next_cursor = self._perform_iteration(next_cursor)

        LOGGER.debug(f"Found {len(self.grabbed)} {self.action_title}")

    def just_save_grabbed_no_git(self):
        for person in self.grabbed:
            person.save_to_file()
        
        followed = [(x.user_dict['rest_id'], x.user_dict['legacy']['screen_name']) for x in self.grabbed]
        json_string = "[\n    " + ",\n    ".join([json.dumps(follower) for follower in followed]) + "\n]"

        with open(f"{USERS_SAVE_PATH}/{self.action_title}.json", 'w') as f:
            f.write(json_string)
import json
import os

from constants import DM_SAVE_PATH

class DmConversation:
    DM_CONVERSATION_CACHE: list[str] = []

    dm_conversation_dict: dict
    def __init__(self, user_dict: dict):
        self.dm_conversation_dict = user_dict
        # checks to make sure the dict is a conversation
        user_dict["conversation_id"]
        user_dict["type"]
        user_dict["last_read_event_id"]
        user_dict["muted"]
        user_dict["status"]

    def save_to_file(self):
        uid = self.dm_conversation_dict["conversation_id"]

        if uid in DmConversation.DM_CONVERSATION_CACHE:
            return

        save_folder = f"{DM_SAVE_PATH}{os.sep}"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        if not os.path.exists(f"{save_folder}.git"):
            # TODO: Handle when not found (also handle windows)
            os.system(f"cd {save_folder} && git init")

        
        with open(f"{save_folder}{uid}.json", 'w') as f: #unique id
            json.dump(self.dm_conversation_dict, f, indent=4)
        
        DmConversation.DM_CONVERSATION_CACHE.append(uid)
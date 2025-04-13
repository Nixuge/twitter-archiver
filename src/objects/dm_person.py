import json
import os

from constants import DM_USERS_SAVE_PATH

class DmPerson:
    DM_PERSON_CACHE: list[str] = []

    dm_user_dict: dict
    def __init__(self, user_dict: dict):
        self.dm_user_dict = user_dict
        # checks to make sure the dict is an user
        user_dict["id_str"]
        user_dict["id"]
        user_dict["screen_name"]
        user_dict["location"]
        user_dict["can_dm"]

    def save_to_file(self):
        uid = self.dm_user_dict["id_str"]

        if uid in DmPerson.DM_PERSON_CACHE:
            return

        save_folder = f"{DM_USERS_SAVE_PATH}{os.sep}"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        # if not os.path.exists(f"{save_folder}.git"):
            # TODO: Handle when not found (also handle windows)
            # os.system(f"cd {save_folder} && git init")

        
        with open(f"{save_folder}{uid}.json", 'w') as f: #unique id
            json.dump(self.dm_user_dict, f, indent=4)
        
        DmPerson.DM_PERSON_CACHE.append(uid)
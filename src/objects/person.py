import json
import os

from constants import USERS_SAVE_PATH

class Person:
    PERSON_CACHE: list[str] = []

    user_dict: dict
    def __init__(self, user_dict: dict):
        self.user_dict = user_dict
        # checks to make sure the dict is an user
        user_dict["rest_id"]
        user_dict["is_blue_verified"]
        user_dict["legacy"]["description"]
        user_dict["legacy"]["name"]
        user_dict["legacy"]["screen_name"]

    def save_to_file(self):
        uid = self.user_dict["rest_id"]

        if uid in Person.PERSON_CACHE:
            # print("Already saved id: " + uid)
            return

        save_folder = f"{USERS_SAVE_PATH}{os.sep}"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        if not os.path.exists(f"{save_folder}.git"):
            os.system(f"cd {save_folder} && git init")

        
        with open(f"{save_folder}{uid}.json", 'w') as f: #unique id
            json.dump(self.user_dict, f, indent=4)
        
        Person.PERSON_CACHE.append(uid)
import asyncio
from curses.ascii import US
import logging
import os
import time
from constants import CLIENT_NAME, DM_SAVE_PATH, TWEETS_SAVE_PATH, USER_ID, USERS_SAVE_PATH
from saver.bookmark_saver import BookmarkSaver
from saver.dm_saver import DmSaver
from saver.follow_tab_saver import Saver
from utilities.logger import LOGGER
from utilities.webhook import WEBHOOK_MANAGER
import utils

#TODO: make sure headers are legit (mainly change referer and see for bookmarks)

#TODO: Seem to be missing some DMs :/



# TODO: Save media including picture (? will attempt.)
# TODO: Use DB with as keys rest_id (+user rest_id for bookmarks)
# TODO: Find tweets with 4K videos/pictures


# TODO: handle fails here.
# Eg save to another dict & then move to main folder on success 
async def main():
    start_time = time.time_ns()

    saver_following = Saver(
        user_id=USER_ID,
        action_id="4QHbs4wmzgtU91f-t96_Eg",
        action_name="Following"
    )
    saver_follower = Saver(
        user_id=USER_ID,
        action_id="jqZ0_HJBA6mnu18iTZYm9w",
        action_name="Followers"
    )
    saver_bookmarks = BookmarkSaver(
        user_id=USER_ID
    )

    saver_dms = DmSaver()

    os.system(f"cd {USERS_SAVE_PATH} && rm *.json")
    # os.system(f"cd {TWEETS_SAVE_PATH} && rm *.json")

    LOGGER.info("Saving all followings...")
    saver_following.grab_all_for_action()
    saver_following.just_save_grabbed_no_git()
    LOGGER.info("Done saving all followings !")

    LOGGER.info("Saving all followers...")
    saver_follower.grab_all_for_action()
    saver_follower.just_save_grabbed_no_git()
    LOGGER.info("Done saving all followers !")

    LOGGER.info("Saving new bookmarks...")
    saver_bookmarks.grab_all_for_action()
    saver_bookmarks.just_save_grabbed_and_prev_no_git()
    LOGGER.info("Done saving new bookmarks !")

    LOGGER.info("Saving all DM conversations...")
    saver_dms.grab_all_for_action()
    saver_dms.just_save_grabbed_no_git()
    LOGGER.info("Done saving new conversations !")

    time_rn = utils.get_formatted_cet_time()

    LOGGER.info("Updating git repos...")

    for path, updated in (
        (USERS_SAVE_PATH, "following & followers"),
        (TWEETS_SAVE_PATH, "bookmarks"),
        (DM_SAVE_PATH, "DMs")
        ):
        LOGGER.info(f"Updating the {updated} git repo...")
        os.system(f"cd {path} && git add . && git commit -m \"Updated {updated}: {time_rn}\"")

    WEBHOOK_MANAGER.queue_webhook(logging.INFO,
                  "Done updating !", 
                  f"Stats:\n\
                    - Total followers: {len(saver_follower.grabbed)}\n\
                    - Total following: {len(saver_following.grabbed)}\n\
                    - New bookmarks: {len(saver_bookmarks.new_bookmarks)}\n\
                    - Total DMs: {(len(saver_dms.grabbed_conversations))} DMs with {len(saver_dms.grabbed_users)} people.\
                  ".replace("                    ", ""),
                  footer=f"Took {(time.time_ns() - start_time)/1000000000}s ({CLIENT_NAME})")

    LOGGER.info("Done updating git repos ! Now waiting to cleanup webhook tasks...")
        
    WEBHOOK_MANAGER.terminate_gracefully()


if __name__ == "__main__":
    asyncio.run(main())
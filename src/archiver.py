from curses.ascii import US
import os
from constants import DM_SAVE_PATH, TWEETS_SAVE_PATH, USER_ID, USERS_SAVE_PATH
from saver.bookmark_saver import BookmarkSaver
from saver.dm_saver import DmSaver
from saver.follow_tab_saver import Saver
import utils



#TODO: make sure headers are legit (mainly change referer and see for bookmarks)

#TODO: Seem to be missing some DMs :/



# TODO: Save media including picture (? will attempt.)
# TODO: Discord webhook on error.
# TODO: make sure the constants eg in headers don't change.
# TODO: Use DB with as keys rest_id (+user rest_id for bookmarks)
# TODO: Find tweets with 4K, video, multiple videos.

# TODO: handle fails here.
# Eg save to another dict & then move to main folder on success 
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


saver_following.grab_all_for_action()
saver_following.just_save_grabbed_no_git()

saver_follower.grab_all_for_action()
saver_follower.just_save_grabbed_no_git()

saver_bookmarks.grab_all_for_action()
saver_bookmarks.just_save_grabbed_and_prev_no_git()

saver_dms.grab_all_for_action()
saver_dms.just_save_grabbed_no_git()

time_rn = utils.get_formatted_cet_time()

for path, updated in (
    (USERS_SAVE_PATH, "following & followers"),
    (TWEETS_SAVE_PATH, "bookmarks"),
    (DM_SAVE_PATH, "DMs")
    ):
    os.system(f"cd {path} && git add . && git commit -m \"Updated {updated}: {time_rn}\"")

import json
from constants import ALREADY_KNOWN_BOOKMARK_SORT_INDEXES, ALREADY_KNOWN_BOOKMARKS, TWEETS_SAVE_PATH, USER_ID
from objects.tweet import Tweet
from request.bookmarks_request import BookmarkRequest
from utilities.logger import LOGGER

# Flaw: Doesn't save deletions.
# Fix: since we already stop when we hit a known id, just 
# remove tweets in the oringial json if they aren't here anymore
# Except i like backing up shit :D

#TODO: Make sure this works if saving multiple bookmark pages at once!!!

class BookmarkSaver:
    user_id: str

    action_id = "ztCdjqsvvdL0dE8R5ME0hQ"
    action_name = "Bookmarks"

    # action_title: str

    previous_tweets: list[str]
    grabbed_tweets: list[Tweet]
    new_bookmarks: list

    def __init__(self, user_id: str):
        self.user_id = user_id
        # self.action_title = action_name.lower()

        self.grabbed_tweets = []
    
    def _perform_iteration(self, cursor: str | None = None):
        LOGGER.debug("Performing iteration.")
        req = BookmarkRequest(
            user_id=USER_ID,
            cursor=cursor
        )

        req.do_all()

        self.grabbed_tweets += req.tweets
        return req.found_known_tweet, req.next_cursor

    def grab_all_for_action(self):
        # Stop when the next request is empty.
        # TODO: Handle fails.
        grabbed_user_count = 0 
        found_known_tweet, next_cursor = self._perform_iteration()
        while len(self.grabbed_tweets) != grabbed_user_count and not found_known_tweet:
            grabbed_user_count = len(self.grabbed_tweets)
            found_known_tweet, next_cursor = self._perform_iteration(next_cursor)

        if found_known_tweet:
            LOGGER.debug("Found previous tweet: stopped prematurely.")

        LOGGER.debug(f"Found {len(self.grabbed_tweets)} bookmarks")

        self.new_bookmarks = [{
            "author_id": x.tweet_poster.user_dict['rest_id'],
            "author_screen_name": x.tweet_poster.user_dict['legacy']['screen_name'],
            "tweet_id": x.tweet_dict['rest_id'],
            "sort_index": x.sort_index
        } for x in self.grabbed_tweets if x.sort_index not in ALREADY_KNOWN_BOOKMARK_SORT_INDEXES]
        
        LOGGER.debug(f"New bookmark count: {len(self.new_bookmarks)}")


    def just_save_grabbed_and_prev_no_git(self):
        for tweet in self.grabbed_tweets:
            tweet.save_tweet_only_to_file()
            tweet.tweet_poster.save_to_file()
            tweet.save_all_media()
        
        bookmarks = self.new_bookmarks + ALREADY_KNOWN_BOOKMARKS
        LOGGER.debug(f"Total bookmark count: {len(bookmarks)}")

        with open(f"{TWEETS_SAVE_PATH}/bookmarks.json", 'w') as f:
            json.dump(bookmarks, f, indent=4)